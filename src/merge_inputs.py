from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import DEFAULT_INPUT_FILES, MANUAL_DIR, PROCESSED_DIR, RAW_DIR, UPSTREAM_DIR
from .demo_data import generate_demo_inputs
from .utils import ensure_directories, save_dataframe


def _first_matching_column(df: pd.DataFrame, candidates: tuple[str, ...], label: str) -> str:
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    raise ValueError(f"{label} is missing one of the required columns: {', '.join(candidates)}")


def _rename_to_exposure_id(df: pd.DataFrame) -> pd.DataFrame:
    id_column = _first_matching_column(df, ("exposure_id", "facility_id", "loan_id"), "Source data")
    if id_column == "exposure_id":
        return df.copy()
    return df.rename(columns={id_column: "exposure_id"})


def _validate_unique_ids(df: pd.DataFrame, source_name: str) -> None:
    duplicate_ids = df.loc[df.duplicated("exposure_id", keep=False), "exposure_id"].unique()
    if len(duplicate_ids) > 0:
        duplicates = ", ".join(sorted(map(str, duplicate_ids[:5])))
        raise ValueError(f"{source_name} contains duplicate exposure identifiers: {duplicates}")


def _ensure_source_files(
    raw_dir: str | Path = RAW_DIR,
    upstream_dir: str | Path = UPSTREAM_DIR,
    manual_dir: str | Path = MANUAL_DIR,
    refresh_demo: bool = False,
) -> None:
    raw_path = Path(raw_dir)
    upstream_path = Path(upstream_dir)
    manual_path = Path(manual_dir)
    ensure_directories(raw_path, upstream_path, manual_path)
    required_files = (
        raw_path / "exposure_master.csv",
        upstream_path / "pd_output.csv",
        upstream_path / "lgd_output.csv",
        upstream_path / "ead_output.csv",
        manual_path / "capital_structure.csv",
    )
    if refresh_demo or any(not file_path.exists() for file_path in required_files):
        generate_demo_inputs(raw_dir=raw_path, upstream_dir=upstream_path, manual_dir=manual_path)


def _normalise_pd_output(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_to_exposure_id(df)
    if "pd_12m" not in out.columns:
        if "pd_final" in out.columns:
            out = out.rename(columns={"pd_final": "pd_12m"})
        else:
            raise ValueError("pd_output.csv must contain either pd_12m or pd_final")
    out = out[["exposure_id", "pd_12m"]].copy()
    out["pd_12m"] = pd.to_numeric(out["pd_12m"], errors="coerce")
    if out["pd_12m"].isna().any():
        raise ValueError("pd_output.csv contains non-numeric PD values")
    _validate_unique_ids(out, "pd_output.csv")
    return out


def _normalise_lgd_output(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_to_exposure_id(df)
    if "lgd_downturn" not in out.columns:
        if "lgd_final" in out.columns:
            out = out.rename(columns={"lgd_final": "lgd_downturn"})
        else:
            raise ValueError("lgd_output.csv must contain either lgd_downturn or lgd_final")
    out = out[["exposure_id", "lgd_downturn"]].copy()
    out["lgd_downturn"] = pd.to_numeric(out["lgd_downturn"], errors="coerce")
    if out["lgd_downturn"].isna().any():
        raise ValueError("lgd_output.csv contains non-numeric LGD values")
    _validate_unique_ids(out, "lgd_output.csv")
    return out


def _normalise_ead_output(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_to_exposure_id(df)
    if "ead_downturn" not in out.columns:
        if "ead" in out.columns:
            out["ead_downturn"] = out["ead"]
        else:
            raise ValueError("ead_output.csv must contain ead_downturn or ead")
    if "ead_central" not in out.columns:
        if "ead" in out.columns:
            out["ead_central"] = out["ead"]
        else:
            out["ead_central"] = out["ead_downturn"]
    out = out[["exposure_id", "ead_central", "ead_downturn"]].copy()
    out["ead_central"] = pd.to_numeric(out["ead_central"], errors="coerce")
    out["ead_downturn"] = pd.to_numeric(out["ead_downturn"], errors="coerce")
    if out[["ead_central", "ead_downturn"]].isna().any().any():
        raise ValueError("ead_output.csv contains non-numeric EAD values")
    _validate_unique_ids(out, "ead_output.csv")
    return out


def _normalise_exposure_master(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_to_exposure_id(df)
    if "product_type" not in out.columns and "facility_type" in out.columns:
        out = out.rename(columns={"facility_type": "product_type"})
    if "security_type" not in out.columns:
        out["security_type"] = "Unknown"
    if "default_flag" not in out.columns:
        out["default_flag"] = 0
    required_columns = [
        "exposure_id",
        "product_type",
        "segment",
        "industry",
        "security_type",
        "default_flag",
    ]
    missing_columns = [column for column in required_columns if column not in out.columns]
    if missing_columns:
        raise ValueError(f"exposure_master.csv is missing required columns: {', '.join(missing_columns)}")
    out = out[required_columns].copy()
    out["default_flag"] = pd.to_numeric(out["default_flag"], errors="coerce").fillna(0).astype(int)
    _validate_unique_ids(out, "exposure_master.csv")
    return out


def load_capital_structure(
    manual_dir: str | Path = MANUAL_DIR,
    raw_dir: str | Path = RAW_DIR,
    upstream_dir: str | Path = UPSTREAM_DIR,
    refresh_demo: bool = False,
) -> pd.DataFrame:
    _ensure_source_files(raw_dir=raw_dir, upstream_dir=upstream_dir, manual_dir=manual_dir, refresh_demo=refresh_demo)
    capital_path = Path(manual_dir) / "capital_structure.csv"
    capital_structure = pd.read_csv(capital_path)
    if "reporting_date" not in capital_structure.columns:
        capital_structure["reporting_date"] = ""
    for column in ("cet1_capital", "total_capital"):
        if column not in capital_structure.columns:
            raise ValueError(f"capital_structure.csv is missing required column: {column}")
        capital_structure[column] = pd.to_numeric(capital_structure[column], errors="coerce")
    if capital_structure[["cet1_capital", "total_capital"]].isna().any().any():
        raise ValueError("capital_structure.csv contains non-numeric capital values")
    return capital_structure[["reporting_date", "cet1_capital", "total_capital"]].copy()


def build_capital_input(
    raw_dir: str | Path = RAW_DIR,
    upstream_dir: str | Path = UPSTREAM_DIR,
    manual_dir: str | Path = MANUAL_DIR,
    processed_dir: str | Path = PROCESSED_DIR,
    refresh_demo: bool = False,
    persist: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    _ensure_source_files(raw_dir=raw_dir, upstream_dir=upstream_dir, manual_dir=manual_dir, refresh_demo=refresh_demo)
    processed_path = Path(processed_dir)
    ensure_directories(processed_path)

    exposure_master = _normalise_exposure_master(pd.read_csv(Path(raw_dir) / "exposure_master.csv"))
    pd_output = _normalise_pd_output(pd.read_csv(Path(upstream_dir) / "pd_output.csv"))
    lgd_output = _normalise_lgd_output(pd.read_csv(Path(upstream_dir) / "lgd_output.csv"))
    ead_output = _normalise_ead_output(pd.read_csv(Path(upstream_dir) / "ead_output.csv"))
    capital_structure = load_capital_structure(
        manual_dir=manual_dir,
        raw_dir=raw_dir,
        upstream_dir=upstream_dir,
        refresh_demo=False,
    )

    capital_input = (
        exposure_master.merge(pd_output, on="exposure_id", how="left")
        .merge(lgd_output, on="exposure_id", how="left")
        .merge(ead_output, on="exposure_id", how="left")
        .sort_values("exposure_id")
        .reset_index(drop=True)
    )

    numeric_columns = ["pd_12m", "lgd_downturn", "ead_central", "ead_downturn"]
    if capital_input[numeric_columns].isna().any().any():
        missing_rows = capital_input.loc[capital_input[numeric_columns].isna().any(axis=1), "exposure_id"].tolist()
        raise ValueError(f"Missing PD, LGD, or EAD values for exposures: {', '.join(missing_rows)}")

    ordered_columns = [
        "exposure_id",
        "pd_12m",
        "lgd_downturn",
        "ead_central",
        "ead_downturn",
        "product_type",
        "segment",
        "industry",
        "security_type",
        "default_flag",
    ]
    capital_input = capital_input[ordered_columns]

    if persist:
        save_dataframe(capital_input, processed_path / "capital_input.csv")

    return capital_input, capital_structure


if __name__ == "__main__":
    capital_input_df, capital_structure_df = build_capital_input(
        raw_dir=DEFAULT_INPUT_FILES["exposure_master"].parent,
        upstream_dir=DEFAULT_INPUT_FILES["pd_output"].parent,
        manual_dir=DEFAULT_INPUT_FILES["capital_structure"].parent,
        processed_dir=PROCESSED_DIR,
        refresh_demo=False,
        persist=True,
    )
    print(f"Prepared {len(capital_input_df)} rows in {PROCESSED_DIR / 'capital_input.csv'}")
    print(f"Capital structure rows loaded: {len(capital_structure_df)}")

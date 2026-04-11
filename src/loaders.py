from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import (
    MONITORING_INPUT_FILES,
    NUMERIC_PORTFOLIO_COLUMNS,
    PORTFOLIO_REQUIRED_COLUMNS,
    RAW_PORTFOLIO_FILE,
    REPORTING_DATE,
    TOP_OBLIGOR_COUNT,
    UPSTREAM_INPUT_FILES,
)


PORTFOLIO_COLUMNS = [
    "reporting_date",
    "borrower_id",
    "facility_id",
    "obligor_name",
    "segment",
    "industry",
    "product_type",
    "collateral_type",
    "geography",
    "limit_amount",
    "drawn_balance",
    "collateral_value",
    "maturity_years",
    "pd",
    "lgd",
    "ead",
]
DEMO_ROWS = [
    (REPORTING_DATE, "BOR001", "FAC001", "Harbour Steel Pty Ltd", "SME", "Manufacturing", "Term Loan", "General Security Agreement", "NSW", 1200000, 980000, 1500000, 3.0, 0.018, 0.42, 1040000),
    (REPORTING_DATE, "BOR002", "FAC002", "Civic Build Group", "SME", "Construction", "Overdraft", "General Security Agreement", "VIC", 800000, 690000, 620000, 1.0, 0.052, 0.58, 742000),
    (REPORTING_DATE, "BOR003", "FAC003", "Riverside Storage Trust", "Property", "Commercial Real Estate", "Commercial Mortgage", "Commercial Property Mortgage", "QLD", 2400000, 2100000, 3300000, 4.0, 0.034, 0.33, 2220000),
    (REPORTING_DATE, "BOR004", "FAC004", "Southern Foods Wholesale", "Trade Finance", "Wholesale Trade", "Working Capital Revolver", "Receivables and Inventory", "NSW", 1500000, 830000, 1180000, 2.5, 0.026, 0.47, 1100000),
    (REPORTING_DATE, "BOR005", "FAC005", "Pacific Imports Pty Ltd", "Trade Finance", "Retail Trade", "Trade Finance", "Receivables and Inventory", "VIC", 600000, 210000, 480000, 1.5, 0.041, 0.55, 420000),
    (REPORTING_DATE, "BOR006", "FAC006", "Metro Advisory Services", "Corporate", "Professional Services", "Guarantee", "Cash Cover and GSA", "NSW", 950000, 0, 900000, 2.0, 0.012, 0.36, 285000),
    (REPORTING_DATE, "BOR007", "FAC007", "Golden Plains Logistics", "Corporate", "Transport", "Equipment Finance", "Specific Equipment Security", "WA", 540000, 540000, 650000, 3.5, 0.013, 0.27, 540000),
    (REPORTING_DATE, "BOR008", "FAC008", "Laneway Hospitality Group", "SME", "Accommodation and Food Services", "Overdraft", "General Security Agreement", "VIC", 500000, 350000, 280000, 1.2, 0.087, 0.52, 402500),
    (REPORTING_DATE, "BOR009", "FAC009", "North Coast Exporters", "Corporate", "Import Export", "Working Capital Revolver", "Receivables and Inventory", "QLD", 650000, 450000, 250000, 2.0, 0.029, 0.44, 510000),
    (REPORTING_DATE, "BOR010", "FAC010", "Urban Projects Developments", "Property", "Property Development", "Property Development Facility", "Commercial Property Mortgage", "NSW", 2200000, 1750000, 2100000, 2.5, 0.041, 0.31, 2110000),
]


def ensure_directories(*paths: str | Path) -> None:
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def write_csv(df: pd.DataFrame, path: str | Path) -> None:
    target = Path(path)
    ensure_directories(target.parent)
    df.to_csv(target, index=False)


def _grade_from_pd(value: float) -> str:
    if value <= 0.015:
        return "A"
    if value <= 0.030:
        return "B"
    if value <= 0.060:
        return "C"
    if value <= 0.100:
        return "D"
    return "E"


def _read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(Path(path))


def _rename_aliases(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    alias_map = {
        "facility_id": ["exposure_id", "loan_id"],
        "limit_amount": ["limit", "approved_limit"],
        "drawn_balance": ["drawn", "current_balance", "balance"],
        "collateral_value": ["collateral", "security_value"],
        "maturity_years": ["maturity", "tenor_years"],
        "collateral_type": ["security_type"],
        "obligor_name": ["borrower_name", "customer_name"],
    }
    for target, aliases in alias_map.items():
        for alias in aliases:
            if alias in out.columns and alias != target:
                out = out.rename(columns={alias: target})
                break
    if "reporting_date" not in out.columns:
        out["reporting_date"] = REPORTING_DATE
    out["reporting_date"] = out["reporting_date"].fillna(REPORTING_DATE).astype(str)
    if "obligor_name" not in out.columns:
        out["obligor_name"] = out["borrower_id"].astype(str) if "borrower_id" in out.columns else ""
    if "collateral_type" not in out.columns:
        out["collateral_type"] = "Unsecured / Other"
    if "geography" not in out.columns:
        out["geography"] = "NSW"
    return out


def normalise_portfolio_input(raw_df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_aliases(raw_df)
    missing = [column for column in PORTFOLIO_REQUIRED_COLUMNS if column not in out.columns]
    if missing:
        raise ValueError(f"Portfolio input is missing required columns: {', '.join(missing)}")
    for column in NUMERIC_PORTFOLIO_COLUMNS:
        out[column] = pd.to_numeric(out[column], errors="coerce")
    if out[NUMERIC_PORTFOLIO_COLUMNS].isna().any().any():
        raise ValueError("Portfolio input contains invalid numeric fields")
    ordered = PORTFOLIO_REQUIRED_COLUMNS + [column for column in ("pd", "lgd", "ead") if column in out.columns]
    return out[ordered].copy()


def _demo_portfolio() -> pd.DataFrame:
    return pd.DataFrame(DEMO_ROWS, columns=PORTFOLIO_COLUMNS)


def _demo_upstream(portfolio_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    expected = portfolio_df[["reporting_date", "facility_id", "pd", "lgd", "ead"]].copy()
    expected["expected_loss"] = expected["pd"] * expected["lgd"] * expected["ead"]
    stress = expected[["reporting_date", "facility_id", "expected_loss"]].copy()
    stress["stress_scenario"] = "management_downturn"
    stress["stressed_loss"] = (stress["expected_loss"] * 1.35).round(2)
    return {
        "pd_output": portfolio_df[["reporting_date", "facility_id", "pd"]].copy(),
        "lgd_output": portfolio_df[["reporting_date", "facility_id", "lgd"]].copy(),
        "ead_output": portfolio_df[["reporting_date", "facility_id", "ead"]].copy(),
        "expected_loss_output": expected[["reporting_date", "facility_id", "expected_loss"]],
        "stress_testing_output": stress[["reporting_date", "facility_id", "stress_scenario", "stressed_loss"]],
    }


def _demo_monitoring(portfolio_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    monthly = portfolio_df[["reporting_date", "facility_id", "borrower_id", "segment", "industry", "product_type", "ead"]].copy()
    monthly["internal_grade_previous"] = portfolio_df["pd"].apply(lambda value: _grade_from_pd(max(value * 0.85, 0.001)))
    monthly["internal_grade_current"] = portfolio_df["pd"].apply(_grade_from_pd)
    monthly["watchlist_flag"] = ((portfolio_df["pd"] >= 0.080) | (portfolio_df["industry"].isin(["Construction", "Property Development"]))).astype(int)
    monthly["days_past_due"] = [5, 24, 12, 8, 18, 0, 0, 42, 11, 27]
    monthly["recent_downgrade_indicator"] = (monthly["internal_grade_current"] > monthly["internal_grade_previous"]).astype(int)
    monthly["monitoring_commentary"] = monthly["watchlist_flag"].map({1: "Watchlist monitoring", 0: "Within routine monitoring"})
    watchlist = monthly[["reporting_date", "facility_id", "borrower_id", "watchlist_flag", "recent_downgrade_indicator"]].copy()
    watchlist["watchlist_reason"] = watchlist["watchlist_flag"].map({1: "Heightened credit monitoring", 0: "Not watchlisted"})
    migration = monthly.groupby(["reporting_date", "segment", "internal_grade_previous", "internal_grade_current"], as_index=False).agg(facility_count=("facility_id", "nunique"), exposure_amount=("ead", "sum")).rename(columns={"internal_grade_previous": "from_grade", "internal_grade_current": "to_grade"})
    realised = portfolio_df.assign(expected_loss=portfolio_df["pd"] * portfolio_df["lgd"] * portfolio_df["ead"]).groupby(["reporting_date", "segment"], as_index=False).agg(expected_loss_amount=("expected_loss", "sum"))
    realised["realised_loss_amount"] = (realised["expected_loss_amount"] * realised["segment"].map({"SME": 1.08, "Corporate": 0.92, "Property": 1.12, "Trade Finance": 0.97}).fillna(1.0)).round(2)
    realised["realised_to_expected_ratio"] = (realised["realised_loss_amount"] / realised["expected_loss_amount"].where(realised["expected_loss_amount"] != 0)).fillna(0.0)
    realised["variance_amount"] = realised["realised_loss_amount"] - realised["expected_loss_amount"]
    frames = []
    for dimension_type, column in [("industry", "industry"), ("product_type", "product_type"), ("geography", "geography")]:
        part = portfolio_df.groupby(["reporting_date", column], as_index=False).agg(exposure_amount=("drawn_balance", "sum"), ead=("ead", "sum")).rename(columns={column: "dimension_value"})
        part["dimension_type"] = dimension_type
        frames.append(part)
    top_obligors = portfolio_df.groupby(["reporting_date", "obligor_name"], as_index=False).agg(exposure_amount=("drawn_balance", "sum"), ead=("ead", "sum")).sort_values(["reporting_date", "ead"], ascending=[True, False]).groupby("reporting_date").head(TOP_OBLIGOR_COUNT).rename(columns={"obligor_name": "dimension_value"})
    top_obligors["dimension_type"] = "top_obligor"
    frames.append(top_obligors)
    concentration = pd.concat(frames, ignore_index=True)
    total_ead = concentration.groupby("reporting_date")["ead"].transform("sum")
    concentration["portfolio_share"] = (concentration["ead"] / total_ead.where(total_ead != 0)).fillna(0.0)
    concentration["concentration_flag"] = concentration["portfolio_share"].apply(lambda value: "heightened_review" if value >= 0.22 else "within_tolerance")
    concentration = concentration[["reporting_date", "dimension_type", "dimension_value", "exposure_amount", "ead", "portfolio_share", "concentration_flag"]]
    return {
        "monthly_risk_pack": monthly,
        "migration_matrix": migration,
        "realised_vs_expected": realised,
        "watchlist_summary": watchlist,
        "concentration_summary": concentration,
    }


def _normalise_metric(df: pd.DataFrame, target: str, aliases: list[str]) -> pd.DataFrame:
    out = _rename_aliases(df)
    for alias in aliases:
        if alias in out.columns and alias != target:
            out = out.rename(columns={alias: target})
            break
    required = ["reporting_date", "facility_id", target]
    missing = [column for column in required if column not in out.columns]
    if missing:
        raise ValueError(f"{target} input is missing required columns: {', '.join(missing)}")
    out[target] = pd.to_numeric(out[target], errors="coerce")
    if out[target].isna().any():
        raise ValueError(f"{target} input contains invalid numeric values")
    return out[required].copy()


def _normalise_stress(df: pd.DataFrame) -> pd.DataFrame:
    out = _rename_aliases(df)
    if "stressed_loss" not in out.columns:
        out = out.rename(columns={"stress_loss": "stressed_loss"})
    if "stress_scenario" not in out.columns:
        out["stress_scenario"] = "management_downturn"
    out["stressed_loss"] = pd.to_numeric(out["stressed_loss"], errors="coerce")
    if out["stressed_loss"].isna().any():
        raise ValueError("Stress input contains invalid stressed losses")
    return out[["reporting_date", "facility_id", "stress_scenario", "stressed_loss"]].copy()


def _normalise_monitoring(df: pd.DataFrame, name: str) -> pd.DataFrame:
    out = _rename_aliases(df)
    if name == "monthly_risk_pack":
        defaults = {"internal_grade_previous": "B", "internal_grade_current": "B", "watchlist_flag": 0, "recent_downgrade_indicator": 0, "days_past_due": 0, "monitoring_commentary": "Monitoring not supplied"}
        for column, value in defaults.items():
            if column not in out.columns:
                out[column] = value
        return out[["reporting_date", "facility_id", "borrower_id", "segment", "internal_grade_previous", "internal_grade_current", "watchlist_flag", "recent_downgrade_indicator", "days_past_due", "monitoring_commentary"]].copy()
    if name == "migration_matrix":
        return out[["reporting_date", "segment", "from_grade", "to_grade", "facility_count", "exposure_amount"]].copy()
    if name == "realised_vs_expected":
        if "expected_loss_amount" not in out.columns:
            out = out.rename(columns={"expected_loss": "expected_loss_amount"})
        if "realised_loss_amount" not in out.columns:
            out = out.rename(columns={"realised_loss": "realised_loss_amount"})
        if "realised_to_expected_ratio" not in out.columns:
            out["realised_to_expected_ratio"] = (pd.to_numeric(out["realised_loss_amount"], errors="coerce") / pd.to_numeric(out["expected_loss_amount"], errors="coerce").where(pd.to_numeric(out["expected_loss_amount"], errors="coerce") != 0)).fillna(0.0)
        if "variance_amount" not in out.columns:
            out["variance_amount"] = pd.to_numeric(out["realised_loss_amount"], errors="coerce") - pd.to_numeric(out["expected_loss_amount"], errors="coerce")
        return out[["reporting_date", "segment", "expected_loss_amount", "realised_loss_amount", "realised_to_expected_ratio", "variance_amount"]].copy()
    if name == "watchlist_summary":
        if "watchlist_reason" not in out.columns:
            out["watchlist_reason"] = "Monitoring exception"
        return out[["reporting_date", "facility_id", "borrower_id", "watchlist_flag", "watchlist_reason", "recent_downgrade_indicator"]].copy()
    if "dimension_type" not in out.columns and "dimension" in out.columns:
        out = out.rename(columns={"dimension": "dimension_type"})
    return out[["reporting_date", "dimension_type", "dimension_value", "exposure_amount", "ead", "portfolio_share", "concentration_flag"]].copy()


def _prepare_demo_files(paths: dict[str, Path], refresh_demo_inputs: bool, include_monitoring: bool) -> None:
    portfolio_path = paths["raw_dir"] / RAW_PORTFOLIO_FILE
    if refresh_demo_inputs or not portfolio_path.exists():
        write_csv(_demo_portfolio(), portfolio_path)
    portfolio = normalise_portfolio_input(_read_csv(portfolio_path))
    for name, frame in _demo_upstream(portfolio).items():
        target = paths["external_dir"] / UPSTREAM_INPUT_FILES[name]
        if refresh_demo_inputs or not target.exists():
            write_csv(frame, target)
    if include_monitoring:
        for name, frame in _demo_monitoring(portfolio).items():
            target = paths["external_dir"] / MONITORING_INPUT_FILES[name]
            if refresh_demo_inputs or not target.exists():
                write_csv(frame, target)


def load_input_bundle(paths: dict[str, Path], refresh_demo_inputs: bool = False, include_monitoring: bool = True) -> dict[str, object]:
    ensure_directories(paths["raw_dir"], paths["interim_dir"], paths["processed_dir"], paths["external_dir"], paths["tables_dir"], paths["charts_dir"], paths["reports_dir"], paths["samples_dir"])
    _prepare_demo_files(paths, refresh_demo_inputs=refresh_demo_inputs, include_monitoring=include_monitoring)
    portfolio = normalise_portfolio_input(_read_csv(paths["raw_dir"] / RAW_PORTFOLIO_FILE))
    upstream = {
        "pd_output": _normalise_metric(_read_csv(paths["external_dir"] / UPSTREAM_INPUT_FILES["pd_output"]), "pd", ["pd_12m", "pd_estimate", "pd_final"]),
        "lgd_output": _normalise_metric(_read_csv(paths["external_dir"] / UPSTREAM_INPUT_FILES["lgd_output"]), "lgd", ["lgd_downturn", "lgd_final"]),
        "ead_output": _normalise_metric(_read_csv(paths["external_dir"] / UPSTREAM_INPUT_FILES["ead_output"]), "ead", ["ead_downturn", "ead_central"]),
        "expected_loss_output": _normalise_metric(_read_csv(paths["external_dir"] / UPSTREAM_INPUT_FILES["expected_loss_output"]), "expected_loss", ["expected_loss_12m", "el_amount"]),
        "stress_testing_output": _normalise_stress(_read_csv(paths["external_dir"] / UPSTREAM_INPUT_FILES["stress_testing_output"])),
    }
    if include_monitoring:
        monitoring = {name: _normalise_monitoring(_read_csv(paths["external_dir"] / filename), name) for name, filename in MONITORING_INPUT_FILES.items()}
    else:
        date = str(portfolio["reporting_date"].iloc[0])
        monitoring = {
            "monthly_risk_pack": pd.DataFrame({"reporting_date": [date] * len(portfolio), "facility_id": portfolio["facility_id"], "borrower_id": portfolio["borrower_id"], "segment": portfolio["segment"], "internal_grade_previous": ["B"] * len(portfolio), "internal_grade_current": ["B"] * len(portfolio), "watchlist_flag": [0] * len(portfolio), "recent_downgrade_indicator": [0] * len(portfolio), "days_past_due": [0] * len(portfolio), "monitoring_commentary": ["Monitoring not supplied"] * len(portfolio)}),
            "migration_matrix": pd.DataFrame({"reporting_date": [date], "segment": ["All Segments"], "from_grade": ["B"], "to_grade": ["B"], "facility_count": [len(portfolio)], "exposure_amount": [portfolio["ead"].sum() if "ead" in portfolio.columns else portfolio["drawn_balance"].sum()]}),
            "realised_vs_expected": pd.DataFrame({"reporting_date": [date], "segment": ["All Segments"], "expected_loss_amount": [0.0], "realised_loss_amount": [0.0], "realised_to_expected_ratio": [0.0], "variance_amount": [0.0]}),
            "watchlist_summary": pd.DataFrame({"reporting_date": [date] * len(portfolio), "facility_id": portfolio["facility_id"], "borrower_id": portfolio["borrower_id"], "watchlist_flag": [0] * len(portfolio), "watchlist_reason": ["Monitoring not supplied"] * len(portfolio), "recent_downgrade_indicator": [0] * len(portfolio)}),
            "concentration_summary": pd.DataFrame({"reporting_date": [date], "dimension_type": ["industry"], "dimension_value": ["Not supplied"], "exposure_amount": [0.0], "ead": [0.0], "portfolio_share": [0.0], "concentration_flag": ["not_supplied"]}),
        }
    return {"portfolio": portfolio, "upstream": upstream, "monitoring": monitoring}

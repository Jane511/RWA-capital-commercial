from __future__ import annotations

import pandas as pd

from .config import CONCENTRATION_SHARE_THRESHOLD


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return (numerator / denominator.where(denominator != 0)).fillna(0.0)


def _migration_summary(migration_df: pd.DataFrame) -> pd.DataFrame:
    out = migration_df.copy()
    out["downgrade_flag"] = (out["to_grade"] > out["from_grade"]).astype(int)
    downgraded = (
        out.loc[out["downgrade_flag"] == 1]
        .groupby(["reporting_date", "segment"], as_index=False)
        .agg(downgrade_exposure=("exposure_amount", "sum"))
    )
    total = (
        out.groupby(["reporting_date", "segment"], as_index=False)
        .agg(migration_exposure=("exposure_amount", "sum"))
        .merge(downgraded, on=["reporting_date", "segment"], how="left")
    )
    total["downgrade_exposure"] = total["downgrade_exposure"].fillna(0.0)
    total["migration_deterioration_share"] = _safe_divide(
        total["downgrade_exposure"],
        total["migration_exposure"],
    )
    return total[["reporting_date", "segment", "migration_deterioration_share"]]


def _concentration_lookup(concentration_df: pd.DataFrame, dimension_type: str, source_column: str, output_column: str) -> pd.DataFrame:
    subset = concentration_df.loc[concentration_df["dimension_type"] == dimension_type].copy()
    if subset.empty:
        return pd.DataFrame(columns=["reporting_date", source_column, output_column, f"{output_column}_share"])
    subset = subset.rename(columns={"dimension_value": source_column})
    subset[output_column] = subset["concentration_flag"]
    subset[f"{output_column}_share"] = subset["portfolio_share"]
    return subset[["reporting_date", source_column, output_column, f"{output_column}_share"]]


def build_capital_base_table(input_bundle: dict[str, object]) -> tuple[pd.DataFrame, pd.DataFrame]:
    portfolio = input_bundle["portfolio"].copy()
    upstream = input_bundle["upstream"]
    monitoring = input_bundle["monitoring"]

    combined_inputs = (
        portfolio.merge(upstream["pd_output"], on=["reporting_date", "facility_id"], how="left", suffixes=("", "_upstream"))
        .merge(upstream["lgd_output"], on=["reporting_date", "facility_id"], how="left")
        .merge(upstream["ead_output"], on=["reporting_date", "facility_id"], how="left")
        .merge(upstream["expected_loss_output"], on=["reporting_date", "facility_id"], how="left")
        .merge(upstream["stress_testing_output"], on=["reporting_date", "facility_id"], how="left")
    )
    if "pd_upstream" in combined_inputs.columns:
        combined_inputs["pd"] = combined_inputs["pd"].fillna(combined_inputs["pd_upstream"])
        combined_inputs = combined_inputs.drop(columns=["pd_upstream"])
    for metric in ["lgd", "ead"]:
        left = f"{metric}_x"
        right = f"{metric}_y"
        if left in combined_inputs.columns or right in combined_inputs.columns:
            combined_inputs[metric] = combined_inputs.get(left, pd.Series(index=combined_inputs.index, dtype=float)).fillna(
                combined_inputs.get(right, pd.Series(index=combined_inputs.index, dtype=float))
            )
            combined_inputs = combined_inputs.drop(columns=[left, right], errors="ignore")
    combined_inputs["expected_loss"] = combined_inputs["expected_loss"].fillna(
        combined_inputs["pd"] * combined_inputs["lgd"] * combined_inputs["ead"]
    )
    combined_inputs["stressed_loss"] = combined_inputs["stressed_loss"].fillna(combined_inputs["expected_loss"] * 1.35)
    combined_inputs["stress_scenario"] = combined_inputs["stress_scenario"].fillna("management_downturn")

    monthly = monitoring["monthly_risk_pack"][
        ["reporting_date", "facility_id", "internal_grade_previous", "internal_grade_current", "watchlist_flag", "recent_downgrade_indicator", "days_past_due", "monitoring_commentary"]
    ]
    watchlist = monitoring["watchlist_summary"][
        ["reporting_date", "facility_id", "watchlist_flag", "watchlist_reason", "recent_downgrade_indicator"]
    ].rename(
        columns={
            "watchlist_flag": "watchlist_flag_watchlist",
            "recent_downgrade_indicator": "recent_downgrade_indicator_watchlist",
        }
    )
    realised = monitoring["realised_vs_expected"][
        ["reporting_date", "segment", "expected_loss_amount", "realised_loss_amount", "realised_to_expected_ratio", "variance_amount"]
    ]
    migration = _migration_summary(monitoring["migration_matrix"])
    concentration = monitoring["concentration_summary"].copy()

    analytical_base = (
        combined_inputs.merge(monthly, on=["reporting_date", "facility_id"], how="left")
        .merge(watchlist, on=["reporting_date", "facility_id"], how="left")
        .merge(realised, on=["reporting_date", "segment"], how="left")
        .merge(migration, on=["reporting_date", "segment"], how="left")
        .merge(_concentration_lookup(concentration, "industry", "industry", "industry_concentration_flag"), on=["reporting_date", "industry"], how="left")
        .merge(_concentration_lookup(concentration, "product_type", "product_type", "product_concentration_flag"), on=["reporting_date", "product_type"], how="left")
        .merge(_concentration_lookup(concentration, "geography", "geography", "geography_concentration_flag"), on=["reporting_date", "geography"], how="left")
        .merge(_concentration_lookup(concentration, "top_obligor", "obligor_name", "top_obligor_flag"), on=["reporting_date", "obligor_name"], how="left")
    )

    analytical_base["watchlist_flag"] = analytical_base["watchlist_flag"].fillna(analytical_base["watchlist_flag_watchlist"]).fillna(0).astype(int)
    analytical_base["recent_downgrade_indicator"] = analytical_base["recent_downgrade_indicator"].fillna(analytical_base["recent_downgrade_indicator_watchlist"]).fillna(0).astype(int)
    analytical_base["watchlist_reason"] = analytical_base["watchlist_reason"].fillna("Not watchlisted")
    analytical_base["watchlist_population"] = analytical_base["watchlist_flag"].map({1: "Watchlist", 0: "Non-watchlist"})
    analytical_base["utilisation"] = _safe_divide(analytical_base["drawn_balance"], analytical_base["limit_amount"])
    analytical_base["undrawn_amount"] = (analytical_base["limit_amount"] - analytical_base["drawn_balance"]).clip(lower=0.0)
    analytical_base["migration_deterioration_share"] = analytical_base["migration_deterioration_share"].fillna(0.0)
    analytical_base["realised_to_expected_ratio"] = analytical_base["realised_to_expected_ratio"].fillna(0.0)
    analytical_base["variance_amount"] = analytical_base["variance_amount"].fillna(0.0)

    flag_columns = [
        "industry_concentration_flag",
        "product_concentration_flag",
        "geography_concentration_flag",
        "top_obligor_flag",
    ]
    share_columns = [f"{column}_share" for column in flag_columns]
    for column in flag_columns:
        analytical_base[column] = analytical_base[column].fillna("within_tolerance")
    for column in share_columns:
        analytical_base[column] = pd.to_numeric(analytical_base[column], errors="coerce").fillna(0.0)
    analytical_base["concentration_tag"] = analytical_base.apply(
        lambda row: "; ".join(
            label
            for label, column in {
                "industry": "industry_concentration_flag",
                "product": "product_concentration_flag",
                "geography": "geography_concentration_flag",
                "top_obligor": "top_obligor_flag",
            }.items()
            if str(row[column]) not in {"within_tolerance", "not_supplied"}
        )
        or "within_tolerance",
        axis=1,
    )
    analytical_base["concentration_overlay_reference"] = analytical_base[share_columns].max(axis=1)
    analytical_base["heightened_concentration_indicator"] = (
        analytical_base["concentration_overlay_reference"] >= CONCENTRATION_SHARE_THRESHOLD
    ).astype(int)
    analytical_base = analytical_base.drop(columns=["watchlist_flag_watchlist", "recent_downgrade_indicator_watchlist"], errors="ignore")
    return combined_inputs, analytical_base

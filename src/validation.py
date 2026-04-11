from __future__ import annotations

import pandas as pd


def _row(check_name: str, status: bool, detail: str) -> dict[str, object]:
    return {"check_name": check_name, "status": bool(status), "detail": detail}


def build_validation_report(
    combined_inputs: pd.DataFrame,
    analytical_base: pd.DataFrame,
    output_tables: dict[str, pd.DataFrame],
    monitoring_bundle: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    required_columns = [
        "reporting_date",
        "borrower_id",
        "facility_id",
        "segment",
        "industry",
        "product_type",
        "collateral_type",
        "geography",
        "limit_amount",
        "drawn_balance",
        "pd",
        "lgd",
        "ead",
        "expected_loss",
        "stressed_loss",
    ]
    missing = [column for column in required_columns if column not in analytical_base.columns]
    rows.append(_row("required_columns_present", not missing, "Analytical base contains required columns" if not missing else f"Missing columns: {', '.join(missing)}"))
    rows.append(_row("duplicate_facility_keys", analytical_base["facility_id"].is_unique, "Facility keys are unique"))
    rows.append(_row("negative_balances", ((analytical_base["limit_amount"] >= 0) & (analytical_base["drawn_balance"] >= 0) & (analytical_base["ead"] >= 0)).all(), "Limit, drawn balance, and EAD are non-negative"))
    rows.append(_row("ead_not_below_drawn", (analytical_base["ead"] >= analytical_base["drawn_balance"]).all(), "EAD is at least drawn balance"))
    rows.append(_row("ead_within_reasonable_limit", (analytical_base["ead"] <= analytical_base["limit_amount"] * 1.25).all(), "EAD stays within simplified demo tolerances"))
    rows.append(_row("pd_lgd_ranges", analytical_base["pd"].between(0, 1).all() and analytical_base["lgd"].between(0, 1).all(), "PD and LGD stay within zero to one"))
    rows.append(_row("monitoring_reporting_dates_present", all("reporting_date" in df.columns and df["reporting_date"].astype(str).str.len().gt(0).all() for df in monitoring_bundle.values()), "Monitoring-linked files contain reporting dates"))
    rows.append(_row("watchlist_keys_match_portfolio", monitoring_bundle["watchlist_summary"]["facility_id"].isin(analytical_base["facility_id"]).all(), "Watchlist facilities reconcile to the analytical base"))
    rows.append(_row("concentration_summary_valid", monitoring_bundle["concentration_summary"]["portfolio_share"].between(0, 1).all() and monitoring_bundle["concentration_summary"]["dimension_type"].notna().all(), "Concentration summary shares and dimensions are valid"))

    rwa_by_facility = output_tables["rwa_by_facility.csv"]
    rwa_by_segment = output_tables["rwa_by_segment.csv"]
    capital_summary = output_tables["capital_summary.csv"]
    expected_loss_adjustment = output_tables["expected_loss_adjustment_summary.csv"]
    watchlist_capital = output_tables["watchlist_capital_summary.csv"]
    rows.append(_row("segment_rwa_reconciliation", abs(rwa_by_facility["rwa"].sum() - rwa_by_segment["total_rwa"].sum()) < 1e-6, "Facility and segment RWA totals reconcile"))
    rows.append(_row("capital_summary_reconciliation", abs(rwa_by_facility["rwa"].sum() - float(capital_summary.loc[0, "total_rwa"])) < 1e-6 and abs(rwa_by_facility["capital_amount"].sum() - float(capital_summary.loc[0, "capital_amount"])) < 1e-6, "Facility totals reconcile to capital summary"))
    rows.append(_row("expected_loss_adjustment_reconciliation", abs(expected_loss_adjustment["capital_after_el_adjustment"].sum() - rwa_by_facility["capital_after_el_adjustment"].sum()) < 1e-6, "Expected loss adjustment summary reconciles to facility output"))
    rows.append(_row("watchlist_summary_reconciliation", abs(watchlist_capital["ead"].sum() - rwa_by_facility["ead"].sum()) < 1e-6 and abs(watchlist_capital["rwa"].sum() - rwa_by_facility["rwa"].sum()) < 1e-6, "Watchlist summary reconciles to facility totals"))
    rows.append(_row("required_outputs_non_empty", all(not df.empty for df in output_tables.values()), "All required output tables are populated"))
    return pd.DataFrame(rows)

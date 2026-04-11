from __future__ import annotations

import pandas as pd

from .config import (
    CAPITAL_RATIO,
    PRODUCT_RISK_MULTIPLIERS,
    PROVISION_COVERAGE_RATIO,
    RWA_CAP,
    RWA_FLOOR,
    SEGMENT_BASE_RISK_WEIGHTS,
    TOP_OBLIGOR_COUNT,
)


def _portfolio_share(series: pd.Series) -> pd.Series:
    total = float(series.sum())
    if total == 0:
        return pd.Series([0.0] * len(series), index=series.index)
    return series / total


def _concentration_flag(series: pd.Series) -> pd.Series:
    return series.apply(lambda value: "heightened_review" if value >= 0.22 else "within_tolerance")


def run_capital_engine(analytical_base: pd.DataFrame) -> dict[str, pd.DataFrame]:
    facilities = analytical_base.copy()
    facilities["segment_base_risk_weight"] = facilities["segment"].map(SEGMENT_BASE_RISK_WEIGHTS).fillna(0.80)
    facilities["product_risk_multiplier"] = facilities["product_type"].map(PRODUCT_RISK_MULTIPLIERS).fillna(1.00)
    facilities["maturity_adjustment"] = 1.0 + facilities["maturity_years"].clip(lower=0.5, upper=5.0).sub(2.0).clip(lower=0.0) * 0.03
    facilities["risk_quality_scalar"] = 0.65 + facilities["pd"] * 3.5 + facilities["lgd"] * 0.45
    facilities["risk_weight"] = (
        facilities["segment_base_risk_weight"]
        * facilities["product_risk_multiplier"]
        * facilities["maturity_adjustment"]
        * facilities["risk_quality_scalar"]
    ).clip(lower=RWA_FLOOR, upper=RWA_CAP)
    facilities["rwa"] = facilities["ead"] * facilities["risk_weight"]
    facilities["capital_amount"] = facilities["rwa"] * CAPITAL_RATIO
    facilities["provision_proxy"] = facilities["expected_loss"] * PROVISION_COVERAGE_RATIO
    facilities["expected_loss_shortfall"] = (
        facilities["expected_loss"] - facilities["provision_proxy"]
    ).clip(lower=0.0)
    facilities["capital_after_el_adjustment"] = facilities["capital_amount"] + facilities["expected_loss_shortfall"]

    rwa_by_facility = facilities[
        [
            "reporting_date",
            "borrower_id",
            "obligor_name",
            "facility_id",
            "segment",
            "industry",
            "product_type",
            "collateral_type",
            "geography",
            "limit_amount",
            "drawn_balance",
            "ead",
            "pd",
            "lgd",
            "maturity_years",
            "expected_loss",
            "stressed_loss",
            "risk_weight",
            "rwa",
            "capital_amount",
            "capital_after_el_adjustment",
            "watchlist_flag",
            "watchlist_reason",
            "recent_downgrade_indicator",
            "realised_to_expected_ratio",
            "variance_amount",
            "migration_deterioration_share",
            "concentration_tag",
        ]
    ].copy()

    rwa_by_segment = facilities.groupby(["reporting_date", "segment"], as_index=False).agg(
        facility_count=("facility_id", "nunique"),
        borrower_count=("borrower_id", "nunique"),
        total_exposure=("drawn_balance", "sum"),
        total_ead=("ead", "sum"),
        expected_loss=("expected_loss", "sum"),
        stressed_loss=("stressed_loss", "sum"),
        total_rwa=("rwa", "sum"),
        capital_amount=("capital_amount", "sum"),
        capital_after_el_adjustment=("capital_after_el_adjustment", "sum"),
        average_risk_weight=("risk_weight", "mean"),
        watchlist_count=("watchlist_flag", "sum"),
        recent_downgrade_count=("recent_downgrade_indicator", "sum"),
    )

    capital_summary = pd.DataFrame(
        [
            {
                "reporting_date": facilities["reporting_date"].iloc[0],
                "portfolio": "commercial_demo_portfolio",
                "facility_count": facilities["facility_id"].nunique(),
                "borrower_count": facilities["borrower_id"].nunique(),
                "total_exposure": facilities["drawn_balance"].sum(),
                "total_ead": facilities["ead"].sum(),
                "expected_loss": facilities["expected_loss"].sum(),
                "stressed_loss": facilities["stressed_loss"].sum(),
                "total_rwa": facilities["rwa"].sum(),
                "capital_amount": facilities["capital_amount"].sum(),
                "capital_after_el_adjustment": facilities["capital_after_el_adjustment"].sum(),
                "capital_ratio_assumption": CAPITAL_RATIO,
                "average_risk_weight": facilities["risk_weight"].mean(),
                "watchlist_exposure": facilities.loc[facilities["watchlist_flag"] == 1, "ead"].sum(),
                "recent_downgrade_exposure": facilities.loc[facilities["recent_downgrade_indicator"] == 1, "ead"].sum(),
            }
        ]
    )

    expected_loss_adjustment_summary = facilities[
        [
            "reporting_date",
            "borrower_id",
            "facility_id",
            "segment",
            "expected_loss",
            "provision_proxy",
            "expected_loss_shortfall",
            "capital_amount",
            "capital_after_el_adjustment",
            "stressed_loss",
        ]
    ].copy()

    monitoring_capital_bridge = facilities.groupby(["reporting_date", "segment"], as_index=False).agg(
        exposure=("drawn_balance", "sum"),
        ead=("ead", "sum"),
        expected_loss=("expected_loss", "sum"),
        stressed_loss=("stressed_loss", "sum"),
        rwa=("rwa", "sum"),
        capital_amount=("capital_amount", "sum"),
        watchlist_count=("watchlist_flag", "sum"),
        recent_downgrade_count=("recent_downgrade_indicator", "sum"),
        realised_to_expected_ratio=("realised_to_expected_ratio", "mean"),
        migration_deterioration_share=("migration_deterioration_share", "mean"),
    )
    segment_commentary = (
        facilities.groupby(["reporting_date", "segment"])["concentration_tag"]
        .apply(lambda values: "heightened concentration review" if any(value != "within_tolerance" for value in values) else "within concentration tolerance")
        .reset_index(name="concentration_commentary")
    )
    monitoring_capital_bridge = monitoring_capital_bridge.merge(segment_commentary, on=["reporting_date", "segment"], how="left")

    watchlist_capital_summary = facilities.groupby(["reporting_date", "watchlist_population"], as_index=False).agg(
        facility_count=("facility_id", "nunique"),
        borrower_count=("borrower_id", "nunique"),
        exposure=("drawn_balance", "sum"),
        ead=("ead", "sum"),
        expected_loss=("expected_loss", "sum"),
        stressed_loss=("stressed_loss", "sum"),
        rwa=("rwa", "sum"),
        capital_amount=("capital_amount", "sum"),
    )

    frames: list[pd.DataFrame] = []
    for dimension_type, column in [
        ("industry", "industry"),
        ("product_type", "product_type"),
        ("collateral_type", "collateral_type"),
        ("geography", "geography"),
    ]:
        part = facilities.groupby(["reporting_date", column], as_index=False).agg(
            facility_count=("facility_id", "nunique"),
            borrower_count=("borrower_id", "nunique"),
            exposure=("drawn_balance", "sum"),
            ead=("ead", "sum"),
            rwa=("rwa", "sum"),
            capital_amount=("capital_amount", "sum"),
        ).rename(columns={column: "dimension_value"})
        part["dimension_type"] = dimension_type
        frames.append(part)
    top_obligors = facilities.groupby(["reporting_date", "obligor_name"], as_index=False).agg(
        facility_count=("facility_id", "nunique"),
        borrower_count=("borrower_id", "nunique"),
        exposure=("drawn_balance", "sum"),
        ead=("ead", "sum"),
        rwa=("rwa", "sum"),
        capital_amount=("capital_amount", "sum"),
    ).sort_values(["reporting_date", "ead"], ascending=[True, False]).groupby("reporting_date").head(TOP_OBLIGOR_COUNT).rename(columns={"obligor_name": "dimension_value"})
    top_obligors["dimension_type"] = "top_obligor"
    frames.append(top_obligors)
    concentration_capital_summary = pd.concat(frames, ignore_index=True)
    concentration_capital_summary["portfolio_share"] = concentration_capital_summary.groupby("reporting_date")["ead"].transform(_portfolio_share)
    concentration_capital_summary["concentration_flag"] = _concentration_flag(concentration_capital_summary["portfolio_share"])
    concentration_capital_summary = concentration_capital_summary[
        [
            "reporting_date",
            "dimension_type",
            "dimension_value",
            "facility_count",
            "borrower_count",
            "exposure",
            "ead",
            "rwa",
            "capital_amount",
            "portfolio_share",
            "concentration_flag",
        ]
    ].copy()

    return {
        "rwa_by_facility.csv": rwa_by_facility,
        "rwa_by_segment.csv": rwa_by_segment,
        "capital_summary.csv": capital_summary,
        "expected_loss_adjustment_summary.csv": expected_loss_adjustment_summary,
        "monitoring_capital_bridge.csv": monitoring_capital_bridge,
        "watchlist_capital_summary.csv": watchlist_capital_summary,
        "concentration_capital_summary.csv": concentration_capital_summary,
    }

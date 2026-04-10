from __future__ import annotations

import pandas as pd

from .config import CAPITAL_SCALE_FACTOR


def add_rwa_metrics(
    exposure_df: pd.DataFrame,
    capital_scale_factor: float = CAPITAL_SCALE_FACTOR,
) -> pd.DataFrame:
    out = exposure_df.copy()
    out["capital_requirement"] = out["expected_loss"] * capital_scale_factor
    out["rwa"] = out["capital_requirement"] * capital_scale_factor
    out["rwa_density"] = (out["rwa"] / out["ead_downturn"].where(out["ead_downturn"] != 0)).fillna(0.0)
    return out


def summarise_portfolio_rwa(exposure_level_rwa_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        exposure_level_rwa_df.groupby(["product_type", "segment", "industry"], dropna=False)
        .agg(
            exposure_count=("exposure_id", "nunique"),
            total_ead_central=("ead_central", "sum"),
            total_ead_downturn=("ead_downturn", "sum"),
            total_expected_loss=("expected_loss", "sum"),
            total_capital_requirement=("capital_requirement", "sum"),
            total_rwa=("rwa", "sum"),
            average_pd_12m=("pd_12m", "mean"),
            average_lgd_downturn=("lgd_downturn", "mean"),
        )
        .reset_index()
        .sort_values(["segment", "product_type", "industry"])
        .reset_index(drop=True)
    )
    return summary

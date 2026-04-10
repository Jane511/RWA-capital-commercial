from __future__ import annotations

import pandas as pd

from .capital_ratios import build_capital_ratio_summary
from .calculate_el import add_expected_loss
from .calculate_rwa import add_rwa_metrics
from .config import STRESS_SCENARIO


def _run_single_scenario(
    capital_input_df: pd.DataFrame,
    capital_structure_df: pd.DataFrame,
    scenario: str,
    pd_multiplier: float,
    lgd_multiplier: float,
) -> dict[str, float | str]:
    stressed_input = capital_input_df.copy()
    stressed_input["pd_12m"] = (stressed_input["pd_12m"] * pd_multiplier).clip(upper=1.0)
    stressed_input["lgd_downturn"] = (stressed_input["lgd_downturn"] * lgd_multiplier).clip(upper=1.0)
    stressed_exposure = add_rwa_metrics(add_expected_loss(stressed_input))
    summary_row = build_capital_ratio_summary(stressed_exposure, capital_structure_df).iloc[0].to_dict()
    summary_row.update(
        {
            "scenario": scenario,
            "pd_multiplier": pd_multiplier,
            "lgd_multiplier": lgd_multiplier,
        }
    )
    return summary_row


def run_stress_test(
    capital_input_df: pd.DataFrame,
    capital_structure_df: pd.DataFrame,
) -> pd.DataFrame:
    base_row = _run_single_scenario(
        capital_input_df=capital_input_df,
        capital_structure_df=capital_structure_df,
        scenario="base",
        pd_multiplier=1.0,
        lgd_multiplier=1.0,
    )
    stressed_row = _run_single_scenario(
        capital_input_df=capital_input_df,
        capital_structure_df=capital_structure_df,
        scenario=STRESS_SCENARIO["scenario"],
        pd_multiplier=STRESS_SCENARIO["pd_multiplier"],
        lgd_multiplier=STRESS_SCENARIO["lgd_multiplier"],
    )
    base_expected_loss = float(base_row["total_expected_loss"])
    base_rwa = float(base_row["total_rwa"])
    for row in (base_row, stressed_row):
        row["incremental_expected_loss"] = float(row["total_expected_loss"]) - base_expected_loss
        row["incremental_rwa"] = float(row["total_rwa"]) - base_rwa
    return pd.DataFrame([base_row, stressed_row])

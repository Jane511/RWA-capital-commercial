from __future__ import annotations

import pandas as pd

from .utils import safe_divide


def build_capital_ratio_summary(
    exposure_level_rwa_df: pd.DataFrame,
    capital_structure_df: pd.DataFrame,
) -> pd.DataFrame:
    capital_row = capital_structure_df.sort_values("reporting_date").iloc[-1]

    total_ead_downturn = float(exposure_level_rwa_df["ead_downturn"].sum())
    total_expected_loss = float(exposure_level_rwa_df["expected_loss"].sum())
    total_capital_requirement = float(exposure_level_rwa_df["capital_requirement"].sum())
    total_rwa = float(exposure_level_rwa_df["rwa"].sum())
    cet1_capital = float(capital_row["cet1_capital"])
    total_capital = float(capital_row["total_capital"])

    summary = pd.DataFrame(
        [
            {
                "reporting_date": capital_row["reporting_date"],
                "total_ead_downturn": total_ead_downturn,
                "total_expected_loss": total_expected_loss,
                "total_capital_requirement": total_capital_requirement,
                "total_rwa": total_rwa,
                "cet1_capital": cet1_capital,
                "total_capital": total_capital,
                "cet1_ratio": safe_divide(cet1_capital, total_rwa),
                "total_capital_ratio": safe_divide(total_capital, total_rwa),
            }
        ]
    )
    return summary

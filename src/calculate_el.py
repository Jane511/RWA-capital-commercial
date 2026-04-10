from __future__ import annotations

import pandas as pd


def add_expected_loss(capital_input_df: pd.DataFrame) -> pd.DataFrame:
    out = capital_input_df.copy()
    out["expected_loss"] = out["pd_12m"] * out["lgd_downturn"] * out["ead_downturn"]
    return out

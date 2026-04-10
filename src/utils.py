from __future__ import annotations

from pathlib import Path

import pandas as pd


def ensure_directories(*paths: str | Path) -> None:
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def save_dataframe(df: pd.DataFrame, path: str | Path) -> None:
    target = Path(path)
    ensure_directories(target.parent)
    df.to_csv(target, index=False)


def safe_divide(numerator: float, denominator: float) -> float:
    if pd.isna(denominator) or denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)

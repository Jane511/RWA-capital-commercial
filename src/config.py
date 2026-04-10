from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
UPSTREAM_DIR = DATA_DIR / "upstream"
MANUAL_DIR = DATA_DIR / "manual"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = ROOT / "output"
NOTEBOOKS_DIR = ROOT / "notebooks"

DEFAULT_INPUT_FILES = {
    "exposure_master": RAW_DIR / "exposure_master.csv",
    "pd_output": UPSTREAM_DIR / "pd_output.csv",
    "lgd_output": UPSTREAM_DIR / "lgd_output.csv",
    "ead_output": UPSTREAM_DIR / "ead_output.csv",
    "capital_structure": MANUAL_DIR / "capital_structure.csv",
}

DEFAULT_OUTPUT_FILES = {
    "capital_input": PROCESSED_DIR / "capital_input.csv",
    "exposure_level_rwa": OUTPUT_DIR / "exposure_level_rwa.csv",
    "portfolio_rwa_summary": OUTPUT_DIR / "portfolio_rwa_summary.csv",
    "capital_ratio_summary": OUTPUT_DIR / "capital_ratio_summary.csv",
    "stressed_capital_summary": OUTPUT_DIR / "stressed_capital_summary.csv",
}

CAPITAL_SCALE_FACTOR = 12.5
STRESS_SCENARIO = {
    "scenario": "stress_pd_up_30_lgd_up_10",
    "pd_multiplier": 1.30,
    "lgd_multiplier": 1.10,
}
AS_OF_DATE = "2026-04-10"

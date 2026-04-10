from __future__ import annotations

from pathlib import Path

import pytest

from src.pipeline import run_pipeline


TEST_ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = TEST_ROOT / "_runtime"


def _runtime_paths(case_name: str) -> dict[str, Path]:
    base = RUNTIME_ROOT / case_name
    return {
        "raw_dir": base / "data" / "raw",
        "upstream_dir": base / "data" / "upstream",
        "manual_dir": base / "data" / "manual",
        "processed_dir": base / "data" / "processed",
        "output_dir": base / "output",
    }


def test_pipeline_builds_required_outputs():
    paths = _runtime_paths("required_outputs")
    result = run_pipeline(
        **paths,
        refresh_demo_inputs=True,
        persist=True,
    )

    exposure_level_rwa = result["exposure_level_rwa"]
    portfolio_summary = result["portfolio_rwa_summary"]
    capital_ratio_summary = result["capital_ratio_summary"]
    stress_summary = result["stressed_capital_summary"].set_index("scenario")

    assert len(exposure_level_rwa) == 12
    assert {"expected_loss", "capital_requirement", "rwa"}.issubset(exposure_level_rwa.columns)
    assert (paths["processed_dir"] / "capital_input.csv").exists()
    assert (paths["output_dir"] / "exposure_level_rwa.csv").exists()
    assert (paths["output_dir"] / "portfolio_rwa_summary.csv").exists()
    assert (paths["output_dir"] / "capital_ratio_summary.csv").exists()
    assert (paths["output_dir"] / "stressed_capital_summary.csv").exists()
    assert len(portfolio_summary) > 0
    assert capital_ratio_summary.loc[0, "cet1_ratio"] > 0
    assert stress_summary.loc["stress_pd_up_30_lgd_up_10", "total_expected_loss"] > stress_summary.loc["base", "total_expected_loss"]
    assert stress_summary.loc["stress_pd_up_30_lgd_up_10", "total_rwa"] > stress_summary.loc["base", "total_rwa"]


def test_capital_formula_is_applied():
    paths = _runtime_paths("capital_formula")
    result = run_pipeline(
        **paths,
        refresh_demo_inputs=True,
        persist=False,
    )

    first_row = result["exposure_level_rwa"].iloc[0]
    assert first_row["capital_requirement"] == pytest.approx(first_row["expected_loss"] * 12.5)
    assert first_row["rwa"] == pytest.approx(first_row["capital_requirement"] * 12.5)

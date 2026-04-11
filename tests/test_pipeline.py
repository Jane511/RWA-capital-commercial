from __future__ import annotations

from pathlib import Path

from src.config import REQUIRED_OUTPUT_TABLES
from src.run_pipeline import run_pipeline


TEST_ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = TEST_ROOT / "_runtime"


def _case_root(case_name: str) -> Path:
    return RUNTIME_ROOT / case_name


def test_pipeline_builds_required_outputs():
    result = run_pipeline(project_root=_case_root("required_outputs"), refresh_demo_inputs=True, persist=True)
    for table_name in REQUIRED_OUTPUT_TABLES:
        assert table_name in result["outputs"]
        assert not result["outputs"][table_name].empty
        assert (result["paths"]["tables_dir"] / table_name).exists()
    rwa_by_facility = result["outputs"]["rwa_by_facility.csv"]
    bridge = result["outputs"]["monitoring_capital_bridge.csv"]
    assert {"watchlist_flag", "recent_downgrade_indicator", "stressed_loss", "rwa", "capital_amount"}.issubset(rwa_by_facility.columns)
    assert bridge["watchlist_count"].sum() > 0
    assert result["validation"]["status"].all()
    assert (result["paths"]["processed_dir"] / "capital_analytical_base.csv").exists()


def test_pipeline_runs_without_monitoring_enrichment():
    result = run_pipeline(project_root=_case_root("without_monitoring"), refresh_demo_inputs=True, include_monitoring=False, persist=False)
    bridge = result["outputs"]["monitoring_capital_bridge.csv"]
    watchlist = result["outputs"]["watchlist_capital_summary.csv"]
    assert bridge["watchlist_count"].sum() == 0
    assert watchlist["watchlist_population"].tolist() == ["Non-watchlist"]

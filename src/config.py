from __future__ import annotations

from pathlib import Path


REPO_NAME = "RWA-capital-commercial"
REPORTING_DATE = "2026-03-31"

UPSTREAM_REPOS = [
    "PD-and-scorecard-commercial",
    "LGD-commercial",
    "EAD-CCF-commercial",
    "expected-loss-engine-commercial",
    "stress-testing-commercial",
    "portfolio-monitor-commercial",
]

ROOT = Path(__file__).resolve().parents[1]


def build_paths(project_root: str | Path | None = None) -> dict[str, Path]:
    root = Path(project_root).resolve() if project_root else ROOT
    data_dir = root / "data"
    outputs_dir = root / "outputs"
    return {
        "root": root,
        "data_dir": data_dir,
        "raw_dir": data_dir / "raw",
        "interim_dir": data_dir / "interim",
        "processed_dir": data_dir / "processed",
        "external_dir": data_dir / "external",
        "notebooks_dir": root / "notebooks",
        "outputs_dir": outputs_dir,
        "tables_dir": outputs_dir / "tables",
        "charts_dir": outputs_dir / "charts",
        "reports_dir": outputs_dir / "reports",
        "samples_dir": outputs_dir / "samples",
    }


RAW_PORTFOLIO_FILE = "demo_portfolio.csv"
UPSTREAM_INPUT_FILES = {
    "pd_output": "pd_output.csv",
    "lgd_output": "lgd_output.csv",
    "ead_output": "ead_output.csv",
    "expected_loss_output": "expected_loss_output.csv",
    "stress_testing_output": "stress_testing_output.csv",
}
MONITORING_INPUT_FILES = {
    "monthly_risk_pack": "monthly_risk_pack.csv",
    "migration_matrix": "migration_matrix.csv",
    "realised_vs_expected": "realised_vs_expected.csv",
    "watchlist_summary": "watchlist_summary.csv",
    "concentration_summary": "concentration_summary.csv",
}

REQUIRED_OUTPUT_TABLES = [
    "rwa_by_facility.csv",
    "rwa_by_segment.csv",
    "capital_summary.csv",
    "expected_loss_adjustment_summary.csv",
    "monitoring_capital_bridge.csv",
    "watchlist_capital_summary.csv",
    "concentration_capital_summary.csv",
    "pipeline_validation_report.csv",
]

PORTFOLIO_REQUIRED_COLUMNS = [
    "reporting_date",
    "borrower_id",
    "facility_id",
    "obligor_name",
    "segment",
    "industry",
    "product_type",
    "collateral_type",
    "geography",
    "limit_amount",
    "drawn_balance",
    "collateral_value",
    "maturity_years",
]

NUMERIC_PORTFOLIO_COLUMNS = [
    "limit_amount",
    "drawn_balance",
    "collateral_value",
    "maturity_years",
]

SEGMENT_BASE_RISK_WEIGHTS = {
    "SME": 0.78,
    "Corporate": 0.92,
    "Property": 0.68,
    "Trade Finance": 0.74,
    "Agribusiness": 0.72,
}

PRODUCT_RISK_MULTIPLIERS = {
    "Term Loan": 1.00,
    "Overdraft": 1.08,
    "Commercial Mortgage": 0.94,
    "Working Capital Revolver": 1.05,
    "Trade Finance": 0.98,
    "Guarantee": 0.90,
    "Property Development Facility": 1.12,
    "Equipment Finance": 0.96,
}

CAPITAL_RATIO = 0.105
PROVISION_COVERAGE_RATIO = 0.70
CONCENTRATION_SHARE_THRESHOLD = 0.22
TOP_OBLIGOR_COUNT = 5
RWA_FLOOR = 0.35
RWA_CAP = 1.60

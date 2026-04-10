from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1]
REPO_NAME='RWA-Capital-Credit-Risk'
PIPELINE_KIND='rwa'
EXPECTED_OUTPUTS=['rwa_by_facility.csv', 'rwa_by_segment.csv', 'capital_summary.csv', 'expected_loss_adjustment_summary.csv']

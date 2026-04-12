# Commercial RWA & Capital Analytics Project

This repository is the end-of-stack capital analytics layer in the commercial credit-risk workflow. It uses upstream PD, LGD, EAD, expected loss, stress testing, and optional monitoring context to produce explainable RWA tables, capital summaries, and monitoring-linked reporting outputs. The project is designed to show how validated risk outputs can be translated into a practical capital view for portfolio review.

## What this repo is

This project demonstrates a simplified commercial capital workflow using transparent assumptions and synthetic data. It is intended for portfolio presentation and methodology discussion, not as a production Basel or APRA capital engine.

## Where it sits in the stack

Upstream inputs:
- `PD-and-scorecard-commercial`
- `LGD-commercial`
- `EAD-CCF-commercial`
- `expected-loss-engine-commercial`
- `stress-testing-commercial`
- optional monitoring context from `portfolio-monitor-commercial`

Downstream consumers:
- capital review and portfolio reporting
- management interpretation of watchlist and concentration effects
- employer-ready presentation outputs at the end of the stack

## Key outputs

- `outputs/tables/rwa_by_facility.csv`
- `outputs/tables/rwa_by_segment.csv`
- `outputs/tables/capital_summary.csv`
- `outputs/tables/expected_loss_adjustment_summary.csv`
- `outputs/tables/monitoring_capital_bridge.csv`
- `outputs/tables/watchlist_capital_summary.csv`
- `outputs/tables/concentration_capital_summary.csv`
- `outputs/tables/pipeline_validation_report.csv`
- `outputs/reports/capital_pipeline_report.md`

## Repo structure

- `data/`: raw, interim, processed, and external capital inputs
- `src/`: reusable capital, monitoring-enrichment, and pipeline modules
- `scripts/`: wrapper scripts for pipeline execution
- `docs/`: methodology, assumptions, data dictionary, and validation notes
- `notebooks/`: walkthrough notebooks for reviewer context
- `outputs/`: exported tables, reports, and sample artifacts
- `tests/`: validation and regression checks

## How to run

```powershell
python -m src.run_pipeline --refresh-demo-inputs
```

Or:

```powershell
python scripts/run_pipeline.py --refresh-demo-inputs
```

Run without monitoring enrichment:

```powershell
python -m src.run_pipeline --refresh-demo-inputs --no-monitoring
```

## Limitations / Demo-Only Note

- All source extracts are synthetic or simulated when upstream files are unavailable.
- Capital mechanics, expected-loss adjustments, and monitoring overlays are simplified for explainability.
- The repo is intended for portfolio demonstration and reporting workflow review, not for production regulatory capital use.

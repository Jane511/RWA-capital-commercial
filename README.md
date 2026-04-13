# Commercial RWA & Capital Analytics Project

This repository is the end-of-stack capital analytics layer in the commercial credit-risk workflow. It uses upstream PD, LGD, EAD, expected loss, stress testing, and optional monitoring context to produce explainable RWA tables, capital summaries, and monitoring-linked reporting outputs. The project is designed to show how validated risk outputs can be translated into a practical capital view for portfolio review, while still being understandable to broader lending-risk teams outside purely regulatory functions.

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

## How this is used in practice

This project can be applied in:

### Bank / Institutional context

- RWA and capital estimation for portfolio risk review and capital-style frameworks
- Segment and watchlist capital analysis for structured management reporting
- Monitoring-enriched capital interpretation using upstream stress and portfolio signals

### Non-bank / Fintech context

- Portfolio capital intensity and return context for lender-side strategy discussion
- Product and segment comparisons using capital-style risk weighting as a decision aid
- Management reporting on where loss, stress, and concentration create the heaviest balance-sheet burden

## Example input files (already in the repo)

- `data/external/pd_output.csv`: upstream PD output contract (demo copy for reviewer runs)
- `data/external/lgd_output.csv`: upstream LGD output contract (demo copy for reviewer runs)
- `data/external/ead_output.csv`: upstream EAD output contract (demo copy for reviewer runs)
- `data/external/expected_loss_output.csv`: upstream expected loss output contract (demo copy for reviewer runs)
- `data/external/stress_testing_output.csv`: upstream stress-testing output contract (demo copy for reviewer runs)
- `data/external/monthly_risk_pack.csv`: optional monitoring-style pack used for enrichment examples
- `outputs/samples/demo_portfolio_input.csv`: small demo portfolio input for quick inspection

## Example output files (already in the repo)

- `outputs/reports/capital_pipeline_report.md`: reviewer-friendly end-of-run summary
- `outputs/tables/capital_summary.csv`: headline capital/RWA summary for portfolio discussion
- `outputs/tables/rwa_by_segment.csv`: segment-level RWA view for concentration discussion
- `outputs/tables/watchlist_capital_summary.csv`: watchlist overlay example for “capital on the problem loans”
- `outputs/tables/monitoring_capital_bridge.csv`: bridge view linking monitoring signals to capital movement
- `outputs/tables/pipeline_validation_report.csv`: run validation checks and reconciliations
- `outputs/charts/rwa_by_segment_chart_data.csv`: chart-ready dataset for presentations

## Example business use case

A portfolio team has PD/LGD/EAD and expected loss outputs and needs a single capital view that is explainable to non-modellers. This repo produces segment-level RWA and capital summaries plus simple overlays (watchlist and concentration) that match how bank portfolio packs are typically discussed.

## How these outputs relate to upstream and optional downstream use

- Inputs are treated as “contracts” from upstream repos (PD/LGD/EAD/EL/stress). This repo focuses on capital aggregation and reporting, not re-building those components.
- Outputs are end-of-stack artifacts intended for portfolio packs; if you want to flow results into monitoring or pricing, treat `outputs/tables/capital_summary.csv` and `outputs/tables/rwa_by_facility.csv` as the handoff tables.

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

Quick start:

```powershell
pip install -r requirements.txt
python -m src.run_pipeline --refresh-demo-inputs
```

After the run, start with:

- `outputs/reports/capital_pipeline_report.md`
- `outputs/tables/capital_summary.csv`
- `outputs/tables/pipeline_validation_report.csv`

Run validation tests:

```powershell
python -m pytest
```

Alternative (wrapper script):

```powershell
python scripts/run_pipeline.py --refresh-demo-inputs
```

Run without monitoring enrichment:

```powershell
python -m src.run_pipeline --refresh-demo-inputs --no-monitoring
```

## Testing and validation

- `tests/test_pipeline.py` runs the pipeline end-to-end and checks that key output tables exist and are non-empty.
- `outputs/tables/pipeline_validation_report.csv` captures the same reconciliations in a reviewer-friendly table.

## Limitations / Demo-Only Note

- All source extracts are synthetic or simulated when upstream files are unavailable.
- Capital mechanics, expected-loss adjustments, and monitoring overlays are simplified for explainability.
- The repo is intended for portfolio demonstration and reporting workflow review, not for production regulatory capital use.

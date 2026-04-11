# RWA-capital-commercial

`RWA-capital-commercial` is the simplified capital-style end-of-stack repo that converts risk, stress, and monitoring outputs into explainable RWA and capital reporting.

## What this repo is

`RWA-capital-commercial` is the simplified capital-style layer at the end of an Australian commercial credit-risk portfolio demonstration. It translates validated upstream PD, LGD, EAD, expected loss, stress-testing, and monitoring outputs into explainable RWA and capital reporting for GitHub review.

This is a public portfolio demonstration, not a production Basel or APRA capital engine. The repo uses transparent assumptions, synthetic sample data when source extracts are not present, and practical bank-style wording rather than regulatory over-claiming.

## Where it sits in the full credit-risk stack

This repo sits at the end of the stack and consumes outputs from:

- `PD-and-scorecard-commercial`
- `LGD-commercial`
- `EAD-CCF-commercial`
- `expected-loss-engine-commercial`
- `stress-testing-commercial`
- `Portfolio-Monitoring-MIS`

`Portfolio-Monitoring-MIS` is treated as an upstream post-origination monitoring and reporting layer. It does not replace the PD, LGD, EAD, or expected-loss inputs. It adds management context to capital-style reporting through watchlist, migration, realised-vs-expected, and concentration views.

## Inputs

The pipeline can run from a direct portfolio input only, or from that portfolio input plus enriched upstream extracts.

Primary portfolio input:

- `data/raw/demo_portfolio.csv`

Upstream component inputs expected in `data/external/`:

- `pd_output.csv`
- `lgd_output.csv`
- `ead_output.csv`
- `expected_loss_output.csv`
- `stress_testing_output.csv`

Monitoring inputs expected in `data/external/`:

- `monthly_risk_pack.csv`
- `migration_matrix.csv`
- `realised_vs_expected.csv`
- `watchlist_summary.csv`
- `concentration_summary.csv`

If those files are not present, the repo generates deterministic demo extracts locally so the workflow remains runnable and the monitoring link is visible even when `Portfolio-Monitoring-MIS` extracts are unavailable.

## What the pipeline does

The pipeline:

- loads or generates a commercial facility-level portfolio input
- loads or simulates upstream PD, LGD, EAD, expected loss, and stress outputs
- loads or simulates monitoring outputs from `Portfolio-Monitoring-MIS`
- builds a capital-ready analytical base table in `data/processed/`
- applies simplified capital-style risk weights, maturity adjustments, capital ratio assumptions, and expected-loss adjustment logic
- produces RWA and capital tables by facility and segment
- adds watchlist, downgrade, migration, realised-vs-expected, and concentration context for management interpretation
- exports flat CSV outputs to `outputs/tables/` plus sample inputs and a summary report

## Outputs

Core output tables:

- `outputs/tables/rwa_by_facility.csv`
- `outputs/tables/rwa_by_segment.csv`
- `outputs/tables/capital_summary.csv`
- `outputs/tables/expected_loss_adjustment_summary.csv`

Monitoring-linked reporting tables:

- `outputs/tables/monitoring_capital_bridge.csv`
- `outputs/tables/watchlist_capital_summary.csv`
- `outputs/tables/concentration_capital_summary.csv`

Validation and sample artifacts:

- `outputs/tables/pipeline_validation_report.csv`
- `outputs/reports/capital_pipeline_report.md`
- `outputs/samples/demo_portfolio_input.csv`

## How to run

```powershell
python -m src.run_pipeline --refresh-demo-inputs
```

Or:

```powershell
python scripts/run_pipeline.py --refresh-demo-inputs
```

To run without monitoring enrichment:

```powershell
python -m src.run_pipeline --refresh-demo-inputs --no-monitoring
```

## Limitations and synthetic-data note

- The repo uses synthetic data whenever external source extracts are missing.
- The capital mechanics are simplified, explainable portfolio assumptions rather than production regulatory calculations.
- Monitoring indicators are primarily used to enrich capital interpretation and bridge reporting, not to claim a full production early-warning or regulatory capital framework.
- Production use would require controlled source systems, policy-approved methodology, model validation, reconciliation controls, and formal governance.

## How it connects to the next repo

This repo is the end of the modelling stack, so there is no required downstream risk model repo after it. The exported tables are intentionally flat so they can feed an optional reporting layer, employer-ready presentation pack, or portfolio review workflow without depending on workspace-specific path conventions.

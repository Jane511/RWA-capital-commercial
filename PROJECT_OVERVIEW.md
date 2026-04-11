# Project Overview - RWA-capital-commercial

`RWA-capital-commercial` is the final simplified capital-style layer in the commercial credit-risk portfolio stack.

## Repo Purpose

`RWA-capital-commercial` is the simplified capital-style engine at the end of the commercial credit-risk stack. It converts upstream risk outputs into explainable facility-, segment-, and portfolio-level RWA and capital reporting.

The repo is designed for public portfolio presentation rather than production regulatory use. It shows how validated component outputs can be assembled into a bank-style capital view with transparent assumptions.

## Workflow Summary

1. Load or generate a facility-level portfolio input in `data/raw/`.
2. Load or simulate component outputs for PD, LGD, EAD, expected loss, and stress testing from `data/external/`.
3. Load or simulate monitoring outputs from `portfolio-monitor-commercial` (planned monitoring repo; not yet published on the public portfolio).
4. Build a combined capital input snapshot in `data/interim/`.
5. Build a monitoring-enriched analytical base table in `data/processed/`.
6. Apply simplified capital-style risk weights, maturity adjustments, capital ratio assumptions, and expected-loss adjustment logic.
7. Export reporting tables, validation results, chart data, and sample inputs to `outputs/`.

## Upstream Inputs

The repo is documented against these upstream repositories:

- `PD-and-scorecard-commercial`
- `LGD-commercial`
- `EAD-CCF-commercial`
- `expected-loss-engine-commercial`
- `stress-testing-commercial`
- `portfolio-monitor-commercial` (planned monitoring repo; not yet published on the public portfolio)

There is no required downstream modelling repo after this layer. Outputs are intended for portfolio review, reporting, and presentation use.

Expected monitoring files:

- `monthly_risk_pack.csv`
- `migration_matrix.csv`
- `realised_vs_expected.csv`
- `watchlist_summary.csv`
- `concentration_summary.csv`

## How Monitoring Outputs Enrich Capital Reporting

`portfolio-monitor-commercial` is positioned as a planned upstream reporting and validation layer that is not yet published on the public portfolio. In this repo it adds:

- watchlist exposure summaries next to capital metrics
- downgrade and migration context for segment-level review
- realised-vs-expected comparisons for management interpretation
- concentration views by industry, product, collateral, geography, and top obligor
- a monitoring-to-capital bridge table that sits alongside the core RWA outputs

The monitoring extracts do not replace PD, LGD, EAD, or expected-loss inputs. They enrich interpretation and reporting around the capital outputs.

Some downstream modules are planned but not yet published on the public portfolio.

## Key Outputs

- `outputs/tables/rwa_by_facility.csv`
- `outputs/tables/rwa_by_segment.csv`
- `outputs/tables/capital_summary.csv`
- `outputs/tables/expected_loss_adjustment_summary.csv`
- `outputs/tables/monitoring_capital_bridge.csv`
- `outputs/tables/watchlist_capital_summary.csv`
- `outputs/tables/concentration_capital_summary.csv`
- `outputs/tables/pipeline_validation_report.csv`

## Limitations

- Synthetic demo data is used when source extracts are unavailable.
- Risk weights and expected-loss adjustment logic are simplified portfolio assumptions.
- The repo is not a Basel or APRA production capital implementation.
- Monitoring overlays are interpretive and demonstrative rather than policy-approved regulatory adjustments.

## Future Enhancements

- parameterised scenario inputs and management overlays
- richer product and collateral segmentation
- explicit provisioning inputs rather than a simplified provision proxy
- more granular concentration and migration trend history
- optional packaging for presentation dashboards or board-style summary reports

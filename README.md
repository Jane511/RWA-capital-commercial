# RWA-Capital-Credit-Risk

## What this repo is

This repo is the simplified capital-style engine at the end of the credit-risk stack for a bank-style Australian credit-risk portfolio demonstration. It uses public-data friendly and synthetic sample data only.

## Where it sits in the full credit-risk stack

Upstream inputs:
- PD-and-Scorecard-Cashflow-Lending
- LGD-Cashflow-and-Property-Lending
- EAD-CCF-Cashflow-Lending
- Expected-Loss-Engine-Australia
- Stress-Testing-Credit-Portfolio

Downstream consumers:
- None - end of stack

## Inputs

The demo pipeline uses `data/raw/demo_portfolio.csv`, generated automatically when missing. The fields cover borrower IDs, facility IDs, segment, industry, product type, limit, drawn balance, collateral, PD, LGD, EAD, and borrower financial metrics.

## What the pipeline does

It loads demo data, builds reusable credit features, runs the `rwa` engine, validates the outputs, and writes downstream-friendly CSV files.

## Outputs

- `outputs/tables/rwa_by_facility.csv`
- `outputs/tables/rwa_by_segment.csv`
- `outputs/tables/capital_summary.csv`
- `outputs/tables/expected_loss_adjustment_summary.csv`
- `outputs/tables/pipeline_validation_report.csv`

## How to run

```powershell
python -m src.codex_run_pipeline
```

Or:

```powershell
python scripts/run_codex_pipeline.py
```

## Limitations and synthetic-data note

- Demo data is synthetic and not confidential bank data.
- Thresholds, overlays, and formulae are transparent portfolio-demonstration assumptions.
- Production use would require governed source data, calibration, model validation, and approval.

## How it connects to the next repo

The exported CSV files are intentionally flat and can be copied to the next repository's `data/external` or replaced with validated production extracts.

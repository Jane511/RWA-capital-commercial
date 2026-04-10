# RWA & Capital Module

This project is a simplified, bank-aligned capital framework for learning and portfolio analysis. It is not a regulatory capital engine and does not represent APRA-approved IRB models.

The module takes PD, LGD, and EAD outputs and converts them into:

- expected loss
- capital requirement
- risk-weighted assets
- capital ratios
- a simple stressed capital view

The build follows the more specific of the two instruction PDFs in this folder and uses `lgd_downturn` plus `ead_downturn` in the EL, capital, and RWA formulas.

## Core formulas

```text
Expected Loss = pd_12m x lgd_downturn x ead_downturn
Capital Requirement = Expected Loss x 12.5
RWA = Capital Requirement x 12.5
CET1 Ratio = CET1 Capital / Total RWA
Total Capital Ratio = Total Capital / Total RWA
```

## Repo structure

```text
data/
  raw/
    exposure_master.csv
  upstream/
    pd_output.csv
    lgd_output.csv
    ead_output.csv
  manual/
    capital_structure.csv
  processed/
    capital_input.csv
notebooks/
  01_prepare_capital_input.ipynb
  02_calculate_el.ipynb
  03_calculate_rwa.ipynb
  04_capital_ratios.ipynb
  05_stress_testing.ipynb
output/
  exposure_level_rwa.csv
  portfolio_rwa_summary.csv
  capital_ratio_summary.csv
  stressed_capital_summary.csv
src/
  merge_inputs.py
  calculate_el.py
  calculate_rwa.py
  capital_ratios.py
  stress_testing.py
  pipeline.py
  run_pipeline.py
tests/
  test_pipeline.py
README.md
requirements.txt
```

## Inputs

Expected files:

- `data/raw/exposure_master.csv`
- `data/upstream/pd_output.csv`
- `data/upstream/lgd_output.csv`
- `data/upstream/ead_output.csv`
- `data/manual/capital_structure.csv`

If any of these files are missing, the pipeline generates deterministic demo inputs automatically so the repo runs from a clean checkout.

## Outputs

Running the pipeline produces:

- `data/processed/capital_input.csv`
- `output/exposure_level_rwa.csv`
- `output/portfolio_rwa_summary.csv`
- `output/capital_ratio_summary.csv`
- `output/stressed_capital_summary.csv`

## How to run

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the full pipeline:

```powershell
python src/run_pipeline.py
```

Regenerate the demo inputs first:

```powershell
python src/run_pipeline.py --refresh-demo-inputs
```

Run tests:

```powershell
pytest
```

## Stress scenario

The repo includes one simple stress scenario from the instruction PDF:

- PD up 30 percent
- LGD up 10 percent

The stressed summary includes both the `base` row and the stressed row so the deltas are easy to compare.

## Interview summary

Use this:

```text
I built a capital module that takes PD, LGD and EAD outputs from my credit models and converts them into expected loss, risk-weighted assets and capital ratios. This mirrors how banks translate credit risk into capital requirements under a Basel-style framework.
```

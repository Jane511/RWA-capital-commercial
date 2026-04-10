# Methodology - RWA-Capital-Credit-Risk

1. Load or generate synthetic demo data.
2. Standardise borrower, facility, exposure, collateral, and financial fields.
3. Build utilisation, margin, DSCR, leverage, liquidity, working-capital, and collateral coverage features.
4. Run the `rwa` engine.
5. Validate and export CSV outputs.

## Output contract

- `outputs/tables/rwa_by_facility.csv`
- `outputs/tables/rwa_by_segment.csv`
- `outputs/tables/capital_summary.csv`
- `outputs/tables/expected_loss_adjustment_summary.csv`

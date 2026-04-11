# Validation Framework - RWA-capital-commercial

## Data Quality Checks

The pipeline writes `outputs/tables/pipeline_validation_report.csv` and checks:

- required analytical base columns
- duplicate facility identifiers
- negative balances or negative EAD values
- EAD below drawn balance
- EAD outside a simple demo tolerance to approved limits
- PD and LGD outside valid ranges
- missing reporting dates in monitoring-linked files
- watchlist keys that do not reconcile to the portfolio
- invalid concentration summary shares or dimensions

## Reconciliations

The validation report also checks that:

- facility RWA totals reconcile to segment RWA totals
- facility RWA and capital totals reconcile to `capital_summary.csv`
- expected-loss adjustment totals reconcile back to facility reporting
- watchlist and non-watchlist totals reconcile back to the facility table

## Monitoring-Linked Validation

Monitoring-linked enrichments are checked for:

- populated reporting dates
- valid watchlist-to-facility joins
- valid concentration dimension labels
- concentration shares between zero and one

These checks are intended to confirm that the monitoring feeds are suitable for enrichment and interpretation, not to claim that the MIS layer is a full prudential control framework.

## Demo Capital Estimation Limitations

- The validation framework is designed for a portfolio demonstration.
- Passing checks does not imply regulatory capital compliance.
- Production use would need additional reconciliations to source systems, approvals, policy controls, and formal model validation evidence.

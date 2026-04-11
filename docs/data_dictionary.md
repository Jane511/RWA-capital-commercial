# Data Dictionary - RWA-capital-commercial

## Core Portfolio Input Fields

| Field | Description |
| --- | --- |
| `reporting_date` | Portfolio reporting date used across the pipeline. |
| `borrower_id` | Borrower or obligor identifier. |
| `facility_id` | Facility-level identifier used as the primary merge key. |
| `obligor_name` | Borrower or group display name. |
| `segment` | High-level portfolio segment such as SME, Corporate, Property, or Trade Finance. |
| `industry` | Industry classification used in reporting and concentration views. |
| `product_type` | Facility or product category. |
| `collateral_type` | Simplified collateral classification. |
| `geography` | State or regional geography tag. |
| `limit_amount` | Approved facility limit. |
| `drawn_balance` | Current drawn exposure. |
| `collateral_value` | Demonstration collateral value. |
| `maturity_years` | Simplified remaining maturity assumption. |

## Upstream Component Fields

| Field | Description |
| --- | --- |
| `pd` | PD input from `PD-and-scorecard-commercial`. |
| `lgd` | LGD input from `LGD-commercial`. |
| `ead` | EAD input from `EAD-CCF-commercial`. |
| `expected_loss` | Expected loss input from `expected-loss-engine-commercial`. |
| `stressed_loss` | Stressed loss input from `stress-testing-commercial`. |
| `stress_scenario` | Stress scenario label where supplied. |

## Monitoring-Linked Fields

| Field | Description |
| --- | --- |
| `internal_grade_previous` | Prior monitoring grade used in migration reporting. |
| `internal_grade_current` | Current monitoring grade used in migration reporting. |
| `watchlist_flag` | Watchlist indicator from monitoring outputs. |
| `watchlist_reason` | High-level watchlist rationale. |
| `recent_downgrade_indicator` | Flag showing recent grade deterioration. |
| `days_past_due` | Simple arrears indicator used in demo monitoring. |
| `monitoring_commentary` | Short management-style monitoring note. |
| `expected_loss_amount` | Segment-level expected loss in realised-vs-expected reporting. |
| `realised_loss_amount` | Segment-level realised loss in realised-vs-expected reporting. |
| `realised_to_expected_ratio` | Ratio of realised to expected loss. |
| `variance_amount` | Difference between realised and expected loss. |
| `migration_deterioration_share` | Share of segment exposure migrating to worse grades. |
| `concentration_tag` | Combined concentration commentary tag applied to facility reporting. |

## Output Fields by Table

### `rwa_by_facility.csv`

| Field | Description |
| --- | --- |
| `reporting_date` | Output reporting date. |
| `borrower_id`, `obligor_name`, `facility_id` | Facility identifiers. |
| `segment`, `industry`, `product_type`, `collateral_type`, `geography` | Reporting descriptors. |
| `limit_amount`, `drawn_balance`, `ead` | Exposure fields used in reporting. |
| `pd`, `lgd`, `maturity_years` | Core capital inputs. |
| `expected_loss`, `stressed_loss` | Loss measures used in capital interpretation. |
| `risk_weight` | Simplified capital-style risk weight. |
| `rwa` | Risk-weighted assets. |
| `capital_amount` | Base capital amount using the demo capital ratio. |
| `capital_after_el_adjustment` | Capital amount after the simplified expected-loss shortfall adjustment. |
| `watchlist_flag`, `watchlist_reason`, `recent_downgrade_indicator` | Monitoring context fields. |
| `realised_to_expected_ratio`, `variance_amount`, `migration_deterioration_share`, `concentration_tag` | Monitoring and interpretation fields. |

### `rwa_by_segment.csv`

| Field | Description |
| --- | --- |
| `facility_count`, `borrower_count` | Segment counts. |
| `total_exposure`, `total_ead` | Segment exposure totals. |
| `expected_loss`, `stressed_loss` | Segment loss totals. |
| `total_rwa`, `capital_amount`, `capital_after_el_adjustment` | Segment capital totals. |
| `average_risk_weight` | Mean simplified risk weight. |
| `watchlist_count`, `recent_downgrade_count` | Segment monitoring counts. |

### `capital_summary.csv`

| Field | Description |
| --- | --- |
| `portfolio` | Portfolio label. |
| `facility_count`, `borrower_count` | Portfolio counts. |
| `total_exposure`, `total_ead` | Portfolio exposures. |
| `expected_loss`, `stressed_loss` | Portfolio loss measures. |
| `total_rwa`, `capital_amount`, `capital_after_el_adjustment` | Portfolio capital totals. |
| `capital_ratio_assumption` | Flat capital ratio used in the demo. |
| `average_risk_weight` | Average portfolio risk weight. |
| `watchlist_exposure`, `recent_downgrade_exposure` | Monitoring-linked portfolio exposures. |

### `expected_loss_adjustment_summary.csv`

| Field | Description |
| --- | --- |
| `provision_proxy` | Simplified provision coverage proxy. |
| `expected_loss_shortfall` | Amount of expected loss not covered by the proxy. |
| `capital_amount`, `capital_after_el_adjustment` | Base and adjusted capital amounts. |

### `monitoring_capital_bridge.csv`

| Field | Description |
| --- | --- |
| `segment` | Segment-level grouping. |
| `exposure`, `ead` | Segment exposures. |
| `expected_loss`, `stressed_loss`, `rwa`, `capital_amount` | Segment capital bridge measures. |
| `watchlist_count`, `recent_downgrade_count` | Monitoring counts. |
| `realised_to_expected_ratio`, `migration_deterioration_share` | Monitoring interpretation ratios. |
| `concentration_commentary` | Segment concentration commentary. |

### `watchlist_capital_summary.csv`

| Field | Description |
| --- | --- |
| `watchlist_population` | `Watchlist` or `Non-watchlist`. |
| `facility_count`, `borrower_count` | Population counts. |
| `exposure`, `ead`, `expected_loss`, `stressed_loss`, `rwa`, `capital_amount` | Population metrics. |

### `concentration_capital_summary.csv`

| Field | Description |
| --- | --- |
| `dimension_type` | `industry`, `product_type`, `collateral_type`, `geography`, or `top_obligor`. |
| `dimension_value` | Value within the chosen concentration dimension. |
| `facility_count`, `borrower_count` | Concentration counts. |
| `exposure`, `ead`, `rwa`, `capital_amount` | Concentration totals. |
| `portfolio_share` | Share of the portfolio by EAD. |
| `concentration_flag` | Simplified concentration flag. |

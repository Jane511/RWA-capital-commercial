# Methodology - RWA-capital-commercial

## Overview

`RWA-capital-commercial` is a simplified capital-style engine that sits after the component model repos. It consumes validated upstream outputs and converts them into explainable RWA and capital summaries for a commercial portfolio demonstration.

## Simplified Capital-Style Mechanics

The repo uses a facility-level analytical base table built from:

- portfolio descriptors such as segment, product, collateral type, geography, limit, and drawn balance
- PD inputs from `PD-and-scorecard-commercial`
- LGD inputs from `LGD-commercial`
- EAD inputs from `EAD-CCF-commercial`
- expected loss inputs from `expected-loss-engine-commercial`
- stressed loss inputs from `stress-testing-commercial`

The simplified RWA mechanics are:

1. assign a segment base risk weight
2. apply a product multiplier
3. apply a maturity-style adjustment
4. scale the result with PD and LGD so higher-risk facilities carry higher demo risk weights
5. calculate `RWA = EAD x risk_weight`
6. calculate `capital_amount = RWA x 10.5%`

This is intentionally transparent and explainable. It is not intended to replicate a full Basel or APRA formula set.

## Treatment of PD, LGD, EAD, and Maturity Assumptions

- PD is treated as the forward-looking default likelihood input.
- LGD is treated as the downturn-style loss severity input.
- EAD is treated as the capital reporting exposure base.
- Maturity is applied as a simple uplift to longer-duration facilities rather than a production regulatory maturity treatment.
- Expected loss is carried into reporting and into a simplified expected-loss adjustment summary.

## Expected Loss Adjustment Summary Logic

The repo uses a simplified provision proxy rather than a production accounting or regulatory provisioning feed.

- `provision_proxy = expected_loss x 70%`
- `expected_loss_shortfall = max(expected_loss - provision_proxy, 0)`
- `capital_after_el_adjustment = capital_amount + expected_loss_shortfall`

This is a portfolio-demonstration bridge, not a formal regulatory deduction framework.

## Role of Stress Outputs

Stress outputs are consumed as a separate upstream feed and used to carry a stressed loss view into:

- `capital_summary.csv`
- `monitoring_capital_bridge.csv`
- `watchlist_capital_summary.csv`
- `expected_loss_adjustment_summary.csv`

The repo does not claim a full stressed capital adequacy framework. It shows how stressed loss context can sit beside simplified capital metrics.

## Role of Monitoring Outputs

`Portfolio-Monitoring-MIS` adds post-origination monitoring context through:

- watchlist flags and watchlist reasons
- downgrade indicators and migration deterioration shares
- realised-vs-expected loss comparisons by segment
- concentration flags by industry, product, geography, and top obligor

These outputs enrich management interpretation and bridge reporting. They are primarily explanatory inputs unless a simplified overlay is explicitly stated.

## How RWA and Capital Summaries Are Derived

- `rwa_by_facility.csv` holds facility-level risk, loss, RWA, capital, and monitoring context.
- `rwa_by_segment.csv` aggregates the facility output to a segment view.
- `capital_summary.csv` provides the portfolio headline totals.
- `monitoring_capital_bridge.csv` combines capital metrics with watchlist, downgrade, migration, realised-vs-expected, and concentration commentary.

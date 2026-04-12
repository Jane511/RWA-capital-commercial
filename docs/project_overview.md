# Project Overview

`RWA-capital-commercial` is the end-of-stack capital analytics layer in the public commercial credit-risk workflow.

## Portfolio role

It combines upstream component outputs into facility-, segment-, and portfolio-level RWA, capital, and monitoring-enriched reporting views.

## Upstream inputs

- `PD-and-scorecard-commercial`
- `LGD-commercial`
- `EAD-CCF-commercial`
- `expected-loss-engine-commercial`
- `stress-testing-commercial`
- optional monitoring context from `portfolio-monitor-commercial`

## Downstream consumers

No required downstream modelling repo. Outputs are intended for portfolio review, capital reporting, and employer-facing end-of-stack presentation.

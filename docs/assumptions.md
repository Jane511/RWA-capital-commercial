# Assumptions - RWA-capital-commercial

## Synthetic-Data Assumptions

- Demo portfolio records are synthetic and deterministic.
- Demo upstream component files are generated locally when external repo outputs are unavailable.
- Demo monitoring files are generated locally when `portfolio-monitor-commercial` extracts are unavailable.
- No hidden internal bank data, workspace-specific folder conventions, or OS-specific source paths are required.

## Simplified Capital Rules

- Segment base risk weights are fixed demo assumptions.
- Product multipliers and maturity adjustments are simplified portfolio levers rather than production regulatory parameters.
- Capital is calculated using a flat 10.5% capital ratio assumption.
- Expected-loss adjustment logic uses a simplified provision proxy instead of a governed accounting or prudential provisioning feed.

## Portfolio Demonstration Limitations

- The repo is not a production Basel engine.
- The repo is not an APRA-approved capital model.
- The outputs are suitable for methodology discussion, repo review, and portfolio demonstration only.
- Production use would require source governance, approved policy interpretation, model validation, controls, and formal reconciliation sign-off.

## Monitoring Indicator Usage

- Watchlist flags, downgrade indicators, migration signals, realised-vs-expected metrics, and concentration tags are primarily explanatory.
- Monitoring indicators enrich capital reporting and portfolio review outputs.
- Monitoring indicators are not intended to imply that post-origination MIS alone drives regulatory capital.
- Where a simplified overlay or commentary is shown, it is disclosed as a demonstration assumption.

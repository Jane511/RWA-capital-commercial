from __future__ import annotations

import argparse
from pathlib import Path

from .calculate_el import add_expected_loss
from .calculate_rwa import add_rwa_metrics, summarise_portfolio_rwa
from .capital_ratios import build_capital_ratio_summary
from .config import MANUAL_DIR, OUTPUT_DIR, PROCESSED_DIR, RAW_DIR, UPSTREAM_DIR
from .merge_inputs import build_capital_input
from .stress_testing import run_stress_test
from .utils import ensure_directories, save_dataframe


def run_pipeline(
    raw_dir: str | Path = RAW_DIR,
    upstream_dir: str | Path = UPSTREAM_DIR,
    manual_dir: str | Path = MANUAL_DIR,
    processed_dir: str | Path = PROCESSED_DIR,
    output_dir: str | Path = OUTPUT_DIR,
    refresh_demo_inputs: bool = False,
    persist: bool = True,
) -> dict:
    processed_path = Path(processed_dir)
    output_path = Path(output_dir)
    ensure_directories(raw_dir, upstream_dir, manual_dir, processed_path, output_path)

    capital_input_df, capital_structure_df = build_capital_input(
        raw_dir=raw_dir,
        upstream_dir=upstream_dir,
        manual_dir=manual_dir,
        processed_dir=processed_path,
        refresh_demo=refresh_demo_inputs,
        persist=persist,
    )
    exposure_level_rwa_df = add_rwa_metrics(add_expected_loss(capital_input_df))
    portfolio_summary_df = summarise_portfolio_rwa(exposure_level_rwa_df)
    capital_ratio_summary_df = build_capital_ratio_summary(exposure_level_rwa_df, capital_structure_df)
    stressed_capital_summary_df = run_stress_test(capital_input_df, capital_structure_df)

    if persist:
        save_dataframe(exposure_level_rwa_df, output_path / "exposure_level_rwa.csv")
        save_dataframe(portfolio_summary_df, output_path / "portfolio_rwa_summary.csv")
        save_dataframe(capital_ratio_summary_df, output_path / "capital_ratio_summary.csv")
        save_dataframe(stressed_capital_summary_df, output_path / "stressed_capital_summary.csv")

    return {
        "capital_input": capital_input_df,
        "capital_structure": capital_structure_df,
        "exposure_level_rwa": exposure_level_rwa_df,
        "portfolio_rwa_summary": portfolio_summary_df,
        "capital_ratio_summary": capital_ratio_summary_df,
        "stressed_capital_summary": stressed_capital_summary_df,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RWA and capital module pipeline.")
    parser.add_argument(
        "--refresh-demo-inputs",
        action="store_true",
        help="Regenerate deterministic demo inputs before running the pipeline.",
    )
    args = parser.parse_args()

    result = run_pipeline(refresh_demo_inputs=args.refresh_demo_inputs, persist=True)
    total_rwa = float(result["exposure_level_rwa"]["rwa"].sum())
    total_expected_loss = float(result["exposure_level_rwa"]["expected_loss"].sum())
    stressed = result["stressed_capital_summary"].set_index("scenario").loc["stress_pd_up_30_lgd_up_10"]

    print(f"Exposures processed: {len(result['exposure_level_rwa'])}")
    print(f"Portfolio expected loss: {total_expected_loss:,.2f}")
    print(f"Portfolio RWA: {total_rwa:,.2f}")
    print(f"Stressed RWA: {float(stressed['total_rwa']):,.2f}")
    print(f"Output files written to: {Path(OUTPUT_DIR).resolve()}")


if __name__ == "__main__":
    main()

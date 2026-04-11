from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import REPO_NAME
from .loaders import write_csv


def write_pipeline_outputs(
    paths: dict[str, Path],
    combined_inputs: pd.DataFrame,
    analytical_base: pd.DataFrame,
    output_tables: dict[str, pd.DataFrame],
    monitoring_bundle: dict[str, pd.DataFrame],
) -> dict[str, Path]:
    written_paths: dict[str, Path] = {}
    write_csv(combined_inputs, paths["interim_dir"] / "combined_capital_inputs.csv")
    write_csv(analytical_base, paths["processed_dir"] / "capital_analytical_base.csv")
    for table_name, df in output_tables.items():
        target = paths["tables_dir"] / table_name
        write_csv(df, target)
        written_paths[table_name] = target

    chart_files = {
        "rwa_by_segment_chart_data.csv": output_tables["rwa_by_segment.csv"][["segment", "total_rwa", "capital_amount", "watchlist_count"]],
        "watchlist_capital_chart_data.csv": output_tables["watchlist_capital_summary.csv"][["watchlist_population", "ead", "rwa", "capital_amount"]],
    }
    for file_name, df in chart_files.items():
        target = paths["charts_dir"] / file_name
        write_csv(df, target)
        written_paths[file_name] = target

    sample_files = {
        "demo_portfolio_input.csv": combined_inputs[["reporting_date", "borrower_id", "facility_id", "segment", "industry", "product_type", "limit_amount", "drawn_balance", "pd", "lgd", "ead"]],
        "demo_monthly_risk_pack.csv": monitoring_bundle["monthly_risk_pack"],
        "demo_concentration_summary.csv": monitoring_bundle["concentration_summary"],
    }
    for file_name, df in sample_files.items():
        target = paths["samples_dir"] / file_name
        write_csv(df, target)
        written_paths[file_name] = target

    capital = output_tables["capital_summary.csv"].iloc[0]
    bridge_lines = [
        f"- {row.segment}: EAD {row.ead:,.0f}, RWA {row.rwa:,.0f}, watchlist {int(row.watchlist_count)}"
        for row in output_tables["monitoring_capital_bridge.csv"].itertuples(index=False)
    ]
    report_text = "\n".join(
        [
            f"# Pipeline Summary - {REPO_NAME}",
            "",
            "This simplified capital-style report consumes component outputs plus monitoring context.",
            "",
            f"- Reporting date: {capital['reporting_date']}",
            f"- Total EAD: {capital['total_ead']:,.0f}",
            f"- Total RWA: {capital['total_rwa']:,.0f}",
            f"- Capital amount: {capital['capital_amount']:,.0f}",
            f"- Capital after EL adjustment: {capital['capital_after_el_adjustment']:,.0f}",
            "",
            "## Monitoring bridge",
            *bridge_lines,
        ]
    )
    report_path = paths["reports_dir"] / "capital_pipeline_report.md"
    report_path.write_text(report_text, encoding="utf-8")
    written_paths["capital_pipeline_report.md"] = report_path
    return written_paths

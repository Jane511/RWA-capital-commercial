from __future__ import annotations

import argparse
from pathlib import Path

from .config import REPO_NAME, REQUIRED_OUTPUT_TABLES, build_paths
from .engine import run_capital_engine
from .features import build_capital_base_table
from .loaders import load_input_bundle
from .outputs import write_pipeline_outputs
from .validation import build_validation_report


def run_pipeline(
    project_root: str | Path | None = None,
    refresh_demo_inputs: bool = False,
    include_monitoring: bool = True,
    persist: bool = True,
) -> dict[str, object]:
    paths = build_paths(project_root)
    inputs = load_input_bundle(paths=paths, refresh_demo_inputs=refresh_demo_inputs, include_monitoring=include_monitoring)
    combined_inputs, analytical_base = build_capital_base_table(inputs)
    outputs = run_capital_engine(analytical_base)
    validation = build_validation_report(
        combined_inputs=combined_inputs,
        analytical_base=analytical_base,
        output_tables=outputs,
        monitoring_bundle=inputs["monitoring"],
    )
    outputs["pipeline_validation_report.csv"] = validation
    written_paths: dict[str, Path] = {}
    if persist:
        written_paths = write_pipeline_outputs(
            paths=paths,
            combined_inputs=combined_inputs,
            analytical_base=analytical_base,
            output_tables=outputs,
            monitoring_bundle=inputs["monitoring"],
        )
    missing_tables = [name for name in REQUIRED_OUTPUT_TABLES if name not in outputs]
    if missing_tables:
        raise RuntimeError(f"Pipeline did not produce required outputs: {', '.join(missing_tables)}")
    return {
        "repo_name": REPO_NAME,
        "paths": paths,
        "inputs": inputs,
        "combined_inputs": combined_inputs,
        "analytical_base": analytical_base,
        "outputs": outputs,
        "validation": validation,
        "written_paths": written_paths,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the simplified RWA capital commercial pipeline.")
    parser.add_argument("--refresh-demo-inputs", action="store_true", help="Regenerate deterministic demo inputs.")
    parser.add_argument("--no-monitoring", action="store_true", help="Run without monitoring enrichment.")
    args = parser.parse_args()
    result = run_pipeline(refresh_demo_inputs=args.refresh_demo_inputs, include_monitoring=not args.no_monitoring, persist=True)
    capital = result["outputs"]["capital_summary.csv"].iloc[0]
    print(f"{REPO_NAME} completed")
    print(f"Reporting date: {capital['reporting_date']}")
    print(f"Total EAD: {capital['total_ead']:,.0f}")
    print(f"Total RWA: {capital['total_rwa']:,.0f}")
    print(f"Capital amount: {capital['capital_amount']:,.0f}")
    print(f"Outputs written to: {result['paths']['tables_dir']}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import AS_OF_DATE, MANUAL_DIR, RAW_DIR, UPSTREAM_DIR
from .utils import ensure_directories, save_dataframe


DEMO_EXPOSURES = [
    {
        "exposure_id": "EXP001",
        "borrower_id": "B001",
        "product_type": "Amortising business term loan",
        "segment": "SME",
        "industry": "Manufacturing",
        "security_type": "General Security Agreement",
        "drawn_balance": 125000,
        "undrawn_limit": 0,
        "collateral_value": 90000,
        "lvr": 0.72,
        "default_flag": 0,
    },
    {
        "exposure_id": "EXP002",
        "borrower_id": "B002",
        "product_type": "Overdraft",
        "segment": "SME",
        "industry": "Retail",
        "security_type": "General Security Agreement",
        "drawn_balance": 42000,
        "undrawn_limit": 58000,
        "collateral_value": 15000,
        "lvr": 0.64,
        "default_flag": 0,
    },
    {
        "exposure_id": "EXP003",
        "borrower_id": "B003",
        "product_type": "Revolving working capital line",
        "segment": "Corporate",
        "industry": "Wholesale",
        "security_type": "General Security Agreement",
        "drawn_balance": 680000,
        "undrawn_limit": 220000,
        "collateral_value": 125000,
        "lvr": 0.81,
        "default_flag": 0,
    },
    {
        "exposure_id": "EXP004",
        "borrower_id": "B004",
        "product_type": "Construction facility",
        "segment": "Property",
        "industry": "Real Estate",
        "security_type": "Commercial Property Mortgage",
        "drawn_balance": 2500000,
        "undrawn_limit": 1500000,
        "collateral_value": 3200000,
        "lvr": 0.78,
        "default_flag": 0,
    },
    {
        "exposure_id": "EXP005",
        "borrower_id": "B005",
        "product_type": "Trade finance line",
        "segment": "SME",
        "industry": "Import Export",
        "security_type": "Inventory and Receivables",
        "drawn_balance": 180000,
        "undrawn_limit": 120000,
        "collateral_value": 90000,
        "lvr": 0.67,
        "default_flag": 1,
    },
    {
        "exposure_id": "EXP006",
        "borrower_id": "B006",
        "product_type": "Development facility",
        "segment": "Property",
        "industry": "Property Development",
        "security_type": "Commercial Property Mortgage",
        "drawn_balance": 1750000,
        "undrawn_limit": 450000,
        "collateral_value": 2100000,
        "lvr": 0.83,
        "default_flag": 0,
    },
    {
        "exposure_id": "EXP007",
        "borrower_id": "B007",
        "product_type": "Equipment term loan",
        "segment": "Corporate",
        "industry": "Transport",
        "security_type": "Specific Equipment Security",
        "drawn_balance": 540000,
        "undrawn_limit": 0,
        "collateral_value": 650000,
        "lvr": 0.83,
        "default_flag": 0,
    },
    {
        "exposure_id": "EXP008",
        "borrower_id": "B008",
        "product_type": "Cash flow revolver",
        "segment": "SME",
        "industry": "Hospitality",
        "security_type": "General Security Agreement",
        "drawn_balance": 12000,
        "undrawn_limit": 38000,
        "collateral_value": 10000,
        "lvr": 0.55,
        "default_flag": 0,
    },
    {
        "exposure_id": "EXP009",
        "borrower_id": "B009",
        "product_type": "Trade working capital line",
        "segment": "Corporate",
        "industry": "Import Export",
        "security_type": "Inventory and Receivables",
        "drawn_balance": 450000,
        "undrawn_limit": 150000,
        "collateral_value": 250000,
        "lvr": 0.71,
        "default_flag": 0,
    },
    {
        "exposure_id": "EXP010",
        "borrower_id": "B010",
        "product_type": "Overdraft",
        "segment": "SME",
        "industry": "Services",
        "security_type": "General Security Agreement",
        "drawn_balance": 135000,
        "undrawn_limit": 15000,
        "collateral_value": 50000,
        "lvr": 0.74,
        "default_flag": 1,
    },
    {
        "exposure_id": "EXP011",
        "borrower_id": "B011",
        "product_type": "Amortising agribusiness loan",
        "segment": "SME",
        "industry": "Agriculture",
        "security_type": "General Security Agreement",
        "drawn_balance": 80000,
        "undrawn_limit": 0,
        "collateral_value": 120000,
        "lvr": 0.58,
        "default_flag": 0,
    },
    {
        "exposure_id": "EXP012",
        "borrower_id": "B012",
        "product_type": "Land subdivision facility",
        "segment": "Property",
        "industry": "Property Development",
        "security_type": "Commercial Property Mortgage",
        "drawn_balance": 950000,
        "undrawn_limit": 650000,
        "collateral_value": 1200000,
        "lvr": 0.79,
        "default_flag": 0,
    },
]

DEMO_PD = [
    {"exposure_id": "EXP001", "pd_12m": 0.024},
    {"exposure_id": "EXP002", "pd_12m": 0.061},
    {"exposure_id": "EXP003", "pd_12m": 0.017},
    {"exposure_id": "EXP004", "pd_12m": 0.032},
    {"exposure_id": "EXP005", "pd_12m": 0.143},
    {"exposure_id": "EXP006", "pd_12m": 0.041},
    {"exposure_id": "EXP007", "pd_12m": 0.013},
    {"exposure_id": "EXP008", "pd_12m": 0.087},
    {"exposure_id": "EXP009", "pd_12m": 0.029},
    {"exposure_id": "EXP010", "pd_12m": 0.121},
    {"exposure_id": "EXP011", "pd_12m": 0.019},
    {"exposure_id": "EXP012", "pd_12m": 0.038},
]

DEMO_LGD = [
    {"exposure_id": "EXP001", "lgd_downturn": 0.32},
    {"exposure_id": "EXP002", "lgd_downturn": 0.41},
    {"exposure_id": "EXP003", "lgd_downturn": 0.35},
    {"exposure_id": "EXP004", "lgd_downturn": 0.29},
    {"exposure_id": "EXP005", "lgd_downturn": 0.48},
    {"exposure_id": "EXP006", "lgd_downturn": 0.31},
    {"exposure_id": "EXP007", "lgd_downturn": 0.27},
    {"exposure_id": "EXP008", "lgd_downturn": 0.52},
    {"exposure_id": "EXP009", "lgd_downturn": 0.44},
    {"exposure_id": "EXP010", "lgd_downturn": 0.46},
    {"exposure_id": "EXP011", "lgd_downturn": 0.28},
    {"exposure_id": "EXP012", "lgd_downturn": 0.33},
]

DEMO_EAD = [
    {"exposure_id": "EXP001", "ead_central": 125000.0, "ead_downturn": 125000.0},
    {"exposure_id": "EXP002", "ead_central": 76800.0, "ead_downturn": 88400.0},
    {"exposure_id": "EXP003", "ead_central": 812000.0, "ead_downturn": 856000.0},
    {"exposure_id": "EXP004", "ead_central": 3400000.0, "ead_downturn": 3925000.0},
    {"exposure_id": "EXP005", "ead_central": 228000.0, "ead_downturn": 258000.0},
    {"exposure_id": "EXP006", "ead_central": 2110000.0, "ead_downturn": 2200000.0},
    {"exposure_id": "EXP007", "ead_central": 540000.0, "ead_downturn": 540000.0},
    {"exposure_id": "EXP008", "ead_central": 31000.0, "ead_downturn": 40500.0},
    {"exposure_id": "EXP009", "ead_central": 510000.0, "ead_downturn": 540000.0},
    {"exposure_id": "EXP010", "ead_central": 145500.0, "ead_downturn": 147750.0},
    {"exposure_id": "EXP011", "ead_central": 80000.0, "ead_downturn": 80000.0},
    {"exposure_id": "EXP012", "ead_central": 1437500.0, "ead_downturn": 1600000.0},
]

DEMO_CAPITAL_STRUCTURE = [
    {
        "reporting_date": AS_OF_DATE,
        "cet1_capital": 20000000,
        "total_capital": 25000000,
    }
]


def generate_demo_inputs(
    raw_dir: str | Path = RAW_DIR,
    upstream_dir: str | Path = UPSTREAM_DIR,
    manual_dir: str | Path = MANUAL_DIR,
) -> dict[str, pd.DataFrame]:
    raw_path = Path(raw_dir)
    upstream_path = Path(upstream_dir)
    manual_path = Path(manual_dir)
    ensure_directories(raw_path, upstream_path, manual_path)

    exposure_df = pd.DataFrame(DEMO_EXPOSURES)
    pd_df = pd.DataFrame(DEMO_PD)
    lgd_df = pd.DataFrame(DEMO_LGD)
    ead_df = pd.DataFrame(DEMO_EAD)
    capital_structure_df = pd.DataFrame(DEMO_CAPITAL_STRUCTURE)

    save_dataframe(exposure_df, raw_path / "exposure_master.csv")
    save_dataframe(pd_df, upstream_path / "pd_output.csv")
    save_dataframe(lgd_df, upstream_path / "lgd_output.csv")
    save_dataframe(ead_df, upstream_path / "ead_output.csv")
    save_dataframe(capital_structure_df, manual_path / "capital_structure.csv")

    return {
        "exposure_master": exposure_df,
        "pd_output": pd_df,
        "lgd_output": lgd_df,
        "ead_output": ead_df,
        "capital_structure": capital_structure_df,
    }

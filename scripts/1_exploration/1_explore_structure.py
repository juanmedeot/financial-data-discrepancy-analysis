"""
1_explore_structure.py
----------------------
Initial dataset structure exploration.
Loads the normalized datasets, prints column schemas, data types,
sample rows, and key identifier statistics.

Usage:
    python scripts/1_exploration/1_explore_structure.py
"""

import os
import sys
import io
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def _find_root() -> str:
    candidate = os.path.abspath(__file__)
    for _ in range(6):
        candidate = os.path.dirname(candidate)
        if os.path.isdir(os.path.join(candidate, "data")) and os.path.isdir(os.path.join(candidate, "scripts")):
            return candidate
    raise RuntimeError("Repository root directory not found.")

ROOT = _find_root()
FILE_SALES   = os.path.join(ROOT, "data", "base_sales.xlsx")
FILE_FINANCE = os.path.join(ROOT, "data", "base_finance.xlsx")

for path, label in [(FILE_SALES, "Sales"), (FILE_FINANCE, "Finance")]:
    xl = pd.ExcelFile(path)
    print(f"\n{'='*60}")
    print(f"DATASET: {label} — Sheets: {xl.sheet_names}")
    df = pd.read_excel(path, sheet_name=0)
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"\nColumns and Types:")
    print(df.dtypes.to_string())
    print(f"\nSample Rows (first 3):")
    print(df.head(3).to_string())
    print(f"\nIdentifier Statistics ('id'):")
    print(f"  Unique count: {df['id'].nunique():,}")
    print(f"  Duplicates: {df['id'].duplicated().sum()}")
    print(f"  Type: {df['id'].dtype}")
    print(f"  Sample IDs: {df['id'].head(5).tolist()}")

"""
2_statistical_summary.py
------------------------
Computes comparative statistical summaries between the two datasets:
annual totals, transaction counts, and ID intersection metrics.

Usage:
    python scripts/1_exploration/2_statistical_summary.py
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

df_sales = pd.read_excel(FILE_SALES,   sheet_name=0)
df_fin   = pd.read_excel(FILE_FINANCE, sheet_name=0)

print("=== GLOBAL TOTALS ===")
print(f"Sales   — Amount: {df_sales['economic_amount'].sum():,.2f} | Quantity: {df_sales['quantity'].sum():,}")
print(f"Finance — Amount: {df_fin['economic_amount'].sum():,.2f}   | Quantity: {df_fin['quantity'].sum():,}")

print("\n=== ID INTERSECTION ===")
ids_sales = set(df_sales["id"].astype(str))
ids_fin   = set(df_fin["id"].astype(str))
print(f"Only in Sales:   {len(ids_sales - ids_fin):,}")
print(f"Only in Finance: {len(ids_fin - ids_sales):,}")
print(f"In Both:         {len(ids_sales & ids_fin):,}")

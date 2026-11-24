"""
3_analyze_differences.py
------------------------
Core difference analysis engine. Performs a full outer join on transaction ID,
classifies discrepancies between Sales and Finance datasets, validates
reconciliation integrity, and stores structured results for reporting.

Difference Classification:
  - only_sales:        Transaction exists exclusively in the Sales dataset.
  - only_finance:      Transaction exists exclusively in the Finance dataset.
  - different_amount:  Transaction exists in both, but economic_amount differs.
  - different_course:  Transaction exists in both, amounts match, but course_group differs.
  - identical:         Transaction matches exactly in both amount and course_group.

Usage:
    python scripts/2_analysis/3_analyze_differences.py
"""

import os
import sys
import io
import pickle
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
OUTPUT_PKL   = os.path.join(ROOT, "data", "results.pkl")

# 1. Load Data
df_sales = pd.read_excel(FILE_SALES,   sheet_name=0)
df_fin   = pd.read_excel(FILE_FINANCE, sheet_name=0)
print(f"[LOAD] Sales: {len(df_sales):,} rows | Finance: {len(df_fin):,} rows")

# 2. Assert Initial Invariants
assert df_sales["id"].duplicated().sum() == 0, "Duplicate IDs found in Sales"
assert df_fin["id"].duplicated().sum()   == 0, "Duplicate IDs found in Finance"
print("[VALIDATION] Unique IDs confirmed.")

# 3. Direct Aggregations
total_sales = df_sales["economic_amount"].sum()
total_fin   = df_fin["economic_amount"].sum()
qty_sales   = int(df_sales["quantity"].sum())
qty_fin     = int(df_fin["quantity"].sum())

print(f"\n[GLOBAL TOTALS]")
print(f"  Sales   — Amount: {total_sales:,.2f} | Quantity: {qty_sales:,}")
print(f"  Finance — Amount: {total_fin:,.2f} | Quantity: {qty_fin:,}")
print(f"  Amount Difference (Sales - Finance): {total_sales - total_fin:,.2f}")
print(f"  Quantity Difference (Sales - Finance): {qty_sales - qty_fin:+,}")

# 4. Outer Join on Transaction ID
sel_sales = df_sales[["id", "customer_email", "course_group", "economic_amount", "quantity"]].copy()
sel_fin   = df_fin[["id",   "customer_email", "course_group", "economic_amount", "quantity"]].copy()

sel_sales.columns = ["id", "email_sales", "course_sales", "amount_sales", "qty_sales"]
sel_fin.columns   = ["id", "email_fin",   "course_fin",   "amount_fin",   "qty_fin"]

merged = pd.merge(sel_sales, sel_fin, on="id", how="outer", indicator=True)

# 5. Classification
def classify_row(row):
    m = row["_merge"]
    if m == "left_only":
        return "only_sales"
    elif m == "right_only":
        return "only_finance"
    else:
        diff = round(row["amount_sales"] - row["amount_fin"], 6)
        if abs(diff) > 0.005:
            return "different_amount"
        elif str(row["course_sales"]).strip() != str(row["course_fin"]).strip():
            return "different_course"
        else:
            return "identical"

merged["diff_type"] = merged.apply(classify_row, axis=1)

print(f"\n[CLASSIFICATION SUMMARY]")
for dt, count in merged["diff_type"].value_counts().items():
    print(f"  {dt}: {count:,}")

# 6. Row-level Differences
merged["amount_sales"] = merged["amount_sales"].fillna(0.0)
merged["amount_fin"]   = merged["amount_fin"].fillna(0.0)
merged["qty_sales"]    = merged["qty_sales"].fillna(0).astype(int)
merged["qty_fin"]      = merged["qty_fin"].fillna(0).astype(int)
merged["diff_amount"]  = merged["amount_sales"] - merged["amount_fin"]
merged["diff_qty"]     = merged["qty_sales"] - merged["qty_fin"]

# 7. Integrity Assertions
sum_row_diffs = merged["diff_amount"].sum()
global_diff   = total_sales - total_fin
assert abs(sum_row_diffs - global_diff) < 0.01, f"Row diffs sum ({sum_row_diffs}) != global diff ({global_diff})"
print(f"\n[ASSERTION] Row-level diff sum matches global difference ({global_diff:,.4f}) -> PASS")

# 8. Save Results
results = {
    "merged":      merged,
    "total_sales": total_sales,
    "total_fin":   total_fin,
    "qty_sales":   qty_sales,
    "qty_fin":     qty_fin,
}

with open(OUTPUT_PKL, "wb") as f:
    pickle.dump(results, f)

print(f"\n[OUTPUT] Results exported to {OUTPUT_PKL}")

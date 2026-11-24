"""
6_exhaustive_control_tests.py
-----------------------------
Quality Assurance Test Suite.
Performs end-to-end mathematical, structural, and categorical validations
to guarantee reconciliation integrity across datasets.

Validation Checks:
  1. Global totals integrity
  2. Merge reconstruction fidelity
  3. Global variance vs sum of category variances
  4. Completeness of transaction classification (100% coverage)
  5. Variance by discrepancy category consistency
  6. Identical records neutrality (zero variance contribution)
  7. Exclusive ID disjointness (no overlap between only_sales and only_finance)
  8. Global quantity reconciliation
  9. No duplicate IDs in source datasets

Usage:
    python scripts/4_tests/6_exhaustive_control_tests.py
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

ROOT     = _find_root()
PKL_PATH = os.path.join(ROOT, "data", "results.pkl")
FILE_SAL = os.path.join(ROOT, "data", "base_sales.xlsx")
FILE_FIN = os.path.join(ROOT, "data", "base_finance.xlsx")

with open(PKL_PATH, "rb") as f:
    data = pickle.load(f)

merged      = data["merged"]
total_sales = data["total_sales"]
total_fin   = data["total_fin"]

df_sales = pd.read_excel(FILE_SAL, sheet_name=0)
df_fin   = pd.read_excel(FILE_FIN, sheet_name=0)

errors = []
print("=" * 70)
print("COMPREHENSIVE QUALITY ASSURANCE CONTROL TESTS")
print("=" * 70)

# TEST 1: Global Totals Integrity
print("\n[TEST 1] Global Totals Direct Verification")
t1_sal = df_sales["economic_amount"].sum()
t1_fin = df_fin["economic_amount"].sum()
ok_s = abs(t1_sal - total_sales) < 0.001
ok_f = abs(t1_fin - total_fin)   < 0.001
print(f"  Sales Match: {ok_s} ({t1_sal:,.2f}) | Finance Match: {ok_f} ({t1_fin:,.2f})")
if not ok_s: errors.append("TEST 1: Global Sales sum mismatch")
if not ok_f: errors.append("TEST 1: Global Finance sum mismatch")

# TEST 2: Merge Reconstruction
print("\n[TEST 2] Outer Join Sum Reconstruction vs Direct Totals")
ok_s = abs(merged["amount_sales"].sum() - t1_sal) < 0.01
ok_f = abs(merged["amount_fin"].sum()   - t1_fin) < 0.01
print(f"  Sales Reconstructed: {ok_s} | Finance Reconstructed: {ok_f}")
if not ok_s: errors.append("TEST 2: Reconstructed Sales amount does not match direct sum")
if not ok_f: errors.append("TEST 2: Reconstructed Finance amount does not match direct sum")

# TEST 3: Global Variance vs Category Variance Sum
print("\n[TEST 3] Variance Decomposition by Category")
global_diff  = t1_sal - t1_fin
cat_diff_sum = merged.groupby("diff_type")["diff_amount"].sum().sum()
ok = abs(cat_diff_sum - global_diff) < 0.01
print(f"  Categorical Variance Sum: {cat_diff_sum:,.4f} | Global Variance: {global_diff:,.4f} | PASS: {ok}")
if not ok: errors.append("TEST 3: Categorical variance sum does not equal global variance")

# TEST 4: Complete Classification Coverage
print("\n[TEST 4] Exhaustive Classification Coverage")
counts = merged["diff_type"].value_counts()
ok = counts.sum() == len(merged)
print(f"  Classified Records: {counts.sum():,} / Total Records: {len(merged):,} | PASS: {ok}")
for dt, c in counts.items():
    print(f"    - {dt}: {c:,}")
if not ok: errors.append("TEST 4: Unclassified records found")

# TEST 5: Variance by Category Consistency
print("\n[TEST 5] Row-level Variance Sum == Global Variance")
row_diff_sum = merged["diff_amount"].sum()
ok = abs(row_diff_sum - global_diff) < 0.01
print(f"  Row Diff Sum: {row_diff_sum:,.4f} | Global Diff: {global_diff:,.4f} | PASS: {ok}")
if not ok: errors.append("TEST 5: Row-level variance sum does not match global variance")

# TEST 6: Identical Records Neutrality
print("\n[TEST 6] Neutrality of Identical Records")
id_diff = merged[merged["diff_type"] == "identical"]["diff_amount"].sum()
ok = abs(id_diff) < 0.0001
print(f"  Sum of Identical Records Diff: {id_diff:,.8f} (Expected: 0.00000000) | PASS: {ok}")
if not ok: errors.append("TEST 6: Identical records contribute non-zero difference")

# TEST 7: Mutual Exclusivity of Single-Dataset IDs
print("\n[TEST 7] Disjointness of Single-Dataset Subsets")
ids_only_sal = set(merged[merged["diff_type"] == "only_sales"]["id"])
ids_only_fin = set(merged[merged["diff_type"] == "only_finance"]["id"])
overlap = ids_only_sal & ids_only_fin
ok = len(overlap) == 0
print(f"  Overlapping IDs between only_sales and only_finance: {len(overlap)} | PASS: {ok}")
if not ok: errors.append("TEST 7: ID overlap detected between exclusive groups")

# TEST 8: Global Quantity Verification
print("\n[TEST 8] Global Quantity Reconciliation")
qty_s = df_sales["quantity"].sum()
qty_f = df_fin["quantity"].sum()
print(f"  Sales Quantity: {qty_s:,} | Finance Quantity: {qty_f:,} | Difference: {qty_s - qty_f:+,}")
if qty_s != data["qty_sales"]: errors.append("TEST 8: Sales quantity mismatch")
if qty_f != data["qty_fin"]:   errors.append("TEST 8: Finance quantity mismatch")

# TEST 9: No Duplicate IDs in Source Datasets
print("\n[TEST 9] No Duplicate Transaction IDs")
dup_sal = df_sales["id"].duplicated().sum()
dup_fin = df_fin["id"].duplicated().sum()
ok = (dup_sal == 0) and (dup_fin == 0)
print(f"  Sales Duplicates: {dup_sal} | Finance Duplicates: {dup_fin} | PASS: {ok}")
if not ok: errors.append("TEST 9: Duplicate IDs found in source datasets")

print("\n" + "=" * 70)
if errors:
    print(f"FAILED TESTS ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL 9 QUALITY CONTROL TESTS PASSED SUCCESSFULLY (9/9 PASS)")
print("=" * 70)

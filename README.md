# Financial Dashboard Discrepancy Analysis (FY 2025)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/license-Proprietary-red.svg)](#)
[![QA Tests: 9/9 Passed](https://img.shields.io/badge/QA%20Tests-9%2F9%20Passed-brightgreen.svg)](#quality-assurance)

---

## Business Problem

Two internal departments — **Finance** and **Sales** — maintain parallel transaction records for fiscal year 2025. Despite representing the same commercial activity, discrepancies arose between the two datasets in reported monetary totals and transaction volumes.

This repository contains an automated reconciliation engine that answers the following business questions:

- What is the **exact net variance** in economic amounts and transaction quantities between the Finance and Sales datasets?
- **Which specific transactions** explain each discrepancy?
  - Transactions present in Sales but missing from Finance
  - Transactions present in Finance but missing from Sales
  - Transactions in both datasets with divergent amounts
  - Transactions with matching amounts but conflicting product categorizations
- Are all findings **fully auditable** with zero unaccounted variance?

---

## Key Findings (FY 2025)

| Metric | Sales | Finance | Variance (Sales − Finance) |
|---|---:|---:|---:|
| **Total Economic Amount** | **$2,181,253.69** | **$2,188,197.73** | **-$6,944.04** |
| **Total Quantity** | **4,386** | **4,381** | **+5** |

> Finance records a higher total than Sales. Full transaction-level detail is in `reports/differences_report_2025.md`.

| Discrepancy Type | Transactions | Monetary Impact |
|---|---:|---:|
| Identical records | 7,932 | $0.00 |
| Course categorization conflict only | 64 | $0.00 |
| Amount discrepancy | 59 | -$6,533.28 |
| Only in Sales | 19 | -$4,150.32 |
| Only in Finance | 15 | +$3,739.56 |
| **Total** | **8,089** | **-$6,944.04** |

---

## Data Privacy

All datasets in this repository have been sanitized prior to publication. Personally identifiable information and commercially sensitive fields have been anonymized using industry-standard techniques. The anonymization is deterministic, preserving all analytical relationships (joins, comparisons, variance calculations) while protecting the underlying data.

---

## Dataset Schema

Both `data/base_sales.xlsx` and `data/base_finance.xlsx` share this schema:

| Column | Type | Description |
|---|---|---|
| `date` | datetime | Transaction timestamp |
| `id` | string | Anonymized transaction identifier |
| `customer_email` | string | Anonymized customer identifier |
| `offer_title` | string | Anonymized offer identifier |
| `course_group` | string | Anonymized product/course category |
| `economic_amount` | float | Net financial amount for the transaction |
| `quantity` | integer | Units recognized |
| `platform_name` | string | Anonymized platform source tag |

---

## Repository Structure

```
.
├── data/
│   ├── base_sales.xlsx     # Sales dataset (8,074 rows)
│   ├── base_sales.csv      # Same data in CSV format
│   ├── base_finance.xlsx   # Finance dataset (8,070 rows)
│   ├── base_finance.csv    # Same data in CSV format
│   └── results.pkl         # Precomputed reconciliation cache
├── reports/
│   ├── differences_report_2025.md   # Full transaction-level discrepancy report
│   └── differences_report_2025.pdf  # PDF version for distribution
├── scripts/
│   ├── 1_exploration/
│   │   ├── 1_explore_structure.py    # Dataset structure and ID profiling
│   │   └── 2_statistical_summary.py  # Global totals and ID intersection
│   ├── 2_analysis/
│   │   └── 3_analyze_differences.py  # Outer join reconciliation engine
│   ├── 3_report/
│   │   ├── 4_generate_markdown_report.py  # Markdown report generator
│   │   └── 5_generate_pdf_report.py       # PDF report compiler
│   └── 4_tests/
│       └── 6_exhaustive_control_tests.py  # 9-test QA validation suite
├── .gitignore
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
git clone https://github.com/juanmedeot/financial-data-discrepancy-analysis.git
cd financial-data-discrepancy-analysis

python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python scripts/2_analysis/3_analyze_differences.py
python scripts/3_report/4_generate_markdown_report.py
python scripts/3_report/5_generate_pdf_report.py
python scripts/4_tests/6_exhaustive_control_tests.py
```

> All scripts resolve the repository root automatically — no path configuration required.

---

## Quality Assurance

The test suite (`scripts/4_tests/6_exhaustive_control_tests.py`) verifies 9 invariants:

| # | Test | Result |
|:---:|---|:---:|
| 01 | Global totals match source dataset sums | **PASS** |
| 02 | Outer join reconstruction matches direct sums | **PASS** |
| 03 | Variance decomposition by category equals global variance | **PASS** |
| 04 | 100% of transactions classified (8,089 / 8,089) | **PASS** |
| 05 | Row-level variance sum equals global variance | **PASS** |
| 06 | Identical records contribute $0.00 to variance | **PASS** |
| 07 | Zero ID overlap between exclusive subsets | **PASS** |
| 08 | Quantity totals reconcile correctly | **PASS** |
| 09 | No duplicate transaction IDs in either dataset | **PASS** |

**Result: `9/9 PASS`**

# Gaming Compliance Exception Review Tool

[![Tests](https://github.com/felimonj958-droid/gaming-compliance-exception-review/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/felimonj958-droid/gaming-compliance-exception-review/actions/workflows/tests.yml)

A Python portfolio project that models a rule-based exception-review workflow for fictional gaming-operations records. It generates deterministic synthetic data, applies transparent validation rules, and produces reviewer-facing exception outputs.

## Disclaimer

This project uses entirely fictional, synthetic data and generic example control rules. It is not affiliated with Pechanga Resort Casino, the Pechanga Gaming Commission, or any gaming organization.

It does not represent actual gaming systems, internal controls, policies, thresholds, records, payout procedures, or investigative practices. The project is designed only to demonstrate an operational approach to data validation, traceability, documentation review, and human escalation.

## What It Does

The tool generates 200 fictional records:

- 120 fictional jackpot-event records
- 80 fictional controlled-material activity records

The generated data includes valid records and intentional exceptions. The validation pipeline reviews the inputs, writes one row per finding to an Excel-compatible CSV, and creates a JSON summary for a reviewer.

## Controls Implemented

| Rule ID | Control | Finding generated when |
|---|---|---|
| R001 | Duplicate identifier check | A jackpot event ID or controlled-material record ID is duplicated |
| R002 | Required-field completeness | A required jackpot field is blank |
| R003 | Jackpot amount limit | A fictional jackpot amount exceeds the configured maximum |
| R004 | Secondary approval requirement | A jackpot at or above the configured threshold lacks approval data |
| R005 | Timestamp integrity | An event is future-dated or approval precedes its related event |
| R006 | Controlled-material traceability | An asset ID, technician ID, or work-order ID is missing |

All rule thresholds are generic examples defined in `config/rules.json`.

## Verified Example Run

The current deterministic dataset produces:

```text
Total fictional records: 200
Total exceptions: 14
Exception rate: 7%
```

The exception summary includes these counts:

```text
R001: 4
R002: 1
R003: 1
R004: 2
R005: 3
R006: 3
```

## Outputs

Running the application generates:

```text
data/input/jackpot_events.csv
data/input/controlled_material_events.csv
data/output/exception_report.csv
data/output/run_summary.json
```

`exception_report.csv` contains one row per flagged issue, including the record type, record ID, rule ID, affected field, observed value, reason, and recommended action.

`run_summary.json` reports total records, record counts by type, total exceptions, exception rate, and counts by rule and record type.

## Setup

Requires Python 3.13 or later.

```bash
git clone [https://github.com/felimonj958-droid/gaming-compliance-exception-review.git](https://github.com/felimonj958-droid/gaming-compliance-exception-review.git)
cd gaming-compliance-exception-review

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the Tool

From the repository root:

```bash
python -m src.main
```

The command regenerates the fictional input data, validates all records, and rewrites the output reports.

## Run Tests

```bash
python -m pytest -q
```

The project currently includes 10 automated tests covering positive and negative rule outcomes. Pytest discovers `test_*.py` files and uses standard Python `assert` statements for test expectations. [cite:455][cite:329]

## Continuous Integration

GitHub Actions runs the test suite on every push to `main` and on pull requests targeting `main`. The workflow definition is located at:

```text
.github/workflows/tests.yml
```

## Repository Structure

```text
gaming-compliance-exception-review/
├── .github/workflows/      # Continuous-integration workflow
├── config/                 # Generic synthetic rule thresholds
├── data/
│   ├── input/              # Generated fictional CSV inputs, ignored by Git
│   └── output/             # Generated reports, ignored by Git
├── src/
│   ├── generate_synthetic_data.py
│   ├── main.py
│   ├── report.py
│   └── rules.py
├── tests/                  # Automated validation tests
├── requirements.txt
└── README.md
```

## Assumptions and Limitations

- All data, identities, values, identifiers, and rules are fictional.
- The tool is deterministic and does not access live systems, external records, or confidential data.
- Configured thresholds are examples only and are not representations of real operational policy.
- Findings are screening signals, not conclusions of wrongdoing or compliance decisions.
- A qualified human reviewer must investigate, document, and resolve each exception.
- The project intentionally does not attempt to automate investigations, eligibility decisions, payout decisions, or disciplinary action.

## Portfolio Intent

This project demonstrates an approach to operational compliance support: create traceable inputs, apply explicit rules consistently, produce concise exception evidence, and retain a clear human-review boundary.

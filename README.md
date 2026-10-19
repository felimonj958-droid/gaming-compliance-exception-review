# Gaming Compliance Exception Review Tool

A Python portfolio project that uses fictional, synthetic data to model a rule-based exception-review workflow for gaming operations.

## Disclaimer

This project uses entirely fictional, synthetic data and generic example control rules. It is not affiliated with Pechanga Resort Casino, the Pechanga Gaming Commission, or any gaming organization. It does not represent actual gaming systems, internal controls, policies, thresholds, records, or investigative practices.

## Current Capability

The project currently generates synthetic CSV input data for two fictional record types:

- Jackpot event records
- Controlled-material activity records

The generator deliberately includes selected data-quality and control exceptions so later validation rules can be tested.

## Planned Validation Checks

- Duplicate record identifiers
- Required-field completeness
- Jackpot amount limits
- Secondary approval for high-value payouts
- Future-dated timestamps
- Invalid approval timing
- Supporting identifiers for controlled-material records

## Project Structure

```text
gaming-compliance-exception-review/
├── config/                 # Synthetic rule thresholds
├── data/
│   ├── input/              # Generated fictional CSV data, ignored by Git
│   └── output/             # Generated exception reports, ignored by Git
├── scripts/                # Environment bootstrap and optional dependency sync
├── src/                    # Generator, validation rules, reporting logic
├── tests/                  # Automated tests
├── requirements.txt        # Python dependencies
└── README.md
```

## Setup

From the repository root:

```bash
./scripts/bootstrap.sh
```

## Generate Synthetic Data

```bash
python src/main.py
```

This creates:

```text
data/input/jackpot_events.csv
data/input/controlled_material_events.csv
```

## Next Development Step

Build and test the validation engine, then export an exception report and run summary.

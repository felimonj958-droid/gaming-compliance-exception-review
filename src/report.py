from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "output"

EXCEPTION_COLUMNS = [
    "record_type",
    "record_id",
    "rule_id",
    "field_name",
    "bad_value",
    "issue",
    "recommended_action",
]


def write_exception_report(exceptions: list[dict[str, Any]]) -> Path:
    """Write structured validation findings to a CSV review queue."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report_df = pd.DataFrame(exceptions, columns=EXCEPTION_COLUMNS)
    report_path = OUTPUT_DIR / "exception_report.csv"
    report_df.to_csv(report_path, index=False)

    return report_path


def write_run_summary(
    jackpot_record_count: int,
    controlled_material_record_count: int,
    exceptions: list[dict[str, Any]],
) -> Path:
    """Write high-level run counts and exception totals to JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rule_counts: dict[str, int] = {}
    record_type_counts: dict[str, int] = {}

    for exception in exceptions:
        rule_id = exception["rule_id"]
        record_type = exception["record_type"]

        rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
        record_type_counts[record_type] = record_type_counts.get(record_type, 0) + 1

    total_records = jackpot_record_count + controlled_material_record_count

    summary = {
        "total_records": total_records,
        "jackpot_records": jackpot_record_count,
        "controlled_material_records": controlled_material_record_count,
        "total_exceptions": len(exceptions),
        "exception_rate": round(len(exceptions) / total_records, 4)
        if total_records
        else 0,
        "exceptions_by_rule": rule_counts,
        "exceptions_by_record_type": record_type_counts,
    }

    summary_path = OUTPUT_DIR / "run_summary.json"

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    return summary_path

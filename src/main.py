from __future__ import annotations

import pandas as pd

from .generate_synthetic_data import main as generate_synthetic_data
from .report import write_exception_report, write_run_summary
from .rules import (
    check_controlled_material_supporting_fields,
    check_duplicate_ids,
    check_jackpot_amount_limits,
    check_jackpot_timestamps,
    check_required_fields,
    check_secondary_approval,
    load_rules_config,
)


def run() -> None:
    """Generate synthetic inputs, validate them, and export review outputs."""
    generate_synthetic_data()

    jackpot_df = pd.read_csv("data/input/jackpot_events.csv")
    controlled_material_df = pd.read_csv(
        "data/input/controlled_material_events.csv"
    )
    config = load_rules_config()

    exceptions = []

    exceptions.extend(
        check_duplicate_ids(
            jackpot_df,
            id_column="event_id",
            record_type="jackpot",
        )
    )
    exceptions.extend(
        check_required_fields(
            jackpot_df,
            id_column="event_id",
            required_fields=[
                "event_id",
                "event_timestamp",
                "machine_id",
                "jackpot_amount",
                "verifier_id",
                "documentation_complete",
                "status",
            ],
            record_type="jackpot",
        )
    )
    exceptions.extend(
        check_jackpot_amount_limits(
            jackpot_df,
            max_amount=config["jackpot_max_amount"],
        )
    )
    exceptions.extend(
        check_secondary_approval(
            jackpot_df,
            approval_threshold=config["jackpot_secondary_approval_threshold"],
        )
    )
    exceptions.extend(check_jackpot_timestamps(jackpot_df))

    exceptions.extend(
        check_duplicate_ids(
            controlled_material_df,
            id_column="record_id",
            record_type="controlled_material",
        )
    )
    exceptions.extend(
        check_required_fields(
            controlled_material_df,
            id_column="record_id",
            required_fields=[
                "record_id",
                "event_timestamp",
                "action",
                "documentation_complete",
                "status",
            ],
            record_type="controlled_material",
        )
    )
    exceptions.extend(
        check_controlled_material_supporting_fields(controlled_material_df)
    )

    report_path = write_exception_report(exceptions)
    summary_path = write_run_summary(
        jackpot_record_count=len(jackpot_df),
        controlled_material_record_count=len(controlled_material_df),
        exceptions=exceptions,
    )

    print(f"Validated {len(jackpot_df)} jackpot records")
    print(
        "Validated "
        f"{len(controlled_material_df)} controlled-material records"
    )
    print(f"Generated {len(exceptions)} exceptions")
    print(f"Exception report: {report_path}")
    print(f"Run summary: {summary_path}")


if __name__ == "__main__":
    run()

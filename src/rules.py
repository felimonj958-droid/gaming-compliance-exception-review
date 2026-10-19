from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .validators import is_blank, make_exception


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "rules.json"


def load_rules_config() -> dict[str, Any]:
    """Load fictional validation thresholds from the project configuration file."""
    with CONFIG_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def check_duplicate_ids(
    df: pd.DataFrame,
    id_column: str,
    record_type: str,
    rule_id: str = "R001",
) -> list[dict[str, Any]]:
    """Flag every record whose identifier appears more than once."""
    exceptions = []

    duplicate_rows = df[df.duplicated(subset=[id_column], keep=False)]

    for _, row in duplicate_rows.iterrows():
        record_id = str(row[id_column])

        exceptions.append(
            make_exception(
                record_type=record_type,
                record_id=record_id,
                rule_id=rule_id,
                field_name=id_column,
                bad_value=record_id,
                issue=f"Duplicate {id_column} detected",
            )
        )

    return exceptions


def check_required_fields(
    df: pd.DataFrame,
    id_column: str,
    required_fields: list[str],
    record_type: str,
    rule_id: str = "R002",
) -> list[dict[str, Any]]:
    """Flag each required field that is blank or missing."""
    exceptions = []

    for _, row in df.iterrows():
        record_id = str(row[id_column])

        for field_name in required_fields:
            bad_value = row.get(field_name)

            if is_blank(bad_value):
                exceptions.append(
                    make_exception(
                        record_type=record_type,
                        record_id=record_id,
                        rule_id=rule_id,
                        field_name=field_name,
                        bad_value=bad_value,
                        issue=f"Required field '{field_name}' is missing",
                    )
                )

    return exceptions


def check_jackpot_amount_limits(
    df: pd.DataFrame,
    max_amount: float,
    rule_id: str = "R003",
) -> list[dict[str, Any]]:
    """Flag invalid or over-limit synthetic jackpot amounts."""
    exceptions = []

    for _, row in df.iterrows():
        record_id = str(row["event_id"])
        amount = pd.to_numeric(row.get("jackpot_amount"), errors="coerce")

        if pd.isna(amount) or amount <= 0:
            exceptions.append(
                make_exception(
                    record_type="jackpot",
                    record_id=record_id,
                    rule_id=rule_id,
                    field_name="jackpot_amount",
                    bad_value=row.get("jackpot_amount"),
                    issue="Jackpot amount must be greater than zero",
                )
            )
        elif amount > max_amount:
            exceptions.append(
                make_exception(
                    record_type="jackpot",
                    record_id=record_id,
                    rule_id=rule_id,
                    field_name="jackpot_amount",
                    bad_value=amount,
                    issue=f"Jackpot amount exceeds configured maximum of {max_amount}",
                )
            )

    return exceptions


def check_secondary_approval(
    df: pd.DataFrame,
    approval_threshold: float,
    rule_id: str = "R004",
) -> list[dict[str, Any]]:
    """Require a secondary approval only for high-value synthetic jackpot events."""
    exceptions = []

    for _, row in df.iterrows():
        record_id = str(row["event_id"])
        amount = pd.to_numeric(row.get("jackpot_amount"), errors="coerce")

        if pd.isna(amount) or amount < approval_threshold:
            continue

        approver_id = row.get("secondary_approver_id")
        approval_timestamp = row.get("approval_timestamp")

        if is_blank(approver_id) or is_blank(approval_timestamp):
            exceptions.append(
                make_exception(
                    record_type="jackpot",
                    record_id=record_id,
                    rule_id=rule_id,
                    field_name="secondary_approver_id",
                    bad_value=approver_id,
                    issue=(
                        "Secondary approval is required for jackpot amounts "
                        f"at or above {approval_threshold}"
                    ),
                )
            )

    return exceptions


def check_jackpot_timestamps(
    df: pd.DataFrame,
    rule_id: str = "R005",
) -> list[dict[str, Any]]:
    """Flag future event times and approvals that predate their events."""
    exceptions = []
    now = pd.Timestamp.now()

    for _, row in df.iterrows():
        record_id = str(row["event_id"])
        event_timestamp = pd.to_datetime(
            row.get("event_timestamp"),
            errors="coerce",
        )
        approval_timestamp = pd.to_datetime(
            row.get("approval_timestamp"),
            errors="coerce",
        )

        if pd.notna(event_timestamp) and event_timestamp > now:
            exceptions.append(
                make_exception(
                    record_type="jackpot",
                    record_id=record_id,
                    rule_id=rule_id,
                    field_name="event_timestamp",
                    bad_value=row.get("event_timestamp"),
                    issue="Event timestamp cannot be in the future",
                )
            )

        if (
            pd.notna(event_timestamp)
            and pd.notna(approval_timestamp)
            and approval_timestamp < event_timestamp
        ):
            exceptions.append(
                make_exception(
                    record_type="jackpot",
                    record_id=record_id,
                    rule_id=rule_id,
                    field_name="approval_timestamp",
                    bad_value=row.get("approval_timestamp"),
                    issue="Approval timestamp cannot precede event timestamp",
                )
            )

    return exceptions


def check_controlled_material_supporting_fields(
    df: pd.DataFrame,
    rule_id: str = "R006",
) -> list[dict[str, Any]]:
    """Flag missing traceability fields on fictional controlled-material records."""
    exceptions = []
    required_fields = ["asset_id", "technician_id", "work_order_id"]

    for _, row in df.iterrows():
        record_id = str(row["record_id"])

        for field_name in required_fields:
            bad_value = row.get(field_name)

            if is_blank(bad_value):
                exceptions.append(
                    make_exception(
                        record_type="controlled_material",
                        record_id=record_id,
                        rule_id=rule_id,
                        field_name=field_name,
                        bad_value=bad_value,
                        issue=(
                            "Controlled-material record is missing required "
                            f"traceability field '{field_name}'"
                        ),
                    )
                )

    return exceptions


def check_controlled_material_supporting_fields(
    df: pd.DataFrame,
    rule_id: str = "R006",
) -> list[dict[str, Any]]:
    """Flag missing traceability fields on fictional controlled-material records."""
    exceptions = []
    required_fields = ["asset_id", "technician_id", "work_order_id"]

    for _, row in df.iterrows():
        record_id = str(row["record_id"])

        for field_name in required_fields:
            bad_value = row.get(field_name)

            if is_blank(bad_value):
                exceptions.append(
                    make_exception(
                        record_type="controlled_material",
                        record_id=record_id,
                        rule_id=rule_id,
                        field_name=field_name,
                        bad_value=bad_value,
                        issue=(
                            "Controlled-material record is missing required "
                            f"traceability field '{field_name}'"
                        ),
                    )
                )

    return exceptions

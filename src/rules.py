from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import pandas as pd

from validators import is_blank, make_exception, parse_dt, safe_float


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "rules.json"


def load_rules_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def check_duplicate_ids(df: pd.DataFrame, id_col: str, record_type: str, rule_id: str) -> list[dict]:
    exceptions = []
    dupes = df[df.duplicated(subset=[id_col], keep=False)]
    for _, row in dupes.iterrows():
        exceptions.append(
            make_exception(
                record_type=record_type,
                record_id=str(row[id_col]),
                rule_id=rule_id,
                field_name=id_col,
                bad_value=row[id_col],
                issue=f"Duplicate {id_col} detected",
            )
        )
    return exceptions


def check_required_fields(df: pd.DataFrame, required_fields: list[str], id_col: str, record_type: str, rule_id: str) -> list[dict]:
    exceptions = []
    for _, row in df.iterrows():
        record_id = str(row[id_col])
        for field in required_fields:
            if is_blank(row.get(field)):
                exceptions.append(
                    make_exception(
                        record_type=record_type,
                        record_id=record_id,
                        rule_id=rule_id,
                        field_name=field,
                        bad_value=row.get(field),
                        issue=f"Required field '{field}' is missing",
                    )
                )
    return exceptions


def check_jackpot_amount_limits(df: pd.DataFrame, max_amount: float) -> list[dict]:
    exceptions = []
    for _, row in df.iterrows():
        record_id = str(row["event_id"])
        amount = safe_float(row.get("jackpot_amount"))
        if amount is None or amount <= 0:
            exceptions.append(
                make_exception(
                    record_type="jackpot",
                    record_id=record_id,
                    rule_id="R003",
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
                    rule_id="R003",
                    field_name="jackpot_amount",
                    bad_value=row.get("jackpot_amount"),
                    issue=f"Jackpot amount exceeds configured maximum of {max_amount}",
                )
            )
    return exceptions


def check_secondary_approval(df: pd.DataFrame, threshold: float) -> list[dict]:
    exceptions = []
    for _, row in df.iterrows():
        record_id = str(row["event_id"])
        amount = safe_float(row.get("jackpot_amount"))
        if amount is not None and amount >= threshold:
            if is_blank(row.get("secondary_approver_id")) or is_blank(row.get("approval_timestamp")):
                exceptions.append(
                    make_exception(
                        record_type="jackpot",
                        record_id=record_id,
                        rule_id="R004",
                        field_name="secondary_approver_id",
                        bad_value=row.get("secondary_approver_id"),
                        issue=f"Secondary approval required for jackpot amount >= {threshold}",
                    )
                )
    return exceptions


def check_timestamps_not_future(df: pd.DataFrame, id_col: str, ts_col: str, record_type: str, rule_id: str) -> list[dict]:
    exceptions = []
    now = datetime.now()
    for _, row in df.iterrows():
        record_id = str(row[id_col])
        ts = parse_dt(row.get(ts_col))
        if ts is not None and ts > now:
            exceptions.append(
                make_exception(
                    record_type=record_type,
                    record_id=record_id,
                    rule_id=rule_id,
                    field_name=ts_col,
                    bad_value=row.get(ts_col),
                    issue=f"{ts_col} cannot be in the future",
                )
            )
    return exceptions


def check_jackpot_timestamp_order(df: pd.DataFrame) -> list[dict]:
    exceptions = []
    for _, row in df.iterrows():
        record_id = str(row["event_id"])
        event_ts = parse_dt(row.get("event_timestamp"))
        approval_ts = parse_dt(row.get("approval_timestamp"))

        if approval_ts is not None and event_ts is not None and approval_ts < event_ts:
            exceptions.append(
                make_exception(
                    record_type="jackpot",
                    record_id=record_id,
                    rule_id="R005",
                    field_name="approval_timestamp",
                    bad_value=row.get("approval_timestamp"),
                    issue="Approval timestamp cannot precede event timestamp",
                )
            )
    return exceptions


def check_controlled_material_supporting_fields(df: pd.DataFrame) -> list[dict]:
    exceptions = []
    for _, row in df.iterrows():
        record_id = str(row["record_id"])
        for field in ["asset_id", "technician_id", "work_order_id"]:
            if is_blank(row.get(field)):
                exceptions.append(
                    make_exception(
                        record_type="controlled_material",
                        record_id=record_id,
                        rule_id="R006",
                        field_name=field,
                        bad_value=row.get(field),
                        issue=f"Controlled-material record missing required field '{field}'",
                    )
                )
    return exceptions


def validate_jackpot_df(df: pd.DataFrame) -> list[dict]:
    config = load_rules_config()
    exceptions = []
    exceptions.extend(check_duplicate_ids(df, "event_id", "jackpot", "R001"))
    exceptions.extend(
        check_required_fields(
            df,
            ["event_id", "event_timestamp", "machine_id", "jackpot_amount", "verifier_id", "documentation_complete", "status"],
            "event_id",
            "jackpot",
            "R002",
        )
    )
    exceptions.extend(check_jackpot_amount_limits(df, config["jackpot_max_amount"]))
    exceptions.extend(check_secondary_approval(df, config["jackpot_secondary_approval_threshold"]))
    exceptions.extend(check_timestamps_not_future(df, "event_id", "event_timestamp", "jackpot", "R005"))
    exceptions.extend(check_jackpot_timestamp_order(df))
    return exceptions


def validate_controlled_material_df(df: pd.DataFrame) -> list[dict]:
    exceptions = []
    exceptions.extend(check_duplicate_ids(df, "record_id", "controlled_material", "R001"))
    exceptions.extend(
        check_required_fields(
            df,
            ["record_id", "event_timestamp", "action", "documentation_complete", "status"],
            "record_id",
            "controlled_material",
            "R002",
        )
    )
    exceptions.extend(check_timestamps_not_future(df, "record_id", "event_timestamp", "controlled_material", "R005"))
    exceptions.extend(check_controlled_material_supporting_fields(df))
    return exceptions

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd


def is_blank(value: Any) -> bool:
    if pd.isna(value):
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def parse_dt(value: Any) -> datetime | None:
    if is_blank(value):
        return None
    try:
        return pd.to_datetime(value).to_pydatetime()
    except Exception:
        return None


def safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def make_exception(
    record_type: str,
    record_id: str,
    rule_id: str,
    field_name: str,
    bad_value: Any,
    issue: str,
    recommended_action: str = "manual_review",
) -> dict:
    return {
        "record_type": record_type,
        "record_id": record_id,
        "rule_id": rule_id,
        "field_name": field_name,
        "bad_value": bad_value,
        "issue": issue,
        "recommended_action": recommended_action,
    }

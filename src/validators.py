from __future__ import annotations

from typing import Any

import pandas as pd


def is_blank(value: Any) -> bool:
    """Return True for missing values, empty strings, or whitespace-only strings."""
    if pd.isna(value):
        return True

    return isinstance(value, str) and value.strip() == ""


def make_exception(
    record_type: str,
    record_id: str,
    rule_id: str,
    field_name: str,
    bad_value: Any,
    issue: str,
    recommended_action: str = "manual_review",
) -> dict[str, Any]:
    """Create one consistently formatted exception record."""
    return {
        "record_type": record_type,
        "record_id": record_id,
        "rule_id": rule_id,
        "field_name": field_name,
        "bad_value": bad_value,
        "issue": issue,
        "recommended_action": recommended_action,
    }

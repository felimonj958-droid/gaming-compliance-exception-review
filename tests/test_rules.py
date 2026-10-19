import pandas as pd

from src.rules import (
    check_controlled_material_supporting_fields,
    check_duplicate_ids,
    check_jackpot_amount_limits,
    check_jackpot_timestamps,
    check_required_fields,
    check_secondary_approval,
)


def test_duplicate_ids_flags_both_matching_rows():
    df = pd.DataFrame({"event_id": ["JPT-001", "JPT-001", "JPT-002"]})

    exceptions = check_duplicate_ids(df, "event_id", "jackpot")

    assert len(exceptions) == 2
    assert {item["record_id"] for item in exceptions} == {"JPT-001"}
    assert {item["rule_id"] for item in exceptions} == {"R001"}


def test_required_fields_flags_blank_verifier():
    df = pd.DataFrame(
        [
            {
                "event_id": "JPT-001",
                "event_timestamp": "2026-10-01T10:00:00",
                "verifier_id": "",
            }
        ]
    )

    exceptions = check_required_fields(
        df,
        id_column="event_id",
        required_fields=["event_id", "event_timestamp", "verifier_id"],
        record_type="jackpot",
    )

    assert len(exceptions) == 1
    assert exceptions[0]["field_name"] == "verifier_id"
    assert exceptions[0]["rule_id"] == "R002"


def test_jackpot_amount_limit_flags_over_limit_value():
    df = pd.DataFrame(
        [{"event_id": "JPT-001", "jackpot_amount": 12500.0}]
    )

    exceptions = check_jackpot_amount_limits(df, max_amount=10000.0)

    assert len(exceptions) == 1
    assert exceptions[0]["record_id"] == "JPT-001"
    assert exceptions[0]["rule_id"] == "R003"


def test_secondary_approval_only_applies_above_threshold():
    df = pd.DataFrame(
        [
            {
                "event_id": "JPT-LOW",
                "jackpot_amount": 2500.0,
                "secondary_approver_id": "",
                "approval_timestamp": "",
            },
            {
                "event_id": "JPT-HIGH",
                "jackpot_amount": 6500.0,
                "secondary_approver_id": "",
                "approval_timestamp": "",
            },
        ]
    )

    exceptions = check_secondary_approval(df, approval_threshold=5000.0)

    assert len(exceptions) == 1
    assert exceptions[0]["record_id"] == "JPT-HIGH"
    assert exceptions[0]["rule_id"] == "R004"


def test_timestamp_rule_flags_future_and_out_of_order_times():
    df = pd.DataFrame(
        [
            {
                "event_id": "JPT-001",
                "event_timestamp": "2099-01-01T10:00:00",
                "approval_timestamp": "2098-12-31T10:00:00",
            }
        ]
    )

    exceptions = check_jackpot_timestamps(df)

    assert len(exceptions) == 2
    assert {item["field_name"] for item in exceptions} == {
        "event_timestamp",
        "approval_timestamp",
    }


def test_controlled_material_rule_identifies_missing_field():
    df = pd.DataFrame(
        [
            {
                "record_id": "CM-001",
                "asset_id": "",
                "technician_id": "TECH-01",
                "work_order_id": "WO-1001",
            }
        ]
    )

    exceptions = check_controlled_material_supporting_fields(df)

    assert len(exceptions) == 1
    assert exceptions[0]["field_name"] == "asset_id"
    assert exceptions[0]["rule_id"] == "R006"

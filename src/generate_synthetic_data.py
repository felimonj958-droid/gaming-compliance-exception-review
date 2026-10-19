from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import random

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE_DIR / "data" / "input"

random.seed(42)


def iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def build_jackpot_events(n: int = 120) -> pd.DataFrame:
    now = datetime.now().replace(microsecond=0, second=0)
    rows = []

    for i in range(1, n + 1):
        event_time = now - timedelta(hours=random.randint(1, 240), minutes=random.randint(0, 59))
        amount = round(random.uniform(50, 9500), 2)
        verifier_id = f"EMP-{random.randint(100, 199)}"
        secondary_approver_id = f"SUP-{random.randint(10, 29)}" if amount >= 5000 else ""
        approval_timestamp = iso(event_time + timedelta(minutes=random.randint(3, 25))) if secondary_approver_id else ""
        documentation_complete = random.choice([True, True, True, False])

        rows.append(
            {
                "event_id": f"JPT-{i:04d}",
                "event_timestamp": iso(event_time),
                "machine_id": f"GM-{random.randint(1000, 1105)}",
                "jackpot_amount": amount,
                "verifier_id": verifier_id,
                "secondary_approver_id": secondary_approver_id,
                "approval_timestamp": approval_timestamp,
                "documentation_complete": documentation_complete,
                "status": random.choice(["closed", "closed", "reviewed"]),
            }
        )

    if len(rows) >= 6:
        rows[2]["event_id"] = rows[1]["event_id"]
        rows[4]["verifier_id"] = ""
        rows[5]["jackpot_amount"] = 12500.00
        rows[6]["event_timestamp"] = iso(now + timedelta(days=1))
        rows[7]["jackpot_amount"] = 6200.00
        rows[7]["secondary_approver_id"] = ""
        rows[7]["approval_timestamp"] = ""
        rows[8]["approval_timestamp"] = iso(datetime.fromisoformat(rows[8]["event_timestamp"]) - timedelta(minutes=5))
        rows[9]["documentation_complete"] = False

    return pd.DataFrame(rows)


def build_controlled_material_events(n: int = 80) -> pd.DataFrame:
    now = datetime.now().replace(microsecond=0, second=0)
    rows = []

    for i in range(1, n + 1):
        event_time = now - timedelta(hours=random.randint(1, 240), minutes=random.randint(0, 59))
        rows.append(
            {
                "record_id": f"CM-{i:04d}",
                "event_timestamp": iso(event_time),
                "action": random.choice(["installation", "removal", "inspection"]),
                "asset_id": f"ASSET-{random.randint(2000, 2105)}",
                "technician_id": f"TECH-{random.randint(10, 35)}",
                "work_order_id": f"WO-{random.randint(5000, 5400)}",
                "documentation_complete": random.choice([True, True, True, False]),
                "status": random.choice(["closed", "closed", "reviewed"]),
            }
        )

    if len(rows) >= 5:
        rows[1]["record_id"] = rows[0]["record_id"]
        rows[2]["asset_id"] = ""
        rows[3]["technician_id"] = ""
        rows[4]["work_order_id"] = ""
        rows[5]["event_timestamp"] = iso(now + timedelta(days=2))
        rows[6]["documentation_complete"] = False

    return pd.DataFrame(rows)


def main() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    jackpot_df = build_jackpot_events()
    controlled_df = build_controlled_material_events()

    jackpot_path = INPUT_DIR / "jackpot_events.csv"
    controlled_path = INPUT_DIR / "controlled_material_events.csv"

    jackpot_df.to_csv(jackpot_path, index=False)
    controlled_df.to_csv(controlled_path, index=False)

    print(f"Wrote {len(jackpot_df)} jackpot records to {jackpot_path}")
    print(f"Wrote {len(controlled_df)} controlled material records to {controlled_path}")


if __name__ == "__main__":
    main()

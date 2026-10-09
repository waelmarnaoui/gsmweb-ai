
import json
import os
from datetime import datetime, timezone
from collections import Counter

from src.crm.performance import fetch_all


STATE_FILE = "reports/crm_monitor_state.json"
LOG_FILE = "reports/hourly_activity.log"


def main():
    os.makedirs("reports", exist_ok=True)

    repairs = fetch_all(
        "Repair",
        "id,createdAt,entryDate,status",
    )

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            state = json.load(file)

        seen_ids = set(state.get("repair_ids", []))
        new_repairs = [
            row for row in repairs
            if row["id"] not in seen_ids
        ]

        now = datetime.now(timezone.utc).isoformat()

        status_counts = Counter(
            row.get("status") or "UNKNOWN"
            for row in new_repairs
        )

        report = {
            "checked_at_utc": now,
            "new_service_jobs_received": len(new_repairs),
            "jobs_by_status": dict(status_counts),
            "cancelled_jobs": status_counts.get("CANCELLED", 0),
            "note": (
                "Counts new repair records, not confirmed unique people "
                "or payments."
            ),
        }

        # Remember all currently visible repair records.
        state["repair_ids"] = sorted(
            seen_ids | {row["id"] for row in repairs}
        )
        state["last_checked_utc"] = now

        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(json.dumps(report, ensure_ascii=False) + "\n")

        print("\nGSMWEB HOURLY REPAIR MONITOR")
        print("=" * 40)
        print(f"Checked at (UTC): {now}")
        print(f"New service jobs received: {len(new_repairs)}")
        print(f"Jobs by status: {dict(status_counts)}")
        print(f"New jobs already marked cancelled: {report['cancelled_jobs']}")
        print("No customer contact details were retrieved.")

    else:
        # First run: establish a baseline without counting old records.
        state = {
            "repair_ids": sorted(row["id"] for row in repairs),
            "last_checked_utc": datetime.now(timezone.utc).isoformat(),
        }

        print("Baseline initialized.")
        print(f"Existing repair records recorded: {len(repairs)}")
        print("New service jobs will be detected on subsequent runs.")

    temporary_path = STATE_FILE + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)

    os.replace(temporary_path, STATE_FILE)
    print("CRM data was only read; no CRM records were changed.")


if __name__ == "__main__":
    main()
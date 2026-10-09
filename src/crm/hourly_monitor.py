
import json
import os
from datetime import datetime, timezone
from collections import Counter

from dotenv import load_dotenv
from supabase import create_client

from src.crm.performance import fetch_all

load_dotenv()

STATE_ID = "hourly_crm_monitor"


def get_state_client():
    url = os.getenv("SUPABASE_URL")
    secret_key = os.getenv("SUPABASE_SECRET_KEY")

    if not url or not secret_key:
        raise RuntimeError(
            "SUPABASE_URL or SUPABASE_SECRET_KEY is missing."
        )

    return create_client(url, secret_key)


def main():
    client = get_state_client()

    repairs = fetch_all(
        "Repair",
        "id,createdAt,entryDate,status",
    )

    result = (
        client.table("gsm_ai_monitor_state")
        .select("state")
        .eq("id", STATE_ID)
        .limit(1)
        .execute()
    )

    now = datetime.now(timezone.utc).isoformat()

    if result.data:
        state = result.data[0]["state"] or {}
        seen_ids = set(state.get("repair_ids", []))

        new_repairs = [
            row for row in repairs
            if row["id"] not in seen_ids
        ]

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
                "Counts new repair records, not confirmed unique "
                "people or payments."
            ),
        }

        print("GSMWEB HOURLY REPAIR MONITOR")
        print("=" * 40)
        print(f"Checked at (UTC): {now}")
        print(f"New service jobs received: {len(new_repairs)}")
        print(f"Jobs by status: {dict(status_counts)}")
        print(f"New jobs already marked cancelled: {report['cancelled_jobs']}")
        print("No customer contact details were retrieved.")

        state["repair_ids"] = sorted(
            seen_ids | {row["id"] for row in repairs}
        )
        state["last_checked_utc"] = now
        state["last_report"] = report

    else:
        state = {
            "repair_ids": sorted(row["id"] for row in repairs),
            "last_checked_utc": now,
            "last_report": {
                "new_service_jobs_received": 0,
                "note": "Initial baseline; existing repairs were not counted.",
            },
        }

        print("GSMWEB CRM MONITOR BASELINE")
        print("=" * 40)
        print(f"Checked at (UTC): {now}")
        print(f"Existing repair records recorded: {len(repairs)}")
        print("Existing repairs were not counted as new activity.")

    (
        client.table("gsm_ai_monitor_state")
        .upsert({
            "id": STATE_ID,
            "state": state,
            "updated_at": now,
        })
        .execute()
    )

    print("Monitor state saved to Supabase.")
    print("CRM records were only read; no CRM records were changed.")


if __name__ == "__main__":
    main()

from collections import Counter
from datetime import date, timedelta

from src.crm.performance import fetch_all, number


def main():
    rows = fetch_all(
        "PaymentTransaction",
        "amount,paidDate,active,repairSettlementId,saleSettlementId",
    )

    today = date.today()
    cutoff = (today - timedelta(days=30)).isoformat()

    print("\nPAYMENT DATE DIAGNOSTIC")
    print("=" * 45)
    print(f"Total payment records: {len(rows)}")
    print(f"Today: {today.isoformat()}")
    print(f"30-day cutoff: {cutoff}")

    print("\nActive status counts:")
    for status, count in Counter(
        str(row.get("active")) for row in rows
    ).items():
        print(f"  active={status}: {count}")

    dates = [
        str(row["paidDate"])[:10]
        for row in rows
        if row.get("paidDate")
    ]

    print("\nPaid-date information:")
    print(f"Records with a paidDate: {len(dates)}")
    print(f"Records without a paidDate: {len(rows) - len(dates)}")

    if dates:
        print(f"Earliest paidDate: {min(dates)}")
        print(f"Latest paidDate: {max(dates)}")

    recent_active = [
        row for row in rows
        if row.get("active") is True
        and row.get("paidDate")
        and str(row["paidDate"])[:10] >= cutoff
    ]

    all_active = [
        row for row in rows
        if row.get("active") is True
    ]

    print("\nActive payment totals:")
    print(f"All active records: {len(all_active)}")
    print(
        "All active amounts (lei):",
        round(sum(number(row.get("amount")) for row in all_active), 2),
    )
    print(f"Active records in last 30 days: {len(recent_active)}")
    print(
        "Recent active amounts (lei):",
        round(
            sum(number(row.get("amount")) for row in recent_active),
            2,
        ),
    )

    print("\nRecent paidDate examples (date only):")
    for paid_date in sorted(set(dates))[-10:]:
        print(f"  {paid_date}")

    print("\nDiagnostic complete. No records were changed.")


if __name__ == "__main__":
    main()
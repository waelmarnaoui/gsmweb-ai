
from datetime import date, timedelta
from collections import Counter

from src.crm.performance import fetch_all


def date_part(value):
    return str(value)[:10] if value else None


def main():
    cutoff = (date.today() - timedelta(days=7)).isoformat()

    clients = fetch_all(
        "Client",
        "id,firstVisit,lastVisit,isRecurring,createdAt",
    )

    repairs = fetch_all(
        "Repair",
        "id,clientId,entryDate,createdAt,status,deliveredAt",
    )

    sales = fetch_all(
        "AccessorySale",
        "id,clientId,saleDate,createdAt",
    )

    print("\nGSMWEB ACTIVITY DIAGNOSTIC")
    print("=" * 45)
    print(f"Today: {date.today().isoformat()}")
    print(f"Last 7 days start: {cutoff}")

    print("\nCLIENTS")
    print(f"Total visible: {len(clients)}")

    for field in ["createdAt", "firstVisit", "lastVisit"]:
        dates = [
            date_part(row.get(field))
            for row in clients
            if date_part(row.get(field))
        ]
        recent = [value for value in dates if value >= cutoff]

        print(f"{field}:")
        print(f"  Records with date: {len(dates)}")
        print(f"  Earliest date: {min(dates) if dates else 'none'}")
        print(f"  Latest date: {max(dates) if dates else 'none'}")
        print(f"  In last 7 days: {len(recent)}")

    print("Recurring flag counts:")
    for value, count in Counter(
        str(row.get("isRecurring")) for row in clients
    ).items():
        print(f"  {value}: {count}")

    print("\nREPAIRS")
    print(f"Total visible: {len(repairs)}")
    print(f"Missing client link: {sum(not r.get('clientId') for r in repairs)}")

    for field in ["entryDate", "createdAt", "deliveredAt"]:
        dates = [
            date_part(row.get(field))
            for row in repairs
            if date_part(row.get(field))
        ]
        recent = [value for value in dates if value >= cutoff]

        print(f"{field}:")
        print(f"  Records with date: {len(dates)}")
        print(f"  Earliest date: {min(dates) if dates else 'none'}")
        print(f"  Latest date: {max(dates) if dates else 'none'}")
        print(f"  In last 7 days: {len(recent)}")

    print("Repair status counts:")
    for value, count in Counter(
        str(row.get("status")) for row in repairs
    ).items():
        print(f"  {value}: {count}")

    print("\nACCESSORY SALES")
    print(f"Total visible: {len(sales)}")
    print(f"Missing client link: {sum(not s.get('clientId') for s in sales)}")

    for field in ["saleDate", "createdAt"]:
        dates = [
            date_part(row.get(field))
            for row in sales
            if date_part(row.get(field))
        ]
        print(
            f"{field}: {len(dates)} records with dates; "
            f"{sum(value >= cutoff for value in dates)} in last 7 days"
        )

    print("\nDiagnostic complete. No records were changed.")


if __name__ == "__main__":
    main()
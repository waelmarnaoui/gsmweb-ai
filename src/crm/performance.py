
from datetime import date, timedelta
from decimal import Decimal
import json
import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()



def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")

    if not url or not key:
        raise RuntimeError(
            "Supabase URL or server-side secret key is missing."
        )

    return create_client(url, key)
   


def fetch_all(table, columns, filters=None):
    """Read rows in pages to avoid the API's default row limit."""
    client = get_supabase_client()
    rows = []
    page_size = 500
    start = 0

    while True:
        query = (
            client.table(table)
            .select(columns)
            .range(start, start + page_size - 1)
        )

        if filters:
            for method, column, value in filters:
                query = getattr(query, method)(column, value)

        batch = query.execute().data or []
        rows.extend(batch)

        if len(batch) < page_size:
            break

        start += page_size

    return rows


def number(value):
    return float(value or 0)


def get_crm_performance(days=30):
    start_date = (date.today() - timedelta(days=days)).isoformat()

    # Active payment transactions are the collection source.
    # Do not add settlement totals to these figures.
    payments = fetch_all(
        "PaymentTransaction",
        "id,repairSettlementId,saleSettlementId,amount,paidDate,active",
        [
            ("eq", "active", True),
            ("gte", "paidDate", start_date),
        ],
    )

    repair_settlements = fetch_all(
        "RepairSettlement",
        "id,repairId",
    )
    sale_settlements = fetch_all(
        "SaleSettlement",
        "id,saleId",
    )

    repair_id_by_settlement = {
        row["id"]: row["repairId"]
        for row in repair_settlements
    }
    sale_id_by_settlement = {
        row["id"]: row["saleId"]
        for row in sale_settlements
    }

    repair_payment_ids = set()
    sale_payment_ids = set()
    repair_revenue = 0.0
    sale_revenue = 0.0
    unmatched_payments = 0

    for payment in payments:
        amount = number(payment.get("amount"))

        repair_settlement_id = payment.get("repairSettlementId")
        sale_settlement_id = payment.get("saleSettlementId")

        if repair_settlement_id and not sale_settlement_id:
            repair_id = repair_id_by_settlement.get(
                repair_settlement_id
            )
            if repair_id:
                repair_payment_ids.add(repair_id)
                repair_revenue += amount
            else:
                unmatched_payments += 1

        elif sale_settlement_id and not repair_settlement_id:
            sale_id = sale_id_by_settlement.get(sale_settlement_id)
            if sale_id:
                sale_payment_ids.add(sale_id)
                sale_revenue += amount
            else:
                unmatched_payments += 1

        else:
            # Missing or ambiguous relationship: don't guess its type.
            unmatched_payments += 1

    repair_rows = fetch_all(
        "Repair",
        "id,clientId,status,deliveredAt,customerPrice,repairCost",
        [
            ("gte", "deliveredAt", start_date),
        ],
    )

    delivered_repairs = [
        row for row in repair_rows
        if row.get("status") == "DELIVERED"
    ]

    accessory_sales = fetch_all(
        "AccessorySale",
        "id,clientId,saleDate,quantity,salePrice,productCost",
        [
            ("gte", "saleDate", start_date),
        ],
    )

    accessory_revenue = sum(
        number(row.get("salePrice")) * number(row.get("quantity"))
        for row in accessory_sales
    )

    accessory_recorded_cost = sum(
        number(row.get("productCost")) * number(row.get("quantity"))
        for row in accessory_sales
    )

    return {
        "generated_at": date.today().isoformat(),
        "period_days": days,
        "start_date": start_date,
        "payment_records": len(payments),
        "collections": {
            "repair_payments_lei": round(repair_revenue, 2),
            "sale_payments_lei": round(sale_revenue, 2),
            "total_matched_payments_lei": round(
                repair_revenue + sale_revenue, 2
            ),
            "unmatched_payment_records": unmatched_payments,
        },
        "repairs": {
            "delivered_repairs_in_period": len(delivered_repairs),
            "listed_repair_value_lei": round(
                sum(number(r.get("customerPrice"))
                    for r in delivered_repairs), 2
            ),
            "recorded_repair_cost_lei": round(
                sum(number(r.get("repairCost"))
                    for r in delivered_repairs), 2
            ),
        },
        "accessory_sales": {
            "sale_records_in_period": len(accessory_sales),
            "listed_sales_value_lei": round(accessory_revenue, 2),
            "recorded_product_cost_lei": round(
                accessory_recorded_cost, 2
            ),
        },
        "notes": [
            "Collections use active payment transactions, not settlement totals.",
            "Listed repair value is not proof of money collected.",
            "Repair profit is not calculated until repairCost is verified.",
            "Accessory sales are reported separately from sale payments.",
            "No customer names, phone numbers, or emails are retrieved.",
        ],
    }


def main():
    report = get_crm_performance(days=30)

    os.makedirs("reports", exist_ok=True)
    filename = os.path.join("reports", "crm_performance.json")

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print("\nGSMWEB CRM PERFORMANCE — READ-ONLY")
    print("=" * 48)
    print(f"Period: last {report['period_days']} days")
    print(f"Payment records: {report['payment_records']}")

    for key, value in report["collections"].items():
        print(f"{key}: {value}")

    print("\nRepairs:")
    for key, value in report["repairs"].items():
        print(f"{key}: {value}")

    print("\nAccessory sales:")
    for key, value in report["accessory_sales"].items():
        print(f"{key}: {value}")

    print("\nNo CRM or Google Ads records were changed.")
    print(f"Report saved to: {filename}")


if __name__ == "__main__":
    main()
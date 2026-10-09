
from src.google_ads.client import get_google_ads_client, get_customer_id
from src.google_ads.conversion_performance import get_conversion_performance


def get_conversion_actions():
    client = get_google_ads_client()
    service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            conversion_action.id,
            conversion_action.name,
            conversion_action.status,
            conversion_action.primary_for_goal,
            conversion_action.type,
            conversion_action.category
        FROM conversion_action
        WHERE conversion_action.status != REMOVED
        ORDER BY conversion_action.id
    """

    rows = service.search(
        customer_id=get_customer_id(),
        query=query,
    )

    actions = []

    for row in rows:
        action = row.conversion_action
        actions.append({
            "id": action.id,
            "name": action.name,
            "status": action.status.name,
            "primary_for_goal": action.primary_for_goal,
            "type": action.type.name,
            "category": action.category.name,
        })

    return actions


def audit_conversion_setup(days=30):
    actions = get_conversion_actions()
    performance = get_conversion_performance(days=days)

    performance_by_id = {}

    for row in performance:
        resource_name = row.get("conversion_action", "")
        action_id = resource_name.rsplit("/", 1)[-1]

        performance_by_id[action_id] = {
            "conversions": row.get("conversions", 0),
            "conversion_value": row.get("conversion_value", 0),
        }

    results = []

    for action in actions:
        metrics = performance_by_id.get(str(action["id"]), {})
        conversions = float(metrics.get("conversions", 0) or 0)
        value = float(metrics.get("conversion_value", 0) or 0)

        if action["status"] != "ENABLED":
            finding = "Not currently enabled"
        elif action["primary_for_goal"] and conversions == 0:
            finding = "Primary action with no recorded conversions"
        elif action["primary_for_goal"]:
            finding = "Primary action with recorded conversions"
        elif conversions > 0:
            finding = "Secondary action with recorded conversions"
        else:
            finding = "No recorded conversions in this period"

        results.append({
            **action,
            "conversions_last_period": conversions,
            "conversion_value_last_period": value,
            "finding": finding,
        })

    return results


def main():
    results = audit_conversion_setup(days=30)

    print("\nGSMWEB CONVERSION AUDIT — LAST 30 DAYS")
    print("=" * 65)

    for action in results:
        print(
            f"\nID: {action['id']} | "
            f"Primary: {action['primary_for_goal']}"
        )
        print(f"Name: {action['name']}")
        print(f"Type: {action['type']} | Category: {action['category']}")
        print(f"Conversions: {action['conversions_last_period']:.2f}")
        print(f"Value: {action['conversion_value_last_period']:.2f}")
        print(f"Finding: {action['finding']}")

    print("\nRead-only audit complete. No Google Ads settings were changed.")


if __name__ == "__main__":
    main()
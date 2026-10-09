import json

from src.google_ads.client import get_google_ads_client, get_customer_id


def get_conversion_actions():
    client = get_google_ads_client()
    customer_id = get_customer_id()

    google_ads_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            conversion_action.id,
            conversion_action.name,
            conversion_action.type,
            conversion_action.status,
            conversion_action.category
        FROM conversion_action
        ORDER BY conversion_action.id
    """

    response = google_ads_service.search(
        customer_id=customer_id,
        query=query,
    )

    conversions = []

    for row in response:
        conversions.append({
            "id": row.conversion_action.id,
            "name": row.conversion_action.name,
            "type": row.conversion_action.type.name,
            "status": row.conversion_action.status.name,
            "category": row.conversion_action.category.name,
        })

    return conversions


def save_conversion_actions(filename="conversion_actions.json"):
    data = get_conversion_actions()

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return data
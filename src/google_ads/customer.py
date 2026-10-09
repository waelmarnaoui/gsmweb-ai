import json

from src.google_ads.client import get_google_ads_client, get_customer_id


def get_conversion_tracking_settings():
    client = get_google_ads_client()
    customer_id = get_customer_id()

    google_ads_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            customer.id,
            customer.currency_code,
            customer.time_zone,
            customer.conversion_tracking_setting.google_ads_conversion_customer,
            customer.conversion_tracking_setting.conversion_tracking_status,
            customer.conversion_tracking_setting.conversion_tracking_id,
            customer.conversion_tracking_setting.cross_account_conversion_tracking_id
        FROM customer
    """

    response = google_ads_service.search(
        customer_id=customer_id,
        query=query,
    )

    settings = []

    for row in response:
        settings.append({
            "customer_id": row.customer.id,
            "currency_code": row.customer.currency_code,
            "time_zone": row.customer.time_zone,
            "google_ads_conversion_customer": (
                row.customer.conversion_tracking_setting
                .google_ads_conversion_customer
            ),
            "conversion_tracking_status": (
                row.customer.conversion_tracking_setting
                .conversion_tracking_status.name
            ),
            "conversion_tracking_id": (
                row.customer.conversion_tracking_setting
                .conversion_tracking_id
            ),
            "cross_account_conversion_tracking_id": (
                row.customer.conversion_tracking_setting
                .cross_account_conversion_tracking_id
            ),
        })

    return settings


def save_conversion_tracking_settings(
    filename="conversion_tracking_settings.json"
):
    data = get_conversion_tracking_settings()

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return data
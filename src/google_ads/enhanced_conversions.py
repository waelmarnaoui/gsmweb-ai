from src.google_ads.client import get_google_ads_client, get_customer_id


def get_enhanced_conversions_status():
    client = get_google_ads_client()
    customer_id = get_customer_id()

    google_ads_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            customer.id,
            customer.conversion_tracking_setting.accepted_customer_data_terms,
            customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled
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
            "accepted_customer_data_terms": (
                row.customer.conversion_tracking_setting
                .accepted_customer_data_terms
            ),
            "enhanced_conversions_for_leads_enabled": (
                row.customer.conversion_tracking_setting
                .enhanced_conversions_for_leads_enabled
            ),
        })

    return settings
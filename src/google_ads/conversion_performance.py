from src.google_ads.client import get_google_ads_client, get_customer_id


def get_conversion_performance(days=30):
    client = get_google_ads_client()
    customer_id = get_customer_id()

    google_ads_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            segments.conversion_action,
            segments.conversion_action_name,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE segments.date DURING LAST_{days}_DAYS
        ORDER BY metrics.conversions DESC
    """

    response = google_ads_service.search(
        customer_id=customer_id,
        query=query,
    )

    conversions = []

    for row in response:
        conversions.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "conversion_action": row.segments.conversion_action,
            "conversion_action_name": row.segments.conversion_action_name,
            "conversions": row.metrics.conversions,
            "conversion_value": row.metrics.conversions_value,
        })

    return conversions
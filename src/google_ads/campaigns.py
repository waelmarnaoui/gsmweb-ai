from src.google_ads.client import get_google_ads_client, get_customer_id


def get_campaign_performance(days=30):
    client = get_google_ads_client()
    customer_id = get_customer_id()

    google_ads_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.ctr,
            metrics.average_cpc
        FROM campaign
        WHERE segments.date DURING LAST_{days}_DAYS
        ORDER BY metrics.cost_micros DESC
    """

    response = google_ads_service.search(
        customer_id=customer_id,
        query=query,
    )

    campaigns = []

    for row in response:
        campaigns.append({
            "id": row.campaign.id,
            "name": row.campaign.name,
            "status": row.campaign.status.name,
            "type": row.campaign.advertising_channel_type.name,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "cost_usd": row.metrics.cost_micros / 1_000_000,
            "conversions": row.metrics.conversions,
            "conversion_value": row.metrics.conversions_value,
            "ctr": row.metrics.ctr,
            "average_cpc_usd": row.metrics.average_cpc / 1_000_000,
        })

    return campaigns
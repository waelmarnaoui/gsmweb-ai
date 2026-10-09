from src.google_ads.client import get_google_ads_client, get_customer_id


def get_search_terms(days=30):
    client = get_google_ads_client()
    customer_id = get_customer_id()

    google_ads_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            search_term_view.search_term,
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM search_term_view
        WHERE segments.date DURING LAST_{days}_DAYS
        ORDER BY metrics.cost_micros DESC
    """

    response = google_ads_service.search(
        customer_id=customer_id,
        query=query,
    )

    search_terms = []

    for row in response:
        search_terms.append({
            "search_term": row.search_term_view.search_term,
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "ad_group_id": row.ad_group.id,
            "ad_group_name": row.ad_group.name,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "cost_usd": row.metrics.cost_micros / 1_000_000,
            "conversions": row.metrics.conversions,
            "conversion_value": row.metrics.conversions_value,
        })

    return search_terms
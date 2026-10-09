import json
from google.ads.googleads.client import GoogleAdsClient

CUSTOMER_ID = "2050434247"

client = GoogleAdsClient.load_from_storage("google-ads.yaml")
google_ads_service = client.get_service("GoogleAdsService")

query = """
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
    WHERE segments.date DURING LAST_30_DAYS
    ORDER BY metrics.cost_micros DESC
"""

response = google_ads_service.search(
    customer_id=CUSTOMER_ID,
    query=query,
)

campaigns = []

for row in response:
    campaign = {
        "id": row.campaign.id,
        "name": row.campaign.name,
        "status": row.campaign.status.name,
        "type": row.campaign.advertising_channel_type.name,
        "impressions": row.metrics.impressions,
        "clicks": row.metrics.clicks,
        "cost_usd": round(row.metrics.cost_micros / 1_000_000, 2),
        "conversions": row.metrics.conversions,
        "conversion_value": row.metrics.conversions_value,
        "ctr": round(row.metrics.ctr * 100, 2),
        "average_cpc_usd": round(row.metrics.average_cpc / 1_000_000, 2),
    }

    campaigns.append(campaign)

with open("campaign_data.json", "w", encoding="utf-8") as file:
    json.dump(campaigns, file, indent=2)

print(f"Saved {len(campaigns)} campaigns to campaign_data.json")
from google.ads.googleads.client import GoogleAdsClient

CUSTOMER_ID = "2050434247"


def get_google_ads_client():
    return GoogleAdsClient.load_from_storage(
        "google-ads.yaml"
    )


def get_customer_id():
    return CUSTOMER_ID
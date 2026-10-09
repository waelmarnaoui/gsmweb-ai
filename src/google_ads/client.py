
import os

from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

load_dotenv()

CUSTOMER_ID = os.getenv(
    "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
    "2050434247",
)


def get_google_ads_client():
    return GoogleAdsClient.load_from_env()


def get_customer_id():
    return CUSTOMER_ID
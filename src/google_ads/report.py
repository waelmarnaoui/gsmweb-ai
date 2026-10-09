
import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import create_client

from src.google_ads.campaigns import get_campaign_performance


def main():
    load_dotenv()

    print("Starting read-only Google Ads report...")

    campaigns = get_campaign_performance(days=30)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period_days": 30,
        "campaign_count": len(campaigns),
        "campaigns": campaigns,
    }

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SECRET_KEY"]
    supabase = create_client(supabase_url, supabase_key)

    supabase.table("gsm_ai_google_ads_reports").upsert(
        {
            "report_date": datetime.now(timezone.utc).date().isoformat(),
            "report": report,
        }
    ).execute()

    print(json.dumps(report, indent=2))
    print("Google Ads report saved to Supabase.")
    print("No campaigns were modified.")


if __name__ == "__main__":
    main()
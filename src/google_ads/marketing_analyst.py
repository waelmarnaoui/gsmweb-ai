
from datetime import datetime
import json
import os

from src.google_ads.campaigns import get_campaign_performance
from src.google_ads.search_terms import get_search_terms


def money(value):
    return f"${value:,.2f}"


def analyze_campaigns(campaigns):
    findings = []

    for campaign in campaigns:
        name = campaign.get("name", "Unknown campaign")
        clicks = float(campaign.get("clicks", 0) or 0)
        impressions = float(campaign.get("impressions", 0) or 0)
        cost = float(campaign.get("cost_usd", 0) or 0)
        conversions = float(campaign.get("conversions", 0) or 0)
        ctr = float(campaign.get("ctr", 0) or 0)
        avg_cpc = float(campaign.get("average_cpc_usd", 0) or 0)

        if clicks >= 30 and conversions == 0 and cost > 0:
            findings.append({
                "priority": "HIGH",
                "campaign": name,
                "issue": "Spend without recorded conversions",
                "evidence": (
                    f"{clicks:.0f} clicks, {money(cost)} cost, "
                    "0 recorded conversions"
                ),
                "recommendation": (
                    "Review search terms, landing page, call tracking, "
                    "and conversion setup before changing the budget."
                ),
            })

        if clicks >= 30 and ctr < 0.02:
            findings.append({
                "priority": "MEDIUM",
                "campaign": name,
                "issue": "Low click-through rate",
                "evidence": f"CTR: {ctr:.2%} across {clicks:.0f} clicks",
                "recommendation": (
                    "Review search intent, ad relevance, and headlines."
                ),
            })

        if clicks >= 20 and avg_cpc > 0:
            findings.append({
                "priority": "INFO",
                "campaign": name,
                "issue": "Cost-per-click review",
                "evidence": f"Average CPC: {money(avg_cpc)}",
                "recommendation": (
                    "Compare CPC with actual customer acquisition "
                    "and gross profit before deciding whether it is high."
                ),
            })

        if impressions == 0:
            findings.append({
                "priority": "INFO",
                "campaign": name,
                "issue": "No impressions in reporting period",
                "evidence": "0 impressions",
                "recommendation": (
                    "Check campaign status, date range, targeting, "
                    "and whether the campaign recently started."
                ),
            })

    return findings


def analyze_search_terms(search_terms):
    findings = []

    for term in search_terms:
        query = str(term.get("search_term", "")).strip()
        clicks = float(term.get("clicks", 0) or 0)
        cost = float(term.get("cost_usd", 0) or 0)
        conversions = float(term.get("conversions", 0) or 0)

        if clicks >= 10 and conversions == 0 and cost > 0:
            findings.append({
                "priority": "REVIEW",
                "search_term": query or "(empty search term)",
                "issue": "Clicks without recorded conversions",
                "evidence": (
                    f"{clicks:.0f} clicks, {money(cost)} cost, "
                    "0 recorded conversions"
                ),
                "recommendation": (
                    "Check relevance and actual customer outcomes. "
                    "Do not automatically add this term as a negative "
                    "keyword based only on this report."
                ),
            })

    return findings


def build_report(days=30):
    campaigns = get_campaign_performance(days=days)
    search_terms = get_search_terms(days=days)

    campaign_findings = analyze_campaigns(campaigns)
    search_findings = analyze_search_terms(search_terms)

    total_cost = sum(
        float(c.get("cost_usd", 0) or 0) for c in campaigns
    )
    total_clicks = sum(
        float(c.get("clicks", 0) or 0) for c in campaigns
    )
    total_impressions = sum(
        float(c.get("impressions", 0) or 0) for c in campaigns
    )
    total_conversions = sum(
        float(c.get("conversions", 0) or 0) for c in campaigns
    )
    total_conversion_value = sum(
        float(c.get("conversion_value", 0) or 0)
        for c in campaigns
    )

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "period_days": days,
        "currency_note": (
            "Google Ads account reporting currency is USD. "
            "Conversion value is the value reported by Google Ads, "
            "not verified GSMWEB revenue or profit."
        ),
        "summary": {
            "campaign_count": len(campaigns),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_cost_usd": round(total_cost, 2),
            "total_conversions": round(total_conversions, 2),
            "total_conversion_value": round(total_conversion_value, 2),
            "average_cpc_usd": (
                round(total_cost / total_clicks, 2)
                if total_clicks else 0
            ),
            "ctr": (
                round(total_clicks / total_impressions, 4)
                if total_impressions else 0
            ),
            "cost_per_recorded_conversion_usd": (
                round(total_cost / total_conversions, 2)
                if total_conversions else None
            ),
        },
        "campaign_findings": campaign_findings,
        "search_term_findings": search_findings,
        "campaigns": campaigns,
    }

    return report


def print_report(report):
    summary = report["summary"]

    print("\n" + "=" * 60)
    print("GSMWEB AI MARKETING ANALYST")
    print("=" * 60)
    print(f"Period: last {report['period_days']} days")
    print(f"Campaigns: {summary['campaign_count']}")
    print(f"Impressions: {summary['total_impressions']:,.0f}")
    print(f"Clicks: {summary['total_clicks']:,.0f}")
    print(f"CTR: {summary['ctr']:.2%}")
    print(f"Ad spend: {money(summary['total_cost_usd'])}")
    print(f"Recorded conversions: {summary['total_conversions']:.2f}")
    print(f"Average CPC: {money(summary['average_cpc_usd'])}")

    cpa = summary["cost_per_recorded_conversion_usd"]
    if cpa is not None:
        print(f"Cost per recorded conversion: {money(cpa)}")
    else:
        print("Cost per recorded conversion: unavailable")

    print("\nCAMPAIGN FINDINGS")
    for finding in report["campaign_findings"]:
        print(f"\n[{finding['priority']}] {finding['campaign']}")
        print(f"Issue: {finding['issue']}")
        print(f"Evidence: {finding['evidence']}")
        print(f"Recommendation: {finding['recommendation']}")

    print("\nSEARCH TERM FINDINGS")
    for finding in report["search_term_findings"]:
        print(f"\n[{finding['priority']}] {finding['search_term']}")
        print(f"Issue: {finding['issue']}")
        print(f"Evidence: {finding['evidence']}")
        print(f"Recommendation: {finding['recommendation']}")

    if not report["campaign_findings"] and not report["search_term_findings"]:
        print("No findings met the current review thresholds.")

    print("\nNOTE")
    print(report["currency_note"])
    print("Recommendations are advisory; no campaign changes were made.")


def main():
    days = 30
    report = build_report(days=days)

    os.makedirs("reports", exist_ok=True)
    filename = os.path.join(
        "reports",
        f"marketing_analysis_{datetime.now():%Y%m%d_%H%M%S}.json",
    )

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print_report(report)
    print(f"\nFull report saved to: {filename}")


if __name__ == "__main__":
    main()
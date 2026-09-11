#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/spy_ads.py - Competitor Facebook & Instagram Ad Spy
Collects live active competitor ads from Meta Ad Library without API keys.
Extracts: Ad copy hooks, headlines, CTAs, media types, and active duration.
"""

import sys
import os
import json
import argparse
from datetime import datetime
import io

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer") and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer") and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from meta_ads_collector import MetaAdsCollector
except ImportError:
    MetaAdsCollector = None

def spy_competitor_ads(query, country="US", max_results=5, proxy="127.0.0.1:10809"):
    if not MetaAdsCollector:
        print("❌ meta_ads_collector is not installed. Run: pip install meta-ads-collector")
        return {"error": "meta_ads_collector_not_installed", "items": []}

    # Normalize proxy string (strip http://)
    clean_proxy = proxy.replace("http://", "").replace("https://", "") if proxy else None

    print(f"🕵️ Searching Meta Ad Library for active ads: '{query}' (Country: {country})...")
    results = []
    try:
        collector = MetaAdsCollector(proxy=clean_proxy, rate_limit_delay=3.0)
        with collector:
            ads = list(collector.search(query=query, country=country, max_results=max_results))
            for ad in ads:
                page_name = ad.page.name if ad.page else "Unknown Page"
                page_id = ad.page.id if ad.page else ""
                body = ""
                headline = ""
                cta = ""
                media_type = "UNKNOWN"
                link_url = ""

                if ad.creatives:
                    c = ad.creatives[0]
                    body = c.body or ""
                    headline = c.title or ""
                    cta = c.call_to_action_type or ""
                    link_url = c.link_url or ""
                    if c.video_url:
                        media_type = "VIDEO"
                    elif c.image_url:
                        media_type = "IMAGE"

                start_date_str = ad.delivery_start_time.strftime("%Y-%m-%d") if ad.delivery_start_time else "Unknown"

                results.append({
                    "id": ad.id,
                    "page_name": page_name,
                    "page_id": page_id,
                    "media_type": media_type,
                    "headline": headline,
                    "body": body,
                    "cta": cta,
                    "link_url": link_url,
                    "start_date": start_date_str,
                    "ad_snapshot_url": ad.ad_snapshot_url or f"https://www.facebook.com/ads/library/?id={ad.id}"
                })
        return {"query": query, "country": country, "total_found": len(results), "items": results}
    except Exception as e:
        print(f"⚠️ Meta Ad Library query encountered an issue: {e}")
        return {"query": query, "error": str(e), "items": results}

def print_ad_report(data):
    print("=" * 80)
    print(f"【Meta 广告间谍实盘情报 · '{data.get('query')}'】")
    print("=" * 80)
    items = data.get("items", [])
    print(f"捕获在投广告数: {len(items)} 条")
    print("-" * 80)

    if not items:
        print("ℹ️ 未捕获到当前正在投放的公开广告，可能原因：")
        print("  1. 当前关键词在目标地区暂无大投放商（蓝海信号！）；")
        print("  2. Meta GraphQL 临时触发 IP 限流，建议稍后重试或更换关键词。")
    else:
        for idx, it in enumerate(items, 1):
            print(f"#{idx} 投放主页: {it['page_name']} | 形式: {it['media_type']} | 上线时间: {it['start_date']}")
            if it['headline']:
                print(f"   标  题: {it['headline']}")
            if it['body']:
                clean_b = it['body'].replace('\n', ' ')
                snippet = clean_b[:120] + "..." if len(clean_b) > 120 else clean_b
                print(f"   文案钩子: \"{snippet}\"")
            if it['cta']:
                print(f"   行动号召 (CTA): {it['cta']}")
            print(f"   👉 广告底稿链接: {it['ad_snapshot_url']}")
            print("-" * 80)
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Spy on competitor Facebook & Instagram ads.")
    parser.add_argument("query", help="Keyword or brand name to search in Meta Ad Library")
    parser.add_argument("--country", default="US", help="Target country code (e.g. US, CA, UK)")
    parser.add_argument("--limit", type=int, default=5, help="Max ads to collect")
    parser.add_argument("--proxy", default="127.0.0.1:10809", help="Proxy host:port")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()
    data = spy_competitor_ads(args.query, country=args.country, max_results=args.limit, proxy=args.proxy)

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print_ad_report(data)

if __name__ == "__main__":
    main()

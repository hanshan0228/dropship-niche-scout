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
import urllib.parse
import asyncio
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

async def _scrape_ads_patchright_async(query, country="US", max_results=5):
    try:
        from patchright.async_api import async_playwright
    except ImportError:
        return []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale="en-US", viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        encoded_q = urllib.parse.quote(query)
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={encoded_q}&search_type=keyword_unordered&media_type=all"
        await page.goto(url, wait_until="domcontentloaded", timeout=40000)
        await page.wait_for_timeout(5000)
        await page.evaluate("window.scrollBy(0, 1200)")
        await page.wait_for_timeout(2000)

        ads = await page.evaluate("""
            () => {
                const items = [];
                const divs = document.querySelectorAll('div');
                const seenIds = new Set();
                for (const d of divs) {
                    const txt = d.innerText || '';
                    if (txt.includes('Library ID:') && (txt.includes('Started running on') || txt.includes('Active'))) {
                        const idMatch = txt.match(/Library ID:\\s*(\\d+)/);
                        if (!idMatch) continue;
                        const id = idMatch[1];
                        if (seenIds.has(id)) continue;
                        seenIds.add(id);

                        const lines = txt.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                        const img = d.querySelector('img');
                        const video = d.querySelector('video');

                        let pageName = 'Sponsored Brand';
                        let startDate = 'Active';
                        let body = '';

                        for (let i = 0; i < lines.length; i++) {
                            if (lines[i].includes('Started running on')) {
                                startDate = lines[i];
                                if (i > 0) pageName = lines[i - 1];
                            }
                        }

                        const bodyCandidates = lines.filter(l => l.length > 25 && !l.includes('Library ID') && !l.includes('Started running') && !l.includes('Sponsored'));
                        if (bodyCandidates.length > 0) {
                            body = bodyCandidates.slice(0, 2).join(' ');
                        }

                        items.push({
                            id: id,
                            page_name: pageName,
                            page_id: '',
                            media_type: video ? 'VIDEO' : 'IMAGE',
                            headline: '',
                            body: body,
                            cta: 'Shop Now',
                            image_url: img ? img.src : '',
                            video_url: '',
                            link_url: '',
                            start_date: startDate,
                            ad_snapshot_url: `https://www.facebook.com/ads/library/?id=${id}`
                        });
                    }
                }
                return items;
            }
        """)
        await browser.close()
        return ads[:max_results]

def _scrape_ads_patchright(query, country="US", max_results=5):
    try:
        return asyncio.run(_scrape_ads_patchright_async(query, country, max_results))
    except Exception as e:
        print(f"Browser fallback error: {e}")
        return []

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

                image_url = ""
                video_url = ""
                if ad.creatives:
                    c = ad.creatives[0]
                    body = getattr(c, "body", "") or getattr(c, "caption", "") or getattr(c, "description", "") or ""
                    headline = getattr(c, "title", "") or ""
                    cta = getattr(c, "cta_text", "") or getattr(c, "cta_type", "") or ""
                    link_url = getattr(c, "link_url", "") or ""
                    image_url = getattr(c, "image_url", "") or getattr(c, "thumbnail_url", "") or ""
                    video_url = getattr(c, "video_url", "") or getattr(c, "video_hd_url", "") or getattr(c, "video_sd_url", "") or ""
                    if video_url:
                        media_type = "VIDEO"
                    elif image_url:
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
                    "image_url": image_url,
                    "video_url": video_url,
                    "link_url": link_url,
                    "start_date": start_date_str,
                    "ad_snapshot_url": ad.ad_snapshot_url or f"https://www.facebook.com/ads/library/?id={ad.id}"
                })
    except Exception as e:
        print(f"ℹ️ MetaAdsCollector note: {e}")

    # Fallback to browser stealth transport if direct collector got 0 ads
    if not results:
        print("ℹ️ Direct collector returned 0 ads. Activating browser transport fallback...")
        results = _scrape_ads_patchright(query, country, max_results)

    return {"query": query, "country": country, "total_found": len(results), "items": results}

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

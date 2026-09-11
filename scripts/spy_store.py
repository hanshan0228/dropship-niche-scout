#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/spy_store.py - Competitor Shopify/WooCommerce Store Intelligence
Extracts product catalogs, pricing distributions, SKU variants, and collections
from competitor standalone stores.
"""

import sys
import os
import json
import argparse
import urllib.parse
from curl_cffi import requests
import io

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer") and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer") and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def spy_shopify_store(store_url, limit=20):
    # Normalize URL
    if not store_url.startswith("http://") and not store_url.startswith("https://"):
        store_url = "https://" + store_url
    parsed = urllib.parse.urlparse(store_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    endpoint = f"{base_url}/products.json?limit={min(limit, 250)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    print(f"🕵️ Scanning competitor store: {base_url}...")
    try:
        r = requests.get(endpoint, headers=headers, impersonate="chrome", timeout=15)
        if r.status_code == 200:
            data = r.json()
            products = data.get("products", [])
            print(f"✅ Successfully retrieved {len(products)} products from {base_url}")
            return analyze_products(base_url, products[:limit])
        elif r.status_code in (403, 404):
            print(f"ℹ️ Direct /products.json returned HTTP {r.status_code}. Attempting collections fallback...")
            # Fallback to shopify_spy CLI if direct json is gated
            return {"domain": base_url, "status": "blocked_or_protected", "products": []}
    except Exception as e:
        print(f"❌ Error connecting to store: {e}")
        return {"domain": base_url, "error": str(e), "products": []}

def analyze_products(domain, products):
    summary = {
        "domain": domain,
        "total_analyzed": len(products),
        "price_summary": {"min": 999999, "max": 0, "avg": 0},
        "items": []
    }
    total_price = 0
    price_count = 0

    for p in products:
        title = p.get("title", "")
        handle = p.get("handle", "")
        product_url = f"{domain}/products/{handle}" if handle else ""
        variants = p.get("variants", [])
        images = [img.get("src") for img in p.get("images", []) if img.get("src")]

        prices = []
        for v in variants:
            try:
                pr = float(v.get("price", 0))
                if pr > 0:
                    prices.append(pr)
                    total_price += pr
                    price_count += 1
                    if pr < summary["price_summary"]["min"]:
                        summary["price_summary"]["min"] = pr
                    if pr > summary["price_summary"]["max"]:
                        summary["price_summary"]["max"] = pr
            except ValueError:
                pass

        min_p = min(prices) if prices else 0
        max_p = max(prices) if prices else 0
        price_str = f"${min_p:.2f}" if min_p == max_p else f"${min_p:.2f} - ${max_p:.2f}"

        summary["items"].append({
            "id": p.get("id"),
            "title": title,
            "product_type": p.get("product_type", ""),
            "vendor": p.get("vendor", ""),
            "price_range": price_str,
            "min_price": min_p,
            "variants_count": len(variants),
            "created_at": p.get("created_at", "")[:10],
            "url": product_url,
            "image": images[0] if images else ""
        })

    if price_count > 0:
        summary["price_summary"]["avg"] = round(total_price / price_count, 2)
    else:
        summary["price_summary"]["min"] = 0

    return summary

def print_store_report(summary):
    print("=" * 80)
    print(f"【竞品独立站深度侦察简报 · {summary['domain']}】")
    print("=" * 80)
    print(f"分析商品数: {summary['total_analyzed']} 款在售商品")
    p_sum = summary.get("price_summary", {})
    print(f"售价价格带: ${p_sum.get('min', 0):.2f} – ${p_sum.get('max', 0):.2f} USD (平均客单价: ${p_sum.get('avg', 0):.2f} USD)")
    print("-" * 80)
    print(f"{'商品名称':<40} | {'价格区间':<16} | {'变体数':<6} | {'上架时间'}")
    print("-" * 80)
    for it in summary["items"][:15]:
        t = it["title"][:38] + ".." if len(it["title"]) > 38 else it["title"]
        print(f"{t:<40} | {it['price_range']:<16} | {it['variants_count']:<6} | {it['created_at']}")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Spy on competitor Shopify store products and pricing.")
    parser.add_argument("url", help="Competitor store URL or domain (e.g. birdiegirlgolf.com)")
    parser.add_argument("--limit", type=int, default=20, help="Max products to analyze")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()
    res = spy_shopify_store(args.url, args.limit)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print_store_report(res)

if __name__ == "__main__":
    main()

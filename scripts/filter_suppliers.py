#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/filter_suppliers.py - AliExpress Supplier Vetting & Audit Gate
Evaluates an AliExpress supplier candidate against strict dropshipping criteria:
1. Store Positive Feedback Rate >= 96.0%
2. Store Age >= 2 years
3. Product Rating >= 4.7★
4. Historical Orders >= 100
5. Ships to US with tracking
6. Dynamic Pre-Ad Margin calculation (NO price cap/floor!).
"""

import sys
import os
import json
import argparse
import io

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer") and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer") and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def vet_supplier(data):
    checks = {}
    violations = []

    name = data.get("name", "Unknown Product")
    cost_usd = float(data.get("cost_usd", 0))
    retail_price = float(data.get("retail_price", 0))
    if retail_price <= 0:
        # Default markup assumption: 3x - 3.5x
        retail_price = max(cost_usd * 3.2, 79.0)

    rating = float(data.get("rating", 0))
    orders = int(data.get("orders", 0))
    store_rate = float(data.get("store_positive_rate", 0))
    store_years = int(data.get("store_years", 0))
    ships_to_us = bool(data.get("ships_to_us", True))

    # 1. Store Positive Feedback Rate (>= 96.0%)
    p_rate_pass = store_rate >= 96.0
    checks["store_positive_rate"] = {
        "pass": p_rate_pass,
        "detail": f"{store_rate:.1f}% (required: >= 96.0%)"
    }
    if not p_rate_pass:
        violations.append(f"Store positive feedback rate ({store_rate:.1f}%) is below 96.0% threshold.")

    # 2. Store Age (>= 2 years)
    years_pass = store_years >= 2
    checks["store_age"] = {
        "pass": years_pass,
        "detail": f"{store_years} years (required: >= 2 years)"
    }
    if not years_pass:
        violations.append(f"Store age ({store_years} yrs) is under 2 years (high churn/abandonment risk).")

    # 3. Product Rating (>= 4.7★)
    rating_pass = rating >= 4.7
    checks["product_rating"] = {
        "pass": rating_pass,
        "detail": f"{rating:.1f}★ (required: >= 4.7★)"
    }
    if not rating_pass:
        violations.append(f"Product rating ({rating:.1f}★) is below 4.7★ (post-sale dispute hazard).")

    # 4. Total Orders (>= 100)
    orders_pass = orders >= 100
    checks["historical_orders"] = {
        "pass": orders_pass,
        "detail": f"{orders}+ sold (required: >= 100)"
    }
    if not orders_pass:
        violations.append(f"Orders count ({orders}) is under 100 (unproven mold / listing quality).")

    # 5. Direct US Shipping
    checks["ships_to_us"] = {
        "pass": ships_to_us,
        "detail": "Direct US tracked line supported" if ships_to_us else "No direct US tracking line"
    }
    if not ships_to_us:
        violations.append("Supplier does not support tracked direct shipping to the US.")

    # 6. Dynamic Margin Economics (NO ARBITRARY PRICE LIMIT, PURE MARGIN AUDIT)
    # Estimate standard fees: Stripe 2.9% + $0.30, Refund 2.5%
    stripe_fee = retail_price * 0.029 + 0.30
    refund_reserve = retail_price * 0.025
    pre_ad_margin = retail_price - cost_usd - stripe_fee - refund_reserve

    margin_pass = pre_ad_margin >= 35.0
    checks["pre_ad_margin"] = {
        "pass": margin_pass,
        "detail": f"+${pre_ad_margin:.2f} (at ${retail_price:.2f} retail, target: >= $35.00)"
    }
    if not margin_pass:
        violations.append(f"Pre-Ad Margin (+${pre_ad_margin:.2f}) is below $35.00 minimum threshold.")

    overall_pass = len(violations) == 0

    return {
        "name": name,
        "cost_usd": cost_usd,
        "retail_price": retail_price,
        "pre_ad_margin": pre_ad_margin,
        "overall_pass": overall_pass,
        "checks": checks,
        "violations": violations,
        "product_url": data.get("url", ""),
        "store_url": data.get("store_url", "")
    }

def print_card(res):
    print("=" * 80)
    status_str = "✅ PASS (优质可靠货源 · 推荐上架)" if res["overall_pass"] else "❌ REJECT (未达刚性门禁 · 淘汰)"
    print(f"【速卖通供应商与货源硬门禁审核卡】 {status_str}")
    print("=" * 80)
    print(f"商品名称: {res['name']}")
    print(f"采购进价: ${res['cost_usd']:.2f} USD (不设限价，按动态毛利核算)")
    print(f"建议零售: ${res['retail_price']:.2f} USD")
    print(f"预估净利: +${res['pre_ad_margin']:.2f} USD (扣除支付手续费与退换预留)")
    if res["product_url"]:
        print(f"商品链接: {res['product_url']}")
    if res["store_url"]:
        print(f"店铺链接: {res['store_url']}")
    print("-" * 80)
    print("刚性门禁考核结果:")
    for check_name, info in res["checks"].items():
        mark = "✅ PASS" if info["pass"] else "❌ FAIL"
        print(f"  [{mark}] {check_name:<20}: {info['detail']}")

    if res["violations"]:
        print("-" * 80)
        print("🚨 拦截与淘汰原因:")
        for v in res["violations"]:
            print(f"  • {v}")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Vet an AliExpress supplier against dropshipping hard gates.")
    parser.add_argument("--name", default="Golf Cart Seat Cover Set", help="Product title")
    parser.add_argument("--cost", type=float, required=True, help="Supplier cost in USD")
    parser.add_argument("--retail", type=float, default=0.0, help="Planned retail price in USD")
    parser.add_argument("--rating", type=float, required=True, help="Product rating (e.g. 4.8)")
    parser.add_argument("--orders", type=int, required=True, help="Total orders count (e.g. 480)")
    parser.add_argument("--store-rate", type=float, required=True, help="Store positive rate percentage (e.g. 96.8)")
    parser.add_argument("--store-years", type=int, required=True, help="Store age in years (e.g. 4)")
    parser.add_argument("--ships-to-us", action="store_true", default=True, help="Supports direct US shipping")
    parser.add_argument("--url", default="", help="AliExpress product URL")
    parser.add_argument("--store-url", default="", help="AliExpress store URL")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    data = {
        "name": args.name,
        "cost_usd": args.cost,
        "retail_price": args.retail,
        "rating": args.rating,
        "orders": args.orders,
        "store_positive_rate": args.store_rate,
        "store_years": args.store_years,
        "ships_to_us": args.ships_to_us,
        "url": args.url,
        "store_url": args.store_url
    }

    result = vet_supplier(data)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_card(result)

    sys.exit(0 if result["overall_pass"] else 2)

if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit Economics Calculator for Dropshipping Products (US Market).

Calculates Landed Cost, Pre-Ad Contribution Margin, Break-even CAC,
Target CAC, and Break-even ROAS based on realistic supplier and shipping rates.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import sys


@dataclass(frozen=True)
class UnitEconomicsResult:
    selling_price: float
    supplier_cost_usd: float
    actual_weight_g: float
    volumetric_weight_g: float
    billable_weight_g: float
    shipping_cost_usd: float
    packaging_cost_usd: float
    landed_cost_usd: float
    payment_fee_usd: float
    refund_reserve_usd: float
    pre_ad_contribution_margin: float
    margin_percentage: float
    break_even_cac: float
    target_cac_min: float
    target_cac_max: float
    break_even_roas: float
    is_qualified_hard_gate: bool
    rejection_reasons: list[str]


def calculate_shipping_cost(weight_g: float, l_cm: float = 0, w_cm: float = 0, h_cm: float = 0, has_battery_or_magnet: bool = False) -> tuple[float, float, float]:
    """Calculate US special line air parcel shipping cost in USD.

    Standard YunExpress / 4PX Special Line Rates (US):
    Base registration fee: 16 RMB ($2.25)
    First 100g: 22 RMB ($3.10)
    Additional 100g: 4.8 RMB ($0.68)
    Volumetric formula: (L * W * H) / 6000 (kg) -> in grams
    FX rate: 7.15 RMB = 1 USD
    """
    fx_rate = 7.15
    volumetric_weight_g = (l_cm * w_cm * h_cm / 6000.0) * 1000.0 if (l_cm and w_cm and h_cm) else 0.0
    billable_weight_g = max(weight_g, volumetric_weight_g)

    # Base pricing model: 22 RMB for first 100g + 4.8 RMB per additional 100g + 16 RMB reg fee
    if billable_weight_g <= 100:
        cost_rmb = 22.0 + 16.0
    else:
        additional_units = (billable_weight_g - 100) / 100.0
        cost_rmb = 22.0 + (additional_units * 4.8) + 16.0

    if has_battery_or_magnet:
        cost_rmb += (billable_weight_g / 1000.0) * 12.0  # Magnet / battery surcharge

    shipping_cost_usd = round(cost_rmb / fx_rate, 2)
    return round(volumetric_weight_g, 1), round(billable_weight_g, 1), shipping_cost_usd


def evaluate_unit_economics(
    selling_price: float,
    supplier_cost_usd: float,
    weight_g: float,
    l_cm: float = 0,
    w_cm: float = 0,
    h_cm: float = 0,
    packaging_usd: float = 2.0,
    payment_fee_pct: float = 0.029,
    payment_fee_fixed: float = 0.30,
    refund_rate_pct: float = 0.03,
    has_magnet: bool = False
) -> UnitEconomicsResult:
    """Evaluate full unit economics according to 25-rule constraints."""
    vol_weight, billable_weight, shipping_usd = calculate_shipping_cost(
        weight_g, l_cm, w_cm, h_cm, has_magnet
    )

    landed_cost = round(supplier_cost_usd + shipping_usd + packaging_usd, 2)
    payment_fee = round(selling_price * payment_fee_pct + payment_fee_fixed, 2)
    refund_reserve = round(selling_price * refund_rate_pct, 2)

    contribution_margin = round(
        selling_price - landed_cost - payment_fee - refund_reserve, 2
    )
    margin_pct = round((contribution_margin / selling_price) * 100, 1) if selling_price > 0 else 0.0

    break_even_cac = contribution_margin
    target_cac_min = round(contribution_margin * 0.48, 2)
    target_cac_max = round(contribution_margin * 0.56, 2)
    break_even_roas = round(selling_price / contribution_margin, 2) if contribution_margin > 0 else 999.0

    rejections: list[str] = []
    if selling_price < 60.0:
        rejections.append(f"Selling price ${selling_price:.2f} is below $60–$150 minimum threshold.")
    if contribution_margin < 35.0:
        rejections.append(f"Pre-ad Contribution Margin ${contribution_margin:.2f} is below $35 Hard Gate.")
    if billable_weight > 1800.0:
        rejections.append(f"Billable weight {billable_weight}g exceeds 1.8kg dropshipping optimal threshold.")

    is_qualified = len(rejections) == 0

    return UnitEconomicsResult(
        selling_price=selling_price,
        supplier_cost_usd=supplier_cost_usd,
        actual_weight_g=weight_g,
        volumetric_weight_g=vol_weight,
        billable_weight_g=billable_weight,
        shipping_cost_usd=shipping_usd,
        packaging_cost_usd=packaging_usd,
        landed_cost_usd=landed_cost,
        payment_fee_usd=payment_fee,
        refund_reserve_usd=refund_reserve,
        pre_ad_contribution_margin=contribution_margin,
        margin_percentage=margin_pct,
        break_even_cac=break_even_cac,
        target_cac_min=target_cac_min,
        target_cac_max=target_cac_max,
        break_even_roas=break_even_roas,
        is_qualified_hard_gate=is_qualified,
        rejection_reasons=rejections
    )


def format_markdown_table(res: UnitEconomicsResult) -> str:
    gate_status = "PASS (通过)" if res.is_qualified_hard_gate else "REJECT (未达标)"
    rejection_note = "无" if not res.rejection_reasons else "; ".join(res.rejection_reasons)

    return f"""### 【单位经济模型 (Unit Economics) 自动化测算结果】

| 指标项 | 测算数值 | 规范参考标准 |
| :--- | :--- | :--- |
| **建议售价 (Selling Price)** | **${res.selling_price:.2f}** | 优先 $60–$150，理想 $80–$150 |
| **采购成本 (Supplier Cost)** | **${res.supplier_cost_usd:.2f}** | 1688 现货盘 |
| **计费重量 (Billable Weight)** | **{res.billable_weight_g:.0f}g** (实重: {res.actual_weight_g:.0f}g, 抛重: {res.volumetric_weight_g:.0f}g) | 推荐 < 1,200g |
| **跨境空运专线运费** | **${res.shipping_cost_usd:.2f}** | 云途/4PX中美专线真实资费 |
| **包材与质检费** | **${res.packaging_cost_usd:.2f}** | 包含加厚气泡袋与配件 |
| **Estimated Landed Cost** | **${res.landed_cost_usd:.2f}** | 采购 + 运费 + 包材 |
| **支付网关手续费 (2.9%+$0.3)** | **${res.payment_fee_usd:.2f}** | Stripe/Shopify Payments |
| **预留退款储备金 (3.0%)** | **${res.refund_reserve_usd:.2f}** | 风险对冲基金 |
| **Pre-Ad 贡献毛利** | **${res.pre_ad_contribution_margin:.2f}** (毛利率: {res.margin_percentage:.1f}%) | **硬门禁 ≥ $35，理想 ≥ $50** |
| **Break-even CAC** | **${res.break_even_cac:.2f}** | 单客保本获客成本 |
| **Target CAC (目标获客成本)** | **${res.target_cac_min:.2f} – ${res.target_cac_max:.2f}** | 占贡献毛利的 48%–56% |
| **Break-even ROAS** | **{res.break_even_roas:.2f}** | 越低抗风险能力越强 (理想 < 1.8) |
| **Hard Gate 状态** | **{gate_status}** | {rejection_note} |
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Dropshipping Unit Economics Calculator")
    parser.add_argument("--price", type=float, required=True, help="Selling price in USD")
    parser.add_argument("--cost-usd", type=float, default=0.0, help="Supplier cost in USD")
    parser.add_argument("--cost-cny", type=float, default=0.0, help="Supplier cost in RMB (CNY)")
    parser.add_argument("--weight", type=float, required=True, help="Product actual weight in grams")
    parser.add_argument("--length", type=float, default=0.0, help="Package length in cm")
    parser.add_argument("--width", type=float, default=0.0, help="Package width in cm")
    parser.add_argument("--height", type=float, default=0.0, help="Package height in cm")
    parser.add_argument("--packaging", type=float, default=2.0, help="Packaging cost in USD")
    parser.add_argument("--refund-rate", type=float, default=0.03, help="Refund reserve rate (default 0.03)")
    parser.add_argument("--has-magnet", action="store_true", help="Has built-in magnets")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of markdown")

    args = parser.parse_args()

    supplier_cost = args.cost_usd
    if args.cost_cny > 0 and supplier_cost == 0.0:
        supplier_cost = round(args.cost_cny / 7.15, 2)

    res = evaluate_unit_economics(
        selling_price=args.price,
        supplier_cost_usd=supplier_cost,
        weight_g=args.weight,
        l_cm=args.length,
        w_cm=args.width,
        h_cm=args.height,
        packaging_usd=args.packaging,
        refund_rate_pct=args.refund_rate,
        has_magnet=args.has_magnet
    )

    if args.json:
        print(json.dumps(res.__dict__, ensure_ascii=False, indent=2))
    else:
        print(format_markdown_table(res))


if __name__ == "__main__":
    main()

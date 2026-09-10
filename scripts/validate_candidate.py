#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hard Gate Automated Assertion Validator for Dropshipping Niche Research.

Enforces machine-level validation of all 25-rule Hard Gates BEFORE an AI agent
is allowed to recommend any product to the user.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import sys


@dataclass(frozen=True)
class ValidationCheck:
    name: str
    passed: bool
    actual_value: str
    threshold: str
    failure_message: str


@dataclass(frozen=True)
class CandidateReport:
    product_name: str
    is_fully_qualified: bool
    overall_status: str
    checks: list[ValidationCheck]
    pre_ad_margin: float
    billable_weight_g: float
    selling_price: float


def run_hard_gate_validation(
    name: str,
    price: float,
    supplier_cost_usd: float,
    weight_g: float,
    length_cm: float,
    width_cm: float,
    height_cm: float,
    min_da: int,
    has_battery: bool,
    has_motor: bool,
    is_emergency: bool,
    has_patent_risk: bool,
    has_trademark_infringement: bool,
    refund_rate: float = 0.03
) -> CandidateReport:
    # 1. Volumetric weight calculation (L*W*H / 6000 kg -> grams)
    volumetric_weight_g = (length_cm * width_cm * height_cm / 6000.0) * 1000.0 if (length_cm and width_cm and height_cm) else 0.0
    billable_weight_g = max(weight_g, volumetric_weight_g)

    # 2. Shipping calculation (YunExpress / 4PX Special Line standard)
    fx_rate = 7.15
    if billable_weight_g <= 100:
        cost_rmb = 22.0 + 16.0
    else:
        additional_units = (billable_weight_g - 100) / 100.0
        cost_rmb = 22.0 + (additional_units * 4.8) + 16.0

    if has_battery:
        cost_rmb += (billable_weight_g / 1000.0) * 12.0

    shipping_usd = round(cost_rmb / fx_rate, 2)
    packaging_usd = 2.0
    landed_cost = round(supplier_cost_usd + shipping_usd + packaging_usd, 2)
    payment_fee = round(price * 0.029 + 0.30, 2)
    refund_reserve = round(price * refund_rate, 2)
    pre_ad_margin = round(price - landed_cost - payment_fee - refund_reserve, 2)

    checks: list[ValidationCheck] = []

    # Check 1: Selling Price
    price_ok = price >= 60.0
    checks.append(ValidationCheck(
        name="1. 建议零售价 (Selling Price)",
        passed=price_ok,
        actual_value=f"${price:.2f}",
        threshold="优先 $60–$150，理想 $80–$150",
        failure_message=f"售价 ${price:.2f} 低于 $60 底线，严禁作为独立 Hero Product！"
    ))

    # Check 2: Pre-Ad Contribution Margin (Hard Gate >= $50 ideal, >= $35 minimum)
    margin_ok = pre_ad_margin >= 50.0
    checks.append(ValidationCheck(
        name="2. 广告前贡献毛利 (Pre-Ad Margin)",
        passed=margin_ok,
        actual_value=f"${pre_ad_margin:.2f}",
        threshold="硬门禁 ≥ $35.00，理想标准 ≥ $50.00",
        failure_message=f"贡献毛利 ${pre_ad_margin:.2f} 低于理想门槛 $50.00，无法抵抗真实 CAC 波动！"
    ))

    # Check 3: Billable Weight / Dimensional Weight (No volumetric trap)
    weight_ok = billable_weight_g <= 1800.0 and (volumetric_weight_g <= 2500.0 if volumetric_weight_g > 0 else True)
    checks.append(ValidationCheck(
        name="3. 计费重量与抛重门禁 (Billable Weight)",
        passed=weight_ok,
        actual_value=f"{billable_weight_g:.0f}g (实重: {weight_g:.0f}g, 体积重: {volumetric_weight_g:.0f}g)",
        threshold="计费重量 ≤ 1,800g，严禁体积重超标 (抛重刺客)",
        failure_message=f"体积重高达 {volumetric_weight_g:.0f}g 严重超标，空运小包运费将吃光利润，必须海运海外仓或一票否决！"
    ))

    # Check 4: Electronic / Motor Failure Risk
    no_motor_ok = not has_motor
    checks.append(ValidationCheck(
        name="4. 电子与电机芯片故障率门禁",
        passed=no_motor_ok,
        actual_value="包含电机/芯片控制板" if has_motor else "纯机械/纯物理材料 (0% 电气故障)",
        threshold="严禁包含易损电机/芯片控制板 (售后故障率必须 < 2%)",
        failure_message="商品包含复杂微型电机与芯片，实际退货/故障率达 5%–8%，无美国仓退款不可逆！"
    ))

    # Check 5: Battery / Sensitive Cargo
    no_battery_ok = not has_battery
    checks.append(ValidationCheck(
        name="5. 敏感货与带电特货门禁",
        passed=no_battery_ok,
        actual_value="含锂电池 (特货专线)" if has_battery else "纯普货 (通关极速)",
        threshold="严禁包含锂电池特货通道 (普货优先)",
        failure_message="产品含内置锂电池，必须走敏感特货通道，运费增加且清关查验滞后风险高！"
    ))

    # Check 6: Emergency Timeline Mismatch
    no_emergency_ok = not is_emergency
    checks.append(ValidationCheck(
        name="6. 履约时效与买家心理匹配",
        passed=no_emergency_ok,
        actual_value="极端急救需求 (风暴断电/赶飞机)" if is_emergency else "计划性养护/自驾出行 (耐受 7–10 天)",
        threshold="必须为计划性消费，严禁急救型时效冲突品",
        failure_message="买家处于急救型刚需状态，与 7–10 天跨境小包时效冲突，将引发灾难性拒付 (Chargeback)！"
    ))

    # Check 7: Patent & Trademark Compliance
    ip_ok = (not has_patent_risk) and (not has_trademark_infringement)
    ip_desc = "合规安全 (指示性合理使用)"
    if has_patent_risk:
        ip_desc = "命中海外有效发明专利 (如 GenTent US8997769B2)"
    elif has_trademark_infringement:
        ip_desc = "涉及直接侵犯车企商标 (印 Logo / 7 孔格栅)"

    checks.append(ValidationCheck(
        name="7. 专利与商标侵权红线",
        passed=ip_ok,
        actual_value=ip_desc,
        threshold="0 侵权风险 (严禁假冒商标，严禁侵犯发明专利)",
        failure_message="商品命中高危发明专利或商标侵权红线，面临 Shopify/Stripe 永久封店冻资风险！"
    ))

    # Check 8: Google SERP DA < 30 Weak Competitor
    da_ok = min_da <= 30
    checks.append(ValidationCheck(
        name="8. Google 首页弱对手验证 (DA < 30)",
        passed=da_ok,
        actual_value=f"首页最低独立站 DA: {min_da}",
        threshold="Google 首页 Top 10 必须存在 DA < 30 的独立垂直小站",
        failure_message=f"Google 首页最低 DA 为 {min_da}，被巨头垄断且无 DA < 30 独立站立足空间，新站 SEO 无法突围！"
    ))

    failed_checks = [c for c in checks if not c.passed]
    is_fully_qualified = len(failed_checks) == 0
    overall_status = "PASS (全部硬门禁达标)" if is_fully_qualified else "FAIL [REJECT] (硬门禁拦截淘汰)"

    return CandidateReport(
        product_name=name,
        is_fully_qualified=is_fully_qualified,
        overall_status=overall_status,
        checks=checks,
        pre_ad_margin=pre_ad_margin,
        billable_weight_g=billable_weight_g,
        selling_price=price
    )


def format_validation_card(report: CandidateReport) -> str:
    status_emoji = "✅" if report.is_fully_qualified else "❌"
    lines = [
        f"```text",
        f"════════════════════════════════════════════════════════════════════════════════",
        f"【25条选品铁律 · 机器级 Hard Gate 强制断言校验卡】",
        f"候选产品名称: {report.product_name}",
        f"校验终局状态: {status_emoji} {report.overall_status}",
        f"建议零售售价: ${report.selling_price:.2f} | 测算广告前毛利: ${report.pre_ad_margin:.2f} | 计费重量: {report.billable_weight_g:.0f}g",
        f"────────────────────────────────────────────────────────────────────────────────"
    ]

    for c in report.checks:
        mark = "[PASS]  " if c.passed else "[REJECT]"
        lines.append(f"{mark} {c.name:<32} | 实测: {c.actual_value:<26} | 标准: {c.threshold}")
        if not c.passed:
            lines.append(f"         └── 拦截原因: {c.failure_message}")

    lines.append(f"════════════════════════════════════════════════════════════════════════════════")
    lines.append(f"```")

    if not report.is_fully_qualified:
        lines.append(f"\n> ⚠️ **风控引擎警告**：该产品在【机器级 Hard Gate】阶段已被一票否决淘汰，禁止作为推荐 Hero Product 输出！")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dropship Niche Hard Gate Validator")
    parser.add_argument("--name", type=str, required=True, help="Product candidate name")
    parser.add_argument("--price", type=float, required=True, help="Target selling price in USD")
    parser.add_argument("--cost-usd", type=float, default=0.0, help="Supplier cost in USD")
    parser.add_argument("--cost-cny", type=float, default=0.0, help="Supplier cost in CNY/RMB")
    parser.add_argument("--weight", type=float, required=True, help="Actual weight in grams")
    parser.add_argument("--length", type=float, default=0.0, help="Package length in cm")
    parser.add_argument("--width", type=float, default=0.0, help="Package width in cm")
    parser.add_argument("--height", type=float, default=0.0, help="Package height in cm")
    parser.add_argument("--min-da", type=int, required=True, help="Lowest DA among independent stores on Google Top 10")
    parser.add_argument("--has-battery", action="store_true", help="Contains battery")
    parser.add_argument("--has-motor", action="store_true", help="Contains electric motor or circuit board")
    parser.add_argument("--is-emergency", action="store_true", help="Emergency / deadline purchase")
    parser.add_argument("--patent-risk", action="store_true", help="Has patent risk")
    parser.add_argument("--trademark-risk", action="store_true", help="Has trademark infringement risk")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    supplier_cost = args.cost_usd
    if args.cost_cny > 0 and supplier_cost == 0.0:
        supplier_cost = round(args.cost_cny / 7.15, 2)

    report = run_hard_gate_validation(
        name=args.name,
        price=args.price,
        supplier_cost_usd=supplier_cost,
        weight_g=args.weight,
        length_cm=args.length,
        width_cm=args.width,
        height_cm=args.height,
        min_da=args.min_da,
        has_battery=args.has_battery,
        has_motor=args.has_motor,
        is_emergency=args.is_emergency,
        has_patent_risk=args.patent_risk,
        has_trademark_infringement=args.trademark_risk
    )

    if args.json:
        dict_data = {
            "product_name": report.product_name,
            "is_fully_qualified": report.is_fully_qualified,
            "overall_status": report.overall_status,
            "pre_ad_margin": report.pre_ad_margin,
            "billable_weight_g": report.billable_weight_g,
            "checks": [c.__dict__ for c in report.checks]
        }
        print(json.dumps(dict_data, ensure_ascii=False, indent=2))
    else:
        print(format_validation_card(report))

    if not report.is_fully_qualified:
        sys.exit(2)  # Return non-zero exit code on failure to block the pipeline!


if __name__ == "__main__":
    main()

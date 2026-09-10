# Dropship Niche Scout (跨境独立站选品与商业模型评估 Skill)

> **专为 Claude Code / AI Agent 打造的确定性 Dropshipping Niche 选词与选品评估工作流。**
> 严格基于 25 条选品铁律，强制杜绝 AI 偷懒、漂移与放水，实现“先淘汰、再抓数、查权重、算利润、定生死”的闭环调研。

---

## 🌟 核心特性与硬门禁

1. **Hard Gate 机器级一票否决**：
   - 自动排查海外发明专利（如 GenTent 专利 US8997769B2 等）；
   - 坚决一票否决电气安全、排气高温起火、高危人身责任与急救型时效冲突品；
   - 广告前贡献毛利低于 $35 直接 Reject，牢牢守住中高客单（$80–$150）与毛利（≥ $50）底线。
2. **强制 Google SERP 首页 Top 10 真实 DA 权重切片**：
   - 杜绝“只看工具 SD 评分”的虚假蓝海陷阱；
   - 必须通过 Ubersuggest `serp_analysis` 逐站抓取 Google 首页真实 Domain Authority (DA)；
   - 必须确认存在 DA < 30 的垂直独立站/Shopify 小店，才允许评定为可行 Niche。
3. **真实单位经济模型测算 (Unit Economics)**：
   - 采购价、国际专线小包运费、包装杂费、支付手续费、预留退款全链路核算；
   - 自动计算 Break-even CAC、Target CAC 和 Break-even ROAS。
4. **标准化输出交付（Section 21 全量大表 + Section 22 四大灵魂拷问）**：
   - 23 项全量指标横向底表；
   - 强制回答：“值不值得卖”、“为什么买我不买亚马逊”、“能承受多少 CAC”、“最可能怎么死”。
5. **云端无缝同步（Tencent Docs / Cloud Sync）**：
   - 内置腾讯在线云文档（docs.qq.com）一键秒级同步能力，将调研资产沉淀为云端知识库。

---

## 🚀 安装与使用

### 安装到 Claude Code

克隆或下载到你的本地 Claude Code Skills 目录：

```bash
git clone https://github.com/hanshan0228/dropship-niche-scout.git ~/.claude/skills/dropship-niche-scout
```

### 在会话中触发调用

在 Claude Code 终端对话框中，你可以通过以下方式随时激活该技能：

```text
/dropship-niche-scout "golf cart accessories"
```

或者自然语言触发：
* “用选品 SOP 评估一下这个词：`jeep tire covers`”
* “帮我深度调研一下这个 Niche，并跑一下 Ubersuggest 数据和 SERP 权重”

---

## 📋 23 项全量评估指标清单

| 维度 | 指标项 | 说明 |
| :--- | :--- | :--- |
| **需求面** | Product, Search Volume, Keyword Cluster, SD, CPC, Intent | 依托 Ubersuggest 官方接口提取 Google US 数据 |
| **竞争面** | Top10 Lowest DA, Brand Dependence | 提取首页最低 DA，评估品牌依赖度 (1–5分) |
| **财务面** | Typical Retail Price, Supplier Cost, Landed Cost, Selling Price, Contribution Margin, Break-even CAC, Target CAC, Break-even ROAS | 严格遵守售价 $80–$150、毛利 ≥ $50 门槛 |
| **履约面** | Return Risk, Shipping Risk | 包装重量、抛重、易碎性、无理由退货率预估 |
| **渠道面** | SEO Score, Google Ads Score, Meta Score | 各渠道获客潜力拆解 (0–10分) |
| **综合面** | Opportunity Score, Confidence Score, 最终分类 | 商业价值与置信度双分，给出 Hero / Upsell / Reject 定性 |

---

## 🛠️ 配套前置依赖

* **Ubersuggest MCP Server**：用于调取 Google US 官方关键词指标与 SERP 首页竞争分析；
* **Tencent Docs MCP Server (可选)**：用于将报告一键写入腾讯在线文档。

---

## 📄 开源许可证

MIT License © 2026 hanshan0228

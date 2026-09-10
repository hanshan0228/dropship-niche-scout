---
name: dropship-niche-scout
description: 严格基于 25 条选品铁律的跨境独立站 Dropshipping Niche 选词与商业模型深度评估工作流。强制执行 Hard Gate 淘汰、Ubersuggest 数据抓取、Google 首页 Top 10 DA 权重核查、单位经济模型测算与标准化输出。
---

# Dropshipping Niche & Product Research (SOP)

本技能用于帮助用户寻找、验证和筛选适合美国市场的 Dropshipping Niche、Hero Product 和配套产品线。
**终极目标**：不是寻找“搜索量最大”或“毛利率最高”的商品，而是寻找 **Risk-Adjusted Expected Profit（风险调整后预期利润）最高的商业机会**。

---

## 核心工作流管线（七步硬门禁）

```
[输入 Niche / 关键词]
       │
       ▼
【Step 1：Hard Gate 淘汰机】──────> 命中任何红线？ ──> [直接 REJECT，输出原因并终止]
       │ (未命中，通过门禁)
       ▼
【Step 2：Ubersuggest 关键词与集群大盘提取】
       │ (调用 keyword_overview / keyword_suggestions)
       ▼
【Step 3：强制 SERP 首页 Top 10 真实 DA 权重核验】──> 首页全是 DA>60 巨头？ ──> [降级/REJECT]
       │ (调用 serp_analysis，必须确认存在 DA < 30 独立站)
       ▼
【Step 4：单位经济模型测算 (Unit Economics)】
       │ (测算 Landed Cost、Pre-Ad Contribution Margin ≥ $50、Break-even CAC)
       ▼
【Step 5：100 分固定模型评分 & 机会/置信度双分】
       │
       ▼
【Step 6：Section 21 全量 23 项指标底表输出】
       │
       ▼
【Step 7：Section 22 必须回答的 4 大灵魂拷问】
       │
       ▼
【可选：一键同步腾讯文档云端】
```

---

## 详细执行规范

### 1. 默认商业模型约束
* **市场**：美国 (US, Location Code: 2840)
* **平台**：Shopify 独立站
* **模式**：Dropshipping（纯轻量纺织/结构件一件代发，优先空运专线小包时效 7–10 天）
* **获客**：Google SEO + Google Shopping 为核心主力，Meta Ads / TikTok 辅助
* **转化载体**：必须配合站内专属**选型计算器 (The Killer Sizer / Calculator)** 消解买家尺寸焦虑
* **品牌依赖度**：必须极低 (Brand Dependence ≤ 2–3 / 5，Category Search > Brand Search)

### 2. 价格与利润刚性门槛
* **优先零售价**：**$60 – $150**，理想 **$80 – $150**，理想 AOV **≥ $100**；
* 低于 $30 的商品**严禁作为 Hero Product**（仅可作为 Order Bump / 加购品）；
* **广告前贡献毛利 (Pre-Ad Contribution Margin)**：**< $35 默认直接 REJECT**，理想标准 **≥ $50**！

### 3. Step 1: Hard Gate 先淘汰，再评分（一票否决项）
出现以下任何一种情况，**必须直接标记为 REJECT 或严重降级**，严禁推荐：
1. **产品责任过高**：涉及 Crash protection、Automotive restraint、医疗宣称、电气安全、高压设备、排气高温起火、一氧化碳风险；
2. **专利侵权风险**：拥有海外有效发明专利（如 GenTent 发电机罩专利 US8997769B2），白牌易被投诉封店；
3. **商标假冒侵权**：产品表面印有车企注册商标（如直接印 JEEP 字母、官方 Logo、7 孔格栅）；
4. **物流不合理**：超长抛重 (长>50cm)、易碎、超重 (>1.5kg)、复杂组装；
5. **履约时效冲突**：极端急救型场景（暴雪断电、赶飞机），与 7–10 天跨境物流冲突导致高拒付；
6. **Fit/Size 风险过高**：服装鞋帽、宠物衣服等高退货尺码件。

### 4. Step 2 & 3: Ubersuggest 与 Google SERP 真实 DA 检验协议
必须调用 Ubersuggest MCP 工具进行实测，严禁主观编造数据：
1. **数据抓取**：
   * `mcp__ubersuggest__keyword_overview`（提取月搜索量、12个月走势、CPC、SD 难度、搜索意图）；
   * `mcp__ubersuggest__keyword_suggestions`（提取整个 Topic Cluster 总池）；
2. **强制执行 SERP 首页 Top 10 真实 DA 解剖**：
   * **必须调用 `mcp__ubersuggest__serp_analysis`**；
   * 重点筛查 Google 首页前 10–15 名站点的 **Domain Authority (DA)**；
   * **刚性门禁**：必须在 Top 10 中找到 **DA < 30（理想 DA 4–20）的垂直独立站/Shopify 小店**；
   * 如果首页全被 Amazon (DA 95)、Home Depot (DA 90)、Walmart (DA 92) 等巨头垄断且无独立站空间，必须明显扣除 SEO 分数或降级！

### 5. Step 4: 单位经济模型计算公式
* **Estimated Landed Cost** = 1688采购价 + 专线小包运费(约$6–$12) + 包装辅料($2)；
* **Pre-Ad Contribution Margin** = 零售价 − Landed Cost − 支付手续费(约3%) − 预留退款储备(约3%)；
* **Break-even CAC** = Pre-Ad Contribution Margin；
* **Target CAC** = 50% – 60% of Pre-Ad Contribution Margin；
* **Break-even ROAS** = 零售价 ÷ Pre-Ad Contribution Margin。

### 6. Step 5: 100 分固定评分体系与双分制
* **A. Unit Economics (30分)**：售价、毛利厚度、Target CAC 空间、Break-even ROAS；
* **B. Demand & Intent (15分)**：月搜索量、集群规模、Transactional 意图占比；
* **C. Brand Independence (15分)**：品牌依赖度（1分极低，5分极高，越低分越高）；
* **D. SEO Opportunity (10分)**：SD 难度、Top 10 最低 DA、弱对手数量；
* **E. Paid Ads Potential (10分)**：Google Shopping 转化度、Meta 短视频视觉冲击力；
* **F. Fulfillment (10分)**：包裹实重、抽真空体积、1688 现货可得性；
* **G. Return / Liability Risk (5分)**：退货率预估、零法律专利人身责任；
* **H. Differentiation & Expansion (5分)**：是否容易被比价、横向配件连带潜力。
* **双分输出**：
  * **Opportunity Score (0–100)**：商业机会价值；
  * **Confidence Score (0–100)**：当前数据与供应链的确实程度。

---

## 交付规范与输出模板（严格执行）

每次调研完成，**必须输出完整的 Section 21 表格与 Section 22 四大问题**：

### 【Section 21: 23 项指标全量底表】

| Metric | Result | Evidence Level (Confirmed/Estimated/Unknown) |
| :--- | :--- | :--- |
| **Product** | [产品英文及中文全称] | Confirmed |
| **Search Volume** | [核心词月搜 + 旺季走势] | Confirmed (Ubersuggest) |
| **Keyword Cluster** | [核心词集群列表与总搜索池] | Confirmed (Ubersuggest) |
| **SD (SEO Difficulty)** | [数值与评级] | Confirmed (Ubersuggest) |
| **CPC** | [美元金额] | Confirmed (Ubersuggest) |
| **Intent** | [Transactional / Commercial / Informational] | Confirmed (Ubersuggest) |
| **Top10 Lowest DA** | [列出排名前列的 DA < 30 独立站及域名] | Confirmed (SERP Analysis) |
| **Typical Retail Price** | [市场常规售价区间] | Confirmed |
| **Supplier Cost** | [1688 采购成本] | Estimated (1688) |
| **Estimated Landed Cost** | [采购 + 专线小包运费 + 包装] | Estimated |
| **Selling Price** | [独立站建议售价，需符合 $80–$150] | Planned |
| **Contribution Margin** | [单单净毛利，必须 ≥ $50] | Estimated |
| **Break-even CAC** | [保本获客成本] | Calculated |
| **Target CAC** | [目标获客成本，毛利的 50% 左右] | Target |
| **Break-even ROAS** | [保本 ROAS] | Calculated |
| **Brand Dependence** | [1–5 分评分，理想 ≤ 2] | Evaluated |
| **Return Risk** | [预估退货率及主要退货原因] | Estimated |
| **Shipping Risk** | [包裹重量、抛重、损坏风险] | Estimated |
| **SEO Score (0-10)** | [得分] | Calculated |
| **Google Ads Score (0-10)**| [得分] | Calculated |
| **Meta Score (0-10)** | [得分] | Calculated |
| **Opportunity Score (0-100)**| [得分] | Evaluated |
| **Confidence Score (0-100)** | [得分] | Evaluated |
| **最终分类** | [Hero Product / Secondary / Upsell / Reject] | Approved |

### 【Section 22: 四大必须回答的核心灵魂拷问】
1. **值不值得卖？**（Yes / No / Conditional，给出清晰理由）；
2. **为什么消费者会买我的，而不是 Amazon 或成熟品牌？**（阐述选型计算器、专车定制保证或功能痛点差异化）；
3. **一个客户最多能承受多少 CAC？**（精确量化 Break-even CAC 与 Target CAC）；
4. **如果测试失败，最可能为什么失败？**（列出最主要的死亡风险点，如季节断崖、素材跑不出、客群太窄等）。

---
name: dropship-niche-scout
description: 工业级跨境独立站 Dropshipping Niche 选词与商业模型深度评估工作流 (V2.0)。基于 25 条选品铁律，支持四大敏捷模式（单品全面评估 eval、长尾集群挖掘 cluster、双品对决 vs、腾讯文档秒级同步 sync）。强制执行 Hard Gate 黑名单、Ubersuggest 数据抓取、Google 首页 Top 10 DA 切片、Python 确定性财务测算与标准 23 项大表输出。
---

# Dropshipping Niche Scout (V2.0 工业级选品引擎)

本技能帮助用户寻找、验证和筛选适合美国市场的 Dropshipping Niche、Hero Product 和配套产品线。
**终极目标**：寻找 **Risk-Adjusted Expected Profit（风险调整后预期利润）最高的商业机会**。

---

## 🚀 四大指令路由 (Sub-Commands)

用户可通过以下指令模式触发精准工作流：

| 指令格式 | 模式定位 | 执行逻辑与交付目标 |
| :--- | :--- | :--- |
| `/dropship-niche-scout eval <关键词>` | **单品深度评估 (默认)** | 严格执行 Hard Gate、Ubersuggest 数据与 SERP 首页 Top 10 DA 分析，调用 Python 脚本测算财务，输出 Section 21 的 23 项全量大表与 Section 22 四大灵魂拷问。 |
| `/dropship-niche-scout cluster <大词>` | **长尾集群挖掘** | 挖掘大词下的流量金字塔（塔尖大盘词、核心爆品池、品牌专区词、新势力长尾暴利词），测算整体 Topic Addressable Market。 |
| `/dropship-niche-scout vs <词A> <词B>` | **双品生死对决** | 将两个候选品放在 8 维生死天平（SEO难度、首页弱对手、客单价、毛利厚度、合规风险、退货率、社媒广告潜力、物流）进行横向对比，给出最终一票投给谁。 |
| `/dropship-niche-scout supplier <关键词>` | **速卖通优质货源精筛** | 联动速卖通 MCP 与 `filter_suppliers.py`，按店铺好评率 ≥ 96%、年限 ≥ 2年、商品评分 ≥ 4.7★、销量 > 100单严格过滤（不设价格死线，按动态毛利核算），直接交付高分货源链接卡片。 |
| `/dropship-niche-scout spy-store <域名/网址>` | **竞品独立站深度扒取** | 调用 `scripts/spy_store.py` (基于 shopify-spy)，一键提取竞品 Shopify 独立站全部在售商品、真实价格带、变体数、上架日期与爆款商品链接。 |
| `/dropship-niche-scout spy-ads <关键词/主页>` | **Meta 社媒广告间谍** | 调用 `scripts/spy_ads.py` (基于 meta-ads-collector)，无需 API Key 逆向抓取竞品在 Facebook/Instagram 上正在投放的真实广告文案钩子、视频图片形式与在投天数。 |
| `/dropship-niche-scout web` | **可视化网页控制台** | 运行 `web_app.py` 启动本地选品作战看板 (http://127.0.0.1:8088)，支持滑块联动测算毛利、竞品图片瀑布流浏览与广告文案视觉化比对。 |
| `/dropship-niche-scout sync <文档标题>` | **腾讯文档云端同步** | 调用内置的 Python 脚本，避开 Windows 命令行长度限制，将本轮调研报告毫秒级推送到腾讯在线文档 (docs.qq.com)。 |

---

## 🛠️ 核心管线与四大不可逾越的硬门禁

### 【门禁一：Step 1 强制执行 Python 机器级断言校验 (validate_candidate.py)】
在向用户推荐任何产品前，**严禁凭直觉或口头推荐！必须先在后台静默运行验证脚本**：
```bash
python C:\Users\hanzhe1\.claude\skills\dropship-niche-scout\scripts\validate_candidate.py \
  --name "<候选品名称>" \
  --price <售价> \
  --cost-cny <1688成本> \
  --weight <克重> \
  --length <长cm> --width <宽cm> --height <高cm> \
  --min-da <首页最低DA>
```
* **一票否决铁律**：如果脚本返回 `FAIL [REJECT]`（退出码 2），**物理禁止作为合格 Hero Product 推荐**！必须直接输出拦截原因向用户如实汇报；
* 每次正式推荐，**必须在回复开头附带脚本生成的【Hard Gate 机器级自检卡】**。

### 【门禁二：Step 2 先对照黑名单淘汰，再评分】
必须查阅 `references/blacklist.md`：
1. **海外发明专利**：凡命中类似 GenTent (US8997769B2) 等发明专利者，直接 REJECT；
2. **商标假冒侵权**：产品表面印车标（如印 JEEP、7 孔格栅、Ford 徽标）者，直接 REJECT；
3. **高危法律责任**：涉及碰撞安全约束、电气火灾、高温起火、医疗宣称者，直接 REJECT；
4. **时效冲突品**：风暴断电急用、赶飞机急用等极端急救品，与 7–10 天跨境物流冲突导致高拒付者，直接 REJECT；
5. **利润门槛**：广告前贡献毛利 **< $35 默认 REJECT**，理想标准 **≥ $50**！

### 【门禁三：Step 3 强制 SERP 首页 Top 10 真实 DA 解剖】
严禁只看 Ubersuggest 的宏观 SD 评分：
1. 必须调用 `mcp__ubersuggest__serp_analysis` 逐站抓取 Google 首页前 10–15 名站点的 **Domain Authority (DA)**；
2. **刚性门禁**：必须在 Top 10 中找到 **DA < 30（理想 DA 4–20）的垂直独立站/Shopify 小店**；
3. 若首页被 Amazon、Home Depot、Walmart 等 DA 90+ 巨头封死且无独立站空间，必须降低评级！

### 【门禁四：Step 4 强制调用 Python 脚本核算财务（拒绝口算）】
严禁在对话中估算或口算运费与毛利：
* **必须查阅 `references/shipping_rates.md` 获取真实克重**；
* **必须在后台运行脚本测算**：
  ```bash
  python C:\Users\hanzhe1\.claude\skills\dropship-niche-scout\scripts\calc_economics.py --price <售价> --cost-cny <1688采购价> --weight <克重>
  ```
* 严格按照脚本返回的精确数值填入交付表格。

### 【门禁五：Step 5 速卖通优质货源硬门禁 (filter_suppliers.py)】
> 详见底层标准：`references/supplier_vetting_standards.md`

当向用户推荐任何速卖通具体货源或跑 `/dropship-niche-scout supplier` 时，**严禁口头推荐！必须先在后台运行校验脚本**：
```bash
python C:\Users\hanzhe1\.claude\skills\dropship-niche-scout\scripts\filter_suppliers.py \
  --name "<商品名称>" \
  --cost <拿货价USD> \
  --retail <建议售价USD> \
  --rating <商品评分> \
  --orders <总出单量> \
  --store-rate <店铺好评率> \
  --store-years <开店年限> \
  --url "<商品链接>"
```
* **一票否决指标**：
  1. **店铺好评率**：必须 **≥ 96.0%**（低于 96% 直接 REJECT）；
  2. **开店时间**：必须 **≥ 2 年**（新店直接 REJECT，杜绝跑路）；
  3. **商品评分**：必须 **≥ 4.7★**（低于 4.7 直接 REJECT，防止售后退款率爆表）；
  4. **历史出单**：必须 **> 100 单**（未验证模具直接淘汰）；
  5. **直发美国**：必须支持全程带号追踪直发美国；
  6. **价格与利润准则（核心：不设价格死线，按动态毛利核算）**：
     - **绝不在进货价端设置机械死线**（无论 $10 还是 $80 均可）；
     - 只要独立站终端售价测算出的 **广告前贡献毛利 (Pre-Ad Margin) ≥ $35.00 (理想 ≥ $50.00)** 即可判定达标！
* 若脚本返回 `FAIL [REJECT]`，物理禁止作为合格货源向用户交付！必须向用户输出拦截原因。

---

## 📋 标准化交付模板 (严格执行)

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
| **Estimated Landed Cost** | [采购 + 专线小包运费 + 包装] | Calculated (Python Script) |
| **Selling Price** | [独立站建议售价，需符合 $80–$150] | Planned |
| **Contribution Margin** | [单单净毛利，必须 ≥ $50] | Calculated (Python Script) |
| **Break-even CAC** | [保本获客成本] | Calculated (Python Script) |
| **Target CAC** | [目标获客成本，毛利的 50% 左右] | Target |
| **Break-even ROAS** | [保本 ROAS] | Calculated (Python Script) |
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
2. **为什么消费者会买我的，而不是 Amazon 或成熟品牌？**（对照 `references/calculator_logic.md` 说明专车选型计算器与 100% 贴合保证）；
3. **一个客户最多能承受多少 CAC？**（量化 Break-even CAC 与 Target CAC）；
4. **如果测试失败，最可能为什么失败？**（列出最主要的死亡风险点）。

---

## ☁️ 云端同步流程 (Sync to Tencent Docs)

当用户输入 `/dropship-niche-scout sync` 或要求同步到腾讯文档时：
1. 将当前生成的 Markdown 调研内容暂存为本地临时文件；
2. 执行内置直连脚本（自动获取本地已配置的 Token 并突破命令行限制）：
   ```bash
   python C:\Users\hanzhe1\.claude\skills\dropship-niche-scout\scripts\sync_tencent_docs.py --title "<文档标题>" --file "<临时文件路径>"
   ```
3. 提取返回的 `url`，直接将在线文档链接交付给用户。

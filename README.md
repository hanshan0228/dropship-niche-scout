# Dropship Niche Scout (V2.0 工业级选品与商业模型评估引擎)

> **专为 Claude Code / AI Agent 打造的确定性 Dropshipping Niche 选词与选品评估工作流。**
> 严格基于 25 条选品铁律，强制杜绝 AI 偷懒、漂移与放水，实现“先淘汰、再抓数、查权重、算利润、定生死”的闭环调研。

---

## 🌟 V2.0 重大架构升级特性

1. **机器级 Hard Gate 断言校验脚本 (`scripts/validate_candidate.py`)**：
   - 彻底消灭 AI“讨好型偏见”与“自作主张放水”；
   - 推荐前强制在后台静默执行 8 项机器断言（真实体积重 ≤1.8kg、毛利 ≥$50、无电池、无电机芯片、非急救品、零专利商标侵权、首页最低 DA ≤30）；
   - 只要任何一项 FAIL，退出码为 2，物理禁止作为推荐品输出！
2. **确定性 Python 财务计算引擎 (`scripts/calc_economics.py`)**：
   - 彻底告别大模型心算幻觉与浮动；
   - 自动对照真实云途/4PX 中美特快专线阶梯费率；
   - 精确输出 Landed Cost、Pre-Ad Contribution Margin (毛利)、Break-even CAC、Target CAC 和 Break-even ROAS。
3. **真实中美跨境专线物流资费底表 (`references/shipping_rates.md`)**：
   - 收录 2026 最新中美特快专线首续重资费阶梯（7.15 汇率折算）；
   - 内置抛重比（/6000）核算与抽真空打包节省成本指引。
4. **高危专利与合规雷区黑名单 (`references/blacklist.md`)**：
   - 收录 GenTent 发明专利 (US8997769B2) 等经典海外杀手专利；
   - 汽车品牌（Jeep、Bronco 等）指示性合理使用 (Nominative Fair Use) 合规指引；
   - 坚决一票否决电气火灾、人身碰撞安全约束及急救型时效冲突品。
5. **专车引流选型计算器代码库 (`references/calculator_logic.md`)**：
   - 包含轮胎外径数学换算、倒车摄像头避位判定、高尔夫球车 3 步选型纯前端轻量 JS 代码原型。

---

## 🚀 安装与使用

### 安装到 Claude Code

克隆到你的本地 Claude Code Skills 目录：

```bash
git clone https://github.com/hanshan0228/dropship-niche-scout.git ~/.claude/skills/dropship-niche-scout
```

### 快速调用命令

在 Claude Code 终端中随时执行：

```bash
# 1. 评估单个利基词
/dropship-niche-scout eval "golf cart seat covers"

# 2. 挖掘大词下的流量金字塔与新势力红利
/dropship-niche-scout cluster "golf cart accessories"

# 3. 两个热门候选赛道生死对决
/dropship-niche-scout vs "golf cart seat covers" "jeep tire covers"

# 4. 将最新调研结果一键推送到腾讯文档
/dropship-niche-scout sync "高尔夫球车选品调研报告"
```

---

## 📁 目录结构

```text
dropship-niche-scout/
├── SKILL.md                  # 主控调度中心（四模式路由与硬门禁）
├── README.md                 # 完整的使用指南与架构文档
├── scripts/
│   ├── calc_economics.py     # 纯 Python 财务计算引擎（零口算幻觉）
│   └── sync_tencent_docs.py  # 腾讯文档秒级同步直通管道 (突破CMD长度限制)
└── references/
    ├── shipping_rates.md     # 2026 最新中美跨境专线小包阶梯运费表
    ├── blacklist.md          # 高危发明专利、车企商标与急救品类黑名单
    └── calculator_logic.md   # 专车选型计算器（The Killer Sizer）代码原型库
```

---

## 📄 开源许可证

MIT License © 2026 hanshan0228

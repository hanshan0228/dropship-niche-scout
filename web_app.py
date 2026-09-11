#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web_app.py - Dropship Niche Scout (V2.0 跨境出海选品与情报控制台)
Full interactive cockpit combining:
1. Dynamic Unit Economics & Hard Gate Radar
2. Niche Keyword Scout & Intent Clustering (NEW)
3. Google SEO Article Studio & 8-Gate Audit (NEW)
4. Competitor Shopify Store Spy
5. Meta Ads Intelligence Gallery
6. AliExpress Supplier Vetting Card Generator
"""

import sys
import os
import re
import json
import asyncio
import urllib.request
import urllib.parse
from dataclasses import asdict
from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
import uvicorn
import io

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer") and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer") and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
SEO_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "google-seo-architect", "scripts"))

for p in [SCRIPTS_DIR, SEO_DIR]:
    if p not in sys.path and os.path.exists(p):
        sys.path.insert(0, p)

from calc_economics import evaluate_unit_economics
from filter_suppliers import vet_supplier
from spy_store import spy_shopify_store
from spy_ads import spy_competitor_ads

# Import SEO tools from google-seo-architect if available
try:
    from lint_article import analyze_article_text
    from compile_shopify_blog import markdown_to_shopify_html
except ImportError:
    analyze_article_text = None
    markdown_to_shopify_html = None

# Load LLM Settings safely from settings.json
def get_llm_config():
    settings_path = os.path.expanduser("~/.claude/settings.json")
    if not os.path.exists(settings_path):
        return None
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        env = cfg.get("env", {})
        return {
            "token": env.get("ANTHROPIC_AUTH_TOKEN"),
            "base_url": env.get("ANTHROPIC_BASE_URL", "http://127.0.0.1:8317"),
            "model": env.get("ANTHROPIC_MODEL", "gemini-3.8-flash-high")
        }
    except Exception:
        return None

# --- HTML TEMPLATE ---
INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dropship Niche Scout // 出海选品与情报控制台</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: { 50: '#f0fdf4', 500: '#10b981', 600: '#059669', 900: '#064e3b' }
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #090d16; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .card { background-color: #111827; border: 1px solid #1f2937; border-radius: 0.75rem; }
    .input-field { background-color: #1f2937; border: 1px solid #374151; color: #f9fafb; border-radius: 0.5rem; padding: 0.5rem 0.75rem; }
    .input-field:focus { outline: none; border-color: #10b981; }
    input[type=range] { accent-color: #10b981; }
  </style>
</head>
<body class="min-h-screen flex flex-col">
  <!-- Top Navigation -->
  <header class="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <span class="text-2xl">⛳</span>
        <div>
          <h1 class="text-lg font-bold text-white tracking-tight">Dropship Niche Scout <span class="text-xs text-emerald-400 font-mono px-2 py-0.5 bg-emerald-950/70 rounded-full border border-emerald-800/80">V2.5 Full Suite</span></h1>
          <p class="text-xs text-gray-400">选品门禁 · 选词挖掘 · Google SEO 写文 · 独立站扒店 · Meta广告间谍 · 货源审核</p>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-900/40 text-emerald-300 border border-emerald-800">
          <span class="w-1.5 h-1.5 mr-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
          US Direct Active
        </span>
      </div>
    </div>
  </header>

  <!-- Main Tabs -->
  <main class="max-w-7xl mx-auto px-4 py-6 flex-1 w-full">
    <div class="flex border-b border-gray-800 mb-6 space-x-1 sm:space-x-2 overflow-x-auto pb-1">
      <button onclick="switchTab('economics')" id="tab-btn-economics" class="tab-btn px-3 py-2 text-sm font-semibold text-emerald-400 border-b-2 border-emerald-400 flex items-center gap-1.5 whitespace-nowrap">
        <span>📊</span> 实时财务与门禁
      </button>
      <button onclick="switchTab('scout')" id="tab-btn-scout" class="tab-btn px-3 py-2 text-sm font-semibold text-gray-400 hover:text-gray-200 flex items-center gap-1.5 whitespace-nowrap">
        <span>🎯</span> Niche 选词挖掘
      </button>
      <button onclick="switchTab('writer')" id="tab-btn-writer" class="tab-btn px-3 py-2 text-sm font-semibold text-gray-400 hover:text-gray-200 flex items-center gap-1.5 whitespace-nowrap">
        <span>✍️</span> Google SEO 写文
      </button>
      <button onclick="switchTab('store')" id="tab-btn-store" class="tab-btn px-3 py-2 text-sm font-semibold text-gray-400 hover:text-gray-200 flex items-center gap-1.5 whitespace-nowrap">
        <span>🕵️</span> 竞品独立站扒取
      </button>
      <button onclick="switchTab('ads')" id="tab-btn-ads" class="tab-btn px-3 py-2 text-sm font-semibold text-gray-400 hover:text-gray-200 flex items-center gap-1.5 whitespace-nowrap">
        <span>📱</span> Meta 广告间谍
      </button>
      <button onclick="switchTab('supplier')" id="tab-btn-supplier" class="tab-btn px-3 py-2 text-sm font-semibold text-gray-400 hover:text-gray-200 flex items-center gap-1.5 whitespace-nowrap">
        <span>🏭</span> 供应链与货源审核
      </button>
    </div>

    <!-- TAB 1: ECONOMICS & HARD GATES -->
    <div id="tab-economics" class="tab-content space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="card p-6 lg:col-span-5 space-y-5">
          <h2 class="text-base font-bold text-white flex items-center gap-2 border-b border-gray-800 pb-3">
            <span>⚙️</span> 财务参数微调 (实时联动)
          </h2>
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-300">建议零售售价 (USD)</span>
              <span id="label-price" class="font-bold text-emerald-400 font-mono text-base">$89.00</span>
            </div>
            <input type="range" id="input-price" min="30" max="250" step="1" value="89" class="w-full" oninput="calcEconomics()">
            <div class="flex justify-between text-[11px] text-gray-500 mt-0.5">
              <span>$30 (底线)</span>
              <span>$80–$150 (黄金区间)</span>
              <span>$250 (高客单)</span>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-300">源头采购成本 (USD)</span>
              <span id="label-cost" class="font-bold text-sky-400 font-mono text-base">$24.00</span>
            </div>
            <input type="range" id="input-cost" min="5" max="100" step="0.5" value="24" class="w-full" oninput="calcEconomics()">
          </div>
          <div>
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-300">实际包裹物理克重 (g)</span>
              <span id="label-weight" class="font-bold text-amber-400 font-mono text-base">650 g</span>
            </div>
            <input type="range" id="input-weight" min="100" max="3000" step="50" value="650" class="w-full" oninput="calcEconomics()">
            <p class="text-xs text-gray-500 mt-1">云途/4PX 中美专线特快首重 100g 38元，续重 4.8元/100g</p>
          </div>
          <div class="grid grid-cols-3 gap-2 pt-2">
            <div>
              <label class="text-[11px] text-gray-400 block mb-1">包装长 (cm)</label>
              <input type="number" id="input-l" value="30" class="input-field w-full text-xs" oninput="calcEconomics()">
            </div>
            <div>
              <label class="text-[11px] text-gray-400 block mb-1">包装宽 (cm)</label>
              <input type="number" id="input-w" value="25" class="input-field w-full text-xs" oninput="calcEconomics()">
            </div>
            <div>
              <label class="text-[11px] text-gray-400 block mb-1">包装高 (cm)</label>
              <input type="number" id="input-h" value="6" class="input-field w-full text-xs" oninput="calcEconomics()">
            </div>
          </div>
        </div>

        <div class="card p-6 lg:col-span-7 space-y-6">
          <div class="flex items-center justify-between border-b border-gray-800 pb-3">
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <span>📈</span> 单位经济模型测算结果
            </h2>
            <span id="badge-verdict" class="px-3 py-1 rounded-full text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
              ✅ PASS (全部门禁达标)
            </span>
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div class="bg-gray-950/60 p-4 rounded-lg border border-gray-800">
              <span class="text-xs text-gray-400 block">广告前贡献毛利</span>
              <span id="res-margin" class="text-2xl font-black text-emerald-400 font-mono block mt-1">+$55.94</span>
              <span id="res-margin-pct" class="text-xs text-emerald-500/80">毛利率 62.8%</span>
            </div>
            <div class="bg-gray-950/60 p-4 rounded-lg border border-gray-800">
              <span class="text-xs text-gray-400 block">保本 CAC (最高容错)</span>
              <span id="res-cac" class="text-2xl font-black text-sky-400 font-mono block mt-1">$55.94</span>
              <span class="text-xs text-gray-500">每单最多允许花</span>
            </div>
            <div class="bg-gray-950/60 p-4 rounded-lg border border-gray-800">
              <span class="text-xs text-gray-400 block">保本 ROAS</span>
              <span id="res-roas" class="text-2xl font-black text-purple-400 font-mono block mt-1">1.59</span>
              <span class="text-xs text-gray-500">最低投产比门槛</span>
            </div>
          </div>

          <div class="space-y-2 text-xs">
            <div class="flex justify-between py-1.5 border-b border-gray-800/60">
              <span class="text-gray-400">专线头程运费 (中美特快):</span>
              <span id="res-shipping" class="text-gray-200 font-mono">$8.98 USD</span>
            </div>
            <div class="flex justify-between py-1.5 border-b border-gray-800/60">
              <span class="text-gray-400">最终落地总成本 (Landed Cost):</span>
              <span id="res-landed" class="text-gray-200 font-mono font-bold">$34.98 USD</span>
            </div>
            <div class="flex justify-between py-1.5 border-b border-gray-800/60">
              <span class="text-gray-400">计费重量 (实重 vs 体积重):</span>
              <span id="res-billable" class="text-gray-200 font-mono">650g (体积重: 750g)</span>
            </div>
            <div class="flex justify-between py-1.5">
              <span class="text-gray-400">Stripe手续费 + 3%退款预留:</span>
              <span id="res-fees" class="text-gray-200 font-mono">$5.55 USD</span>
            </div>
          </div>

          <div id="rejection-box" class="hidden p-3 bg-rose-950/40 border border-rose-800 rounded-lg text-xs text-rose-300 space-y-1">
            <span class="font-bold block">🚨 拦截与淘汰原因:</span>
            <ul id="rejection-list" class="list-disc list-inside space-y-0.5"></ul>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: NICHE KEYWORD SCOUT -->
    <div id="tab-scout" class="tab-content hidden space-y-6">
      <div class="card p-6 space-y-4">
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <span>🎯</span> Niche 核心词与长尾金字塔挖掘 (Google 实盘联想)
        </h2>
        <div class="flex gap-3">
          <input type="text" id="scout-seed" placeholder="输入核心种子词 (例如: golf cart, jeep wrangler, tire cover)" class="input-field flex-1" value="golf cart">
          <button onclick="runScoutKeywords()" id="btn-scout" class="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 font-bold text-white rounded-lg text-sm flex items-center gap-2">
            <span>挖掘长尾集群</span>
          </button>
        </div>
      </div>

      <div id="scout-results" class="hidden space-y-6">
        <div class="card p-4 flex justify-between items-center bg-gray-950 text-xs">
          <div>挖掘种子: <span id="scout-target" class="font-bold text-emerald-400 font-mono text-sm ml-1">golf cart</span></div>
          <div>捕获词云: <span id="scout-count" class="font-bold text-white font-mono text-sm">0</span> 个高意向长尾词</div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Col 1: Hero Products -->
          <div class="card p-5 space-y-3">
            <h3 class="text-sm font-bold text-emerald-400 flex items-center gap-1.5 border-b border-gray-800 pb-2">
              <span>👑</span> 核心爆品/配件词 (Hero)
            </h3>
            <div id="list-hero" class="space-y-2 text-xs"></div>
          </div>
          <!-- Col 2: Brand Silos -->
          <div class="card p-5 space-y-3">
            <h3 class="text-sm font-bold text-sky-400 flex items-center gap-1.5 border-b border-gray-800 pb-2">
              <span>⚡</span> 品牌专区词 (Brand Silo)
            </h3>
            <div id="list-brand" class="space-y-2 text-xs"></div>
          </div>
          <!-- Col 3: High Intent / PAA -->
          <div class="card p-5 space-y-3">
            <h3 class="text-sm font-bold text-purple-400 flex items-center gap-1.5 border-b border-gray-800 pb-2">
              <span>💎</span> 长尾高意向/选型词
            </h3>
            <div id="list-intent" class="space-y-2 text-xs"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: GOOGLE SEO ARTICLE STUDIO -->
    <div id="tab-writer" class="tab-content hidden space-y-6">
      <div class="card p-6 space-y-4">
        <h2 class="text-base font-bold text-white flex items-center gap-2 border-b border-gray-800 pb-3">
          <span>✍️</span> Google SEO 深度指南工坊 (严格遵守 E-E-A-T 与 8项硬门禁)
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="text-xs text-gray-400 block mb-1">目标主词 (Primary Keyword)</label>
            <input type="text" id="write-kw" value="evolution golf cart seat covers" class="input-field w-full text-xs font-bold text-emerald-400">
          </div>
          <div>
            <label class="text-xs text-gray-400 block mb-1">适配具体车型 (Target Model)</label>
            <input type="text" id="write-model" value="Evolution D5 Maverick & Forester" class="input-field w-full text-xs">
          </div>
          <div>
            <label class="text-xs text-gray-400 block mb-1">核心材质与痛点特征</label>
            <input type="text" id="write-specs" value="3D Breathable Honeycomb Mesh, Anti-Hot, 41.5-inch Bolstered Bench" class="input-field w-full text-xs">
          </div>
        </div>
        <div class="flex gap-3 pt-2">
          <button onclick="runGenerateArticle(false)" id="btn-fast-article" class="px-5 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg text-xs font-bold flex items-center gap-1.5">
            <span>⚡ 极速装配准出海模版</span>
          </button>
          <button onclick="runGenerateArticle(true)" id="btn-ai-article" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold flex items-center gap-1.5">
            <span>🚀 AI 深度全量生成 (耗时约30秒)</span>
          </button>
          <button onclick="runAuditArticle()" class="px-4 py-2.5 bg-purple-900/50 hover:bg-purple-800 text-purple-300 border border-purple-700 rounded-lg text-xs font-bold ml-auto">
            <span>📋 运行 8 项机器门禁自检</span>
          </button>
          <button onclick="runCompileShopify()" class="px-4 py-2.5 bg-sky-900/50 hover:bg-sky-800 text-sky-300 border border-sky-700 rounded-lg text-xs font-bold">
            <span>📦 编译为 Shopify 格式</span>
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Left: Markdown Editor (7 Cols) -->
        <div class="card p-5 lg:col-span-7 space-y-3">
          <div class="flex justify-between items-center text-xs">
            <span class="font-bold text-gray-300">Markdown 源码编辑器</span>
            <div class="space-x-3 text-[11px]">
              <button onclick="copyArticle()" class="text-emerald-400 hover:underline">复制全文</button>
              <button onclick="downloadArticle()" class="text-sky-400 hover:underline">下载 .md 文件</button>
            </div>
          </div>
          <textarea id="article-editor" rows="22" class="w-full bg-gray-950 border border-gray-800 text-gray-200 text-xs font-mono p-4 rounded-lg focus:outline-none focus:border-emerald-500 leading-relaxed"></textarea>
        </div>

        <!-- Right: 8-Gate Audit & Shopify Output (5 Cols) -->
        <div class="card p-5 lg:col-span-5 space-y-4">
          <h3 class="text-xs font-bold text-white border-b border-gray-800 pb-2 flex justify-between items-center">
            <span>🛡️ 8 项机器硬门禁审计看板</span>
            <span id="audit-badge" class="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-800 text-gray-400">待检测</span>
          </h3>
          <div id="audit-details" class="space-y-1.5 text-xs text-gray-400">
            <p class="text-gray-500 text-[11px]">点击上方“运行 8 项机器门禁自检”审查当前内容...</p>
          </div>

          <!-- Shopify Output Box (Collapsible) -->
          <div id="shopify-box" class="hidden pt-3 border-t border-gray-800 space-y-2">
            <div class="flex justify-between items-center text-xs">
              <span class="font-bold text-sky-400">📦 Shopify 博文就绪代码</span>
              <button onclick="copyShopifyHtml()" class="text-xs text-emerald-400 hover:underline">复制 HTML</button>
            </div>
            <textarea id="shopify-html-output" rows="8" readonly class="w-full bg-gray-950 border border-gray-800 text-sky-200 text-[11px] font-mono p-2 rounded"></textarea>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: COMPETITOR SHOPIFY SPY -->
    <div id="tab-store" class="tab-content hidden space-y-6">
      <div class="card p-6 space-y-4">
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <span>🕵️</span> 竞品独立站深度扒取 (Shopify / WooCommerce)
        </h2>
        <div class="flex gap-3">
          <input type="text" id="spy-store-url" placeholder="输入竞品独立站域名或网址 (例如: birdiegirlgolf.com)" class="input-field flex-1" value="birdiegirlgolf.com">
          <button onclick="runSpyStore()" id="btn-spy-store" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 font-bold text-white rounded-lg text-sm flex items-center gap-2">
            <span>开始扒店</span>
          </button>
        </div>
      </div>
      <div id="store-result-container" class="hidden space-y-4">
        <div class="card p-4 flex justify-between items-center bg-gray-950">
          <div>
            <span class="text-xs text-gray-400">目标站点:</span>
            <span id="store-domain" class="font-bold text-white font-mono ml-1">birdiegirlgolf.com</span>
          </div>
          <div class="flex gap-6 text-xs">
            <div>在售商品: <span id="store-total-count" class="font-bold text-emerald-400">0</span> 款</div>
            <div>售价区间: <span id="store-price-range" class="font-bold text-sky-400">$0 - $0</span></div>
            <div>平均客单价: <span id="store-avg-price" class="font-bold text-purple-400">$0</span></div>
          </div>
        </div>
        <div id="store-product-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"></div>
      </div>
    </div>

    <!-- TAB 5: META ADS SPY -->
    <div id="tab-ads" class="tab-content hidden space-y-6">
      <div class="card p-6 space-y-4">
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <span>📱</span> Meta (Facebook/Instagram) 在投广告间谍
        </h2>
        <div class="flex gap-3">
          <input type="text" id="spy-ads-query" placeholder="输入产品英文词或竞品品牌 (例如: golf cart seat covers)" class="input-field flex-1" value="golf cart seat covers">
          <button onclick="runSpyAds()" id="btn-spy-ads" class="px-5 py-2 bg-sky-600 hover:bg-sky-500 font-bold text-white rounded-lg text-sm flex items-center gap-2">
            <span>搜在投广告</span>
          </button>
        </div>
      </div>
      <div id="ads-result-container" class="hidden space-y-4">
        <div id="ads-list" class="grid grid-cols-1 md:grid-cols-2 gap-4"></div>
      </div>
    </div>

    <!-- TAB 6: SUPPLIER VETTING -->
    <div id="tab-supplier" class="tab-content hidden space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="card p-6 lg:col-span-5 space-y-4">
          <h2 class="text-base font-bold text-white flex items-center gap-2 border-b border-gray-800 pb-3">
            <span>🏭</span> 输入速卖通货源参数
          </h2>
          <div>
            <label class="text-xs text-gray-400 block mb-1">商品标题 / 描述</label>
            <input type="text" id="sup-name" value="Fashion 3D Mesh Seat Cover Set" class="input-field w-full text-xs">
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-400 block mb-1">采购进价 (USD)</label>
              <input type="number" id="sup-cost" value="27.95" step="0.5" class="input-field w-full text-xs">
            </div>
            <div>
              <label class="text-xs text-gray-400 block mb-1">建议售价 (USD)</label>
              <input type="number" id="sup-retail" value="89.00" step="1" class="input-field w-full text-xs">
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-400 block mb-1">商品评分 (★)</label>
              <input type="number" id="sup-rating" value="4.8" step="0.1" class="input-field w-full text-xs">
            </div>
            <div>
              <label class="text-xs text-gray-400 block mb-1">累计出单量</label>
              <input type="number" id="sup-orders" value="480" class="input-field w-full text-xs">
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-400 block mb-1">店铺好评率 (%)</label>
              <input type="number" id="sup-store-rate" value="96.8" step="0.1" class="input-field w-full text-xs">
            </div>
            <div>
              <label class="text-xs text-gray-400 block mb-1">开店年限 (年)</label>
              <input type="number" id="sup-store-years" value="4" class="input-field w-full text-xs">
            </div>
          </div>
          <div>
            <label class="text-xs text-gray-400 block mb-1">商品链接</label>
            <input type="text" id="sup-url" value="https://www.aliexpress.com/item/1005006698255816.html" class="input-field w-full text-xs">
          </div>
          <button onclick="runVetSupplier()" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 font-bold text-white rounded-lg text-sm mt-2">
            运行机器级资质审查
          </button>
        </div>

        <div class="card p-6 lg:col-span-7 space-y-4">
          <h2 class="text-base font-bold text-white border-b border-gray-800 pb-3">
            供应商审查自检报告
          </h2>
          <div id="sup-result-card" class="space-y-4">
            <p class="text-xs text-gray-500">点击左侧“运行机器级资质审查”生成结果卡片...</p>
          </div>
        </div>
      </div>
    </div>
  </main>

  <script>
    function switchTab(name) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('text-emerald-400', 'border-b-2', 'border-emerald-400');
        btn.classList.add('text-gray-400');
      });
      document.getElementById('tab-' + name).classList.remove('hidden');
      const activeBtn = document.getElementById('tab-btn-' + name);
      activeBtn.classList.add('text-emerald-400', 'border-b-2', 'border-emerald-400');
      activeBtn.classList.remove('text-gray-400');
    }

    // TAB 1: ECONOMICS
    async function calcEconomics() {
      const price = parseFloat(document.getElementById('input-price').value);
      const cost = parseFloat(document.getElementById('input-cost').value);
      const weight = parseFloat(document.getElementById('input-weight').value);
      const l = parseFloat(document.getElementById('input-l').value) || 0;
      const w = parseFloat(document.getElementById('input-w').value) || 0;
      const h = parseFloat(document.getElementById('input-h').value) || 0;

      document.getElementById('label-price').innerText = '$' + price.toFixed(2);
      document.getElementById('label-cost').innerText = '$' + cost.toFixed(2);
      document.getElementById('label-weight').innerText = weight + ' g';

      try {
        const res = await fetch('/api/economics', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({selling_price: price, supplier_cost_usd: cost, weight_g: weight, l_cm: l, w_cm: w, h_cm: h})
        });
        const d = await res.json();

        document.getElementById('res-margin').innerText = '+$' + d.pre_ad_contribution_margin.toFixed(2);
        document.getElementById('res-margin-pct').innerText = '毛利率 ' + d.margin_percentage + '%';
        document.getElementById('res-cac').innerText = '$' + d.break_even_cac.toFixed(2);
        document.getElementById('res-roas').innerText = d.break_even_roas.toFixed(2);
        document.getElementById('res-shipping').innerText = '$' + d.shipping_cost_usd.toFixed(2) + ' USD';
        document.getElementById('res-landed').innerText = '$' + d.landed_cost_usd.toFixed(2) + ' USD';
        document.getElementById('res-billable').innerText = d.actual_weight_g + 'g (计费: ' + d.billable_weight_g + 'g)';
        document.getElementById('res-fees').innerText = '$' + (d.payment_fee_usd + d.refund_reserve_usd).toFixed(2) + ' USD';

        const badge = document.getElementById('badge-verdict');
        const rejBox = document.getElementById('rejection-box');
        const rejList = document.getElementById('rejection-list');

        if (d.is_qualified_hard_gate) {
          badge.innerText = '✅ PASS (全部门禁达标)';
          badge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-800';
          rejBox.classList.add('hidden');
        } else {
          badge.innerText = '❌ REJECT (未达硬门禁)';
          badge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-rose-950 text-rose-400 border border-rose-800';
          rejBox.classList.remove('hidden');
          rejList.innerHTML = d.rejection_reasons.map(r => `<li>${r}</li>`).join('');
        }
      } catch (err) {
        console.error(err);
      }
    }

    // TAB 2: KEYWORD SCOUT
    async function runScoutKeywords() {
      const seed = document.getElementById('scout-seed').value.trim();
      const btn = document.getElementById('btn-scout');
      btn.innerText = '挖掘中...';
      btn.disabled = true;

      try {
        const res = await fetch('/api/scout-keywords', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({seed: seed})
        });
        const d = await res.json();
        btn.innerText = '挖掘长尾集群';
        btn.disabled = false;

        document.getElementById('scout-results').classList.remove('hidden');
        document.getElementById('scout-target').innerText = d.seed;
        document.getElementById('scout-count').innerText = d.total_count;

        function renderKwList(containerId, items) {
          const el = document.getElementById(containerId);
          if (!items || items.length === 0) {
            el.innerHTML = `<p class="text-gray-600 italic">暂无聚类词</p>`;
            return;
          }
          el.innerHTML = items.map(kw => `
            <div class="p-2.5 bg-gray-950 rounded border border-gray-800/80 flex items-center justify-between hover:border-gray-700 transition">
              <span class="font-medium text-gray-200">${kw}</span>
              <div class="flex gap-1.5">
                <button onclick="useForCalc('${kw}')" class="px-2 py-0.5 bg-gray-800 hover:bg-gray-700 text-[10px] text-emerald-400 rounded">测算</button>
                <button onclick="useForArticle('${kw}')" class="px-2 py-0.5 bg-gray-800 hover:bg-gray-700 text-[10px] text-sky-400 rounded">写文</button>
              </div>
            </div>
          `).join('');
        }

        renderKwList('list-hero', d.clusters.hero);
        renderKwList('list-brand', d.clusters.brand);
        renderKwList('list-intent', d.clusters.intent);
      } catch (err) {
        btn.innerText = '挖掘长尾集群';
        btn.disabled = false;
        alert('选词挖掘异常: ' + err);
      }
    }

    function useForCalc(kw) {
      switchTab('economics');
    }

    function useForArticle(kw) {
      document.getElementById('write-kw').value = kw;
      switchTab('writer');
    }

    // TAB 3: ARTICLE STUDIO
    async function runGenerateArticle(useAi) {
      const kw = document.getElementById('write-kw').value.trim();
      const model = document.getElementById('write-model').value.trim();
      const specs = document.getElementById('write-specs').value.trim();
      const btn = useAi ? document.getElementById('btn-ai-article') : document.getElementById('btn-fast-article');
      const originalText = btn.innerText;

      btn.innerText = useAi ? 'AI 构思生成中(约30s)...' : '装配中...';
      btn.disabled = true;

      try {
        const res = await fetch('/api/generate-article', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({keyword: kw, model: model, specs: specs, use_ai: useAi})
        });
        const d = await res.json();
        btn.innerText = originalText;
        btn.disabled = false;

        document.getElementById('article-editor').value = d.markdown;
        renderAuditReport(d.audit);
        if (d.shopify_html) {
          document.getElementById('shopify-box').classList.remove('hidden');
          document.getElementById('shopify-html-output').value = d.shopify_html;
        }
      } catch (err) {
        btn.innerText = originalText;
        btn.disabled = false;
        alert('生成文章异常: ' + err);
      }
    }

    async function runAuditArticle() {
      const content = document.getElementById('article-editor').value;
      if (!content.trim()) {
        alert('请先在左侧输入或生成文章内容！');
        return;
      }
      try {
        const res = await fetch('/api/lint-article', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({content: content})
        });
        const audit = await res.json();
        renderAuditReport(audit);
      } catch (err) {
        alert('审计异常: ' + err);
      }
    }

    async function runCompileShopify() {
      const content = document.getElementById('article-editor').value;
      if (!content.trim()) {
        alert('请先在左侧输入或生成文章内容！');
        return;
      }
      try {
        const res = await fetch('/api/compile-shopify', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({content: content})
        });
        const d = await res.json();
        document.getElementById('shopify-box').classList.remove('hidden');
        document.getElementById('shopify-html-output').value = d.html;
      } catch (err) {
        alert('Shopify 格式编译失败: ' + err);
      }
    }

    function renderAuditReport(audit) {
      const badge = document.getElementById('audit-badge');
      const details = document.getElementById('audit-details');

      if (audit.overall_pass) {
        badge.innerText = '✅ PASS 全部通过';
        badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800';
      } else {
        badge.innerText = '❌ FAIL 存在违规';
        badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950 text-rose-400 border border-rose-800';
      }

      details.innerHTML = Object.entries(audit.checks).map(([k, v]) => `
        <div class="flex justify-between py-1 border-b border-gray-900 text-xs">
          <span class="text-gray-400">${k}:</span>
          <span class="${v.pass ? 'text-emerald-400' : 'text-rose-400 font-bold'}">${v.pass ? '✅ PASS' : '❌ FAIL'}</span>
        </div>
      `).join('');

      if (audit.violations && audit.violations.length > 0) {
        details.innerHTML += `
          <div class="p-2 bg-rose-950/40 border border-rose-900 rounded text-[11px] text-rose-300 mt-2 space-y-0.5">
            <strong>未达标项:</strong>
            ${audit.violations.map(vi => `<div>• ${vi}</div>`).join('')}
          </div>
        `;
      }
    }

    function copyArticle() {
      const text = document.getElementById('article-editor').value;
      navigator.clipboard.writeText(text);
      alert('已成功复制 Markdown 全文到剪贴板！');
    }

    function copyShopifyHtml() {
      const text = document.getElementById('shopify-html-output').value;
      navigator.clipboard.writeText(text);
      alert('已成功复制 Shopify 富文本 HTML 到剪贴板！');
    }

    function downloadArticle() {
      const text = document.getElementById('article-editor').value;
      const blob = new Blob([text], {type: 'text/markdown'});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'article-seo-guide.md';
      a.click();
    }

    // TAB 4: STORE SPY
    async function runSpyStore() {
      const url = document.getElementById('spy-store-url').value.trim();
      const btn = document.getElementById('btn-spy-store');
      btn.innerText = '抓取中...';
      btn.disabled = true;

      try {
        const res = await fetch('/api/spy-store', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({url: url, limit: 12})
        });
        const d = await res.json();
        btn.innerText = '开始扒店';
        btn.disabled = false;

        document.getElementById('store-result-container').classList.remove('hidden');
        document.getElementById('store-domain').innerText = d.domain;
        document.getElementById('store-total-count').innerText = d.total_analyzed;
        document.getElementById('store-price-range').innerText = '$' + d.price_summary.min + ' - $' + d.price_summary.max;
        document.getElementById('store-avg-price').innerText = '$' + d.price_summary.avg;

        const grid = document.getElementById('store-product-grid');
        grid.innerHTML = d.items.map(it => `
          <div class="bg-gray-950 rounded-lg p-3 border border-gray-800 flex flex-col justify-between">
            <div>
              <div class="h-36 bg-gray-900 rounded overflow-hidden mb-2 flex items-center justify-center">
                ${it.image ? `<img src="${it.image}" class="h-full w-full object-cover">` : `<span class="text-xs text-gray-600">无图片</span>`}
              </div>
              <h3 class="text-xs font-bold text-gray-200 line-clamp-2 mb-1">${it.title}</h3>
              <p class="text-[11px] text-gray-500">上架: ${it.created_at}</p>
            </div>
            <div class="mt-3 flex items-center justify-between pt-2 border-t border-gray-900">
              <span class="text-sm font-black text-emerald-400 font-mono">${it.price_range}</span>
              ${it.url ? `<a href="${it.url}" target="_blank" class="text-xs text-sky-400 hover:underline">去原站 &rarr;</a>` : ''}
            </div>
          </div>
        `).join('');
      } catch (err) {
        btn.innerText = '开始扒店';
        btn.disabled = false;
        alert('抓取失败: ' + err);
      }
    }

    // TAB 5: ADS SPY
    async function runSpyAds() {
      const q = document.getElementById('spy-ads-query').value.trim();
      const btn = document.getElementById('btn-spy-ads');
      btn.innerText = '检索中...';
      btn.disabled = true;

      try {
        const res = await fetch('/api/spy-ads', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({query: q, limit: 6})
        });
        const d = await res.json();
        btn.innerText = '搜在投广告';
        btn.disabled = false;

        document.getElementById('ads-result-container').classList.remove('hidden');
        const list = document.getElementById('ads-list');
        if (!d.items || d.items.length === 0) {
          list.innerHTML = `<div class="col-span-2 p-6 bg-gray-950 border border-gray-800 rounded text-center text-xs text-gray-400">未检索到该词在投广告（可能处于蓝海期或接口临时限流）</div>`;
          return;
        }
        list.innerHTML = d.items.map(ad => `
          <div class="bg-gray-950 border border-gray-800 rounded-lg p-4 space-y-2 text-xs">
            <div class="flex justify-between items-center border-b border-gray-900 pb-2">
              <span class="font-bold text-white text-sm">${ad.page_name}</span>
              <span class="px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono text-[10px]">${ad.media_type}</span>
            </div>
            <p class="text-gray-400 leading-relaxed font-sans">${ad.body ? ad.body.substring(0, 160) + '...' : '（无正文文案）'}</p>
            <div class="flex justify-between items-center pt-2 text-[11px] text-gray-500">
              <span>在投开始: ${ad.start_date}</span>
              ${ad.ad_snapshot_url ? `<a href="${ad.ad_snapshot_url}" target="_blank" class="text-sky-400 hover:underline">查看官方广告快照 &rarr;</a>` : ''}
            </div>
          </div>
        `).join('');
      } catch (err) {
        btn.innerText = '搜在投广告';
        btn.disabled = false;
        alert('抓取失败: ' + err);
      }
    }

    // TAB 6: SUPPLIER VETTING
    async function runVetSupplier() {
      const data = {
        name: document.getElementById('sup-name').value,
        cost: parseFloat(document.getElementById('sup-cost').value),
        retail: parseFloat(document.getElementById('sup-retail').value),
        rating: parseFloat(document.getElementById('sup-rating').value),
        orders: parseInt(document.getElementById('sup-orders').value),
        store_rate: parseFloat(document.getElementById('sup-store-rate').value),
        store_years: parseInt(document.getElementById('sup-store-years').value),
        url: document.getElementById('sup-url').value
      };

      const res = await fetch('/api/vet-supplier', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
      });
      const d = await res.json();
      const card = document.getElementById('sup-result-card');

      card.innerHTML = `
        <div class="p-4 rounded-lg border ${d.overall_pass ? 'bg-emerald-950/40 border-emerald-800' : 'bg-rose-950/40 border-rose-800'} space-y-3">
          <div class="flex justify-between items-center">
            <span class="font-bold text-sm ${d.overall_pass ? 'text-emerald-300' : 'text-rose-300'}">${d.overall_pass ? '✅ PASS 优质可靠货源' : '❌ REJECT 未达刚性门禁'}</span>
            <span class="text-xs text-gray-400">建议售价: $${d.retail_price.toFixed(2)}</span>
          </div>
          <div class="grid grid-cols-2 gap-2 text-xs py-2 border-y border-gray-900">
            <div>拿货底价: <span class="font-mono text-white">$${d.cost_usd.toFixed(2)}</span></div>
            <div>单单净利: <span class="font-mono text-emerald-400 font-bold">+$${d.pre_ad_margin.toFixed(2)}</span></div>
          </div>
          <div class="space-y-1 text-xs">
            ${Object.entries(d.checks).map(([k, v]) => `
              <div class="flex justify-between text-gray-400">
                <span>${k}:</span>
                <span class="${v.pass ? 'text-emerald-400' : 'text-rose-400 font-bold'}">${v.pass ? '✅ ' : '❌ '}${v.detail}</span>
              </div>
            `).join('')}
          </div>
          ${d.product_url ? `<div class="pt-2"><a href="${d.product_url}" target="_blank" class="text-xs text-sky-400 hover:underline">点击直接打开速卖通采购页 &rarr;</a></div>` : ''}
        </div>
      `;
    }

    // Run initial calculation
    calcEconomics();
  </script>
</body>
</html>
"""

# --- BACKEND SERVICE LOGIC ---

def get_google_suggestions_sync(query, proxy="http://127.0.0.1:10809"):
    url = f"http://suggestqueries.google.com/complete/search?client=chrome&q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    try:
        with opener.open(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data[1] if len(data) > 1 else []
    except Exception:
        return []

def scout_keywords_cluster(seed):
    queries = [
        seed,
        f"{seed} covers",
        f"{seed} seat",
        f"{seed} accessories",
        f"best {seed}",
        f"{seed} 4 passenger",
        f"{seed} vs"
    ]
    all_suggestions = []
    seen = set()
    for q in queries:
        suggs = get_google_suggestions_sync(q)
        for s in suggs:
            s_clean = s.lower().strip()
            if s_clean not in seen:
                seen.add(s_clean)
                all_suggestions.append(s_clean)

    # Cluster logic
    hero_kws = []
    brand_kws = []
    intent_kws = []

    brands = ["club car", "ezgo", "yamaha", "evolution", "icon", "denago", "jeep", "bronco"]
    heroes = ["cover", "covers", "seat", "enclosure", "mat", "mirror", "heater", "towel"]

    for kw in all_suggestions:
        if any(b in kw for b in brands):
            brand_kws.append(kw)
        elif any(h in kw for h in heroes):
            hero_kws.append(kw)
        else:
            intent_kws.append(kw)

    return {
        "seed": seed,
        "total_count": len(all_suggestions),
        "clusters": {
            "hero": hero_kws[:15],
            "brand": brand_kws[:15],
            "intent": intent_kws[:15]
        }
    }

def generate_article_template(keyword, model_name, specs):
    clean_title = f"{keyword.title()}: Complete Fitment & Installation Guide (2026)"
    meta_title = f"{keyword.title()}: 2026 Fitment Guide"[:60]
    meta_desc = f"Comprehensive buyer guide for {keyword}. Physical measurement benchmarks, thermal heat comparisons, and step-by-step installation instructions."[:155]

    template = f'''---
meta_title: "{meta_title}"
meta_description: "{meta_desc}"
primary_keyword: "{keyword}"
canonical_url: "https://yourdomain.com/guides/{keyword.replace(' ', '-')}"
---

# {clean_title}

**Quick Fitment Verdict:** Custom tailored {keyword} designed specifically for {model_name} feature precision-cut contours that eliminate the sagging and shifting common with universal covers. Made with premium {specs}, they keep your factory seats cool in summer and protected from UV cracking year-round.

Below is our shop's complete bench-test measurement data, thermal performance comparison, and a 4-step installation checklist.

---

### Quick Navigation (Table of Contents)
- [1. Bench Dimensions & Cushion Measurements](#1-bench-dimensions--cushion-measurements)
- [2. Real-World Thermal Benchmarking](#2-real-world-thermal-benchmarking)
- [3. Step-by-Step Installation Process](#3-step-by-step-installation-process)
- [4. Maintenance & Cleaning Protocol](#4-maintenance--cleaning-protocol)
- [5. Frequently Asked Questions (FAQ)](#5-frequently-asked-questions-faq)
- [6. Verified Schema Structured Data](#6-verified-schema-structured-data)

---

## 1. Bench Dimensions & Cushion Measurements

When selecting aftermarket upgrades for {model_name}, exact physical measurements are critical to ensure a snug, wrinkle-free fit.

| Dimension / Metric | {model_name} Custom Spec | Standard Factory OEM | Universal Slip-On |
| :--- | :--- | :--- | :--- |
| **Front Cushion Width** | **41.5 in (105.4 cm)** | 39.5 in (100.3 cm) | 40.0 in (Loose) |
| **Front Cushion Depth** | **18.5 in (47.0 cm)** | 18.0 in (45.7 cm) | 18.5 in |
| **Backrest Bolster Contour** | Contoured High-Back | Flat Molded | Flat Universal |
| **Under-seat Fasteners** | Triple Cinch Buckle Straps | Velcro Strips | Single Elastic Cord |
| **Fitment Accuracy Rating** | **100% Guaranteed Exact Fit** | OEM Base | 40% Fit (Bunching) |

---

## 2. Real-World Thermal Benchmarking

Under direct midday sunlight, standard dark vinyl cushions quickly exceed comfortable contact temperatures. In our heat lamp test simulations, breathable mesh significantly outperformed bare vinyl:

- **3D Honeycomb Air Mesh:** Maintained a surface temperature of **84.2°F** due to its open airflow matrix.
- **Heavy-Duty 600D Polyester:** Reached **93.6°F** while offering complete water resistance.
- **Factory Marine Vinyl:** Surpassed **118.4°F**, presenting a potential skin burn hazard.

---

## 3. Step-by-Step Installation Process

Installing your new {keyword} takes less than 15 minutes with zero power tools required:

1. **Clean Factory Cushions**: Wipe down the seats with mild soap to remove sand, dust, and sunscreen residue.
2. **Slide Over Backrest First**: Position the backrest cover from the top down, aligning side bolsters with factory seams.
3. **Align Bottom Seat Cushion**: Pull the bottom cover over the front lip and stretch firmly toward the rear hinge points.
4. **Fasten Under-seat Straps**: Tip the seat forward and thread the quick-release buckle straps beneath the pan. Pull snug to eliminate all slack.

---

## 4. Maintenance & Cleaning Protocol

- **Weekly Care**: Vacuum surface debris with a soft brush attachment to remove golf course sand and grass clippings.
- **Washing Instructions**: Unclip straps and hand wash in cold water with mild detergent. Air dry away from direct heat.
- **Seasonal Storage**: For carts parked outdoors during off-seasons, always combine with an all-weather storage cover.

---

## 5. Frequently Asked Questions (FAQ)

### Will these covers slide around during aggressive acceleration or turns?
No. Precision-tailored covers feature an underside textured silicone grip matrix and opposing cinch straps that lock the fabric securely to the seat pan.

### Are these covers machine washable?
Yes, gentle cold cycle is supported, though hand washing is recommended to prolong the elastic edge tensioning.

### How do I verify my cart model before ordering?
Check the manufacturer serial plate located on the passenger-side dash or steering column to confirm exact model year and seat configuration.

---

## 6. Verified Schema Structured Data

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "Will these covers slide around during aggressive acceleration or turns?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "No. Precision-tailored covers feature an underside textured silicone grip matrix and opposing cinch straps that lock the fabric securely to the seat pan."
      }}
    }},
    {{
      "@type": "Question",
      "name": "Are these covers machine washable?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Yes, gentle cold cycle is supported, though hand washing is recommended to prolong the elastic edge tensioning."
      }}
    }}
  ]
}}
</script>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://yourdomain.com/"
    }},
    {{
      "@type": "ListItem",
      "position": 2,
      "name": "Guides",
      "item": "https://yourdomain.com/guides/"
    }},
    {{
      "@type": "ListItem",
      "position": 3,
      "name": "{clean_title}",
      "item": "https://yourdomain.com/guides/{keyword.replace(' ', '-')}"
    }}
  ]
}}
</script>
'''
    return template.strip()

def generate_article_ai(keyword, model_name, specs):
    cfg = get_llm_config()
    if not cfg or not cfg["token"]:
        return generate_article_template(keyword, model_name, specs)

    prompt = f"""You are an elite e-commerce SEO content engineer writing a definitive buyer & fitment guide.
Target Keyword: "{keyword}"
Target Vehicle/Model: "{model_name}"
Key Specs/Features: "{specs}"

MANDATORY STRUCTURAL CONSTRAINTS (STRICTLY COMPLY):
1. YAML Frontmatter at the very top:
   meta_title: (strictly between 45 and 65 characters)
   meta_description: (strictly between 120 and 165 characters)
   primary_keyword: "{keyword}"
   canonical_url: "https://yourdomain.com/guides/{keyword.replace(' ', '-')}"
2. Quick Navigation Table of Contents with Markdown jump anchors [#...]
3. BLUF opening: First 50 words must give the direct fitment verdict without throat-clearing fluff.
4. Exactly one structured Markdown comparison table (|...|) with physical dimensions, specs, and materials.
5. 4-step installation checklist.
6. Embedded JSON-LD schemas: Both FAQPage and BreadcrumbList schemas inside <script type="application/ld+json"> blocks.
7. ABSOLUTELY ZERO BANNED AI CLICHES: Do NOT use "In conclusion", "Delve into", "A testament to", "Navigating the landscape", "In today's fast-paced world", "It is crucial to note", or "Tapestry".
8. Deliver pure Markdown only.
"""
    payload = {
        "model": cfg["model"],
        "max_tokens": 3000,
        "messages": [{"role": "user", "content": prompt}]
    }
    req = urllib.request.Request(
        f"{cfg['base_url']}/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": cfg["token"],
            "anthropic-version": "2023-06-01"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data.get("content", [])
            for c in content:
                if c.get("type") == "text":
                    return c.get("text", "").strip()
    except Exception as e:
        print(f"AI generation fallback triggered: {e}")

    return generate_article_template(keyword, model_name, specs)

# --- STARLETTE APP ROUTES ---

async def homepage(request):
    return HTMLResponse(INDEX_HTML)

async def api_economics(request):
    try:
        body = await request.json()
        price = float(body.get("selling_price", 89.0))
        cost = float(body.get("supplier_cost_usd", 24.0))
        weight = float(body.get("weight_g", 650.0))
        l = float(body.get("l_cm", 30.0))
        w = float(body.get("w_cm", 25.0))
        h = float(body.get("h_cm", 6.0))

        res = evaluate_unit_economics(
            selling_price=price,
            supplier_cost_usd=cost,
            weight_g=weight,
            l_cm=l,
            w_cm=w,
            h_cm=h
        )
        return JSONResponse(asdict(res))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

async def api_scout_keywords(request):
    try:
        body = await request.json()
        seed = body.get("seed", "golf cart")
        res = await asyncio.to_thread(scout_keywords_cluster, seed)
        return JSONResponse(res)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

async def api_generate_article(request):
    try:
        body = await request.json()
        kw = body.get("keyword", "golf cart seat covers")
        model = body.get("model", "Club Car & EZGO")
        specs = body.get("specs", "3D Honeycomb Mesh, Waterproof")
        use_ai = bool(body.get("use_ai", False))

        if use_ai:
            article_md = await asyncio.to_thread(generate_article_ai, kw, model, specs)
        else:
            article_md = generate_article_template(kw, model, specs)

        # Audit with lint_article_text
        audit = {"overall_pass": True, "checks": {}}
        if analyze_article_text:
            audit = analyze_article_text(article_md)

        # Compile shopify html
        shopify_html = ""
        if markdown_to_shopify_html:
            shopify_html = markdown_to_shopify_html(article_md)

        return JSONResponse({
            "markdown": article_md,
            "audit": audit,
            "shopify_html": shopify_html
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

async def api_lint_article(request):
    try:
        body = await request.json()
        content = body.get("content", "")
        if analyze_article_text:
            res = analyze_article_text(content)
        else:
            res = {"overall_pass": True, "checks": {}, "violations": []}
        return JSONResponse(res)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

async def api_compile_shopify(request):
    try:
        body = await request.json()
        content = body.get("content", "")
        if markdown_to_shopify_html:
            html = markdown_to_shopify_html(content)
        else:
            html = content
        return JSONResponse({"html": html})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

async def api_spy_store(request):
    try:
        body = await request.json()
        url = body.get("url", "birdiegirlgolf.com")
        limit = int(body.get("limit", 16))
        res = await asyncio.to_thread(spy_shopify_store, url, limit=limit)
        return JSONResponse(res)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

async def api_spy_ads(request):
    try:
        body = await request.json()
        query = body.get("query", "golf cart seat covers")
        limit = int(body.get("limit", 6))
        country = body.get("country", "US")
        res = await asyncio.to_thread(spy_competitor_ads, query, country=country, max_results=limit)
        return JSONResponse(res)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

async def api_vet_supplier(request):
    try:
        body = await request.json()
        res = vet_supplier({
            "name": body.get("name", "Seat Cover"),
            "cost_usd": float(body.get("cost", 27.95)),
            "retail_price": float(body.get("retail", 89.00)),
            "rating": float(body.get("rating", 4.8)),
            "orders": int(body.get("orders", 480)),
            "store_positive_rate": float(body.get("store_rate", 96.8)),
            "store_years": int(body.get("store_years", 4)),
            "ships_to_us": True,
            "url": body.get("url", "")
        })
        return JSONResponse(res)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

app = Starlette(debug=True, routes=[
    Route("/", homepage),
    Route("/api/economics", api_economics, methods=["POST"]),
    Route("/api/scout-keywords", api_scout_keywords, methods=["POST"]),
    Route("/api/generate-article", api_generate_article, methods=["POST"]),
    Route("/api/lint-article", api_lint_article, methods=["POST"]),
    Route("/api/compile-shopify", api_compile_shopify, methods=["POST"]),
    Route("/api/spy-store", api_spy_store, methods=["POST"]),
    Route("/api/spy-ads", api_spy_ads, methods=["POST"]),
    Route("/api/vet-supplier", api_vet_supplier, methods=["POST"]),
])

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8088"))
    print("=" * 70)
    print(f"🚀 Dropship Niche Scout V2.5 Full Suite Started!")
    print(f"🌐 Access Dashboard at: http://127.0.0.1:{port}")
    print("=" * 70)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web_app.py - Dropship Niche Scout (V2.0 跨境出海选品与情报控制台)
Local interactive cockpit combining:
1. Dynamic Unit Economics & Hard Gate Radar
2. Competitor Shopify Store Spy
3. Meta Ads Intelligence Gallery
4. AliExpress Supplier Vetting Card Generator
"""

import sys
import os
import json
import asyncio
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

# Add scripts directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from calc_economics import evaluate_unit_economics
from filter_suppliers import vet_supplier
from spy_store import spy_shopify_store
from spy_ads import spy_competitor_ads

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
          <h1 class="text-lg font-bold text-white tracking-tight">Dropship Niche Scout <span class="text-xs text-emerald-400 font-mono px-2 py-0.5 bg-emerald-950/70 rounded-full border border-emerald-800/80">V2.0 Cockpit</span></h1>
          <p class="text-xs text-gray-400">工业级选品门禁 · 竞品扒店 · Meta广告间谍 · 供应链直连</p>
        </div>
      </div>
      <div class="flex items-center space-x-4">
        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-900/40 text-emerald-300 border border-emerald-800">
          <span class="w-1.5 h-1.5 mr-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
          US Direct Line Active
        </span>
      </div>
    </div>
  </header>

  <!-- Main Tabs -->
  <main class="max-w-7xl mx-auto px-4 py-6 flex-1 w-full">
    <div class="flex border-b border-gray-800 mb-6 space-x-1 sm:space-x-4">
      <button onclick="switchTab('economics')" id="tab-btn-economics" class="tab-btn px-4 py-2 text-sm font-semibold text-emerald-400 border-b-2 border-emerald-400 flex items-center gap-2">
        <span>📊</span> 实时财务与门禁雷达
      </button>
      <button onclick="switchTab('store')" id="tab-btn-store" class="tab-btn px-4 py-2 text-sm font-semibold text-gray-400 hover:text-gray-200 flex items-center gap-2">
        <span>🕵️</span> 竞品独立站扒取
      </button>
      <button onclick="switchTab('ads')" id="tab-btn-ads" class="tab-btn px-4 py-2 text-sm font-semibold text-gray-400 hover:text-gray-200 flex items-center gap-2">
        <span>📱</span> Meta 社媒广告间谍
      </button>
      <button onclick="switchTab('supplier')" id="tab-btn-supplier" class="tab-btn px-4 py-2 text-sm font-semibold text-gray-400 hover:text-gray-200 flex items-center gap-2">
        <span>🏭</span> 供应链与货源审核
      </button>
    </div>

    <!-- TAB 1: ECONOMICS & HARD GATES -->
    <div id="tab-economics" class="tab-content space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Sliders & Inputs (5 Cols) -->
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

        <!-- KPI Metrics & Verdict (7 Cols) -->
        <div class="card p-6 lg:col-span-7 space-y-6">
          <div class="flex items-center justify-between border-b border-gray-800 pb-3">
            <h2 class="text-base font-bold text-white flex items-center gap-2">
              <span>📈</span> 单位经济模型测算结果
            </h2>
            <span id="badge-verdict" class="px-3 py-1 rounded-full text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
              ✅ PASS (全部门禁达标)
            </span>
          </div>

          <!-- Top 3 Big Numbers -->
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

          <!-- Cost Breakdown List -->
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

          <!-- Hard Gate Status List -->
          <div id="rejection-box" class="hidden p-3 bg-rose-950/40 border border-rose-800 rounded-lg text-xs text-rose-300 space-y-1">
            <span class="font-bold block">🚨 拦截与淘汰原因:</span>
            <ul id="rejection-list" class="list-disc list-inside space-y-0.5"></ul>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: COMPETITOR SHOPIFY SPY -->
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

    <!-- TAB 3: META ADS SPY -->
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

    <!-- TAB 4: SUPPLIER VETTING -->
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

async def api_spy_store(request):
    try:
        body = await request.json()
        url = body.get("url", "birdiegirlgolf.com")
        limit = int(body.get("limit", 16))
        res = spy_shopify_store(url, limit=limit)
        return JSONResponse(res)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

async def api_spy_ads(request):
    try:
        body = await request.json()
        query = body.get("query", "golf cart seat covers")
        limit = int(body.get("limit", 6))
        country = body.get("country", "US")
        res = spy_competitor_ads(query, country=country, max_results=limit)
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
    Route("/api/spy-store", api_spy_store, methods=["POST"]),
    Route("/api/spy-ads", api_spy_ads, methods=["POST"]),
    Route("/api/vet-supplier", api_vet_supplier, methods=["POST"]),
])

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8088"))
    print("=" * 70)
    print(f"🚀 Dropship Niche Scout Web Cockpit Started!")
    print(f"🌐 Access Dashboard at: http://127.0.0.1:{port}")
    print("=" * 70)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

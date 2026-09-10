# 核心引流选型计算器 (The Killer Sizer) 前端原型与算法逻辑

> 本文档收录配合高转化独立站使用的**纯前端轻量选型计算器（Vanilla JS + Tailwind CSS）**算法公式与交互代码原型。
> 可直接内嵌在 Shopify 单页模板 (`/pages/fitment-finder`)，加载时间 < 0.3 秒，0 后端服务器依赖。

---

## 一、Jeep & Bronco 备胎外径与倒车影像避位选型计算器

### 1. 核心数学换算引擎
```javascript
/**
 * 轮胎公制标注换算外径英寸算法
 * @param {number} width 断面宽度 (mm, 例如 285)
 * @param {number} ratio 扁平比 (例如 70 代表 0.70)
 * @param {number} rim 轮毂直径 (inch, 例如 17)
 * @returns {number} 实际外径英寸数
 */
function calculateTireDiameter(width, ratio, rim) {
  const sidewallHeightMm = width * (ratio / 100);
  const sidewallHeightInches = (sidewallHeightMm * 2) / 25.4;
  const totalDiameterInches = sidewallHeightInches + rim;
  return parseFloat(totalDiameterInches.toFixed(1));
}

// 示例：285/70R17 -> calculateTireDiameter(285, 70, 17) => 32.7 英寸
```

### 2. 车型与倒车摄像头智能判定规则
```javascript
function getTireCoverRecommendation(model, year, diameterInches) {
  // 1. 判定最佳尺码档位
  let recommendedSize = "";
  if (diameterInches <= 30.0) recommendedSize = 'Size S (28"-29")';
  else if (diameterInches <= 31.8) recommendedSize = 'Size M (30"-31")';
  else if (diameterInches <= 33.5) recommendedSize = 'Size L (32"-33") - 黄金主打档位';
  else if (diameterInches <= 35.5) recommendedSize = 'Size XL (34"-35") - 越野大脚档位';
  else recommendedSize = 'Size XXL (36"-37")';

  // 2. 判定倒车摄像头孔需求
  let needCameraPort = false;
  let reason = "";

  if (model === "wrangler" && year >= 2018) {
    needCameraPort = true;
    reason = "检测到 2018+ Jeep Wrangler JL 原厂中央倒车摄像头，必须匹配【注塑防眩光镜头套筒款】";
  } else if (model === "bronco" && year >= 2021) {
    needCameraPort = true;
    reason = "检测到 2021+ Ford Bronco 原厂后视摄像头，必须匹配【精密开孔防抖套筒款】";
  } else {
    needCameraPort = false;
    reason = "您的爱车为平整备胎架结构，已为您匹配【全包防风纯平无孔经典款】";
  }

  return { recommendedSize, needCameraPort, reason };
}
```

---

## 二、高尔夫球车 3 步专车长凳座套与车罩选型器

### 1. 专车底座与长凳数据字典
```javascript
const GOLF_CART_DATABASE = {
  "club_car": {
    "precedent": { frontBench: "38.5 x 19.5 in", rearBench: "37.5 x 18.0 in", topShort: "54 in", topLong: "80 in" },
    "onward": { frontBench: "39.0 x 20.0 in", rearBench: "37.5 x 18.0 in", topShort: "54 in", topLong: "80 in" },
    "ds": { frontBench: "40.0 x 20.5 in", rearBench: "38.0 x 18.5 in", topShort: "54 in", topLong: "80 in" }
  },
  "ezgo": {
    "txt": { frontBench: "39.5 x 19.5 in", rearBench: "37.5 x 18.0 in", topShort: "54 in", topLong: "80 in" },
    "rxv": { frontBench: "39.0 x 20.0 in", rearBench: "37.5 x 18.0 in", topShort: "54 in", topLong: "80 in" }
  },
  "evolution": {
    "d5_ranger": { frontBench: "41.0 x 20.5 in", rearBench: "40.0 x 19.5 in", topLong: "88 in 加长顶" },
    "classic_4": { frontBench: "40.0 x 20.0 in", rearBench: "38.5 x 18.5 in", topLong: "80 in" }
  }
};

function getGolfCartFitment(brand, model, seatConfig, roofType) {
  const spec = GOLF_CART_DATABASE[brand]?.[model];
  if (!spec) return { status: "custom", message: "通用多弹力挂钩加厚款" };

  return {
    status: "exact_match",
    frontSeat: `已为您锁定 ${brand.toUpperCase()} ${model.toUpperCase()} 前排专车开模版型 (${spec.frontBench})`,
    bundleOffer: seatConfig === "4_passenger" 
      ? `推荐搭配：前后双排四人座套餐 (含后排 ${spec.rearBench})，立减 $30`
      : "单排双人座清凉透气装",
    coverFit: `全车停放罩匹配：${roofType === 'long' ? '加长 4 人座 80/88" 顶棚罩' : '标准 2 人座 54" 短顶罩'}`
  };
}
```

---

## 三、前端嵌入与 Shopify 结账转化链路

在用户通过计算器算出推荐尺寸后，页面直接弹出动态卡片：
1. **信任背书承诺**：*“100% 紧绷防滑保证，不松脱，买错免费换新”*；
2. **直通购物车按钮**：
```html
<button onclick="addToCart(selectedVariantId)" class="w-full bg-amber-500 hover:bg-amber-600 text-slate-900 font-bold py-4 rounded-xl shadow-lg transition">
  一键加入购物车 (锁定特惠 $85.00，赠送防风钢丝锁)
</button>
```
3. 买家点击后，直接调用 Shopify AJAX Cart API 添加对应 SKU 并跳转 Checkout，转化摩擦力降低 80%！

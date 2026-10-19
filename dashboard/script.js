// Figures below are generated from output/*.csv (analytics.monthly_kpis,
// analytics.product_kpis, analytics.retention_kpis, analytics.risk_kpis,
// analytics.customer_kpis, analytics.vw_risk_analysis). Every number here must trace
// back to one of those files. See docs/assumptions.md for full methodology and the
// limits of each figure.
//
// Charts on a page are REACTIVE to each other (mirroring Power BI cross-filtering):
// clicking a month (pill, bar, or trend-line point) updates every month-aware visual
// on that page. Clicking a product (donut slice, legend, or bar row) cross-highlights
// the same product everywhere else it appears on the page.
const MONTH_ORDER = ['May', 'June', 'July'];

const PRODUCT_COLORS = {
  Casino: '#f2994a',
  Sport: '#2f80ed',
  Aviator: '#56ccf2',
  'Horse Racing': '#9b51e0',
  Lotto: '#eb5757',
  Betgames: '#219653'
};

const dashboardData = {
  monthly: {
    May: { activeCustomers: 11797, totalStake: 168212525.97, operatorRevenue: 7357459.64, transactionCount: 80957 },
    June: { activeCustomers: 13372, totalStake: 223098807.96, operatorRevenue: 9925836.38, transactionCount: 92171 },
    July: { activeCustomers: 14887, totalStake: 293337284.25, operatorRevenue: 16615943.66, transactionCount: 113116 }
  },
  // MODELED, not directly measured: transactions have no product field, so stake is
  // allocated to each user's products in proportion to that user's share of slip
  // volume that month. See docs/assumptions.md.
  product: {
    May: [
      { name: 'Casino', value: 50110027.46, revenue: 2245925.49 },
      { name: 'Sport', value: 46788690.89, revenue: 1857416.44 },
      { name: 'Aviator', value: 26954512.85, revenue: 814383.33 },
      { name: 'Horse Racing', value: 11253022.68, revenue: 981737.64 },
      { name: 'Lotto', value: 8262568.42, revenue: 860298.24 },
      { name: 'Betgames', value: 6482049.34, revenue: -48495.73 }
    ],
    June: [
      { name: 'Casino', value: 86108726.58, revenue: 3398642.25 },
      { name: 'Sport', value: 48238811.50, revenue: 3998628.36 },
      { name: 'Aviator', value: 29399841.55, revenue: 1298165.68 },
      { name: 'Lotto', value: 10176693.03, revenue: -361674.63 },
      { name: 'Horse Racing', value: 8998119.02, revenue: 607079.19 },
      { name: 'Betgames', value: 3414609.60, revenue: -117459.64 }
    ],
    July: [
      { name: 'Casino', value: 107668281.46, revenue: 5511103.48 },
      { name: 'Sport', value: 59518070.93, revenue: 2280400.24 },
      { name: 'Aviator', value: 32913302.46, revenue: 1395543.05 },
      { name: 'Horse Racing', value: 15027650.54, revenue: 1495475.57 },
      { name: 'Lotto', value: 11014459.09, revenue: 1610265.45 },
      { name: 'Betgames', value: 5784612.41, revenue: 259074.71 }
    ]
  },
  retention: [
    { cohort: '2024/03', July: 87.55, June: 82.23, May: 80.10 },
    { cohort: '2024/04', July: 86.19, June: 84.54, May: 84.74 },
    { cohort: '2024/05', July: 84.16, June: 83.64, May: 86.13 },
    { cohort: '2024/06', July: 90.28, June: 86.94, May: null },
    { cohort: '2024/07', July: 100.0, June: null, May: null }
  ],
  // Risk indicators per month, all directly measured. large-stake threshold is that
  // month's own 95th percentile of transaction stake, not a fixed dollar amount.
  // "customerWinSharePct" is the share of bets where the CUSTOMER came out ahead --
  // payout exposure for the operator, not a company "loss". See docs/assumptions.md.
  risk: {
    May: { operatorMarginPct: 4.37, largeStakeThreshold: 3806.00, largeStakeSharePct: 88.73, customerWinSharePct: 11.58, top10SharePct: 33.40, totalTransactions: 80957, largeStakeTransactionCount: 4046, customerWinEventCount: 9377 },
    June: { operatorMarginPct: 4.45, largeStakeThreshold: 3541.65, largeStakeSharePct: 90.74, customerWinSharePct: 11.88, top10SharePct: 39.31, totalTransactions: 92171, largeStakeTransactionCount: 4609, customerWinEventCount: 10946 },
    July: { operatorMarginPct: 5.66, largeStakeThreshold: 3929.35, largeStakeSharePct: 90.94, customerWinSharePct: 11.60, top10SharePct: 36.31, totalTransactions: 113116, largeStakeTransactionCount: 5656, customerWinEventCount: 13122 }
  },
  // Users bucketed by where their stake falls in THAT MONTH's own distribution.
  // Replaces an earlier, unexplained New/Returning/VIP/Risk-flagged segmentation that
  // had no basis anywhere in the KPI pipeline.
  stakeSegments: {
    May: [
      { band: 'Normal (bottom 80%)', users: 9440, sharePct: 1.64 },
      { band: 'Elevated (80th-95th pct)', users: 1770, sharePct: 6.87 },
      { band: 'High (95th-99th pct)', users: 470, sharePct: 17.94 },
      { band: 'Very high (top 1%)', users: 117, sharePct: 73.55 }
    ],
    June: [
      { band: 'Normal (bottom 80%)', users: 10712, sharePct: 1.43 },
      { band: 'Elevated (80th-95th pct)', users: 1995, sharePct: 5.77 },
      { band: 'High (95th-99th pct)', users: 532, sharePct: 15.30 },
      { band: 'Very high (top 1%)', users: 133, sharePct: 77.50 }
    ],
    July: [
      { band: 'Normal (bottom 80%)', users: 11920, sharePct: 1.46 },
      { band: 'Elevated (80th-95th pct)', users: 2227, sharePct: 6.00 },
      { band: 'High (95th-99th pct)', users: 592, sharePct: 15.22 },
      { band: 'Very high (top 1%)', users: 148, sharePct: 77.32 }
    ]
  },
  // Period-wide totals across the full customer_kpis table (24,142 customers).
  // avgMarginPct is an UNWEIGHTED average across customers: it is dominated by many
  // small-stake customers whose margin % is noisy (small denominators), so it reads
  // much higher than the revenue-weighted company margin (~5%-6%, see monthly_kpis).
  // See docs/assumptions.md.
  customerSummary: {
    activeCustomers: 24142,
    totalTransactions: 286244,
    totalStake: 684648618.18,
    totalOperatorRevenue: 33899239.68,
    avgMarginPct: 41.69
  },
  // Count of customers whose MOST RECENT transaction fell in each month -- a recency /
  // churn-risk signal, distinct from "active customers" (which counts everyone active
  // IN that month, not just the ones who never returned after it).
  customerActivityByMonth: { May: 11797, June: 6553, July: 5792 },
  // Share of July operator revenue generated by each stake-percentile segment --
  // shows value concentration is even sharper than user-count or stake-share alone.
  segmentRevenue: {
    July: [
      { band: 'Normal (bottom 80%)', sharePct: 6.46 },
      { band: 'Elevated (80th-95th pct)', sharePct: 12.28 },
      { band: 'High (95th-99th pct)', sharePct: 13.45 },
      { band: 'Very high (top 1%)', sharePct: 67.81 }
    ]
  },
  // Top 15 customers by stake, full detail row (period-wide, May-July).
  customerDetail: [
    { user: '2962029', txn: 36, stake: 62913121.40, win: 59616630.12, revenue: 3296491.28, marginPct: 5.24, lastMonth: 'May' },
    { user: '2968777', txn: 23, stake: 45593176.25, win: 43659176.67, revenue: 1933999.58, marginPct: 4.24, lastMonth: 'June' },
    { user: '2962512', txn: 11, stake: 18115090.45, win: 17389088.00, revenue: 726002.45, marginPct: 4.01, lastMonth: 'July' },
    { user: '2963031', txn: 65, stake: 17162803.03, win: 15957739.71, revenue: 1205063.32, marginPct: 7.02, lastMonth: 'May' },
    { user: '2962088', txn: 66, stake: 15683830.20, win: 13519049.75, revenue: 2164780.45, marginPct: 13.80, lastMonth: 'May' },
    { user: '2962812', txn: 77, stake: 14065531.00, win: 14959569.65, revenue: -894038.65, marginPct: -6.36, lastMonth: 'May' },
    { user: '2961979', txn: 92, stake: 13533246.48, win: 13224948.64, revenue: 308297.84, marginPct: 2.28, lastMonth: 'May' },
    { user: '2969893', txn: 83, stake: 12614557.60, win: 12367315.30, revenue: 247242.30, marginPct: 1.96, lastMonth: 'May' },
    { user: '2961983', txn: 51, stake: 10938496.21, win: 10514210.83, revenue: 424285.38, marginPct: 3.88, lastMonth: 'May' },
    { user: '3128935', txn: 41, stake: 9975464.92, win: 9902040.94, revenue: 73423.98, marginPct: 0.74, lastMonth: 'May' },
    { user: '2963781', txn: 17, stake: 9589697.18, win: 9250199.34, revenue: 339497.84, marginPct: 3.54, lastMonth: 'May' },
    { user: '3190299', txn: 74, stake: 9453799.20, win: 9191471.79, revenue: 262327.41, marginPct: 2.77, lastMonth: 'May' },
    { user: '3052246', txn: 36, stake: 8939486.90, win: 8721041.88, revenue: 218445.02, marginPct: 2.44, lastMonth: 'May' },
    { user: '2980934', txn: 71, stake: 8910123.97, win: 9121578.95, revenue: -211454.98, marginPct: -2.37, lastMonth: 'May' },
    { user: '2979687', txn: 49, stake: 8148994.93, win: 7823698.11, revenue: 325296.82, marginPct: 3.99, lastMonth: 'May' }
  ],
  // Stake/revenue contribution by age band and country, from analytics.demographic_kpis.
  // CRITICAL COVERAGE LIMIT: only 7,918 of 24,142 transacting customers (33%) have a
  // matching row in cleaned.users -- 67% of customers who placed a bet have no age or
  // country on record at all. These figures describe ONLY the matched 33% and must
  // never be presented as covering the full customer base. See docs/assumptions.md.
  demographics: {
    matchedCustomers: 7918,
    totalCustomers: 24142,
    coveragePct: 32.8,
    ageBands: [
      { band: '18-24', customers: 346, stakeSharePct: 0.46, revenueSharePct: 0.85 },
      { band: '25-34', customers: 1877, stakeSharePct: 24.18, revenueSharePct: 18.25 },
      { band: '35-44', customers: 3070, stakeSharePct: 49.26, revenueSharePct: 57.49 },
      { band: '45-54', customers: 1899, stakeSharePct: 15.89, revenueSharePct: 8.50 },
      { band: '55-64', customers: 598, stakeSharePct: 8.36, revenueSharePct: 12.23 },
      { band: '65+', customers: 128, stakeSharePct: 1.86, revenueSharePct: 2.68 }
    ],
    countries: [
      { name: 'South Africa', customers: 7325, stakeSharePct: 97.79, revenueSharePct: 97.99 },
      { name: 'Unknown', customers: 198, stakeSharePct: 0.96, revenueSharePct: 0.85 },
      { name: 'Rest of world (35+ countries)', customers: 395, stakeSharePct: 1.25, revenueSharePct: 1.16 }
    ]
  },
  // Highest revenue-generating customers across May-July, ranked by operator revenue
  // (stake minus payout) -- the most commercially valuable customers. This is NOT a
  // ranking of customers who won the most money (that would be a payout-risk list).
  customers: [
    { user: '2962029', txn: 36, stake: 62913121.40, revenue: 3296491.28, marginPct: 5.24 },
    { user: '2962088', txn: 66, stake: 15683830.20, revenue: 2164780.45, marginPct: 13.80 },
    { user: '2968777', txn: 23, stake: 45593176.25, revenue: 1933999.58, marginPct: 4.24 },
    { user: '2963031', txn: 65, stake: 17162803.03, revenue: 1205063.32, marginPct: 7.02 },
    { user: '2963504', txn: 78, stake: 8010079.00, revenue: 1023654.74, marginPct: 12.78 }
  ],
  // Period-wide sample (top 40 customers by stake) used for the profitability scatter.
  // X = net_margin_pct (operator revenue / stake), Y = operator revenue from this
  // customer. Positive = profitable for the operator; negative = this customer was a
  // net winner (payout exposure).
  customerScatter: [
    { marginPct: 5.24, revenue: 3296491.28 }, { marginPct: 4.24, revenue: 1933999.58 },
    { marginPct: 4.01, revenue: 726002.45 }, { marginPct: 7.02, revenue: 1205063.32 },
    { marginPct: 13.80, revenue: 2164780.45 }, { marginPct: -6.36, revenue: -894038.65 },
    { marginPct: 2.28, revenue: 308297.84 }, { marginPct: 1.96, revenue: 247242.30 },
    { marginPct: 3.88, revenue: 424285.38 }, { marginPct: 0.74, revenue: 73423.98 },
    { marginPct: 3.54, revenue: 339497.84 }, { marginPct: 2.77, revenue: 262327.41 },
    { marginPct: 2.44, revenue: 218445.02 }, { marginPct: -2.37, revenue: -211454.98 },
    { marginPct: 3.99, revenue: 325296.82 }, { marginPct: 12.78, revenue: 1023654.74 },
    { marginPct: 1.30, revenue: 93931.30 }, { marginPct: -3.86, revenue: -248626.96 },
    { marginPct: 5.66, revenue: 343501.57 }, { marginPct: 11.27, revenue: 597866.61 },
    { marginPct: -6.70, revenue: -335103.51 }, { marginPct: 5.49, revenue: 254598.39 },
    { marginPct: 3.06, revenue: 140398.76 }, { marginPct: 2.63, revenue: 120491.60 },
    { marginPct: -8.98, revenue: -406095.78 }, { marginPct: 19.26, revenue: 862192.56 },
    { marginPct: 10.97, revenue: 456339.49 }, { marginPct: 5.77, revenue: 229805.45 },
    { marginPct: 9.42, revenue: 362083.08 }, { marginPct: 6.96, revenue: 265111.07 },
    { marginPct: 2.91, revenue: 100444.81 }, { marginPct: 5.14, revenue: 174372.98 },
    { marginPct: -10.66, revenue: -344871.29 }, { marginPct: 0.68, revenue: 21970.14 },
    { marginPct: 0.81, revenue: 25558.53 }, { marginPct: 4.02, revenue: 123737.77 },
    { marginPct: 2.25, revenue: 69107.36 }, { marginPct: 1.80, revenue: 52791.94 },
    { marginPct: -9.78, revenue: -283265.62 }, { marginPct: 4.90, revenue: 140316.18 }
  ]
};

// Shared page state: changing either of these and calling renderAll() updates every
// reactive visual present on the current page.
const state = {
  month: 'July',
  product: null
};

function setMonth(month) {
  state.month = month;
  renderAll();
}

function setProduct(name) {
  state.product = state.product === name ? null : name;
  renderAll();
}

const formatShortCurrency = (value) => {
  const sign = value < 0 ? '-' : '';
  const abs = Math.abs(value);
  if (abs >= 1000000) return `${sign}R${(abs / 1000000).toFixed(1)}m`;
  if (abs >= 1000) return `${sign}R${(abs / 1000).toFixed(1)}k`;
  return `${sign}R${abs.toFixed(0)}`;
};

const formatNumber = (value) => new Intl.NumberFormat('en-ZA', { maximumFractionDigits: 0 }).format(value);
const formatCurrency = (value) => new Intl.NumberFormat('en-ZA', { style: 'currency', currency: 'ZAR', maximumFractionDigits: 0 }).format(value);

function renderMonthFilters() {
  const container = document.getElementById('monthFilter');
  if (!container) return;

  container.innerHTML = MONTH_ORDER.map(month => `
    <button type="button" class="month-pill ${month === state.month ? 'is-selected' : ''}" data-month="${month}">${month}</button>
  `).join('');

  container.querySelectorAll('.month-pill').forEach(btn => {
    btn.addEventListener('click', () => setMonth(btn.dataset.month));
  });
}

function renderKpis() {
  const container = document.getElementById('kpiCards');
  if (!container) return;

  const m = dashboardData.monthly[state.month];
  const r = dashboardData.risk[state.month];
  const prevIndex = MONTH_ORDER.indexOf(state.month) - 1;
  const prevMonth = prevIndex >= 0 ? MONTH_ORDER[prevIndex] : null;
  const growthMeta = prevMonth
    ? `${(((m.activeCustomers - dashboardData.monthly[prevMonth].activeCustomers) / dashboardData.monthly[prevMonth].activeCustomers) * 100).toFixed(0)}% vs ${prevMonth}`
    : 'First month in range';

  const kpiCards = [
    { label: 'Active customers', value: formatNumber(m.activeCustomers), meta: growthMeta, tone: 'positive' },
    { label: 'Total stake', value: formatShortCurrency(m.totalStake), meta: state.month, tone: 'neutral' },
    { label: 'Operator revenue', value: `+${formatShortCurrency(m.operatorRevenue)}`, meta: 'Stake minus payout', tone: 'positive' },
    { label: 'Operator margin', value: `${r.operatorMarginPct.toFixed(1)}%`, meta: 'House edge', tone: 'neutral' }
  ];

  container.innerHTML = kpiCards.map(card => `
    <article class="kpi-card">
      <p class="label">${card.label}</p>
      <p class="value">${card.value}</p>
      <p class="meta ${card.tone}">${card.meta}</p>
    </article>
  `).join('');
}

function createTrendChart() {
  const chart = document.getElementById('trendChart');
  if (!chart) return;

  const width = 760;
  const height = 280;
  const leftPad = 42;
  const rightPad = 18;
  const topPad = 18;
  const bottomPad = 32;
  const monthlySeries = MONTH_ORDER.map(month => ({ month, ...dashboardData.monthly[month] }));
  const maxStake = Math.max(...monthlySeries.map(d => d.totalStake));
  const maxRevenue = Math.max(...monthlySeries.map(d => d.operatorRevenue));

  const xForIndex = (i) => leftPad + (i * (width - leftPad - rightPad)) / (monthlySeries.length - 1);
  const yForStake = (v) => height - bottomPad - ((v / maxStake) * (height - topPad - bottomPad));
  const yForRevenue = (v) => height - bottomPad - ((v / maxRevenue) * (height - topPad - bottomPad));

  const stakePoints = monthlySeries.map((d, i) => `${xForIndex(i)},${yForStake(d.totalStake)}`).join(' ');
  const revenuePoints = monthlySeries.map((d, i) => `${xForIndex(i)},${yForRevenue(d.operatorRevenue)}`).join(' ');

  const grid = Array.from({ length: 5 }, (_, i) => {
    const y = 18 + (i * (height - 48)) / 4;
    return `<line x1="42" y1="${y}" x2="${width - 16}" y2="${y}" stroke="rgba(11,78,162,0.08)" stroke-width="1" />`;
  }).join('');

  const labels = monthlySeries.map((d, i) => `
    <text x="${xForIndex(i)}" y="${height - 10}" text-anchor="middle" fill="#6884a8" font-size="12">${d.month}</text>
  `).join('');

  // Clickable markers on the revenue line double as the month selector for this chart.
  const markers = monthlySeries.map((d, i) => `
    <circle class="trend-marker" data-month="${d.month}" cx="${xForIndex(i)}" cy="${yForRevenue(d.operatorRevenue)}"
      r="${d.month === state.month ? 7 : 5}" fill="${d.month === state.month ? '#f5c84c' : '#0a4fcf'}"
      stroke="#ffffff" stroke-width="2" style="cursor:pointer" />
  `).join('');

  chart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="Monthly performance chart">
      ${grid}
      <polyline points="${stakePoints}" fill="none" stroke="#f5c84c" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
      <polyline points="${revenuePoints}" fill="none" stroke="#0a4fcf" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
      ${markers}
      <text x="42" y="18" fill="#6884a8" font-size="12">Stake</text>
      <text x="116" y="18" fill="#6884a8" font-size="12">Operator revenue (click a point to filter the page)</text>
      ${labels}
    </svg>
  `;

  chart.querySelectorAll('.trend-marker').forEach(el => {
    el.addEventListener('click', () => setMonth(el.dataset.month));
  });
}

function renderMonthlyActiveBarChart() {
  const container = document.getElementById('monthlyActiveBars');
  if (!container) return;

  const max = Math.max(...MONTH_ORDER.map(m => dashboardData.monthly[m].activeCustomers));
  container.innerHTML = MONTH_ORDER.map(month => {
    const value = dashboardData.monthly[month].activeCustomers;
    const heightPct = (value / max) * 100;
    return `
      <div class="bar-chart-col ${month === state.month ? 'is-selected' : ''}" data-month="${month}">
        <div class="bar-chart-value">${formatNumber(value)}</div>
        <div class="bar-chart-col-fill" style="height:${heightPct}%"></div>
        <div class="bar-chart-label">${month}</div>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.bar-chart-col').forEach(el => {
    el.addEventListener('click', () => setMonth(el.dataset.month));
  });
}

function renderProductDonut() {
  const svgContainer = document.getElementById('productDonut');
  const legendContainer = document.getElementById('productDonutLegend');
  if (!svgContainer && !legendContainer) return;

  const products = dashboardData.product[state.month];
  const total = products.reduce((sum, p) => sum + p.value, 0);
  const r = 70;
  const strokeWidth = 32;
  const circumference = 2 * Math.PI * r;
  let cumulative = 0;

  if (svgContainer) {
    const slices = products.map(p => {
      const share = p.value / total;
      const dash = share * circumference;
      const offset = -cumulative * circumference;
      cumulative += share;
      const isSelected = state.product === p.name;
      return `
        <circle class="donut-slice ${isSelected ? 'is-selected' : ''}" data-product="${p.name}"
          cx="110" cy="110" r="${r}" fill="none" stroke="${PRODUCT_COLORS[p.name] || '#999'}"
          stroke-width="${strokeWidth}" stroke-dasharray="${dash} ${circumference - dash}"
          stroke-dashoffset="${offset}" transform="rotate(-90 110 110)" />
      `;
    }).join('');

    svgContainer.innerHTML = `
      <svg viewBox="0 0 220 220" width="220" height="220" aria-label="Product contribution donut chart">
        ${slices}
        <text x="110" y="104" text-anchor="middle" font-size="13" fill="#6884a8">${state.month} stake</text>
        <text x="110" y="126" text-anchor="middle" font-size="16" font-weight="700" fill="#153450">${formatShortCurrency(total)}</text>
      </svg>
    `;

    svgContainer.querySelectorAll('.donut-slice').forEach(el => {
      el.addEventListener('click', () => setProduct(el.dataset.product));
    });
  }

  if (legendContainer) {
    legendContainer.innerHTML = products.map(p => {
      const sharePct = (p.value / total) * 100;
      const isSelected = state.product === p.name;
      return `
        <div class="donut-legend-item ${isSelected ? 'is-selected' : ''}" data-product="${p.name}">
          <span class="donut-legend-swatch" style="background:${PRODUCT_COLORS[p.name] || '#999'}"></span>
          <span class="donut-legend-name">${p.name}</span>
          <span class="donut-legend-value">${sharePct.toFixed(1)}%</span>
        </div>
      `;
    }).join('');

    legendContainer.querySelectorAll('.donut-legend-item').forEach(el => {
      el.addEventListener('click', () => setProduct(el.dataset.product));
    });
  }
}

function renderProductBars() {
  const container = document.getElementById('productBars');
  if (!container) return;

  const products = dashboardData.product[state.month];
  const max = Math.max(...products.map(d => d.value));
  container.innerHTML = products.map(product => {
    const width = (product.value / max) * 100;
    const isSelected = state.product === product.name;
    return `
      <div class="product-row ${isSelected ? 'is-selected' : ''}" data-product="${product.name}" style="cursor:pointer; ${isSelected ? 'outline:2px solid var(--brand-blue); border-radius:10px;' : ''}">
        <div class="product-label">${product.name}</div>
        <div class="bar-track"><div class="bar-fill" style="width:${width}%; ${isSelected ? `background:${PRODUCT_COLORS[product.name]}` : ''}"></div></div>
        <div class="product-value">${formatShortCurrency(product.value)}</div>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.product-row').forEach(el => {
    el.addEventListener('click', () => setProduct(el.dataset.product));
  });
}

function renderRetentionTable() {
  const container = document.getElementById('retentionTable');
  if (!container) return;

  const months = ['July', 'June', 'May'];
  const rows = dashboardData.retention.map((row) => {
    const cells = months.map((month) => {
      const value = row[month];
      if (value === null || value === undefined) return '<td>—</td>';
      const cls = value >= 80 ? 'cell-good' : 'cell-risk';
      return `<td><span class="${cls}">${value.toFixed(2)}%</span></td>`;
    }).join('');

    return `<tr><td>${row.cohort}</td>${cells}</tr>`;
  }).join('');

  container.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Cohort</th>
          <th>July</th>
          <th>June</th>
          <th>May</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderRisk() {
  const container = document.getElementById('riskSummary');
  if (!container) return;

  const r = dashboardData.risk[state.month];
  const items = [
    { label: 'Operator margin (house edge)', value: r.operatorMarginPct },
    { label: `Stake from large-stake transactions (>R${formatNumber(r.largeStakeThreshold)})`, value: r.largeStakeSharePct },
    { label: 'Transactions where customer won (payout exposure)', value: r.customerWinSharePct },
    { label: 'Stake concentration: top 10 users', value: r.top10SharePct }
  ];

  container.innerHTML = items.map(item => `
    <div class="risk-item">
      <div class="risk-header">
        <span>${item.label}</span>
        <strong>${item.value.toFixed(1)}%</strong>
      </div>
      <div class="risk-track">
        <div class="risk-fill" style="width:${Math.min(item.value, 100)}%"></div>
      </div>
    </div>
  `).join('');
}

function renderStakeSegments() {
  const container = document.getElementById('stakeSegments');
  if (!container) return;

  const segments = dashboardData.stakeSegments[state.month];
  container.innerHTML = segments.map(segment => `
    <div class="risk-item">
      <div class="risk-header">
        <span>${segment.band} &middot; ${formatNumber(segment.users)} users</span>
        <strong>${segment.sharePct.toFixed(1)}% of ${state.month} stake</strong>
      </div>
      <div class="risk-track">
        <div class="risk-fill" style="width:${segment.sharePct}%"></div>
      </div>
    </div>
  `).join('');
}

function renderCustomerList() {
  const container = document.getElementById('customerList');
  if (!container) return;

  container.innerHTML = dashboardData.customers.map(customer => `
    <article class="customer-item">
      <div class="name">User ${customer.user}</div>
      <div class="line"><span>Transactions</span><strong>${customer.txn}</strong></div>
      <div class="line"><span>Stake</span><strong>${formatShortCurrency(customer.stake)}</strong></div>
      <div class="line"><span>Operator revenue</span><strong class="positive">${formatCurrency(customer.revenue)}</strong></div>
      <div class="line"><span>Margin</span><strong>${customer.marginPct.toFixed(1)}%</strong></div>
    </article>
  `).join('');
}

function renderTopStakeBarChart() {
  const container = document.getElementById('topStakeBars');
  if (!container) return;

  const max = Math.max(...dashboardData.customers.map(c => c.stake));
  container.innerHTML = dashboardData.customers.map(customer => `
    <div class="bar-chart-col">
      <div class="bar-chart-value">${formatShortCurrency(customer.stake)}</div>
      <div class="bar-chart-col-fill" style="height:${(customer.stake / max) * 100}%"></div>
      <div class="bar-chart-label">${customer.user}</div>
    </div>
  `).join('');
}

function renderCustomerScatter() {
  const chart = document.getElementById('customerScatter');
  if (!chart) return;

  const width = 520;
  const height = 260;
  const leftPad = 54;
  const rightPad = 20;
  const topPad = 16;
  const bottomPad = 30;
  const data = dashboardData.customerScatter;
  const maxMargin = Math.max(...data.map(d => Math.abs(d.marginPct))) * 1.1;
  const maxRevenue = Math.max(...data.map(d => Math.abs(d.revenue))) * 1.1;

  const xFor = (v) => leftPad + ((v + maxMargin) / (maxMargin * 2)) * (width - leftPad - rightPad);
  const yFor = (v) => height - bottomPad - ((v + maxRevenue) / (maxRevenue * 2)) * (height - topPad - bottomPad);

  const zeroX = xFor(0);
  const zeroY = yFor(0);
  const dots = data.map(d => {
    const color = d.revenue >= 0 ? '#1fa77a' : '#d95d5d';
    return `<circle class="scatter-dot" cx="${xFor(d.marginPct)}" cy="${yFor(d.revenue)}" r="5" fill="${color}" fill-opacity="0.75" stroke="#ffffff" stroke-width="1">
      <title>Margin ${d.marginPct.toFixed(1)}% / Operator revenue ${formatShortCurrency(d.revenue)}</title>
    </circle>`;
  }).join('');

  chart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="Customer margin vs operator revenue scatter chart">
      <line x1="${leftPad}" y1="${zeroY}" x2="${width - rightPad}" y2="${zeroY}" stroke="#dfeaf9" stroke-width="1" />
      <line x1="${zeroX}" y1="${topPad}" x2="${zeroX}" y2="${height - bottomPad}" stroke="#dfeaf9" stroke-width="1" />
      <text x="4" y="${zeroY + 4}" font-size="11" fill="#6884a8">R0</text>
      <text x="${leftPad}" y="${height - 8}" font-size="11" fill="#6884a8">Lower margin %</text>
      <text x="${width - rightPad - 100}" y="${height - 8}" font-size="11" fill="#6884a8">Higher margin % &rarr;</text>
      ${dots}
    </svg>
  `;
}

// --- Page 2 additions: Customer Behaviour and Retention ---

function renderCustomerSummaryKpis() {
  const container = document.getElementById('customerKpiCards');
  if (!container) return;

  const s = dashboardData.customerSummary;
  const cards = [
    { label: 'Active customers', value: formatNumber(s.activeCustomers), meta: 'May-July, distinct', tone: 'neutral' },
    { label: 'Total transactions', value: formatNumber(s.totalTransactions), meta: 'May-July total', tone: 'neutral' },
    { label: 'Total stake', value: formatShortCurrency(s.totalStake), meta: 'May-July total', tone: 'neutral' },
    { label: 'Operator revenue', value: `+${formatShortCurrency(s.totalOperatorRevenue)}`, meta: 'May-July total', tone: 'positive' },
    { label: 'Avg customer margin', value: `${s.avgMarginPct.toFixed(1)}%`, meta: 'Unweighted avg -- see footnote', tone: 'neutral' }
  ];

  container.innerHTML = cards.map(card => `
    <article class="kpi-card">
      <p class="label">${card.label}</p>
      <p class="value">${card.value}</p>
      <p class="meta ${card.tone}">${card.meta}</p>
    </article>
  `).join('');
}

function renderCustomerActivityChart() {
  const container = document.getElementById('customerActivityBars');
  if (!container) return;

  const max = Math.max(...MONTH_ORDER.map(m => dashboardData.customerActivityByMonth[m]));
  container.innerHTML = MONTH_ORDER.map(month => {
    const value = dashboardData.customerActivityByMonth[month];
    return `
      <div class="bar-chart-col">
        <div class="bar-chart-value">${formatNumber(value)}</div>
        <div class="bar-chart-col-fill" style="height:${(value / max) * 100}%"></div>
        <div class="bar-chart-label">${month}</div>
      </div>
    `;
  }).join('');
}

function renderCustomerDetailTable() {
  const container = document.getElementById('customerDetailTable');
  if (!container) return;

  const rows = dashboardData.customerDetail.map(c => `
    <tr>
      <td>${c.user}</td>
      <td>${c.txn}</td>
      <td>${formatShortCurrency(c.stake)}</td>
      <td>${formatShortCurrency(c.win)}</td>
      <td class="${c.revenue >= 0 ? 'cell-good' : 'cell-risk'}">${formatShortCurrency(c.revenue)}</td>
      <td>${c.marginPct.toFixed(1)}%</td>
      <td>${c.lastMonth}</td>
    </tr>
  `).join('');

  container.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>User ID</th><th>Transactions</th><th>Stake</th><th>Win</th>
          <th>Operator revenue</th><th>Margin</th><th>Last active</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderAgeBandChart() {
  const container = document.getElementById('ageBandBars');
  if (!container) return;

  container.innerHTML = dashboardData.demographics.ageBands.map(a => `
    <div class="risk-item">
      <div class="risk-header">
        <span>${a.band} &middot; ${formatNumber(a.customers)} customers</span>
        <strong>${a.stakeSharePct.toFixed(1)}% of stake / ${a.revenueSharePct.toFixed(1)}% of revenue</strong>
      </div>
      <div class="risk-track">
        <div class="risk-fill" style="width:${a.stakeSharePct}%"></div>
      </div>
    </div>
  `).join('');
}

function renderCountryChart() {
  const container = document.getElementById('countryBars');
  if (!container) return;

  container.innerHTML = dashboardData.demographics.countries.map(c => `
    <div class="risk-item">
      <div class="risk-header">
        <span>${c.name} &middot; ${formatNumber(c.customers)} customers</span>
        <strong>${c.stakeSharePct.toFixed(1)}% of stake</strong>
      </div>
      <div class="risk-track">
        <div class="risk-fill" style="width:${c.stakeSharePct}%"></div>
      </div>
    </div>
  `).join('');
}

// --- Page 3 addition: Financial Performance and Product Mix ---

function renderProductTable() {
  const container = document.getElementById('productTable');
  if (!container) return;

  const products = [...dashboardData.product[state.month]].sort((a, b) => b.value - a.value);
  const rows = products.map(p => `
    <tr class="${state.product === p.name ? 'cell-good' : ''}">
      <td>${p.name}</td>
      <td>${formatShortCurrency(p.value)}</td>
      <td class="${p.revenue >= 0 ? 'cell-good' : 'cell-risk'}">${formatShortCurrency(p.revenue)}</td>
      <td>${((p.revenue / p.value) * 100).toFixed(1)}%</td>
    </tr>
  `).join('');

  container.innerHTML = `
    <table>
      <thead><tr><th>Product category</th><th>Est. stake</th><th>Est. operator revenue</th><th>Est. margin</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

// --- Page 4 additions: Risk & Concentration Monitoring ---

function renderRiskTrendChart() {
  const chart = document.getElementById('riskTrendChart');
  if (!chart) return;

  const width = 720;
  const height = 240;
  const leftPad = 42;
  const rightPad = 18;
  const topPad = 18;
  const bottomPad = 32;
  const series = MONTH_ORDER.map(m => ({ month: m, ...dashboardData.risk[m] }));
  const maxMargin = Math.max(...series.map(d => d.operatorMarginPct)) * 1.3;
  const maxConcentration = Math.max(...series.map(d => d.top10SharePct)) * 1.1;

  const xForIndex = (i) => leftPad + (i * (width - leftPad - rightPad)) / (series.length - 1);
  const yForMargin = (v) => height - bottomPad - (v / maxMargin) * (height - topPad - bottomPad);
  const yForConc = (v) => height - bottomPad - (v / maxConcentration) * (height - topPad - bottomPad);

  const marginPoints = series.map((d, i) => `${xForIndex(i)},${yForMargin(d.operatorMarginPct)}`).join(' ');
  const concPoints = series.map((d, i) => `${xForIndex(i)},${yForConc(d.top10SharePct)}`).join(' ');
  const labels = series.map((d, i) => `<text x="${xForIndex(i)}" y="${height - 10}" text-anchor="middle" fill="#6884a8" font-size="12">${d.month}</text>`).join('');

  chart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="Risk exposure trend chart">
      <polyline points="${marginPoints}" fill="none" stroke="#0a4fcf" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
      <polyline points="${concPoints}" fill="none" stroke="#d95d5d" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
      <text x="42" y="18" fill="#0a4fcf" font-size="12">Operator margin %</text>
      <text x="200" y="18" fill="#d95d5d" font-size="12">Top-10 user stake share % (concentration)</text>
      ${labels}
    </svg>
  `;
}

function renderLargeStakeBarChart() {
  const container = document.getElementById('largeStakeBars');
  if (!container) return;

  const max = Math.max(...MONTH_ORDER.map(m => dashboardData.risk[m].largeStakeTransactionCount));
  container.innerHTML = MONTH_ORDER.map(month => {
    const r = dashboardData.risk[month];
    return `
      <div class="bar-chart-col ${month === state.month ? 'is-selected' : ''}" data-month="${month}">
        <div class="bar-chart-value">${formatNumber(r.largeStakeTransactionCount)}</div>
        <div class="bar-chart-col-fill" style="height:${(r.largeStakeTransactionCount / max) * 100}%"></div>
        <div class="bar-chart-label">${month}</div>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.bar-chart-col').forEach(el => {
    el.addEventListener('click', () => setMonth(el.dataset.month));
  });
}

function renderCustomerWinBarChart() {
  const container = document.getElementById('customerWinBars');
  if (!container) return;

  const max = Math.max(...MONTH_ORDER.map(m => dashboardData.risk[m].customerWinEventCount));
  container.innerHTML = MONTH_ORDER.map(month => {
    const r = dashboardData.risk[month];
    return `
      <div class="bar-chart-col ${month === state.month ? 'is-selected' : ''}" data-month="${month}">
        <div class="bar-chart-value">${formatNumber(r.customerWinEventCount)}</div>
        <div class="bar-chart-col-fill" style="height:${(r.customerWinEventCount / max) * 100}%; background:linear-gradient(180deg, #ffd166 0%, #d9ad1d 100%);"></div>
        <div class="bar-chart-label">${month}</div>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.bar-chart-col').forEach(el => {
    el.addEventListener('click', () => setMonth(el.dataset.month));
  });
}

function renderRiskSummaryTable() {
  const container = document.getElementById('riskTable');
  if (!container) return;

  const rows = MONTH_ORDER.map(month => {
    const r = dashboardData.risk[month];
    return `
      <tr class="${month === state.month ? 'cell-good' : ''}">
        <td>${month}</td>
        <td>${formatNumber(r.totalTransactions)}</td>
        <td>R${formatNumber(r.largeStakeThreshold)}</td>
        <td>${formatNumber(r.largeStakeTransactionCount)}</td>
        <td>${r.largeStakeSharePct.toFixed(1)}%</td>
        <td>${formatNumber(r.customerWinEventCount)}</td>
        <td>${r.customerWinSharePct.toFixed(1)}%</td>
        <td>${r.top10SharePct.toFixed(1)}%</td>
        <td>${r.operatorMarginPct.toFixed(1)}%</td>
      </tr>
    `;
  }).join('');

  container.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Month</th><th>Transactions</th><th>Large-stake threshold</th><th>Large-stake txns</th>
          <th>Large-stake share</th><th>Customer-win events</th><th>Customer-win share</th>
          <th>Top-10 stake share</th><th>Operator margin</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

// --- Page 5 additions: Growth Opportunities ---

function renderRetentionLiftChart() {
  const container = document.getElementById('retentionLiftBars');
  if (!container) return;

  const rows = dashboardData.retention.filter(r => r.July !== null && r.July !== undefined);
  const max = Math.max(...rows.map(r => r.July));
  container.innerHTML = rows.map(r => `
    <div class="bar-chart-col">
      <div class="bar-chart-value">${r.July.toFixed(1)}%</div>
      <div class="bar-chart-col-fill" style="height:${(r.July / max) * 100}%"></div>
      <div class="bar-chart-label">${r.cohort}</div>
    </div>
  `).join('');
}

function renderGrowthSegmentChart() {
  const container = document.getElementById('growthSegmentBars');
  if (!container) return;

  const segments = dashboardData.segmentRevenue.July;
  const max = Math.max(...segments.map(s => s.sharePct));
  container.innerHTML = segments.map(s => `
    <div class="risk-item">
      <div class="risk-header">
        <span>${s.band}</span>
        <strong>${s.sharePct.toFixed(1)}% of July operator revenue</strong>
      </div>
      <div class="risk-track">
        <div class="risk-fill" style="width:${(s.sharePct / max) * 100}%"></div>
      </div>
    </div>
  `).join('');
}

function renderProductPriorityChart() {
  const container = document.getElementById('productPriorityBars');
  if (!container) return;

  const products = [...dashboardData.product.July].sort((a, b) => b.revenue - a.revenue);
  const max = Math.max(...products.map(p => Math.abs(p.revenue)));
  container.innerHTML = products.map(p => `
    <div class="product-row">
      <div class="product-label">${p.name}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${(Math.abs(p.revenue) / max) * 100}%; background:${p.revenue >= 0 ? 'linear-gradient(90deg, var(--brand-blue) 0%, var(--success) 100%)' : 'linear-gradient(90deg, var(--brand-blue) 0%, var(--danger) 100%)'}"></div></div>
      <div class="product-value">${formatShortCurrency(p.revenue)}</div>
    </div>
  `).join('');
}

function renderAll() {
  renderMonthFilters();
  renderKpis();
  createTrendChart();
  renderMonthlyActiveBarChart();
  renderProductDonut();
  renderProductBars();
  renderProductTable();
  renderRetentionTable();
  renderRisk();
  renderStakeSegments();
  renderCustomerList();
  renderTopStakeBarChart();
  renderCustomerScatter();
  renderCustomerSummaryKpis();
  renderCustomerActivityChart();
  renderCustomerDetailTable();
  renderAgeBandChart();
  renderCountryChart();
  renderRiskTrendChart();
  renderLargeStakeBarChart();
  renderCustomerWinBarChart();
  renderRiskSummaryTable();
  renderRetentionLiftChart();
  renderGrowthSegmentChart();
  renderProductPriorityChart();
}

renderAll();


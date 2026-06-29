const API_BASE = 'http://localhost:8000';

// 转义与风险判定工具（来自 lib/sanitize.js、lib/risk.js）
const { escapeHtml, escapeAttr } = window.AlphaSanitize || {};
const { countHighRiskAssets } = window.AlphaRisk || {};

// State
let currentResults = [];
let originalResults = []; // Store full dataset for filtering
let currentQueryId = null;
let charts = {};

// DOM Elements
const dom = {
    input: document.getElementById('nl-query-input'),
    searchBtn: document.getElementById('search-btn'),
    platformSelect: document.getElementById('platform-select'),
    resultsContainer: document.getElementById('results-container'),
    queryStatusText: document.getElementById('query-status-text'),
    analyzeBtn: document.getElementById('analyze-btn'),
    stats: {
        total: document.getElementById('total-assets'),
        highRisk: document.getElementById('high-risk'),
        queryCount: document.getElementById('query-count'),
        countries: document.getElementById('country-count')
    },
    overlay: document.getElementById('scanning-overlay'),
    progressBar: document.getElementById('scan-progress'),
    currentTime: document.getElementById('current-time'),
    viewAllBtn: document.getElementById('view-all-btn')
};

// Reset Filter Logic
dom.viewAllBtn.addEventListener('click', () => {
    updateUI(originalResults, false); // Restore original data
    dom.viewAllBtn.style.display = 'none';
    dom.queryStatusText.innerText = `资产列表 [${originalResults.length}]`;
});

// Initialize Charts
function initCharts() {
    charts.port = echarts.init(document.getElementById('port-chart'));
    charts.protocol = echarts.init(document.getElementById('protocol-chart'));
    charts.map = echarts.init(document.getElementById('geo-map'));

    window.addEventListener('resize', () => {
        Object.values(charts).forEach(chart => chart.resize());
    });

    // Add Click Listeners for Interaction
    if (charts.port) {
        charts.port.on('click', function (params) {
            filterResults('port', params.name);
        });
    }

    if (charts.protocol) {
        charts.protocol.on('click', function (params) {
            filterResults('protocol', params.name);
        });
    }

    // Set initial empty states
    const commonOption = {
        grid: { top: 30, right: 10, bottom: 20, left: 40 },
        textStyle: { fontFamily: 'Rajdhani' },
        tooltip: { trigger: 'item', backgroundColor: 'rgba(0,0,0,0.8)', borderColor: '#00f2ff', textStyle: { color: '#fff' } }
    };

    charts.port.setOption({
        ...commonOption,
        xAxis: { type: 'category', data: [], axisLabel: { color: '#94a3b8' } },
        yAxis: { type: 'value', splitLine: { lineStyle: { color: '#334155' } }, axisLabel: { color: '#94a3b8' } },
        series: [{ type: 'bar', data: [], itemStyle: { color: '#00f2ff' } }]
    });

    charts.protocol.setOption({
        ...commonOption,
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            itemStyle: { borderRadius: 5, borderColor: '#050b14', borderWidth: 2 },
            label: { color: '#fff' },
            data: []
        }]
    });

    charts.map.setOption({
        geo: {
            map: 'world',
            roam: true,
            itemStyle: {
                areaColor: '#1e293b',
                borderColor: '#40a9ff'
            },
            emphasis: {
                itemStyle: { areaColor: '#00f2ff' }
            }
        },
        series: []
    });
}

// Clock
function updateTime() {
    const now = new Date();
    dom.currentTime.innerHTML = `
        ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}<span style="font-size:14px; margin-left:5px">:${now.getSeconds().toString().padStart(2, '0')}</span>
    `;
}
setInterval(updateTime, 1000);
updateTime();

// Search Logic
dom.searchBtn.addEventListener('click', async () => {
    const query = dom.input.value.trim();
    if (!query) return;

    const platform = dom.platformSelect.value;

    // UI Scanning State
    dom.overlay.style.display = 'flex';
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress > 90) progress = 90;
        dom.progressBar.style.width = `${progress}%`;
    }, 200);

    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nl_query: query, platform: platform })
        });

        const data = await response.json();

        clearInterval(progressInterval);
        dom.progressBar.style.width = '100%';

        setTimeout(() => {
            dom.overlay.style.display = 'none';
            dom.progressBar.style.width = '0%';

            if (response.ok) {
                console.log('Query Source:', data.source); // Debug log
                currentResults = data.results;
                currentQueryId = data.query_id;
                updateUI(data.results, true).then(() => {
                    dom.queryStatusText.innerText = `资产列表 [${data.results.length}]`;
                    dom.analyzeBtn.disabled = data.results.length === 0;
                    loadHistory(); // Refresh history
                });
            } else {
                alert('Search failed: ' + data.detail);
            }
        }, 500);

    } catch (error) {
        clearInterval(progressInterval);
        dom.overlay.style.display = 'none';
        alert('Error: ' + error.message);
    }
});

// Update Dashboard with Results
async function updateUI(results, updateCharts = true) {
    if (updateCharts) {
        originalResults = results; // Save for filtering
    }
    currentResults = results;

    if (results.length === 0) {
        dom.resultsContainer.innerHTML = '<div class="empty-state"><i class="fas fa-satellite-dish"></i><p>未发现目标资产</p></div>';
        // Still update stats even if empty to clear them
        if (updateCharts) updateChartsData(results);
        return;
    }

    // 1. Update Asset List
    dom.resultsContainer.innerHTML = results.map((asset, idx) => {
        // Smart Fallbacks
        let displayTitle = asset.title;
        if (!displayTitle || !displayTitle.trim()) {
            displayTitle = asset.host || asset.domain || `${asset.ip}:${asset.port}`;
        }
        if (displayTitle.length > 60) displayTitle = displayTitle.substring(0, 60) + '...';

        const displayServer = asset.server || asset.protocol || 'Unknown Svc';
        const displayLocation = [asset.country, asset.city].filter(Boolean).join(' ') || 'Unknown Loc';
        const displayOrg = asset.org || 'Unknown Org';

        return `
        <div class="asset-card" onclick="showAssetDetail(${idx})" data-asset-index="${idx}">
            <div class="card-row">
                <span class="ip-address">${escapeHtml(asset.ip)}</span>
                <span class="port-badge">${escapeHtml(asset.port)}</span>
            </div>
            <div class="asset-title" title="${escapeAttr(displayTitle)}">${escapeHtml(displayTitle)}</div>
            <div class="asset-meta">
                <div class="meta-item" title="Location"><i class="fas fa-globe"></i> ${escapeHtml(displayLocation)}</div>
                <div class="meta-item" title="Server"><i class="fas fa-server"></i> ${escapeHtml(displayServer)}</div>
                <div class="meta-item" title="Organization"><i class="fas fa-building"></i> ${escapeHtml(displayOrg)}</div>
            </div>
        </div>
        `;
    }).join('');

    // 2. Update Stats
    dom.stats.total.innerText = results.length;
    // 高危资产：基于暴露的敏感端口（SSH/RDP/数据库等）真实统计，取代原 Math.random() 假数据
    dom.stats.highRisk.innerText = countHighRiskAssets ? countHighRiskAssets(results) : 0;
    const uniqueCountries = new Set(results.map(r => r.country)).size;
    dom.stats.countries.innerText = uniqueCountries;

    // 3. Update Charts and Map
    updateCharts(results);
    // Map update is handled by global stats or specific filter logic
}

function updateCharts(results) {
    // Port Distribution
    const ports = {};
    results.forEach(r => ports[r.port] = (ports[r.port] || 0) + 1);
    const portData = Object.entries(ports)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    charts.port.setOption({
        xAxis: { data: portData.map(d => d[0]) },
        series: [{ data: portData.map(d => d[1]) }]
    });

    // Protocol Distribution
    const protocols = {};
    results.forEach(r => protocols[r.protocol || 'unknown'] = (protocols[r.protocol || 'unknown'] || 0) + 1);
    const protocolData = Object.entries(protocols).map(([name, value]) => ({ name, value }));

    charts.protocol.setOption({
        series: [{ data: protocolData }]
    });
}

// Update map and charts with global stats
async function initDashboard() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const stats = await response.json();

        // 1. Update Global Numbers
        dom.stats.total.innerText = stats.total_assets;
        dom.stats.countries.innerText = Object.keys(stats.country_distribution).length;

        // 2. Update Map
        if (stats.geo_distribution && stats.geo_distribution.length > 0) {
            charts.map.setOption({
                geo: {
                    map: 'world',
                    roam: true,
                    itemStyle: {
                        areaColor: '#1e293b',
                        borderColor: '#40a9ff'
                    },
                    emphasis: {
                        itemStyle: { areaColor: '#00f2ff' }
                    }
                },
                series: [{
                    type: 'scatter',
                    coordinateSystem: 'geo',
                    data: stats.geo_distribution,
                    symbolSize: function (val) {
                        // val is an object {name, value, ip, city}
                        // value is [lon, lat, count]
                        const count = val.value ? val.value[2] : 1;
                        return Math.min(25, 8 + count * 3);
                    },
                    itemStyle: {
                        color: '#00f2ff',
                        shadowBlur: 10,
                        shadowColor: '#00f2ff'
                    },
                    emphasis: {
                        itemStyle: {
                            color: '#ff0055'
                        }
                    },
                    label: {
                        show: false
                    },
                    tooltip: {
                        formatter: function (params) {
                            return `${escapeHtml(params.data.ip)}<br/>
                                    ${escapeHtml(params.data.city || 'Unknown')}, ${escapeHtml(params.data.name)}<br/>
                                    经纬度: ${params.value[0].toFixed(2)}, ${params.value[1].toFixed(2)}<br/>
                                    <span style="color: #ffa500;">💡 点击查看资产详情</span>`;
                        }
                    }
                }]
            });

            // Add click event handler for map-list linking
            charts.map.off('click'); // Remove previous handlers
            charts.map.on('click', function (params) {
                if (params.componentType === 'series' && params.seriesType === 'scatter') {
                    const clickedIP = params.data.ip;
                    console.log('Map clicked, IP:', clickedIP);
                    highlightAssetByIP(clickedIP);
                }
            });
        }

        // 3. Update Charts from Global Stats
        // Ports
        const portData = Object.entries(stats.port_distribution).map(([k, v]) => [k, v]);
        charts.port.setOption({
            xAxis: { data: portData.map(d => d[0]) },
            series: [{ data: portData.map(d => d[1]) }]
        });

        // Protocols
        const protocolData = Object.entries(stats.protocol_distribution).map(([name, value]) => ({ name, value }));
        charts.protocol.setOption({
            series: [{ data: protocolData }]
        });

    } catch (e) {
        console.error('Failed to init dashboard:', e);
    }
}

// Highlight asset in list by IP (for map-list linking)
function highlightAssetByIP(ip) {
    // Find the asset index
    const assetIndex = currentResults.findIndex(a => a.ip === ip);

    if (assetIndex === -1) {
        console.log(`Asset with IP ${ip} not in current results`);
        return;
    }

    // Remove previous highlights
    document.querySelectorAll('.asset-card').forEach(card => {
        card.classList.remove('highlight-flash');
    });

    // Find and highlight the card
    const cards = document.querySelectorAll('.asset-card');
    if (cards[assetIndex]) {
        const targetCard = cards[assetIndex];

        // Add highlight effect
        targetCard.classList.add('highlight-flash');

        // Scroll into view
        targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Remove highlight after animation
        setTimeout(() => {
            targetCard.classList.remove('highlight-flash');
        }, 2000);
    }
}

// Show asset detail in modal with Raw Data
function showAssetDetail(index) {
    const asset = currentResults[index];
    if (!asset) return;

    const detailModal = document.getElementById('asset-detail-modal');
    const detailContent = document.getElementById('asset-detail-content');

    // Format Raw Data pretty
    const rawDataJson = JSON.stringify(asset.raw_data || {}, null, 2);

    detailContent.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
            <div class="detail-field"><label>IP 地址</label><div>${escapeHtml(asset.ip || 'N/A')}</div></div>
            <div class="detail-field"><label>端口</label><div>${escapeHtml(asset.port || 'N/A')}</div></div>
            <div class="detail-field"><label>协议</label><div>${escapeHtml(asset.protocol || 'N/A')}</div></div>
            <div class="detail-field"><label>国家</label><div>${escapeHtml(asset.country || 'N/A')}</div></div>
            <div class="detail-field"><label>城市</label><div>${escapeHtml(asset.city || 'N/A')}</div></div>
            <div class="detail-field"><label>服务器</label><div>${escapeHtml(asset.server || 'N/A')}</div></div>
            <div class="detail-field" style="grid-column: 1 / -1;"><label>标题</label><div>${escapeHtml(asset.title || 'N/A')}</div></div>
            <div class="detail-field" style="grid-column: 1 / -1;"><label>域名/主机</label><div>${escapeHtml(asset.domain || asset.host || 'N/A')}</div></div>
            <div class="detail-field" style="grid-column: 1 / -1;"><label>组织机构</label><div>${escapeHtml(asset.org || 'N/A')}</div></div>
        </div>
        
        <div class="detail-field" style="grid-column: 1 / -1; margin-bottom: 20px;">
            <button onclick="triggerAssetAnalysis(${Number.isSafeInteger(Number(asset.id)) ? asset.id : 0})" class="btn-primary" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;">
                <i class="fas fa-brain"></i> AI 安全分析 (单资产)
            </button>
            <div id="asset-analysis-result" style="margin-top: 15px; display: none;"></div>
        </div>
        
        <div class="detail-field" style="grid-column: 1 / -1;">
            <label>原始数据 (Raw JSON)</label>
            <pre style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 4px; overflow: auto; max-height: 200px; color: #a5b4fc; font-family: monospace; font-size: 11px;">${escapeHtml(rawDataJson)}</pre>
        </div>
    `;

    detailModal.style.display = 'block';
}

// Trigger AI Analysis for Single Asset
async function triggerAssetAnalysis(assetId) {
    const resultDiv = document.getElementById('asset-analysis-result');
    const btn = document.querySelector('button[onclick^="triggerAssetAnalysis"]');
    const originalText = btn.innerHTML;

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div style="text-align: center; color: var(--primary); padding: 20px;"><i class="fas fa-circle-notch fa-spin fa-2x"></i><br><span style="margin-top: 10px; display: inline-block;">正在进行资产深度分析，请稍候...</span></div>';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/analyze-asset/${assetId}`, { method: 'POST' });
        const data = await response.json();

        if (response.ok) {
            let riskColor = '#4ade80'; // Low
            if (data.risk_level === 'High') riskColor = '#ef4444';
            if (data.risk_level === 'Medium') riskColor = '#f59e0b';

            const vulnList = (data.vulnerabilities || []).map(v => `<li>${escapeHtml(v)}</li>`).join('') || '<li>未发现明显漏洞</li>';
            const recList = (data.recommendations || []).map(r => `<li>${escapeHtml(r)}</li>`).join('') || '<li>暂无建议</li>';

            resultDiv.innerHTML = `
                <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid var(--border-color); border-radius: 8px; padding: 15px; animation: slideDown 0.3s ease;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">
                        <h3 style="margin: 0; color: var(--text-primary); font-size: 16px;"><i class="fas fa-shield-alt"></i> 分析结果</h3>
                        <span style="background: ${riskColor}; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold;">${escapeHtml(data.risk_level)} Risk</span>
                    </div>

                    <div style="margin-bottom: 15px; color: #cbd5e1; font-size: 14px; line-height: 1.5;">
                        ${escapeHtml(data.summary || '无摘要信息')}
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <strong style="color: #f87171; font-size: 13px; display: block; margin-bottom: 5px;"><i class="fas fa-exclamation-triangle"></i> 潜在漏洞</strong>
                            <ul style="margin: 0; padding-left: 20px; color: var(--text-secondary); font-size: 13px;">
                                ${vulnList}
                            </ul>
                        </div>
                        <div>
                            <strong style="color: #4ade80; font-size: 13px; display: block; margin-bottom: 5px;"><i class="fas fa-check-circle"></i> 安全建议</strong>
                            <ul style="margin: 0; padding-left: 20px; color: var(--text-secondary); font-size: 13px;">
                                ${recList}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        } else {
            resultDiv.innerHTML = `<div style="color: #ef4444; padding: 10px; background: rgba(239,68,68,0.1); border-radius: 4px;">分析失败: ${escapeHtml(data.detail)}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div style="color: #ef4444; padding: 10px; background: rgba(239,68,68,0.1); border-radius: 4px;">系统错误: ${escapeHtml(e.message)}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// Analysis Logic
dom.analyzeBtn.addEventListener('click', async () => {
    let queryId = currentQueryId;
    if (!queryId) return;

    const btn = dom.analyzeBtn;
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> 分析中...';

    try {
        const response = await fetch(`${API_BASE}/analyze?query_id=${queryId}`, { method: 'POST' });
        const report = await response.json();

        if (response.ok) {
            showReportModal(report);
            loadReports(); // Refresh reports list
        } else {
            alert('Analysis failed: ' + report.detail);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
});

// History & Report Loaders
// 缓存历史/报告原始数据，避免把不可信字符串拼进 onclick 的 JS 字面量（XSS 注入点）
let historyCache = [];
let reportsCache = [];

async function loadHistory() {
    try {
        const resp = await fetch(`${API_BASE}/queries`);
        const queries = await resp.json();

        const container = document.getElementById('history-container');
        if (queries.length === 0) return;

        dom.stats.queryCount.innerText = queries.length;

        // 反转后缓存，渲染时只传索引，查询文本不进 HTML 属性 / JS 字面量
        historyCache = queries.slice().reverse();
        container.innerHTML = historyCache.map((q, idx) => `
            <div class="history-item" onclick="rerunQueryFromHistory(${idx})">
                <div class="item-time">${escapeHtml(new Date(q.created_at).toLocaleString())}</div>
                <div class="item-text">
                    <span style="color:var(--primary)">[${escapeHtml(q.platform)}]</span> ${escapeHtml(q.nl_query)}
                </div>
            </div>
        `).join('');
    } catch (e) { console.error(e); }
}

// 从缓存按索引重跑查询，避免 nl_query 进入 HTML/JS 字符串上下文
function rerunQueryFromHistory(idx) {
    const q = historyCache[idx];
    if (!q) return;
    rerunQuery(q.nl_query, q.platform);
}

async function loadReports() {
    try {
        const resp = await fetch(`${API_BASE}/reports`);
        const reports = await resp.json();

        const container = document.getElementById('reports-container');
        if (reports.length === 0) return;

        // 缓存反转后的报告，渲染只传索引，避免把对象 JSON 拼进 onclick 属性（XSS 注入点）
        reportsCache = reports.slice().reverse();
        container.innerHTML = reportsCache.map((r, idx) => {
            const riskClass = escapeAttr(String(r.risk_level || 'unknown').toLowerCase());
            const summary = escapeHtml(String(r.summary || '').substring(0, 50));
            return `
            <div class="report-item ${riskClass}">
                <div class="item-time">${escapeHtml(new Date(r.created_at).toLocaleString())}</div>
                <div class="item-text" onclick="showReportDetails(${idx})" style="cursor: pointer;">
                    <strong>${escapeHtml(r.risk_level)} Risk</strong>: ${summary}...
                </div>
                <div class="download-buttons" style="margin-top: 5px; display: flex; gap: 5px;">
                    <button class="btn-download" onclick="event.stopPropagation(); downloadReport(${Number.isSafeInteger(Number(r.id)) ? r.id : 0}, 'markdown')" title="下载 Markdown">
                        <i class="fas fa-file-alt"></i> MD
                    </button>
                    <button class="btn-download" onclick="event.stopPropagation(); downloadReport(${Number.isSafeInteger(Number(r.id)) ? r.id : 0}, 'pdf')" title="下载 PDF">
                        <i class="fas fa-file-pdf"></i> PDF
                    </button>
                </div>
            </div>
            `;
        }).join('');
    } catch (e) { console.error(e); }
}

// Modal Logic
const modal = document.getElementById('report-modal');
const closeBtn = document.querySelector('.close-btn');

function showReportModal(report) {
    const content = document.getElementById('report-detail-content');
    content.innerHTML = `
        <div style="margin-bottom: 20px;">
            <span style="background: ${getRiskColor(report.risk_level)}; padding: 5px 10px; border-radius: 4px; font-weight: bold; color: #fff;">
                ${escapeHtml(report.risk_level)} Risk Level
            </span>
            <span style="margin-left: 10px; color: var(--text-muted);">${escapeHtml(report.summary)}</span>
        </div>
        <div class="markdown-body" style="color: #e0f2fe;">
            ${formatMarkdown(report.content)}
        </div>
    `;
    modal.style.display = 'block';
}

// 从缓存按索引展示报告详情，避免把对象 JSON 拼进 onclick 属性
function showReportDetails(idx) {
    const report = reportsCache[idx];
    if (!report) return;
    showReportModal(report);
}

closeBtn.onclick = () => modal.style.display = 'none';
window.onclick = (e) => { if (e.target == modal) modal.style.display = 'none'; }

function getRiskColor(level) {
    switch (String(level || '').toLowerCase()) {
        case 'high': return '#ff0055';
        case 'medium': return '#ffbf00';
        case 'low': return '#00ff9d';
        default: return '#94a3b8';
    }
}

function formatMarkdown(text) {
    // 先转义 HTML 防止 LLM 输出中的标签执行，再做 markdown 语法替换
    // （markdown 的 * # 不属于 HTML 特殊字符，转义后仍可被正则匹配）
    return escapeHtml(text)
        .replace(/\n/g, '<br>')
        .replace(/### (.*)/g, '<h3 style="color:var(--primary); margin:15px 0;">$1</h3>')
        .replace(/## (.*)/g, '<h2 style="color:var(--primary); margin:20px 0;">$1</h2>')
        .replace(/# (.*)/g, '<h1 style="color:var(--primary); margin:25px 0;">$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong style="color:var(--secondary)">$1</strong>');
}

function rerunQuery(nl, platform) {
    dom.input.value = nl;
    dom.platformSelect.value = platform;
    dom.searchBtn.click();
}

// Download report function
function downloadReport(reportId, format) {
    const url = `${API_BASE}/download/report/${reportId}?format=${format}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = `report_${reportId}.${format === 'pdf' ? 'pdf' : 'md'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Close asset detail modal
const assetDetailModal = document.getElementById('asset-detail-modal');
if (assetDetailModal) {
    const closeAssetBtn = assetDetailModal.querySelector('.close-btn');
    if (closeAssetBtn) {
        closeAssetBtn.onclick = () => assetDetailModal.style.display = 'none';
    }
    window.addEventListener('click', (e) => {
        if (e.target == assetDetailModal) assetDetailModal.style.display = 'none';
    });
}

// Clear History Button
document.getElementById('clear-history-btn').addEventListener('click', async () => {
    if (!confirm('确定要清除所有查询历史和报告吗？\n\n注意：资产数据不会被删除。')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/clear-history`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            // Refresh UI
            loadHistory();
            loadReports();
        } else {
            alert('清除失败: ' + data.detail);
        }
    } catch (error) {
        alert('清除失败: ' + error.message);
    }
});

// Init
// Filter current results based on chart interaction
function filterResults(field, value) {
    console.log(`Filtering by ${field}: ${value}`);
    if (!originalResults || originalResults.length === 0) return;

    let filtered = [];
    if (field === 'port') {
        filtered = originalResults.filter(a => String(a.port) === String(value));
    } else if (field === 'protocol') {
        filtered = originalResults.filter(a => (a.protocol || '').toLowerCase() === value.toLowerCase());
    } else if (field === 'city') {
        filtered = originalResults.filter(a => (a.city || '').toLowerCase() === value.toLowerCase());
    }

    // Update List Display only (don't update charts to avoid loop)
    updateUI(filtered, false);

    // Show Reset Button
    dom.viewAllBtn.style.display = 'inline-block';
    dom.queryStatusText.innerText = `已筛选 [${filtered.length}/${originalResults.length}]`;
}

// Helper to update charts wrapper
function updateChartsData(results) {
    if (typeof updateCharts === 'function') {
        updateCharts(results);
    }
}

// Load recent 100 assets on startup
async function loadRecentAssets() {
    try {
        console.log("Loading recent assets...");
        const response = await fetch(`${API_BASE}/assets/recent?limit=100`);
        if (!response.ok) throw new Error("API Error");

        const assets = await response.json();

        if (assets && assets.length > 0) {
            console.log(`Loaded ${assets.length} recent assets`);
            updateUI(assets, true);
        } else {
            console.log("No recent assets found");
            dom.resultsContainer.innerHTML = '<div class="empty-state"><i class="fas fa-database"></i><p>数据库暂无资产</p></div>';
        }
    } catch (e) {
        console.error("Failed to load recent assets:", e);
    }
}

// Init
initCharts();
loadHistory();
loadReports();
initDashboard(); // Init global stats (map & charts)
loadRecentAssets(); // Load default view

// ============ Export & Filter Functionality ============

// Export Dropdown Toggle
const exportBtn = document.getElementById('export-btn');
const exportMenu = document.getElementById('export-menu');

if (exportBtn && exportMenu) {
    exportBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        exportMenu.style.display = exportMenu.style.display === 'none' ? 'block' : 'none';
    });

    document.addEventListener('click', () => {
        exportMenu.style.display = 'none';
    });

    // Export Options
    document.querySelectorAll('.export-option').forEach(option => {
        option.addEventListener('click', async (e) => {
            e.preventDefault();
            const format = option.dataset.format;

            // Build export URL with current filters
            const params = new URLSearchParams();
            params.append('format', format);

            const keyword = document.getElementById('asset-filter')?.value;
            const country = document.getElementById('filter-country')?.value;
            const protocol = document.getElementById('filter-protocol')?.value;

            if (keyword) params.append('keyword', keyword);
            if (country) params.append('country', country);
            if (protocol) params.append('protocol', protocol);

            // Trigger download
            window.location.href = `${API_BASE}/assets/export?${params.toString()}`;
            exportMenu.style.display = 'none';
        });
    });
}

// Filter Dropdowns
const filterCountry = document.getElementById('filter-country');
const filterProtocol = document.getElementById('filter-protocol');
const filterKeyword = document.getElementById('asset-filter');

// Populate filter dropdowns from current data
function updateFilterOptions(assets) {
    if (!filterCountry || !filterProtocol) return;

    const countries = [...new Set(assets.map(a => a.country).filter(Boolean))];
    const protocols = [...new Set(assets.map(a => a.protocol).filter(Boolean))];

    // Country dropdown — 必须转义，country 来自外部 API 不可信
    filterCountry.innerHTML = '<option value="">国家</option>';
    countries.forEach(c => {
        filterCountry.innerHTML += `<option value="${escapeAttr(c)}">${escapeHtml(c)}</option>`;
    });

    // Protocol dropdown — 同上
    filterProtocol.innerHTML = '<option value="">协议</option>';
    protocols.forEach(p => {
        filterProtocol.innerHTML += `<option value="${escapeAttr(p)}">${escapeHtml(p)}</option>`;
    });
}

// Apply filters
function applyFilters() {
    if (!originalResults || originalResults.length === 0) return;

    const keyword = filterKeyword?.value?.toLowerCase() || '';
    const country = filterCountry?.value || '';
    const protocol = filterProtocol?.value || '';

    let filtered = originalResults.filter(a => {
        let match = true;
        if (keyword) {
            const searchFields = [a.ip, a.title, a.domain, a.host].map(f => (f || '').toLowerCase());
            match = searchFields.some(f => f.includes(keyword));
        }
        if (country && match) {
            match = (a.country || '').toLowerCase() === country.toLowerCase();
        }
        if (protocol && match) {
            match = (a.protocol || '').toLowerCase() === protocol.toLowerCase();
        }
        return match;
    });

    updateUI(filtered, false);
    dom.queryStatusText.innerText = `已筛选 [${filtered.length}/${originalResults.length}]`;

    if (filtered.length < originalResults.length) {
        dom.viewAllBtn.style.display = 'inline-block';
    }
}

// Add event listeners for filters
if (filterKeyword) {
    filterKeyword.addEventListener('input', debounce(applyFilters, 300));
}
if (filterCountry) {
    filterCountry.addEventListener('change', applyFilters);
}
if (filterProtocol) {
    filterProtocol.addEventListener('change', applyFilters);
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Update filter options when data loads
const originalUpdateUI = window.updateUI || updateUI;
window.updateUI = function (results, shouldUpdateCharts = true) {
    originalUpdateUI(results, shouldUpdateCharts);
    if (shouldUpdateCharts && results.length > 0) {
        updateFilterOptions(results);
    }
};

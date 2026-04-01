/* === Tri-State AI Dashboard — Client-side Logic === */

const TS_BLUE = '#005a9c';
const TS_BLUE2 = '#0073cf';
const TS_DARK = '#003d6b';
const COLORS = [TS_BLUE, TS_BLUE2, '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c', '#34495e'];

// --- Tab switching ---
function switchTab(name, btn) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    btn.classList.add('active');

    // Lazy-load data on first tab visit
    if (!loaded[name]) {
        loaders[name]();
        loaded[name] = true;
    }
}

const loaded = { sentiment: false, members: false, energy: false, price: false, qa: true };
const loaders = {
    sentiment: loadSentiment,
    members: loadMembers,
    energy: loadEnergy,
    price: loadPrice,
};

// --- Helpers ---
function kpiCard(label, value, delta, deltaClass) {
    let html = '<div class="kpi-card"><div class="kpi-label">' + label + '</div><div class="kpi-value">' + value + '</div>';
    if (delta) html += '<div class="kpi-delta ' + (deltaClass || 'neutral') + '">' + delta + '</div>';
    return html + '</div>';
}

async function fetchJSON(url) {
    const res = await fetch(url);
    return res.json();
}

// ============================================
// SENTIMENT TAB
// ============================================
async function loadSentiment() {
    try {
        const summary = await fetchJSON('/api/sentiment/summary');
        const trend = await fetchJSON('/api/sentiment/trend');
        const topics = await fetchJSON('/api/sentiment/by_topic');
        const volume = await fetchJSON('/api/sentiment/volume');
        const headlines = await fetchJSON('/api/sentiment/headlines');

        // KPIs
        document.getElementById('sentiment-kpis').innerHTML =
            kpiCard('Avg Sentiment', summary.avg_sentiment.toFixed(2), summary.avg_sentiment > 0 ? 'Positive' : 'Negative', summary.avg_sentiment > 0 ? 'positive' : 'negative') +
            kpiCard('Articles Analyzed', summary.article_count.toLocaleString(), summary.real_count + ' verified', 'neutral') +
            kpiCard('Topics Covered', summary.topic_count) +
            kpiCard('Lowest Sentiment', summary.worst_topic, summary.worst_score.toFixed(2), 'negative');

        // Trend chart
        var topicNames = [];
        trend.forEach(function(r) {
            if (topicNames.indexOf(r.topic) === -1) topicNames.push(r.topic);
        });

        var traces = topicNames.map(function(topic, i) {
            var rows = trend.filter(function(r) { return r.topic === topic; });
            return {
                x: rows.map(function(r) { return r.date; }),
                y: rows.map(function(r) { return r.sentiment_score; }),
                name: topic,
                type: 'scatter',
                mode: 'lines',
                line: { color: COLORS[i % COLORS.length] }
            };
        });

        Plotly.newPlot('sentiment-trend', traces, {
            font: { family: 'Segoe UI, sans-serif' },
            xaxis: { tickformat: '%b %Y', dtick: 'M3' },
            yaxis: { title: 'Sentiment Score' },
            shapes: [{ type: 'line', x0: 0, x1: 1, xref: 'paper', y0: 0, y1: 0, line: { dash: 'dash', color: 'gray', width: 1 } }],
            legend: { orientation: 'h', y: -0.15, x: 0.5, xanchor: 'center' },
            margin: { b: 80, t: 10 }
        }, { responsive: true });

        // Topic bar chart
        var barColors = topics.scores.map(function(v) { return v < -0.1 ? '#e74c3c' : v < 0.1 ? '#f39c12' : TS_BLUE; });
        Plotly.newPlot('sentiment-topics', [{
            x: topics.scores,
            y: topics.topics,
            type: 'bar',
            orientation: 'h',
            marker: { color: barColors },
            text: topics.scores.map(function(v) { return v.toFixed(2); }),
            textposition: 'auto'
        }], {
            font: { family: 'Segoe UI, sans-serif' },
            xaxis: { title: 'Avg Sentiment Score' },
            shapes: [{ type: 'line', x0: 0, x1: 0, y0: -0.5, y1: topics.topics.length - 0.5, line: { dash: 'dash', color: 'gray' } }],
            margin: { l: 160, t: 10 }
        }, { responsive: true });

        // Volume donut
        Plotly.newPlot('sentiment-volume', [{
            values: volume.counts,
            labels: volume.topics,
            type: 'pie',
            hole: 0.4,
            marker: { colors: COLORS }
        }], {
            font: { family: 'Segoe UI, sans-serif' },
            margin: { t: 10 }
        }, { responsive: true });

        // Headlines table
        var html = '<table class="data-table"><thead><tr><th>Date</th><th>Headline</th><th>Topic</th><th>Source</th><th>Sentiment</th><th>Status</th></tr></thead><tbody>';
        headlines.forEach(function(h) {
            var sentClass = h.sentiment_score > 0.1 ? 'positive' : h.sentiment_score < -0.1 ? 'negative' : 'neutral';
            var verified = h.verified === 'Verified' ? '<span class="badge badge-real">\u2713 Verified</span>' : '<span class="badge badge-sim">Modeled</span>';
            html += '<tr><td>' + h.date + '</td><td>' + h.headline + '</td><td>' + h.topic + '</td><td>' + h.source + '</td><td class="kpi-delta ' + sentClass + '">' + h.sentiment_score.toFixed(2) + '</td><td>' + verified + '</td></tr>';
        });
        html += '</tbody></table>';
        document.getElementById('sentiment-headlines').innerHTML = html;

    } catch (err) {
        console.error('Sentiment load error:', err);
        document.getElementById('sentiment-kpis').innerHTML = '<p style="color:red;">Error loading sentiment data: ' + err.message + '</p>';
    }
}

// ============================================
// MEMBER RISK TAB
// ============================================
async function loadMembers() {
    try {
        var summary = await fetchJSON('/api/members/summary');
        var scatter = await fetchJSON('/api/members/scatter');
        var table = await fetchJSON('/api/members/table');
        var departed = await fetchJSON('/api/members/departed');

        // KPIs
        document.getElementById('member-kpis').innerHTML =
            kpiCard('Active Members', summary.active_count) +
            kpiCard('At-Risk Members', summary.at_risk_count, summary.at_risk_pct + '% of active', 'negative') +
            kpiCard('Revenue at Risk', '$' + summary.revenue_at_risk + 'M/yr', '', 'negative') +
            kpiCard('Avg Rate Gap', '$' + summary.avg_rate_gap + '/MWh', 'vs market alternatives', 'negative');

        // Alert banner
        document.getElementById('member-alert').innerHTML =
            '<div class="alert-banner"><span class="alert-value">$' + summary.revenue_at_risk + 'M in annual revenue at risk</span><br>' +
            '<span class="alert-text">' + summary.at_risk_count + ' of ' + summary.active_count + ' active members show elevated flight risk. Board activity monitoring and proactive engagement could prevent the next departure.</span></div>';

        // Scatter chart
        Plotly.newPlot('member-scatter', [{
            x: scatter.map(function(r) { return r.rate_gap; }),
            y: scatter.map(function(r) { return r.risk_score; }),
            text: scatter.map(function(r) {
                return '<b>' + r.member + '</b><br>State: ' + r.state + '<br>Consumers: ' + r.consumers.toLocaleString() + '<br>Revenue: $' + r.annual_revenue_millions.toFixed(1) + 'M<br>Risk: ' + r.risk_score.toFixed(2) + '<br>Rate Gap: $' + r.rate_gap.toFixed(0) + '/MWh';
            }),
            hoverinfo: 'text',
            mode: 'markers',
            marker: {
                size: scatter.map(function(r) { return Math.max(8, r.annual_revenue_millions / 2); }),
                color: scatter.map(function(r) { return r.risk_score; }),
                colorscale: [[0, '#27ae60'], [0.5, '#f39c12'], [1, '#e74c3c']],
                showscale: true,
                colorbar: { title: 'Risk' }
            },
            type: 'scatter'
        }], {
            font: { family: 'Segoe UI, sans-serif' },
            xaxis: { title: 'Rate Gap vs Market ($/MWh)' },
            yaxis: { title: 'Flight Risk Score' },
            shapes: [
                { type: 'line', x0: -5, x1: 35, y0: 0.3, y1: 0.3, line: { dash: 'dash', color: 'gray', width: 1 } },
                { type: 'line', x0: 15, x1: 15, y0: 0, y1: 1, line: { dash: 'dash', color: 'gray', width: 1 } }
            ],
            margin: { t: 10 }
        }, { responsive: true });

        // Risk table
        var html = '<table class="data-table"><thead><tr><th>Member</th><th>State</th><th>Consumers</th><th>Risk</th><th>Score</th><th>Rate Gap</th><th>Revenue</th><th>Satisfaction</th></tr></thead><tbody>';
        table.forEach(function(r) {
            var riskClass = r.risk_score > 0.5 ? 'risk-high' : r.risk_score > 0.3 ? 'risk-medium' : 'risk-low';
            var riskLabel = r.risk_score > 0.5 ? 'HIGH' : r.risk_score > 0.3 ? 'MEDIUM' : 'LOW';
            html += '<tr><td>' + r.member + '</td><td>' + r.state + '</td><td>' + r.consumers.toLocaleString() + '</td><td class="' + riskClass + '">' + riskLabel + '</td><td>' + r.risk_score.toFixed(2) + '</td><td>$' + r.rate_gap.toFixed(0) + '/MWh</td><td>$' + r.annual_revenue_millions.toFixed(1) + 'M</td><td>' + r.satisfaction_score.toFixed(2) + '</td></tr>';
        });
        html += '</tbody></table>';
        document.getElementById('member-table').innerHTML = html;

        // Departed table
        html = '<table class="data-table"><thead><tr><th>Member</th><th>Status</th><th>Consumers</th><th>Key Driver</th><th>Warning Signs</th><th>Lesson</th></tr></thead><tbody>';
        departed.forEach(function(r) {
            html += '<tr><td><strong>' + r.member + '</strong></td><td>' + r.status + '</td><td>' + r.consumers + '</td><td>' + r.driver + '</td><td>' + r.warning + '</td><td>' + r.lesson + '</td></tr>';
        });
        html += '</tbody></table>';
        document.getElementById('departed-table').innerHTML = html;

    } catch (err) {
        console.error('Members load error:', err);
    }
}

// ============================================
// ENERGY MIX TAB
// ============================================
async function loadEnergy() {
    try {
        var summary = await fetchJSON('/api/energy/summary');
        var mix = await fetchJSON('/api/energy/mix');
        var co2 = await fetchJSON('/api/energy/co2');

        // KPIs
        document.getElementById('energy-kpis').innerHTML =
            kpiCard('Coal %', summary.coal_now + '%', (summary.coal_change > 0 ? '+' : '') + summary.coal_change + '% since 2015', 'positive') +
            kpiCard('Renewables %', summary.renewable_now + '%', '+' + summary.renewable_change.toFixed(1) + '% since 2015', 'positive') +
            kpiCard('Latest CO\u2082 (k tons)', summary.co2_latest) +
            kpiCard('Total Generation', summary.total_gwh + ' GWh');

        // Stacked area
        var sources = ['coal_pct', 'natural_gas_pct', 'wind_pct', 'solar_pct', 'hydro_pct', 'purchased_pct'];
        var labels = { coal_pct: 'Coal', natural_gas_pct: 'Natural Gas', wind_pct: 'Wind', solar_pct: 'Solar', hydro_pct: 'Hydro', purchased_pct: 'Purchased' };
        var srcColors = { coal_pct: '#5d4e37', natural_gas_pct: '#3498db', wind_pct: '#1abc9c', solar_pct: '#f1c40f', hydro_pct: '#2980b9', purchased_pct: '#95a5a6' };
        var dates = mix.map(function(r) { return r.date; });

        var traces = sources.map(function(src) {
            return {
                x: dates,
                y: mix.map(function(r) { return r[src]; }),
                name: labels[src],
                type: 'scatter',
                mode: 'lines',
                fill: 'tonexty',
                stackgroup: 'one',
                line: { color: srcColors[src] }
            };
        });

        Plotly.newPlot('energy-mix-chart', traces, {
            font: { family: 'Segoe UI, sans-serif' },
            xaxis: { tickformat: '%b %Y', dtick: 'M6' },
            yaxis: { title: '% of Generation' },
            legend: { orientation: 'h', y: -0.15, x: 0.5, xanchor: 'center' },
            margin: { b: 80, t: 10 }
        }, { responsive: true });

        // CO2 chart
        Plotly.newPlot('energy-co2-chart', [{
            x: co2.years,
            y: co2.co2,
            type: 'bar',
            marker: { color: TS_BLUE },
            text: co2.co2.map(function(v) { return v.toLocaleString(); }),
            textposition: 'auto'
        }], {
            font: { family: 'Segoe UI, sans-serif' },
            yaxis: { title: 'CO\u2082 (thousand tons)' },
            shapes: [{
                type: 'line',
                x0: co2.years[0] - 0.5,
                x1: co2.years[co2.years.length - 1] + 0.5,
                y0: co2.target_2030,
                y1: co2.target_2030,
                line: { dash: 'dash', color: 'green', width: 2 }
            }],
            annotations: [{
                x: co2.years[co2.years.length - 1],
                y: co2.target_2030,
                text: '2030 Target (' + co2.target_2030.toLocaleString() + 'k)',
                showarrow: true, ax: -60, ay: -25,
                font: { color: 'green', size: 11 }
            }],
            margin: { t: 10 }
        }, { responsive: true });

    } catch (err) {
        console.error('Energy load error:', err);
    }
}

// ============================================
// PRICE FORECAST TAB
// ============================================
async function loadPrice() {
    try {
        var summary = await fetchJSON('/api/price/summary');
        var forecast = await fetchJSON('/api/price/forecast');

        // KPIs
        document.getElementById('price-kpis').innerHTML =
            kpiCard('Avg Price', '$' + summary.avg_price + '/MWh') +
            kpiCard('Min Price', '$' + summary.min_price + '/MWh') +
            kpiCard('Max Price', '$' + summary.max_price + '/MWh') +
            kpiCard('Data Points', summary.record_count.toLocaleString());

        // Price chart
        Plotly.newPlot('price-chart', [{
            x: forecast.map(function(r) { return r.date; }),
            y: forecast.map(function(r) { return r.price_mwh; }),
            type: 'scatter',
            mode: 'lines',
            name: 'Price',
            line: { color: TS_BLUE, width: 1.5 }
        }], {
            font: { family: 'Segoe UI, sans-serif' },
            xaxis: { tickformat: '%b %Y' },
            yaxis: { title: 'Price ($/MWh)' },
            margin: { b: 50, t: 10 }
        }, { responsive: true });

        // Initial scenario
        updateScenario();

    } catch (err) {
        console.error('Price load error:', err);
    }
}

async function updateScenario() {
    var demand = parseFloat(document.getElementById('sl-demand').value);
    var temp = parseFloat(document.getElementById('sl-temp').value);
    var wind = parseFloat(document.getElementById('sl-wind').value);
    var solar = parseFloat(document.getElementById('sl-solar').value);
    var gas = parseFloat(document.getElementById('sl-gas').value);

    document.getElementById('sv-demand').textContent = demand;
    document.getElementById('sv-temp').textContent = temp + '\u00B0F';
    document.getElementById('sv-wind').textContent = wind;
    document.getElementById('sv-solar').textContent = solar;
    document.getElementById('sv-gas').textContent = '$' + gas.toFixed(2);

    try {
        var res = await fetch('/api/price/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                demand_mw: demand, temperature_f: temp,
                wind_generation_mw: wind, solar_generation_mw: solar,
                natural_gas_price: gas, is_weekend: false
            })
        });
        var result = await res.json();
        var diff = result.predicted_price - result.avg_price;
        var diffClass = diff > 0 ? 'negative' : 'positive';

        document.getElementById('scenario-result').innerHTML =
            kpiCard('Predicted Price', '$' + result.predicted_price.toFixed(2) + '/MWh') +
            kpiCard('vs Average', (diff > 0 ? '+' : '') + '$' + diff.toFixed(2) + '/MWh', (diff / result.avg_price * 100).toFixed(1) + '%', diffClass) +
            kpiCard('Historical Average', '$' + result.avg_price.toFixed(2) + '/MWh');
    } catch (e) {
        document.getElementById('scenario-result').innerHTML = kpiCard('Predicted Price', 'Loading...');
    }
}

// ============================================
// Q&A TAB
// ============================================
function askQuestion(text) {
    var input = document.getElementById('qa-input');
    var question = text || input.value.trim();
    if (!question) return;
    input.value = '';

    var messages = document.getElementById('qa-messages');
    messages.innerHTML += '<div class="qa-msg user">' + question + '</div>';

    fetch('/api/qa/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        messages.innerHTML += '<div class="qa-msg assistant">' + data.answer + '</div>';
        messages.scrollTop = messages.scrollHeight;
    })
    .catch(function() {
        messages.innerHTML += '<div class="qa-msg assistant">Sorry, something went wrong. Please try again.</div>';
    });
}

// ============================================
// INIT: Load first tab
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    loadSentiment();
    loaded.sentiment = true;
});

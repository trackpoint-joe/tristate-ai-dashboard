"""Inline data provenance badges with hover tooltips for transparency."""

import streamlit as st

BADGE_CSS = """
<style>
.data-badge {
    display: inline-block;
    padding: 0.2rem 0.55rem;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 600;
    margin: 0.1rem 0.1rem;
    vertical-align: middle;
    cursor: help;
    position: relative;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.data-badge:hover {
    transform: translateY(-2px);
    box-shadow: 0 3px 8px rgba(0,0,0,0.15);
    z-index: 10;
}

.badge-real {
    background: #e8f5e9;
    color: #2e7d32;
    border: 1px solid #a5d6a7;
}
.badge-real:hover { background: #c8e6c9; }

.badge-simulated {
    background: #fff3e0;
    color: #e65100;
    border: 1px solid #ffcc80;
}
.badge-simulated:hover { background: #ffe0b2; }

.badge-model {
    background: #e8f1fa;
    color: #005a9c;
    border: 1px solid #90caf9;
}
.badge-model:hover { background: #bbdefb; }

/* Tooltip */
.badge-tip {
    position: relative;
    display: inline-block;
}
.badge-tip .tip-text {
    visibility: hidden;
    opacity: 0;
    background: #1a1a2e;
    color: #fff;
    font-size: 0.78rem;
    font-weight: 400;
    line-height: 1.4;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    position: absolute;
    z-index: 100;
    bottom: 130%;
    left: 50%;
    transform: translateX(-50%);
    min-width: 220px;
    max-width: 320px;
    text-align: left;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    pointer-events: none;
    transition: opacity 0.2s ease, visibility 0.2s ease;
    white-space: normal;
}
.badge-tip .tip-text::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -6px;
    border-width: 6px;
    border-style: solid;
    border-color: #1a1a2e transparent transparent transparent;
}
.badge-tip:hover .tip-text {
    visibility: visible;
    opacity: 1;
}

/* Provenance bar */
.provenance-bar {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 0.45rem 0.75rem;
    margin-bottom: 0.75rem;
    font-size: 0.82rem;
    color: #555;
    line-height: 1.8;
}
.provenance-bar .prod-note {
    font-style: italic;
    color: #888;
    font-size: 0.78rem;
}

/* Chart-level badge strip */
.chart-badge-strip {
    margin: 0.25rem 0 0.1rem 0;
    line-height: 1.8;
}
</style>
"""

_css_injected = False

def _inject_css():
    global _css_injected
    if not _css_injected:
        st.markdown(BADGE_CSS, unsafe_allow_html=True)
        _css_injected = True


def real(text="Real Data", tooltip=None):
    _inject_css()
    if tooltip:
        return (f'<span class="badge-tip"><span class="data-badge badge-real">✓ {text}</span>'
                f'<span class="tip-text">{tooltip}</span></span>')
    return f'<span class="data-badge badge-real">✓ {text}</span>'

def simulated(text="Simulated", tooltip=None):
    _inject_css()
    if tooltip:
        return (f'<span class="badge-tip"><span class="data-badge badge-simulated">⚠ {text}</span>'
                f'<span class="tip-text">{tooltip}</span></span>')
    return f'<span class="data-badge badge-simulated">⚠ {text}</span>'

def model(text="ML Model", tooltip=None):
    _inject_css()
    if tooltip:
        return (f'<span class="badge-tip"><span class="data-badge badge-model">⚙ {text}</span>'
                f'<span class="tip-text">{tooltip}</span></span>')
    return f'<span class="data-badge badge-model">⚙ {text}</span>'


def provenance(real_items=None, simulated_items=None, production_note=None):
    """Render a tab-level data provenance bar."""
    _inject_css()
    parts = []
    if real_items:
        for item in real_items:
            parts.append(real(item))
    if simulated_items:
        for item in simulated_items:
            parts.append(simulated(item))

    html = f'<div class="provenance-bar">📋 <strong>Data sources:</strong> {" ".join(parts)}'
    if production_note:
        html += f'<br><span class="prod-note">In production: {production_note}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def chart_badges(*badges):
    """Render a small badge strip directly above a chart or table.

    Usage:
        chart_badges(
            real("Headlines", "25 verified articles from published news sources"),
            simulated("Sentiment Scores", "Generated using topic-level base scores, not a live NLP model"),
        )
    """
    _inject_css()
    html = f'<div class="chart-badge-strip">{" ".join(badges)}</div>'
    st.markdown(html, unsafe_allow_html=True)

"""Tab 1: Public Sentiment Analysis about Tri-State G&T."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

DATA_PATH = Path(__file__).parent.parent / "data" / "sentiment_data.csv"

# Import source bias data
sys.path.insert(0, str(Path(__file__).parent.parent / "data"))
from real_headlines import SOURCE_BIAS

# Tri-State brand palette for charts
TS_BLUE = "#005a9c"
TS_BLUE2 = "#0073cf"
TS_DARK = "#003d6b"
TS_LIGHT = "#e8f1fa"
TS_GRAY = "#787878"
TS_COLORS = [TS_BLUE, TS_BLUE2, "#2ecc71", "#f39c12", "#e74c3c", "#9b59b6", "#1abc9c", "#34495e"]


def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df


def render():
    from tabs.data_badge import provenance, chart_badges, real, simulated, model

    st.header("Public Sentiment Analysis")
    st.markdown(
        "AI-powered analysis of public discourse, news coverage, and regulatory "
        "filings related to Tri-State Generation & Transmission. "
        "Sentiment scores range from **-1.0** (very negative) to **+1.0** (very positive)."
    )
    provenance(
        real_items=["25 verified headlines from published sources"],
        simulated_items=["475 modeled headlines", "Sentiment scores", "Bias adjustments"],
        production_note="Live news API feeds, NLP sentiment model, empirical bias calibration",
    )

    df = load_data()

    # --- Filters ---
    col1, col2, col3 = st.columns(3)
    with col1:
        topics = st.multiselect(
            "Filter by Topic",
            options=sorted(df["topic"].unique()),
            default=sorted(df["topic"].unique()),
        )
    with col2:
        sources = st.multiselect(
            "Filter by Source",
            options=sorted(df["source"].unique()),
            default=sorted(df["source"].unique()),
        )
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(df["date"].min().date(), df["date"].max().date()),
            min_value=df["date"].min().date(),
            max_value=df["date"].max().date(),
        )

    # Apply filters
    mask = (
        df["topic"].isin(topics)
        & df["source"].isin(sources)
    )
    if len(date_range) == 2:
        mask &= (df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])
    filtered = df[mask]

    # --- KPI Cards ---
    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    avg_sent = filtered["sentiment_score"].mean()
    real_count = int(filtered["is_real"].sum()) if "is_real" in filtered.columns else 0
    k1.metric("Average Sentiment", f"{avg_sent:.2f}", delta=f"{'Positive' if avg_sent > 0 else 'Negative'}")
    k2.metric("Articles Analyzed", f"{len(filtered):,}", delta=f"{real_count} verified")
    k3.metric("Topics Covered", f"{filtered['topic'].nunique()}")
    most_neg = filtered.groupby("topic")["sentiment_score"].mean().idxmin()
    most_neg_score = filtered.groupby("topic")["sentiment_score"].mean().min()
    k4.metric("Lowest Sentiment", most_neg, delta=f"{most_neg_score:.2f}")

    # --- Sentiment Over Time ---
    st.markdown("### Sentiment Trend Over Time")
    monthly = (
        filtered.set_index("date")
        .groupby("topic")
        .resample("ME")["sentiment_score"]
        .mean()
        .reset_index()
    )
    fig_trend = px.line(
        monthly, x="date", y="sentiment_score", color="topic",
        title="Monthly Average Sentiment by Topic",
        labels={"sentiment_score": "Sentiment Score", "date": "Date"},
        template="plotly_white",
        color_discrete_sequence=TS_COLORS,
    )
    fig_trend.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig_trend.update_layout(
        height=550,
        xaxis=dict(title="", tickformat="%b %Y", dtick="M3"),
        margin=dict(b=120),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_trend, width="stretch")

    # --- Sentiment by Topic ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Sentiment Distribution by Topic")
        topic_avg = filtered.groupby("topic")["sentiment_score"].mean().sort_values()
        colors = ["#e74c3c" if v < -0.1 else "#f39c12" if v < 0.1 else TS_BLUE for v in topic_avg.values]
        fig_bar = go.Figure(go.Bar(
            x=topic_avg.values,
            y=topic_avg.index,
            orientation="h",
            marker_color=colors,
            text=[f"{v:.2f}" for v in topic_avg.values],
            textposition="auto",
        ))
        fig_bar.update_layout(
            template="plotly_white", height=400,
            xaxis_title="Average Sentiment Score",
            yaxis_title="",
        )
        fig_bar.add_vline(x=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig_bar, width="stretch")

    with col_b:
        st.markdown("### Article Volume by Topic")
        topic_counts = filtered["topic"].value_counts()
        fig_pie = px.pie(
            values=topic_counts.values,
            names=topic_counts.index,
            template="plotly_white",
            hole=0.4,
            color_discrete_sequence=TS_COLORS,
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, width="stretch")

    # --- SOURCE BIAS & HEATMAP (collapsed for cleaner demo flow) ---
    st.markdown("---")
    with st.expander("Detailed Analysis: Source Bias, Credibility & Heatmap", expanded=False):
        st.markdown("### Source Bias & Credibility Assessment")
        st.markdown(
            "Understanding editorial perspective is critical for interpreting sentiment data. "
            "Each source carries inherent framing bias that affects how Tri-State stories are reported."
        )

        source_list = filtered["source"].unique()
        bias_rows = []
        for src in sorted(source_list):
            info = SOURCE_BIAS.get(src, {
                "bias_score": 0.0, "bias_label": "Unknown",
                "description": "No bias profile available.", "type": "Unknown",
                "credibility": "Unknown",
            })
            raw_sentiment = filtered[filtered["source"] == src]["sentiment_score"].mean()
            adjusted_sentiment = raw_sentiment - (info["bias_score"] * 0.3)
            article_count = len(filtered[filtered["source"] == src])

            bias_rows.append({
                "Source": src, "Type": info["type"], "Bias": info["bias_label"],
                "Bias Score": info["bias_score"],
                "Credibility": info.get("credibility", "Unknown"),
                "Articles": article_count,
                "Raw Sentiment": round(raw_sentiment, 3),
                "Adjusted Sentiment": round(adjusted_sentiment, 3),
            })

        bias_df = pd.DataFrame(bias_rows)

        col_bias1, col_bias2 = st.columns([3, 2])
        with col_bias1:
            fig_bias = go.Figure()
            for _, row in bias_df.iterrows():
                color = (
                    "#e74c3c" if abs(row["Bias Score"]) > 0.3
                    else "#f39c12" if abs(row["Bias Score"]) > 0.1
                    else TS_BLUE
                )
                fig_bias.add_trace(go.Scatter(
                    x=[row["Bias Score"]], y=[row["Source"]],
                    mode="markers",
                    marker=dict(size=max(10, row["Articles"] // 2), color=color),
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{row['Source']}</b><br>"
                        f"Bias: {row['Bias']} ({row['Bias Score']:+.2f})<br>"
                        f"Type: {row['Type']}<br>"
                        f"Credibility: {row['Credibility']}<br>"
                        f"Articles: {row['Articles']}<extra></extra>"
                    ),
                ))
            fig_bias.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
            fig_bias.add_vrect(x0=-1, x1=-0.3, fillcolor="#fee2e2", opacity=0.15, line_width=0)
            fig_bias.add_vrect(x0=-0.3, x1=-0.1, fillcolor="#fef3c7", opacity=0.15, line_width=0)
            fig_bias.add_vrect(x0=-0.1, x1=0.1, fillcolor="#d1fae5", opacity=0.15, line_width=0)
            fig_bias.add_vrect(x0=0.1, x1=0.3, fillcolor="#fef3c7", opacity=0.15, line_width=0)
            fig_bias.add_vrect(x0=0.3, x1=1, fillcolor="#dbeafe", opacity=0.15, line_width=0)
            fig_bias.update_layout(
                title="Source Editorial Bias Spectrum",
                template="plotly_white", height=400,
                xaxis=dict(title="Conservative ← Center → Progressive", range=[-0.8, 0.8], dtick=0.2),
                yaxis=dict(title=""), margin=dict(r=30),
            )
            st.plotly_chart(fig_bias, width="stretch")

        with col_bias2:
            st.markdown("**Source Credibility:**")
            for _, row in bias_df.sort_values("Bias Score").iterrows():
                icon = "🔴" if abs(row["Bias Score"]) > 0.3 else "🟡" if abs(row["Bias Score"]) > 0.1 else "🟢"
                st.markdown(f"{icon} **{row['Source']}** — {row['Bias']} ({row['Credibility']})")

        st.markdown("#### Raw vs Bias-Adjusted Sentiment")
        fig_compare = go.Figure()
        bias_sorted = bias_df.sort_values("Raw Sentiment")
        fig_compare.add_trace(go.Bar(
            y=bias_sorted["Source"], x=bias_sorted["Raw Sentiment"],
            name="Raw Sentiment", orientation="h", marker_color=TS_BLUE, opacity=0.6,
        ))
        fig_compare.add_trace(go.Bar(
            y=bias_sorted["Source"], x=bias_sorted["Adjusted Sentiment"],
            name="Bias-Adjusted", orientation="h", marker_color="#e74c3c", opacity=0.8,
        ))
        fig_compare.add_vline(x=0, line_dash="dash", line_color="gray")
        fig_compare.update_layout(
            template="plotly_white", height=400, barmode="group",
            xaxis_title="Sentiment Score",
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            margin=dict(b=80),
        )
        st.plotly_chart(fig_compare, width="stretch")

        st.markdown("#### Sentiment Heatmap: Topic x Source")
        pivot = filtered.pivot_table(
            index="topic", columns="source", values="sentiment_score", aggfunc="mean"
        ).fillna(0)
        fig_heat = px.imshow(
            pivot, color_continuous_scale="RdYlGn", zmin=-0.6, zmax=0.6,
            labels=dict(color="Avg Sentiment"), template="plotly_white",
        )
        fig_heat.update_layout(height=400)
        st.plotly_chart(fig_heat, width="stretch")

    # --- Recent Headlines ---
    st.markdown("### Recent Headlines")
    if "is_real" in filtered.columns:
        recent = filtered.nlargest(20, "date")[["date", "topic", "source", "headline", "sentiment_score", "is_real"]].copy()
        recent["verified"] = recent["is_real"].apply(lambda x: "Verified" if x else "Modeled")
    else:
        recent = filtered.nlargest(20, "date")[["date", "topic", "source", "headline", "sentiment_score"]].copy()
        recent["verified"] = "Modeled"

    recent["sentiment_label"] = recent["sentiment_score"].apply(
        lambda x: "Positive" if x > 0.1 else ("Negative" if x < -0.1 else "Neutral")
    )
    display_cols = ["date", "headline", "topic", "source", "sentiment_label", "verified"]
    st.dataframe(recent[display_cols], width="stretch", hide_index=True)

    # --- DATA SOURCE & METHODOLOGY ---
    st.markdown("---")
    st.markdown("### Data Source & Methodology")

    with st.expander("How This Data Was Collected & Processed", expanded=False):
        real_count_total = int(df["is_real"].sum()) if "is_real" in df.columns else 0
        total_count = len(df)

        st.markdown(f"""
#### Data Composition

This dashboard analyzes **{total_count} articles** from two categories:

| Category | Count | Description |
|----------|-------|-------------|
| **Verified Headlines** | {real_count_total} | Real headlines from Colorado Sun, RTO Insider, CPR News, NPR, Utility Dive, Power Magazine, EDF, Colorado Newsline |
| **Modeled Headlines** | {total_count - real_count_total} | Synthetic headlines modeled after real coverage patterns |

#### Production Data Pipeline

In production, 100% of data would come from real sources via:
1. **News API integrations** (NewsAPI, GDELT, MediaCloud)
2. **RSS feeds** from trade publications
3. **FERC/PUC docket scraping** for regulatory filings
4. **Social media APIs** for public discourse
5. **Member cooperative communications**

#### Bias Mitigation Strategy

1. **Source Bias Profiling** - Each source has a documented editorial lean score
2. **Bias-Adjusted Scoring** - 30% correction factor based on known editorial lean
3. **Multi-Source Triangulation** - Weight consensus sentiment higher
4. **Stakeholder Segmentation** - Segment by audience perspective
5. **Transparency** - Every data point labeled as verified or modeled

#### Limitations

- Sentiment scores are probabilistic estimates, not facts
- Source bias scores are approximations
- NLP models can misinterpret sarcasm or domain-specific language
- This tool should **inform** decisions, not **automate** them
""")

    # --- Strategic Insights ---
    st.markdown("### AI-Generated Strategic Insights")
    st.info(
        "**Key Findings:**\n\n"
        "1. **Member Relations and Rate Changes** consistently show the most negative sentiment, "
        "driven by contract flexibility disputes, bond downgrades, and member departures "
        "(United Power exit May 2024, LPEA withdrawal filing March 2024).\n\n"
        "2. **The Craig Station coal plant controversy** dominates recent coverage (Q1 2026), with "
        "Tri-State notably opposing the DOE's emergency order - positioning the cooperative "
        "as pro-transition against federal intervention. This is a positive narrative opportunity.\n\n"
        "3. **Renewable Energy and Community Impact** are the strongest positive sentiment drivers. "
        "The $2.5B New ERA funding and SPP RTO West membership are underreported positive stories.\n\n"
        "4. **Source bias analysis reveals** that progressive-leaning outlets drive slightly more "
        "negative coverage on rates/coal, while industry publications are more positive on reliability. "
        "Bias-adjusted scores show the overall narrative is more neutral than raw scores suggest.\n\n"
        "**Recommendation:** Deploy bias-aware sentiment monitoring for Communications "
        "and Member Services. Leverage the Craig Station narrative (Tri-State opposing "
        "forced coal extension) as a proactive messaging opportunity."
    )

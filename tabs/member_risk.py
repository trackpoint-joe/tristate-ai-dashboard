"""Tab 2: Member Retention Risk Intelligence."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "member_risk_data.csv"

TS_BLUE = "#005a9c"
TS_DARK = "#003d6b"
TS_LIGHT = "#e8f1fa"


def load_data():
    return pd.read_csv(DATA_PATH)


def render():
    from tabs.data_badge import provenance, chart_badges, real, simulated, model

    st.header("Member Retention Risk Intelligence")
    st.markdown(
        "AI-driven early warning system for member cooperative retention. "
        "Combines rate analysis, satisfaction signals, public board activity, and "
        "behavioral indicators to predict flight risk and recommend retention actions."
    )
    provenance(
        real_items=["Member cooperative names", "Departed member events"],
        simulated_items=["Risk scores", "Rate figures", "Satisfaction ratings", "Warning signals"],
        production_note="Live member data feeds, board minutes NLP monitoring, actual rate comparisons",
    )

    df = load_data()
    active = df[df["status"] == "active"].copy()
    at_risk = active[active["risk_score"] > 0.3]
    departing = df[df["status"].isin(["departing_2026", "partial_exit"])]

    # --- KPI Cards ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Active Members", len(active))
    k2.metric("At-Risk Members", len(at_risk),
              delta=f"{len(at_risk)/len(active)*100:.0f}% of active", delta_color="inverse")
    revenue_at_risk = at_risk["annual_revenue_millions"].sum()
    k3.metric("Revenue at Risk", f"${revenue_at_risk:.0f}M/yr")
    avg_rate_gap = active["rate_gap"].mean()
    k4.metric("Avg Rate Gap", f"${avg_rate_gap:.0f}/MWh",
              delta="vs market alternatives", delta_color="inverse")

    # --- Executive Summary (above the fold) ---
    st.markdown(
        f'<div style="background:#fce4ec; border-left:5px solid #e74c3c; padding:1rem 1.25rem; '
        f'border-radius:0 6px 6px 0; margin:0.75rem 0;">'
        f'<span style="font-size:1.3rem; font-weight:700; color:#c62828;">'
        f'${revenue_at_risk:.0f}M in annual revenue at risk</span><br>'
        f'<span style="color:#555;">{len(at_risk)} of {len(active)} active members show elevated flight risk. '
        f'Board activity monitoring and proactive engagement could prevent the next departure.</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # --- Risk Heatmap by Member ---
    st.markdown("### Member Risk Overview")

    # Scatter: risk score vs rate gap, sized by revenue
    fig_scatter = px.scatter(
        active, x="rate_gap", y="risk_score",
        size="annual_revenue_millions",
        color="risk_score",
        color_continuous_scale=["#27ae60", "#f39c12", "#e74c3c"],
        hover_name="member",
        hover_data={
            "state": True,
            "consumers": ":,",
            "annual_revenue_millions": ":.1f",
            "risk_score": ":.2f",
            "rate_gap": ":.1f",
            "satisfaction_score": ":.2f",
        },
        labels={
            "rate_gap": "Rate Gap vs Market Alternative ($/MWh)",
            "risk_score": "Flight Risk Score",
            "annual_revenue_millions": "Annual Revenue ($M)",
        },
        template="plotly_white",
    )
    fig_scatter.update_layout(
        height=500,
        coloraxis_colorbar_title="Risk",
    )
    # Add quadrant lines
    fig_scatter.add_hline(y=0.3, line_dash="dash", line_color="gray", opacity=0.5,
                           annotation_text="Risk Threshold")
    fig_scatter.add_vline(x=15, line_dash="dash", line_color="gray", opacity=0.5,
                           annotation_text="Rate Concern Threshold")

    st.plotly_chart(fig_scatter, width="stretch")
    st.caption(
        "Bubble size = annual revenue. Upper-right quadrant = high risk + high rate gap — priority retention targets. "
        "Hover over any bubble for member details."
    )

    # --- Risk Ranked Table ---
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown("### Risk-Ranked Member Table")
        display = active.sort_values("risk_score", ascending=False).copy()
        display["risk_level"] = display["risk_score"].apply(
            lambda x: "HIGH" if x > 0.5 else ("MEDIUM" if x > 0.3 else "LOW")
        )
        display["rate_gap_display"] = display["rate_gap"].apply(lambda x: f"${x:.0f}/MWh")
        display["revenue_display"] = display["annual_revenue_millions"].apply(lambda x: f"${x:.1f}M")

        st.dataframe(
            display[["member", "state", "consumers", "risk_level", "risk_score",
                     "rate_gap_display", "revenue_display", "satisfaction_score"]].rename(columns={
                "member": "Member",
                "state": "State",
                "consumers": "Consumers",
                "risk_level": "Risk Level",
                "risk_score": "Risk Score",
                "rate_gap_display": "Rate Gap",
                "revenue_display": "Revenue",
                "satisfaction_score": "Satisfaction",
            }),
            width="stretch", hide_index=True, height=450,
        )

    with col_b:
        st.markdown("### Risk Distribution")
        risk_bins = pd.cut(active["risk_score"], bins=[0, 0.15, 0.3, 0.5, 1.0],
                           labels=["Low", "Moderate", "Elevated", "High"])
        risk_counts = risk_bins.value_counts().sort_index()
        colors = {"Low": "#27ae60", "Moderate": TS_BLUE, "Elevated": "#f39c12", "High": "#e74c3c"}

        fig_dist = go.Figure(go.Bar(
            x=risk_counts.index.astype(str),
            y=risk_counts.values,
            marker_color=[colors.get(str(k), TS_BLUE) for k in risk_counts.index],
            text=risk_counts.values,
            textposition="auto",
        ))
        fig_dist.update_layout(template="plotly_white", height=250,
                               xaxis_title="Risk Level", yaxis_title="Members")
        st.plotly_chart(fig_dist, width="stretch")

        st.markdown("### Revenue by Risk Level")
        active["risk_level"] = pd.cut(active["risk_score"], bins=[0, 0.15, 0.3, 0.5, 1.0],
                                       labels=["Low", "Moderate", "Elevated", "High"])
        rev_by_risk = active.groupby("risk_level", observed=True)["annual_revenue_millions"].sum()
        fig_rev = go.Figure(go.Pie(
            labels=rev_by_risk.index.astype(str),
            values=rev_by_risk.values,
            marker_colors=[colors.get(str(k), TS_BLUE) for k in rev_by_risk.index],
            hole=0.4,
            textinfo="label+percent",
        ))
        fig_rev.update_layout(height=250, showlegend=False)
        st.plotly_chart(fig_rev, width="stretch")

    # --- State-level Analysis ---
    st.markdown("### Risk by State")
    state_summary = active.groupby("state").agg({
        "member": "count",
        "consumers": "sum",
        "annual_revenue_millions": "sum",
        "risk_score": "mean",
        "rate_gap": "mean",
    }).rename(columns={
        "member": "Members",
        "consumers": "Total Consumers",
        "annual_revenue_millions": "Total Revenue ($M)",
        "risk_score": "Avg Risk Score",
        "rate_gap": "Avg Rate Gap ($/MWh)",
    }).round(2)
    st.dataframe(state_summary, width="stretch")

    # --- Member Deep Dive ---
    st.markdown("---")
    st.markdown("### Member Deep Dive")
    selected_member = st.selectbox(
        "Select a member cooperative for detailed analysis:",
        options=df["member"].tolist(),
    )

    member = df[df["member"] == selected_member].iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Risk Score", f"{member['risk_score']:.2f}",
              delta="HIGH" if member['risk_score'] > 0.5 else ("MEDIUM" if member['risk_score'] > 0.3 else "LOW"),
              delta_color="inverse" if member['risk_score'] > 0.3 else "normal")
    m2.metric("Satisfaction", f"{member['satisfaction_score']:.2f}")
    m3.metric("Rate Gap", f"${member['rate_gap']:.0f}/MWh",
              delta_color="inverse")

    m4, m5, m6 = st.columns(3)
    m4.metric("Consumers Served", f"{member['consumers']:,}")
    m5.metric("Annual Revenue", f"${member['annual_revenue_millions']:.1f}M")
    m6.metric("Contract Through", str(member['contract_end_year']))

    st.markdown("**Early Warning Signals:**")
    for signal in member["early_warning_signals"].split("; "):
        icon = "🔴" if any(w in signal.lower() for w in ["consultant", "alternative", "negative"]) else \
               "🟡" if any(w in signal.lower() for w in ["policy", "rate gap", "large"]) else "🟢"
        st.markdown(f"- {icon} {signal}")

    st.markdown("**Recommended Retention Actions:**")
    for action in member["recommended_actions"].split("; "):
        st.markdown(f"- {action}")

    if member["status"] in ["departing_2026", "partial_exit"]:
        st.warning(
            f"**{member['member']}** is currently {'in the process of departing (effective 2026)' if member['status'] == 'departing_2026' else 'operating under a partial requirements contract'}. "
            f"Estimated Contract Termination Payment: **${member['estimated_ctp_millions']:.1f}M**."
        )

    # --- Departed Members Lessons ---
    st.markdown("---")
    st.markdown("### Lessons from Departed Members")
    departed_data = {
        "Member": ["United Power", "Delta-Montrose Electric", "La Plata Electric (LPEA)", "Kit Carson Electric"],
        "Status": ["Exited May 2024", "Exited 2024", "Departing April 2026", "Partial Exit"],
        "Consumers": ["108,000", "34,000", "35,000", "29,000"],
        "Key Driver": [
            "Sought cheaper, cleaner power + local control",
            "Sought independence and cost reduction",
            "Rate concerns + desire for local renewable development",
            "Rate differential + community solar goals",
        ],
        "Warning Signs (in hindsight)": [
            "Years of public advocacy, FERC filings, hired consultants, board resolutions",
            "Board discussions about alternatives, rate comparison studies",
            "Board vote March 2024, public feasibility studies, consultant engagement",
            "Gradual reduction in purchased power, local generation investments",
        ],
        "Lesson for Retention": [
            "Early engagement before positions harden; address rate gap proactively",
            "Smaller members can exit too — don't focus only on large ones",
            "Board activity is the clearest leading indicator — monitor it",
            "Partial exit can be a retention tool if offered proactively",
        ],
    }
    st.dataframe(pd.DataFrame(departed_data), width="stretch", hide_index=True)

    # --- Strategic Insights ---
    st.markdown("### AI-Generated Strategic Insights")
    st.info(
        "**Key Findings:**\n\n"
        f"1. **{len(at_risk)} of {len(active)} active members show elevated risk scores** "
        f"representing **${revenue_at_risk:.0f}M in annual revenue**. "
        "The rate gap between Tri-State wholesale rates and market alternatives is the primary driver.\n\n"
        "2. **Colorado members carry the highest risk** due to state policy supporting cooperative "
        "choice and proximity to competitive power markets. Wyoming and Nebraska members show lower risk.\n\n"
        "3. **Larger members have disproportionate leverage** — they can achieve purchasing economies "
        "independently. Focus retention efforts on members with 20,000+ consumers.\n\n"
        "4. **Board activity is the strongest leading indicator** of exit intent. Departed members "
        "showed 12-24 months of public board discussion before filing. Automated monitoring of "
        "member board packets could provide early warning.\n\n"
        "**Recommendation:** Deploy an automated member board minutes monitoring system using NLP "
        "to scan for exit-related language, rate comparison studies, and consultant engagements. "
        "Pair with proactive executive outreach to at-risk members with customized value propositions "
        "showing the true cost of departure versus contract renegotiation."
    )

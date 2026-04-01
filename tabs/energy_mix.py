"""Tab 2: Energy Generation Mix & Transition Tracker."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "energy_mix_data.csv"

# Tri-State brand
TS_BLUE = "#005a9c"
TS_DARK = "#003d6b"


def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df


def render():
    from tabs.data_badge import provenance, chart_badges, real, simulated, model

    st.header("Energy Generation Mix & Transition Tracker")
    st.markdown(
        "Tracking Tri-State's generation portfolio evolution from coal-heavy to a diversified, "
        "cleaner energy mix — aligned with the **Responsible Energy Plan** targeting "
        "**80% CO₂ reduction by 2030** from 2005 levels."
    )
    provenance(
        real_items=["Transition trends based on public EIA patterns", "2030 target from Responsible Energy Plan"],
        simulated_items=["Monthly generation figures", "CO2 calculations"],
        production_note="EIA API data feeds, Tri-State generation reporting systems",
    )

    df = load_data()

    # --- KPI Cards ---
    latest = df[df["date"] == df["date"].max()].iloc[0]
    earliest = df[df["date"] == df["date"].min()].iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    coal_change = latest["coal_pct"] - earliest["coal_pct"]
    k1.metric("Current Coal %", f"{latest['coal_pct']:.1f}%", delta=f"{coal_change:+.1f}% since 2015", delta_color="inverse")
    renew_current = latest["wind_pct"] + latest["solar_pct"] + latest["hydro_pct"]
    renew_earliest = earliest["wind_pct"] + earliest["solar_pct"] + earliest["hydro_pct"]
    k2.metric("Current Renewables %", f"{renew_current:.1f}%", delta=f"+{renew_current - renew_earliest:.1f}% since 2015")
    k3.metric("Latest CO₂ (k tons)", f"{latest['co2_tons_thousands']:.0f}")
    k4.metric("Total Generation", f"{latest['total_gwh']:.0f} GWh")

    st.markdown("---")

    # --- Stacked Area: Generation Mix Over Time ---
    st.markdown("### Generation Mix Over Time")
    source_cols = ["coal_pct", "natural_gas_pct", "wind_pct", "solar_pct", "hydro_pct", "purchased_pct"]
    source_labels = {
        "coal_pct": "Coal",
        "natural_gas_pct": "Natural Gas",
        "wind_pct": "Wind",
        "solar_pct": "Solar",
        "hydro_pct": "Hydro",
        "purchased_pct": "Purchased Power",
    }
    source_colors = {
        "Coal": "#5d4e37",
        "Natural Gas": "#3498db",
        "Wind": "#1abc9c",
        "Solar": "#f1c40f",
        "Hydro": "#2980b9",
        "Purchased Power": "#95a5a6",
    }

    melted = df.melt(
        id_vars=["date"], value_vars=source_cols,
        var_name="source", value_name="percentage",
    )
    melted["source"] = melted["source"].map(source_labels)

    fig_area = px.area(
        melted, x="date", y="percentage", color="source",
        color_discrete_map=source_colors,
        template="plotly_white",
        labels={"percentage": "% of Generation", "date": ""},
    )
    fig_area.update_layout(height=450, legend=dict(orientation="h", yanchor="bottom", y=-0.25))
    st.plotly_chart(fig_area, width="stretch")

    # --- Annual Comparison ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Annual Average by Source")
        annual = df.groupby("year")[source_cols].mean().reset_index()
        annual_melted = annual.melt(
            id_vars=["year"], value_vars=source_cols,
            var_name="source", value_name="percentage",
        )
        annual_melted["source"] = annual_melted["source"].map(source_labels)

        fig_bar = px.bar(
            annual_melted, x="year", y="percentage", color="source",
            color_discrete_map=source_colors,
            template="plotly_white",
            labels={"percentage": "% of Generation", "year": ""},
        )
        fig_bar.update_layout(height=400, barmode="stack", legend=dict(orientation="h", yanchor="bottom", y=-0.3))
        st.plotly_chart(fig_bar, width="stretch")

    with col_b:
        st.markdown("### CO₂ Emissions Trend")
        annual_co2 = df.groupby("year")["co2_tons_thousands"].sum().reset_index()
        # Add 2030 target reference
        baseline_2015 = annual_co2[annual_co2["year"] == 2015]["co2_tons_thousands"].values[0]
        target_2030 = baseline_2015 * 0.20  # 80% reduction

        fig_co2 = go.Figure()
        fig_co2.add_trace(go.Bar(
            x=annual_co2["year"], y=annual_co2["co2_tons_thousands"],
            marker_color=TS_BLUE, name="Actual CO₂",
            text=[f"{v:,.0f}" for v in annual_co2["co2_tons_thousands"]],
            textposition="auto",
        ))
        fig_co2.add_hline(
            y=target_2030, line_dash="dash", line_color="green",
            annotation_text=f"2030 Target ({target_2030:,.0f}k tons)",
        )
        fig_co2.update_layout(template="plotly_white", height=400, yaxis_title="CO₂ (thousand tons)")
        st.plotly_chart(fig_co2, width="stretch")

    # --- Renewable Growth Detail ---
    st.markdown("### Renewable Energy Growth Detail")
    renew_cols = ["wind_pct", "solar_pct", "hydro_pct"]
    df["total_renewable_pct"] = df[renew_cols].sum(axis=1)

    monthly_renew = df[["date", "wind_pct", "solar_pct", "hydro_pct", "total_renewable_pct"]].copy()
    fig_renew = go.Figure()
    fig_renew.add_trace(go.Scatter(x=monthly_renew["date"], y=monthly_renew["wind_pct"],
                                    mode="lines", name="Wind", line=dict(color="#1abc9c")))
    fig_renew.add_trace(go.Scatter(x=monthly_renew["date"], y=monthly_renew["solar_pct"],
                                    mode="lines", name="Solar", line=dict(color="#f1c40f")))
    fig_renew.add_trace(go.Scatter(x=monthly_renew["date"], y=monthly_renew["hydro_pct"],
                                    mode="lines", name="Hydro", line=dict(color="#2980b9")))
    fig_renew.add_trace(go.Scatter(x=monthly_renew["date"], y=monthly_renew["total_renewable_pct"],
                                    mode="lines", name="Total Renewables",
                                    line=dict(color="#27ae60", width=3, dash="dot")))
    fig_renew.update_layout(template="plotly_white", height=400,
                            yaxis_title="% of Generation",
                            legend=dict(orientation="h", yanchor="bottom", y=-0.25))
    st.plotly_chart(fig_renew, width="stretch")

    # --- Strategic Insights ---
    st.markdown("### AI-Generated Strategic Insights")
    st.info(
        "**Key Findings:**\n\n"
        f"1. **Coal generation has declined from {earliest['coal_pct']:.1f}% to {latest['coal_pct']:.1f}%** "
        "over the tracking period — a significant but insufficient pace to meet the 80% CO₂ reduction target by 2030.\n\n"
        f"2. **Renewables (wind + solar + hydro) have grown from {renew_earliest:.1f}% to {renew_current:.1f}%** "
        "of the generation mix. Solar shows the fastest growth trajectory.\n\n"
        "3. **Natural gas serves as the transition fuel** — providing dispatchable capacity as coal retires, "
        "but its share will also need to decline long-term.\n\n"
        "4. **AI Opportunity:** Predictive models for renewable output forecasting could optimize dispatch "
        "decisions, reduce curtailment, and improve the economic case for accelerated renewable deployment.\n\n"
        "**Recommendation:** Deploy ML-based generation optimization to maximize renewable utilization, "
        "improve demand-supply matching, and reduce reliance on gas peaking — potentially saving "
        "$2-5M annually in fuel costs."
    )

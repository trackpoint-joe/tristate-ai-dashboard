"""
Generate realistic sample datasets for the Tri-State AI Intelligence Dashboard.
All data is modeled after publicly available patterns for Tri-State G&T.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)
DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_sentiment_data():
    """Generate realistic news/public sentiment data about Tri-State."""
    topics = [
        "Energy Transition",
        "Member Relations",
        "Rate Changes",
        "Renewable Energy",
        "Coal Retirement",
        "Grid Reliability",
        "Regulatory Compliance",
        "Community Impact",
    ]

    sources = [
        "Denver Post",
        "Colorado Sun",
        "Casper Star-Tribune",
        "Albuquerque Journal",
        "E&E News",
        "Utility Dive",
        "Reuters Energy",
        "Public Comment - FERC",
        "Public Comment - PUC",
        "Social Media",
    ]

    headlines = {
        "Energy Transition": [
            "Tri-State Accelerates Clean Energy Goals Ahead of 2030 Target",
            "Tri-State's Responsible Energy Plan Draws Mixed Reactions from Members",
            "Western Cooperatives Face Challenges in Energy Transition Timeline",
            "Tri-State Announces New Solar Project in Eastern Colorado",
            "Energy Transition Costs Raise Concerns Among Rural Cooperatives",
            "Tri-State Signs 500MW Wind Power Purchase Agreement",
            "Clean Energy Shift Creates Job Transition Questions for Tri-State Workers",
        ],
        "Member Relations": [
            "United Power Seeks Greater Flexibility in Tri-State Contract",
            "La Plata Electric Explores Partial Requirements Options",
            "Tri-State Introduces New Contract Flexibility Framework",
            "Member Cooperatives Push for More Local Generation Rights",
            "Tri-State Board Approves Revised Member Exit Provisions",
            "Kit Carson Electric Reports Savings After Partial Exit",
            "Small Rural Co-ops Express Support for Tri-State Stability",
        ],
        "Rate Changes": [
            "Tri-State Proposes 4.2% Wholesale Rate Increase for 2026",
            "FERC Reviews Tri-State Rate Filing Amid Member Concerns",
            "Cooperative Members Question Rising Wholesale Power Costs",
            "Tri-State Rates Remain Competitive vs Regional Utilities",
            "Rate Restructuring Could Benefit Smaller Member Systems",
            "Wholesale Rate Stability Critical for Rural Communities",
        ],
        "Renewable Energy": [
            "Tri-State Commissions 200MW Solar Farm in New Mexico",
            "Battery Storage Integration Advances at Tri-State Facilities",
            "Colorado Cooperative Renewable Portfolio Reaches 40%",
            "Tri-State Wind Capacity Surpasses 1GW Milestone",
            "New Pumped Hydro Study Shows Promise for Tri-State Territory",
            "Distributed Solar Growth Creates Grid Management Challenges",
        ],
        "Coal Retirement": [
            "Craig Station Unit 3 Retirement Timeline Under Discussion",
            "Tri-State Plans Managed Coal Plant Transition Through 2030",
            "Community Impact Plans Announced for Craig Station Workers",
            "Coal Retirement Costs Create Long-term Financial Obligations",
            "Environmental Groups Praise Accelerated Coal Phase-out",
            "Workforce Transition Programs Launched for Affected Communities",
        ],
        "Grid Reliability": [
            "Tri-State Invests $150M in Transmission Upgrades",
            "Winter Storm Tests Western Grid Reliability",
            "Tri-State Grid Performance Exceeds NERC Standards",
            "New SCADA Systems Improve Real-time Grid Monitoring",
            "Wildfire Risk Drives Enhanced Vegetation Management Program",
            "Tri-State Deploys Advanced Fault Detection Technology",
        ],
        "Regulatory Compliance": [
            "Tri-State Passes NERC CIP Compliance Audit",
            "FERC Order Impacts Cooperative Wholesale Market Participation",
            "Colorado Clean Energy Standards Tighten for Wholesale Providers",
            "Tri-State Enhances Cybersecurity Program for Grid Protection",
            "New EPA Rules Affect Remaining Coal Fleet Operations",
        ],
        "Community Impact": [
            "Tri-State Awards $2M in Community Development Grants",
            "Rural Broadband Initiative Leverages Cooperative Infrastructure",
            "Cooperative Model Delivers Value to Rural Western Communities",
            "Tri-State Foundation Supports Workforce Development Programs",
            "Member Communities Benefit from Cooperative Dividend Distribution",
        ],
    }

    # --- Import real headlines ---
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from real_headlines import REAL_HEADLINES

    rows = []

    # Add real headlines first
    base_sentiment = {
        "Energy Transition": 0.15,
        "Member Relations": -0.20,
        "Rate Changes": -0.25,
        "Renewable Energy": 0.35,
        "Coal Retirement": -0.05,
        "Grid Reliability": 0.25,
        "Regulatory Compliance": 0.05,
        "Community Impact": 0.45,
    }

    for rh in REAL_HEADLINES:
        sentiment = np.clip(
            base_sentiment.get(rh["topic"], 0.0) + np.random.normal(0, 0.15), -1, 1
        )
        rows.append({
            "date": rh["date"],
            "topic": rh["topic"],
            "source": rh["source"],
            "headline": rh["headline"],
            "sentiment_score": round(sentiment, 3),
            "relevance_score": round(np.random.uniform(0.7, 1.0), 2),
            "is_real": True,
        })

    # Add synthetic headlines to fill out the dataset
    base_date = datetime(2024, 1, 1)
    for i in range(475):
        date = base_date + timedelta(days=np.random.randint(0, 820))
        topic = np.random.choice(topics, p=[0.18, 0.16, 0.14, 0.15, 0.12, 0.10, 0.08, 0.07])
        source = np.random.choice(sources)
        headline = np.random.choice(headlines[topic])

        sentiment = np.clip(
            base_sentiment[topic] + np.random.normal(0, 0.25), -1, 1
        )

        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "topic": topic,
            "source": source,
            "headline": headline,
            "sentiment_score": round(sentiment, 3),
            "relevance_score": round(np.random.uniform(0.4, 1.0), 2),
            "is_real": False,
        })

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    df.to_csv(os.path.join(DATA_DIR, "sentiment_data.csv"), index=False)
    print(f"Generated {len(df)} sentiment records ({len(REAL_HEADLINES)} real, {len(df)-len(REAL_HEADLINES)} synthetic)")


def generate_energy_mix_data():
    """Generate Tri-State generation mix data modeled after EIA public data."""
    rows = []
    for year in range(2015, 2027):
        for month in range(1, 13):
            if year == 2026 and month > 3:
                break

            # Tri-State's transition: coal declining, renewables growing
            year_offset = year - 2015

            coal_pct = max(10, 65 - year_offset * 4.5 + np.random.normal(0, 2))
            natural_gas_pct = 18 + year_offset * 0.8 + np.random.normal(0, 1.5)
            wind_pct = 8 + year_offset * 1.8 + np.random.normal(0, 1)
            solar_pct = 2 + year_offset * 1.5 + np.random.normal(0, 0.8)
            hydro_pct = 4 + np.random.normal(0, 0.5)
            purchased_pct = 3 + year_offset * 0.3 + np.random.normal(0, 0.5)

            # Normalize to 100%
            total = coal_pct + natural_gas_pct + wind_pct + solar_pct + hydro_pct + purchased_pct
            factor = 100 / total

            # Total generation varies by season (higher in summer/winter)
            seasonal = 1.0 + 0.12 * np.sin(2 * np.pi * (month - 1) / 12) + 0.08 * np.cos(4 * np.pi * (month - 1) / 12)
            total_gwh = (1100 + year_offset * 30) * seasonal + np.random.normal(0, 40)

            rows.append({
                "year": year,
                "month": month,
                "date": f"{year}-{month:02d}-01",
                "total_gwh": round(max(800, total_gwh), 1),
                "coal_pct": round(coal_pct * factor, 1),
                "natural_gas_pct": round(natural_gas_pct * factor, 1),
                "wind_pct": round(wind_pct * factor, 1),
                "solar_pct": round(solar_pct * factor, 1),
                "hydro_pct": round(max(0.5, hydro_pct * factor), 1),
                "purchased_pct": round(max(0.5, purchased_pct * factor), 1),
                "co2_tons_thousands": round(
                    max(100, (coal_pct * factor / 100) * total_gwh * 0.95
                    + (natural_gas_pct * factor / 100) * total_gwh * 0.4), 1
                ),
            })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "energy_mix_data.csv"), index=False)
    print(f"Generated {len(df)} energy mix records")


def generate_price_data():
    """Generate wholesale electricity price data for Western Interconnection."""
    rows = []
    base_date = datetime(2022, 1, 1)

    for day_offset in range(1550):  # ~4.2 years of daily data
        date = base_date + timedelta(days=day_offset)
        if date > datetime(2026, 3, 31):
            break

        month = date.month
        dow = date.weekday()
        year = date.year

        # Base price with trend (slight increase over time)
        base_price = 35 + (year - 2022) * 2.5

        # Seasonal pattern — higher in summer (AC) and winter (heating)
        seasonal = 12 * np.sin(2 * np.pi * (month - 7) / 12) ** 2 + 5 * (month in [12, 1, 2])

        # Day of week effect
        dow_effect = -3 if dow >= 5 else 0

        # Random weather/demand spikes
        spike = 0
        if np.random.random() < 0.03:  # 3% chance of price spike
            spike = np.random.uniform(20, 80)

        # Natural gas price influence (correlated)
        ng_price = 2.5 + (year - 2022) * 0.3 + np.random.normal(0, 0.4)

        # Renewable curtailment effect (midday solar depression)
        solar_depression = -3 * max(0, (year - 2023)) * (month in [4, 5, 6, 7, 8, 9])

        price = max(8, base_price + seasonal + dow_effect + spike + solar_depression
                     + ng_price * 3 + np.random.normal(0, 6))

        # Demand (MW)
        base_demand = 2800
        demand_seasonal = 400 * np.sin(2 * np.pi * (month - 7) / 12) ** 2 + 200 * (month in [12, 1, 2])
        demand_dow = -300 if dow >= 5 else 0
        demand = max(1800, base_demand + demand_seasonal + demand_dow + np.random.normal(0, 150))

        # Temperature (Denver area, affects demand)
        temp_base = 50 + 25 * np.sin(2 * np.pi * (month - 4) / 12)
        temp = temp_base + np.random.normal(0, 8)

        # Wind generation (MW)
        wind_gen = max(0, 350 + 100 * np.sin(2 * np.pi * (month - 3) / 12) + np.random.normal(0, 120))

        # Solar generation (MW)
        solar_capacity = 200 + (year - 2022) * 80
        solar_gen = max(0, solar_capacity * (0.25 + 0.15 * np.sin(2 * np.pi * (month - 3) / 12))
                        + np.random.normal(0, 30))

        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "price_mwh": round(price, 2),
            "demand_mw": round(demand, 0),
            "temperature_f": round(temp, 1),
            "wind_generation_mw": round(wind_gen, 1),
            "solar_generation_mw": round(solar_gen, 1),
            "natural_gas_price": round(ng_price, 2),
            "day_of_week": dow,
            "month": month,
            "is_weekend": int(dow >= 5),
            "is_spike": int(spike > 0),
        })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, "price_data.csv"), index=False)
    print(f"Generated {len(df)} price records")


if __name__ == "__main__":
    print("Generating Tri-State AI Dashboard sample data...")
    generate_sentiment_data()
    generate_energy_mix_data()
    generate_price_data()
    print("Done! All data files saved to data/ directory.")

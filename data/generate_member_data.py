"""
Generate realistic member cooperative data for the Member Retention Risk tab.
Modeled after Tri-State's actual member cooperatives (public information).
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

np.random.seed(42)
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# Real and realistic member cooperatives (public information)
MEMBERS = [
    # Colorado members
    {"name": "Empire Electric", "state": "CO", "consumers": 15200, "peak_mw": 68, "status": "active"},
    {"name": "Gunnison County Electric", "state": "CO", "consumers": 8900, "peak_mw": 42, "status": "active"},
    {"name": "Highline Electric", "state": "CO", "consumers": 6400, "peak_mw": 31, "status": "active"},
    {"name": "Intermountain REA", "state": "CO", "consumers": 28500, "peak_mw": 112, "status": "active"},
    {"name": "K.C. Electric", "state": "CO", "consumers": 3100, "peak_mw": 18, "status": "active"},
    {"name": "Morgan County REA", "state": "CO", "consumers": 7600, "peak_mw": 38, "status": "active"},
    {"name": "Mountain Parks Electric", "state": "CO", "consumers": 22300, "peak_mw": 95, "status": "active"},
    {"name": "Mountain View Electric", "state": "CO", "consumers": 54000, "peak_mw": 198, "status": "active"},
    {"name": "Poudre Valley REA", "state": "CO", "consumers": 43000, "peak_mw": 165, "status": "active"},
    {"name": "San Isabel Electric", "state": "CO", "consumers": 19800, "peak_mw": 76, "status": "active"},
    {"name": "San Luis Valley REC", "state": "CO", "consumers": 11200, "peak_mw": 48, "status": "active"},
    {"name": "San Miguel Power", "state": "CO", "consumers": 11500, "peak_mw": 52, "status": "active"},
    {"name": "Southeast Colorado Power", "state": "CO", "consumers": 6800, "peak_mw": 34, "status": "active"},
    {"name": "White River Electric", "state": "CO", "consumers": 4100, "peak_mw": 22, "status": "active"},
    {"name": "Y-W Electric", "state": "CO", "consumers": 8700, "peak_mw": 41, "status": "active"},
    # New Mexico members
    {"name": "Central New Mexico EC", "state": "NM", "consumers": 16500, "peak_mw": 72, "status": "active"},
    {"name": "Columbus Electric", "state": "NM", "consumers": 5600, "peak_mw": 28, "status": "active"},
    {"name": "Continental Divide EC", "state": "NM", "consumers": 8200, "peak_mw": 39, "status": "active"},
    {"name": "Jemez Mountains EC", "state": "NM", "consumers": 7800, "peak_mw": 36, "status": "active"},
    {"name": "Mora-San Miguel EC", "state": "NM", "consumers": 4200, "peak_mw": 21, "status": "active"},
    {"name": "Northern Rio Arriba EC", "state": "NM", "consumers": 5100, "peak_mw": 25, "status": "active"},
    {"name": "Otero County EC", "state": "NM", "consumers": 9300, "peak_mw": 44, "status": "active"},
    {"name": "Sierra Electric", "state": "NM", "consumers": 6700, "peak_mw": 32, "status": "active"},
    {"name": "Socorro Electric", "state": "NM", "consumers": 10100, "peak_mw": 46, "status": "active"},
    {"name": "Springer Electric", "state": "NM", "consumers": 2800, "peak_mw": 14, "status": "active"},
    # Wyoming members
    {"name": "Big Horn REA", "state": "WY", "consumers": 4500, "peak_mw": 23, "status": "active"},
    {"name": "Bridger Valley Electric", "state": "WY", "consumers": 6200, "peak_mw": 30, "status": "active"},
    {"name": "Carbon Power & Light", "state": "WY", "consumers": 7400, "peak_mw": 35, "status": "active"},
    {"name": "Garland Light & Power", "state": "WY", "consumers": 3200, "peak_mw": 16, "status": "active"},
    {"name": "High Plains Power", "state": "WY", "consumers": 4800, "peak_mw": 24, "status": "active"},
    {"name": "High West Energy", "state": "WY", "consumers": 9100, "peak_mw": 43, "status": "active"},
    {"name": "Niobrara Electric", "state": "WY", "consumers": 3600, "peak_mw": 19, "status": "active"},
    {"name": "Wheatland REA", "state": "WY", "consumers": 5400, "peak_mw": 27, "status": "active"},
    {"name": "Wyrulec Company", "state": "WY", "consumers": 4100, "peak_mw": 21, "status": "active"},
    # Nebraska
    {"name": "Chimney Rock PPI", "state": "NE", "consumers": 3800, "peak_mw": 20, "status": "active"},
    # Departed members (for context)
    {"name": "United Power", "state": "CO", "consumers": 108000, "peak_mw": 420, "status": "departed_2024"},
    {"name": "La Plata Electric (LPEA)", "state": "CO", "consumers": 35000, "peak_mw": 145, "status": "departing_2026"},
    {"name": "Kit Carson Electric", "state": "NM", "consumers": 29000, "peak_mw": 118, "status": "partial_exit"},
    {"name": "Delta-Montrose Electric", "state": "CO", "consumers": 34000, "peak_mw": 138, "status": "departed_2024"},
]


def generate_member_risk_data():
    """Generate member risk assessment data."""
    rows = []

    for m in MEMBERS:
        if m["status"].startswith("departed"):
            continue  # Skip fully departed members from active risk assessment

        # Risk factors — larger members with more consumers have more exit leverage
        size_factor = min(1.0, m["consumers"] / 50000)

        # Colorado members have more exit options (state policy supports it)
        state_factor = {"CO": 0.3, "NM": 0.15, "WY": 0.05, "NE": 0.02}[m["state"]]

        # Departing members get high risk
        if m["status"] == "departing_2026":
            base_risk = 0.92
        elif m["status"] == "partial_exit":
            base_risk = 0.70
        else:
            base_risk = 0.08 + size_factor * 0.35 + state_factor + np.random.normal(0, 0.08)

        risk_score = np.clip(base_risk, 0.02, 0.98)

        # Rate comparison — what members pay vs alternatives
        tri_state_rate = 62 + np.random.normal(0, 3)  # $/MWh
        market_rate = 48 + np.random.normal(0, 5) + (m["state"] == "NM") * 4
        rate_gap = tri_state_rate - market_rate

        # Contract details
        contract_end = 2050 if m["status"] == "active" else (2026 if "departing" in m["status"] else 2040)
        ctp_estimate = m["peak_mw"] * np.random.uniform(0.8, 1.5) * 1e6  # Contract termination payment

        # Satisfaction signals (simulated from board activity, public comments, etc.)
        satisfaction = np.clip(0.7 - risk_score * 0.5 + np.random.normal(0, 0.1), 0.1, 1.0)

        # Early warning signals
        signals = []
        if risk_score > 0.5:
            signals.append("Board discussing power supply alternatives")
        if risk_score > 0.4 and m["state"] == "CO":
            signals.append("Colorado policy supports cooperative choice")
        if rate_gap > 18:
            signals.append("Significant rate gap vs market alternatives")
        if m["consumers"] > 30000:
            signals.append("Large enough to achieve purchasing economies independently")
        if risk_score > 0.6:
            signals.append("Engaged consultant for exit feasibility study")
        if satisfaction < 0.4:
            signals.append("Negative sentiment in public board minutes")
        if len(signals) == 0:
            signals.append("No significant risk signals detected")

        # Recommended retention actions
        actions = []
        if risk_score > 0.5:
            actions.append("Proactive executive engagement")
            actions.append("Customized rate impact analysis")
        if rate_gap > 15:
            actions.append("Explore partial requirements contract")
        if m["consumers"] > 20000:
            actions.append("Co-design local generation project")
        if risk_score > 0.3:
            actions.append("Schedule member satisfaction review")
        if len(actions) == 0:
            actions.append("Standard quarterly engagement")

        rows.append({
            "member": m["name"],
            "state": m["state"],
            "consumers": m["consumers"],
            "peak_demand_mw": m["peak_mw"],
            "status": m["status"],
            "risk_score": round(risk_score, 3),
            "satisfaction_score": round(satisfaction, 3),
            "tri_state_rate": round(tri_state_rate, 2),
            "market_alternative_rate": round(market_rate, 2),
            "rate_gap": round(rate_gap, 2),
            "contract_end_year": contract_end,
            "estimated_ctp_millions": round(ctp_estimate / 1e6, 1),
            "annual_revenue_millions": round(m["peak_mw"] * 8760 * 0.45 * tri_state_rate / 1e6, 1),
            "early_warning_signals": "; ".join(signals),
            "recommended_actions": "; ".join(actions),
        })

    df = pd.DataFrame(rows).sort_values("risk_score", ascending=False).reset_index(drop=True)
    df.to_csv(os.path.join(DATA_DIR, "member_risk_data.csv"), index=False)
    print(f"Generated risk profiles for {len(df)} member cooperatives")


if __name__ == "__main__":
    generate_member_risk_data()

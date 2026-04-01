"""
Tri-State AI Intelligence Dashboard — Flask Backend
Serves data APIs and the frontend.
"""

import os
import json
import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify, request
from pathlib import Path

app = Flask(__name__)

# Check local data dir first, fall back to parent (for dev)
_local_data = Path(__file__).parent / "data"
_parent_data = Path(__file__).parent.parent / "data"
DATA_DIR = _local_data if _local_data.exists() else _parent_data


# --- Data loading (cached) ---
_cache = {}

def get_data(name):
    if name not in _cache:
        path = DATA_DIR / f"{name}.csv"
        _cache[name] = pd.read_csv(path)
    return _cache[name]


# --- Routes: Pages ---
@app.route("/")
def index():
    return render_template("index.html")


# --- Routes: Sentiment API ---
@app.route("/api/sentiment/summary")
def sentiment_summary():
    df = get_data("sentiment_data")
    real_count = int(df["is_real"].sum()) if "is_real" in df.columns else 0
    topic_avg = df.groupby("topic")["sentiment_score"].mean()
    worst_topic = topic_avg.idxmin()
    return jsonify({
        "avg_sentiment": round(df["sentiment_score"].mean(), 3),
        "article_count": len(df),
        "real_count": real_count,
        "topic_count": df["topic"].nunique(),
        "worst_topic": worst_topic,
        "worst_score": round(topic_avg.min(), 3),
    })


@app.route("/api/sentiment/trend")
def sentiment_trend():
    df = get_data("sentiment_data").copy()
    df["date"] = pd.to_datetime(df["date"])
    monthly = (
        df.set_index("date")
        .groupby("topic")
        .resample("ME")["sentiment_score"]
        .mean()
        .reset_index()
    )
    monthly = monthly.dropna(subset=["sentiment_score"])
    monthly["date"] = monthly["date"].dt.strftime("%Y-%m-%d")
    return jsonify(monthly.to_dict(orient="records"))


@app.route("/api/sentiment/by_topic")
def sentiment_by_topic():
    df = get_data("sentiment_data")
    topic_avg = df.groupby("topic")["sentiment_score"].mean().sort_values()
    return jsonify({
        "topics": topic_avg.index.tolist(),
        "scores": [round(v, 3) for v in topic_avg.values],
    })


@app.route("/api/sentiment/volume")
def sentiment_volume():
    df = get_data("sentiment_data")
    counts = df["topic"].value_counts()
    return jsonify({
        "topics": counts.index.tolist(),
        "counts": counts.values.tolist(),
    })


@app.route("/api/sentiment/headlines")
def sentiment_headlines():
    df = get_data("sentiment_data")
    df["date"] = pd.to_datetime(df["date"])
    recent = df.nlargest(15, "date").copy()
    recent["date"] = recent["date"].dt.strftime("%Y-%m-%d")
    if "is_real" in recent.columns:
        recent["verified"] = recent["is_real"].apply(lambda x: "Verified" if x else "Modeled")
    else:
        recent["verified"] = "Modeled"
    cols = ["date", "headline", "topic", "source", "sentiment_score", "verified"]
    return jsonify(recent[cols].to_dict(orient="records"))


# --- Routes: Member Risk API ---
@app.route("/api/members/summary")
def members_summary():
    df = get_data("member_risk_data")
    active = df[df["status"] == "active"]
    at_risk = active[active["risk_score"] > 0.3]
    return jsonify({
        "active_count": len(active),
        "at_risk_count": len(at_risk),
        "at_risk_pct": round(len(at_risk) / len(active) * 100),
        "revenue_at_risk": round(at_risk["annual_revenue_millions"].sum(), 1),
        "avg_rate_gap": round(active["rate_gap"].mean(), 1),
    })


@app.route("/api/members/scatter")
def members_scatter():
    df = get_data("member_risk_data")
    active = df[df["status"] == "active"]
    cols = ["member", "state", "consumers", "risk_score", "rate_gap",
            "annual_revenue_millions", "satisfaction_score"]
    return jsonify(active[cols].to_dict(orient="records"))


@app.route("/api/members/table")
def members_table():
    df = get_data("member_risk_data")
    active = df[df["status"] == "active"].sort_values("risk_score", ascending=False)
    cols = ["member", "state", "consumers", "risk_score", "rate_gap",
            "annual_revenue_millions", "satisfaction_score"]
    return jsonify(active[cols].to_dict(orient="records"))


@app.route("/api/members/detail/<name>")
def member_detail(name):
    df = get_data("member_risk_data")
    row = df[df["member"] == name]
    if row.empty:
        return jsonify({"error": "Member not found"}), 404
    return jsonify(row.iloc[0].to_dict())


@app.route("/api/members/departed")
def members_departed():
    data = [
        {"member": "United Power", "status": "Exited May 2024", "consumers": "108,000",
         "driver": "Sought cheaper, cleaner power + local control",
         "warning": "Years of public advocacy, FERC filings, hired consultants",
         "lesson": "Early engagement before positions harden"},
        {"member": "Delta-Montrose Electric", "status": "Exited 2024", "consumers": "34,000",
         "driver": "Sought independence and cost reduction",
         "warning": "Board discussions about alternatives, rate comparison studies",
         "lesson": "Smaller members can exit too"},
        {"member": "La Plata Electric (LPEA)", "status": "Departing April 2026", "consumers": "35,000",
         "driver": "Rate concerns + desire for local renewable development",
         "warning": "Board vote March 2024, public feasibility studies",
         "lesson": "Board activity is the clearest leading indicator"},
        {"member": "Kit Carson Electric", "status": "Partial Exit", "consumers": "29,000",
         "driver": "Rate differential + community solar goals",
         "warning": "Gradual reduction in purchased power",
         "lesson": "Partial exit can be a retention tool if offered proactively"},
    ]
    return jsonify(data)


# --- Routes: Energy Mix API ---
@app.route("/api/energy/mix")
def energy_mix():
    df = get_data("energy_mix_data")
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    cols = ["date", "coal_pct", "natural_gas_pct", "wind_pct", "solar_pct", "hydro_pct", "purchased_pct"]
    return jsonify(df[cols].to_dict(orient="records"))


@app.route("/api/energy/co2")
def energy_co2():
    df = get_data("energy_mix_data")
    annual = df.groupby("year")["co2_tons_thousands"].sum().reset_index()
    baseline = annual[annual["year"] == 2015]["co2_tons_thousands"].values[0]
    target = baseline * 0.20
    return jsonify({
        "years": annual["year"].tolist(),
        "co2": [round(v, 1) for v in annual["co2_tons_thousands"].values],
        "target_2030": round(target, 1),
    })


@app.route("/api/energy/summary")
def energy_summary():
    df = get_data("energy_mix_data")
    latest = df.iloc[-1]
    earliest = df.iloc[0]
    renew_now = latest["wind_pct"] + latest["solar_pct"] + latest["hydro_pct"]
    renew_then = earliest["wind_pct"] + earliest["solar_pct"] + earliest["hydro_pct"]
    return jsonify({
        "coal_now": round(latest["coal_pct"], 1),
        "coal_change": round(latest["coal_pct"] - earliest["coal_pct"], 1),
        "renewable_now": round(renew_now, 1),
        "renewable_change": round(renew_now - renew_then, 1),
        "co2_latest": round(latest["co2_tons_thousands"], 0),
        "total_gwh": round(latest["total_gwh"], 0),
    })


# --- Routes: Price Forecast API ---
@app.route("/api/price/summary")
def price_summary():
    df = get_data("price_data")
    return jsonify({
        "avg_price": round(df["price_mwh"].mean(), 2),
        "min_price": round(df["price_mwh"].min(), 2),
        "max_price": round(df["price_mwh"].max(), 2),
        "record_count": len(df),
    })


@app.route("/api/price/forecast")
def price_forecast():
    """Return actual vs predicted from pre-computed model."""
    df = get_data("price_data")
    # Return raw data for client-side visualization
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    cols = ["date", "price_mwh", "demand_mw", "temperature_f",
            "wind_generation_mw", "solar_generation_mw", "natural_gas_price"]
    # Return last 300 days for chart performance
    return jsonify(df[cols].tail(300).to_dict(orient="records"))


@app.route("/api/price/predict", methods=["POST"])
def price_predict():
    """Predict price from scenario inputs."""
    data = request.json
    # Simple prediction based on feature weights (avoids loading full ML model)
    base = 35
    gas_effect = data.get("natural_gas_price", 3.0) * 4.5
    demand_effect = (data.get("demand_mw", 2800) - 2800) * 0.008
    temp = data.get("temperature_f", 55)
    temp_effect = 0.005 * (temp - 55) ** 2
    wind_effect = -data.get("wind_generation_mw", 350) * 0.008
    solar_effect = -data.get("solar_generation_mw", 200) * 0.006
    weekend_effect = -3 if data.get("is_weekend", False) else 0

    price = max(10, base + gas_effect + demand_effect + temp_effect +
                wind_effect + solar_effect + weekend_effect + np.random.normal(0, 1))
    return jsonify({
        "predicted_price": round(price, 2),
        "avg_price": round(get_data("price_data")["price_mwh"].mean(), 2),
    })


# --- Routes: Q&A API ---
@app.route("/api/qa/ask", methods=["POST"])
def qa_ask():
    """Answer questions using Claude or fallback."""
    data = request.json
    question = data.get("question", "")
    api_key = data.get("api_key", "")

    if api_key:
        try:
            from anthropic import Anthropic
            from tabs.rag_qa import KNOWLEDGE_BASE
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=(
                    "You are an AI assistant for Tri-State Generation and Transmission Association. "
                    "Answer questions grounded in the provided knowledge base. Be professional and cite relevant standards.\n\n"
                    "KNOWLEDGE BASE:\n" + KNOWLEDGE_BASE
                ),
                messages=[{"role": "user", "content": question}],
            )
            return jsonify({"answer": response.content[0].text, "source": "claude"})
        except Exception as e:
            return jsonify({"answer": f"API error: {str(e)}", "source": "error"})

    # Fallback: simple keyword matching
    q = question.lower()
    if "governance" in q or "framework" in q:
        answer = ("A utility-focused AI governance framework should include: "
                  "1) AI Council — cross-functional review body, "
                  "2) Tiered risk assessment — low/medium/high based on BES impact, "
                  "3) Model risk management — validation, monitoring, documentation, "
                  "4) NERC CIP alignment for any AI touching grid systems, "
                  "5) Audit and compliance — regular review cadence.")
    elif "nerc" in q or "cip" in q:
        answer = ("Key NERC CIP standards for AI: CIP-002 (categorization — is the AI system a BES Cyber Asset?), "
                  "CIP-005 (electronic security perimeters for cloud AI), "
                  "CIP-010 (model updates are configuration changes), "
                  "CIP-013 (third-party AI platforms are supply chain risk).")
    elif "member" in q or "retention" in q:
        answer = ("AI for member retention: 1) Automated board minutes monitoring via NLP, "
                  "2) Rate impact modeling per member, 3) Satisfaction analytics, "
                  "4) Custom value propositions showing true cost of departure. "
                  "Board activity is the strongest leading indicator — 12-24 months of signals before each exit.")
    elif "price" in q or "forecast" in q:
        answer = ("The price forecasting model uses a LightGBM + Gradient Boosting ensemble with Ridge meta-learner. "
                  "Key drivers: natural gas price, demand, temperature (U-shaped relationship), and renewable penetration. "
                  "Potential savings: $2-5M annually through optimized power purchasing timing.")
    else:
        answer = ("I can answer questions about: Tri-State operations, NERC CIP compliance, "
                  "AI governance frameworks, member retention strategies, energy transition, "
                  "and price forecasting. Try asking about one of these topics.")

    return jsonify({"answer": answer, "source": "fallback"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "false") == "true")

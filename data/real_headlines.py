"""
Real headlines about Tri-State G&T sourced from public news outlets.
These are verified headlines from actual published articles.
"""

REAL_HEADLINES = [
    # --- Energy Transition / Coal / Renewables ---
    {
        "date": "2024-08-14",
        "source": "Colorado Sun",
        "headline": "Tri-State Generation going big into renewable energy",
        "topic": "Renewable Energy",
        "is_real": True,
    },
    {
        "date": "2024-10-29",
        "source": "Colorado Sun",
        "headline": "Tri-State won $2.5 billion to close coal plants, get new renewable energy for rural customers",
        "topic": "Energy Transition",
        "is_real": True,
    },
    {
        "date": "2024-11-05",
        "source": "Colorado Sun",
        "headline": "Funding from New ERA program to Colorado's Tri-State energy is giving hope to our rural communities",
        "topic": "Community Impact",
        "is_real": True,
    },
    {
        "date": "2025-07-15",
        "source": "Colorado Sun",
        "headline": "Tri-State joining a regional transmission organization sounds wonky to Coloradans, but it's a big power move",
        "topic": "Energy Transition",
        "is_real": True,
    },
    {
        "date": "2025-12-31",
        "source": "CPR News",
        "headline": "Trump administration orders aging Colorado coal plant to stay open, one day before closing",
        "topic": "Coal Retirement",
        "is_real": True,
    },
    {
        "date": "2026-01-15",
        "source": "RTO Insider",
        "headline": "Colo. Officials Push Back on Craig Coal Plant Extension",
        "topic": "Coal Retirement",
        "is_real": True,
    },
    {
        "date": "2026-01-29",
        "source": "Colorado Sun",
        "headline": "Colorado AG asks Trump administration to let Craig's coal plant close as planned",
        "topic": "Coal Retirement",
        "is_real": True,
    },
    {
        "date": "2026-01-30",
        "source": "Colorado Sun",
        "headline": "Tri-State says no thanks to federal orders to keep Craig coal power plant open",
        "topic": "Coal Retirement",
        "is_real": True,
    },
    {
        "date": "2026-01-30",
        "source": "CPR News",
        "headline": "Colorado power providers challenge Trump order blocking coal plant closure",
        "topic": "Regulatory Compliance",
        "is_real": True,
    },
    {
        "date": "2026-02-04",
        "source": "RTO Insider",
        "headline": "Fight Heats up over Colorado's Craig Coal Plant Extension",
        "topic": "Coal Retirement",
        "is_real": True,
    },
    {
        "date": "2026-02-22",
        "source": "RTO Insider",
        "headline": "Colorado Bill Addresses Impacts of Coal Plant Extensions",
        "topic": "Regulatory Compliance",
        "is_real": True,
    },
    {
        "date": "2026-02-23",
        "source": "NPR",
        "headline": "Colorado coal plant objects to Trump order to stay open",
        "topic": "Coal Retirement",
        "is_real": True,
    },
    {
        "date": "2026-03-18",
        "source": "Colorado Sun",
        "headline": "Colorado sues to block Energy Department orders keeping Craig coal unit open",
        "topic": "Regulatory Compliance",
        "is_real": True,
    },
    {
        "date": "2026-03-19",
        "source": "RTO Insider",
        "headline": "Petitions Filed to Overturn DOE's Craig Coal Plant Extension",
        "topic": "Regulatory Compliance",
        "is_real": True,
    },
    {
        "date": "2026-03-29",
        "source": "RTO Insider",
        "headline": "SPP RTO Expands into Western Interconnection April 1",
        "topic": "Energy Transition",
        "is_real": True,
    },
    {
        "date": "2026-03-30",
        "source": "Colorado Sun",
        "headline": "Life of coal burning Craig Unit 1 extended again by Trump administration",
        "topic": "Coal Retirement",
        "is_real": True,
    },
    {
        "date": "2026-03-30",
        "source": "RTO Insider",
        "headline": "DOE Extends 202(c) Order for Craig Plant Days Before it Joins SPP RTO West",
        "topic": "Regulatory Compliance",
        "is_real": True,
    },

    # --- Member Relations ---
    {
        "date": "2024-03-26",
        "source": "Colorado Sun",
        "headline": "LPEA Board Votes to Leave Tri-State Generation and Transmission",
        "topic": "Member Relations",
        "is_real": True,
    },
    {
        "date": "2024-04-30",
        "source": "Colorado Sun",
        "headline": "Colorado's two largest energy co-ops break from Xcel, Tri-State aiming for more local control and lower costs",
        "topic": "Member Relations",
        "is_real": True,
    },
    {
        "date": "2025-11-17",
        "source": "Colorado Sun",
        "headline": "United Power seeks 'hyperlocal' energy for Colorado customers after dumping longtime supplier",
        "topic": "Member Relations",
        "is_real": True,
    },

    # --- Financial / Rates ---
    {
        "date": "2024-04-09",
        "source": "Colorado Sun",
        "headline": "Agencies downgrade Tri-State bonds, adding to rural power cooperative's ongoing pressures",
        "topic": "Rate Changes",
        "is_real": True,
    },

    # --- Grid / Technology ---
    {
        "date": "2026-03-01",
        "source": "Power Magazine",
        "headline": "Tri-State's Vision for Lower Cost, Greater Efficiency About to Become Reality",
        "topic": "Grid Reliability",
        "is_real": True,
    },

    # --- Utility Dive opinion ---
    {
        "date": "2024-09-15",
        "source": "Utility Dive",
        "headline": "Detractors take note: Tri-State is meeting its reliability, affordability and clean energy obligations",
        "topic": "Grid Reliability",
        "is_real": True,
    },

    # --- Legal / Environmental ---
    {
        "date": "2026-01-15",
        "source": "EDF",
        "headline": "Groups Take Trump Administration to Court Over Illegal Craig Coal Plant Extension",
        "topic": "Regulatory Compliance",
        "is_real": True,
    },
    {
        "date": "2026-01-20",
        "source": "Colorado Newsline",
        "headline": "Trump's 'emergency' Colorado coal plant order will raise electricity costs, operator says",
        "topic": "Rate Changes",
        "is_real": True,
    },
]

# Source editorial bias profiles (for bias indicator feature)
# Scale: -1.0 (strong industry/conservative) to +1.0 (strong environmental/progressive)
# 0.0 = neutral/balanced journalism
SOURCE_BIAS = {
    "Colorado Sun": {
        "bias_score": 0.15,
        "bias_label": "Slightly Progressive",
        "description": "Independent nonprofit newsroom. Balanced reporting with slight progressive editorial lean on energy/climate.",
        "type": "Local News",
        "credibility": "High",
    },
    "Utility Dive": {
        "bias_score": 0.0,
        "bias_label": "Neutral / Industry",
        "description": "Industry trade publication. Fact-driven coverage focused on utility business impacts.",
        "type": "Trade Publication",
        "credibility": "High",
    },
    "RTO Insider": {
        "bias_score": 0.0,
        "bias_label": "Neutral / Technical",
        "description": "Specialized energy market publication. Technical, regulatory-focused reporting.",
        "type": "Trade Publication",
        "credibility": "High",
    },
    "Denver Post": {
        "bias_score": 0.10,
        "bias_label": "Center-Left",
        "description": "Major metro daily. Generally balanced with slight progressive lean on environmental issues.",
        "type": "Metro Newspaper",
        "credibility": "High",
    },
    "CPR News": {
        "bias_score": 0.15,
        "bias_label": "Slightly Progressive",
        "description": "Colorado Public Radio. Public media with balanced reporting, slight progressive framing.",
        "type": "Public Media",
        "credibility": "High",
    },
    "NPR": {
        "bias_score": 0.15,
        "bias_label": "Slightly Progressive",
        "description": "National Public Radio. Mainstream public media with slight progressive lean.",
        "type": "Public Media",
        "credibility": "High",
    },
    "Colorado Newsline": {
        "bias_score": 0.25,
        "bias_label": "Progressive",
        "description": "Nonprofit news outlet. Progressive-leaning coverage of state policy and energy issues.",
        "type": "Digital News",
        "credibility": "Medium-High",
    },
    "Casper Star-Tribune": {
        "bias_score": -0.10,
        "bias_label": "Slightly Conservative",
        "description": "Wyoming daily newspaper. Balanced with slight conservative lean reflecting state politics.",
        "type": "Local News",
        "credibility": "High",
    },
    "Albuquerque Journal": {
        "bias_score": 0.0,
        "bias_label": "Center",
        "description": "New Mexico's largest newspaper. Centrist, balanced coverage.",
        "type": "Metro Newspaper",
        "credibility": "High",
    },
    "E&E News": {
        "bias_score": 0.10,
        "bias_label": "Slightly Progressive",
        "description": "Energy and environment focused publication. Balanced with slight progressive framing.",
        "type": "Specialty News",
        "credibility": "High",
    },
    "Reuters Energy": {
        "bias_score": 0.0,
        "bias_label": "Neutral",
        "description": "Global wire service. Factual, neutral reporting on energy markets.",
        "type": "Wire Service",
        "credibility": "Very High",
    },
    "Power Magazine": {
        "bias_score": -0.05,
        "bias_label": "Neutral / Industry",
        "description": "Power generation industry publication. Technical, industry-focused.",
        "type": "Trade Publication",
        "credibility": "High",
    },
    "EDF": {
        "bias_score": 0.60,
        "bias_label": "Environmental Advocacy",
        "description": "Environmental Defense Fund. Strong environmental advocacy perspective.",
        "type": "Advocacy Organization",
        "credibility": "Medium (Advocacy)",
    },
    "Public Comment - FERC": {
        "bias_score": 0.0,
        "bias_label": "Varies",
        "description": "Public comments in FERC proceedings. Wide range of perspectives.",
        "type": "Regulatory Filing",
        "credibility": "Varies",
    },
    "Public Comment - PUC": {
        "bias_score": 0.0,
        "bias_label": "Varies",
        "description": "Public comments in state PUC proceedings. Wide range of perspectives.",
        "type": "Regulatory Filing",
        "credibility": "Varies",
    },
    "Social Media": {
        "bias_score": 0.0,
        "bias_label": "Varies Widely",
        "description": "Social media posts and discussions. Unverified, highly variable quality and bias.",
        "type": "Social Media",
        "credibility": "Low",
    },
}

import streamlit as st
import base64
from pathlib import Path

st.set_page_config(
    page_title="Tri-State AI Intelligence Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Tri-State Brand Colors ---
BRAND = {
    "primary_blue": "#005a9c",
    "secondary_blue": "#0073cf",
    "dark_blue": "#003d6b",
    "light_blue": "#e8f1fa",
    "accent_gray": "#787878",
    "light_gray": "#f0f5fa",
    "dark_text": "#1a1a2e",
    "white": "#ffffff",
}

# --- Custom CSS for Tri-State Branding ---
st.markdown(f"""
<style>
    /* --- Global --- */
    .stApp {{
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    }}

    /* --- Header bar --- */
    header[data-testid="stHeader"] {{
        background-color: {BRAND["primary_blue"]};
    }}

    /* --- Sidebar branding --- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {BRAND["dark_blue"]} 0%, {BRAND["primary_blue"]} 100%);
        color: white;
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: white !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.2);
    }}

    /* --- Tab styling --- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0px;
        background-color: {BRAND["light_blue"]};
        border-radius: 8px 8px 0 0;
        padding: 4px 4px 0 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
        color: {BRAND["accent_gray"]};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {BRAND["white"]} !important;
        color: {BRAND["primary_blue"]} !important;
        border-bottom: 3px solid {BRAND["primary_blue"]};
    }}

    /* --- Metric cards --- */
    div[data-testid="stMetric"] {{
        background-color: {BRAND["light_blue"]};
        border-left: 4px solid {BRAND["primary_blue"]};
        padding: 12px 16px;
        border-radius: 4px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    div[data-testid="stMetric"] label {{
        color: {BRAND["accent_gray"]} !important;
        font-size: 0.85rem;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {BRAND["dark_blue"]} !important;
        font-weight: 700;
        font-size: clamp(1.2rem, 2.5vw, 2.2rem) !important;
        white-space: nowrap;
        overflow: visible;
    }}

    /* --- Info boxes (strategic insights) --- */
    .stAlert {{
        background-color: {BRAND["light_blue"]} !important;
        border-left: 4px solid {BRAND["primary_blue"]} !important;
        color: {BRAND["dark_text"]} !important;
    }}

    /* --- Headers --- */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: {BRAND["dark_blue"]};
    }}

    /* --- Buttons --- */
    .stButton > button {{
        background-color: {BRAND["primary_blue"]};
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: 600;
    }}
    .stButton > button:hover {{
        background-color: {BRAND["secondary_blue"]};
        color: white;
    }}

    /* --- Dataframe --- */
    .stDataFrame {{
        border: 1px solid {BRAND["light_blue"]};
        border-radius: 4px;
    }}

    /* --- Branded divider --- */
    .brand-divider {{
        height: 3px;
        background: linear-gradient(90deg, {BRAND["primary_blue"]}, {BRAND["secondary_blue"]}, {BRAND["light_blue"]});
        border: none;
        margin: 1rem 0;
        border-radius: 2px;
    }}

    /* --- Logo container --- */
    .logo-container {{
        text-align: center;
        background-color: {BRAND["white"]};
        padding: 1.5rem 1rem;
        margin: 0.5rem 0.75rem;
        border-radius: 8px;
    }}
    .logo-container img {{
        max-width: 240px;
        width: 100%;
    }}

    /* --- Sidebar footer --- */
    .sidebar-footer {{
        position: fixed;
        bottom: 0;
        padding: 1rem;
        font-size: 0.75rem;
        color: rgba(255,255,255,0.6);
    }}
</style>
""", unsafe_allow_html=True)


# --- Sidebar with Logo ---
logo_path = Path(__file__).parent / "assets" / "tristate_logo.png"
if logo_path.exists():
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
    st.sidebar.markdown(
        f'<div class="logo-container">'
        f'<img src="data:image/png;base64,{logo_b64}" alt="Tri-State Logo">'
        f'</div>',
        unsafe_allow_html=True,
    )

st.sidebar.markdown('<div class="brand-divider"></div>', unsafe_allow_html=True)
st.sidebar.markdown("### AI & Innovation")
st.sidebar.markdown(
    "Demonstrating practical AI capabilities "
    "aligned with Tri-State's strategic priorities "
    "and the Responsible Energy Plan."
)
st.sidebar.markdown('<div class="brand-divider"></div>', unsafe_allow_html=True)
st.sidebar.markdown(
    '<p style="font-size:0.75rem; color:rgba(255,255,255,0.5);">'
    'Prototype Demo | Powered by LightGBM & Claude<br>'
    'Not for production use'
    '</p>',
    unsafe_allow_html=True,
)

# --- Main Content ---
st.markdown(
    f'<h1 style="color:{BRAND["dark_blue"]}; margin-bottom:0;">'
    f'Tri-State AI Intelligence Dashboard</h1>'
    f'<p style="color:{BRAND["accent_gray"]}; font-size:1.1rem; margin-top:0;">'
    f'Enterprise AI Capabilities for Generation, Transmission & Member Services</p>',
    unsafe_allow_html=True,
)
st.markdown('<div class="brand-divider"></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Sentiment",
    "Member Risk",
    "Energy Mix",
    "Price Forecast",
    "AI Q&A",
])

with tab1:
    from tabs import sentiment
    sentiment.render()

with tab2:
    from tabs import member_risk
    member_risk.render()

with tab3:
    from tabs import energy_mix
    energy_mix.render()

with tab4:
    from tabs import price_forecast
    price_forecast.render()

with tab5:
    from tabs import rag_qa
    rag_qa.render()

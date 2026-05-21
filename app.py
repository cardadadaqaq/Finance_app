import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
import requests
from io import StringIO

st.set_page_config(page_title="Navy Terminal Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

    html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        background-color: #050D1A !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    [data-testid="stSidebar"] {
        background-color: #03080F !important;
        border-right: 1px solid #0F2540 !important;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #080F1E !important;
        border: 1px solid #0F2540 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stHeader"] {
        background-color: #03080F !important;
        border-bottom: 1px solid #0F2540 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
    }
    p, span, li, div, label, .stMarkdown {
        color: #C8D8E8 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }

    /* ---- PAGE TITLE ---- */
    .page-title {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.35rem;
        font-weight: 600;
        color: #FFFFFF !important;
        letter-spacing: 0.1em;
        border-left: 3px solid #2979FF;
        padding: 0.4rem 0 0.4rem 1rem;
        margin-bottom: 0.4rem;
        background: linear-gradient(90deg, rgba(41,121,255,0.06), transparent);
    }
    .page-subtitle {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.82rem;
        color: #5A7A9A !important;
        letter-spacing: 0.06em;
        margin-bottom: 1.8rem;
        padding-left: 1.2rem;
        text-transform: uppercase;
    }

    /* ---- METRICS ---- */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #5A7A9A !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.09em;
    }
    [data-testid="metric-container"] {
        background-color: #070E1C !important;
        border: 1px solid #0F2540 !important;
        border-top: 2px solid #1A3A6A !important;
        border-radius: 4px !important;
        padding: 0.8rem 1rem !important;
        transition: border-top-color 0.2s ease;
    }
    [data-testid="metric-container"]:hover {
        border-top-color: #2979FF !important;
    }

    /* ---- LABELS ---- */
    .stTextInput label, .stSelectbox label, .stMultiSelect label,
    .stSlider label, .stNumberInput label, .stRadio label, label[data-testid] {
        color: #5A7A9A !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }

    /* ---- SLIDER ---- */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #2979FF !important;
        border-color: #2979FF !important;
    }
    .stSlider [data-baseweb="slider"] div[class*="Track"] div:first-child {
        background-color: #2979FF !important;
    }
    .stSlider span { color: #5A7A9A !important; }

    /* ---- INPUTS ---- */
    .stNumberInput input, input[type="text"], textarea, .stTextInput input {
        background-color: #070E1C !important;
        color: #FFFFFF !important;
        border: 1px solid #0F2540 !important;
        border-radius: 3px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.88rem !important;
    }
    input[type="text"]:focus, textarea:focus, .stTextInput input:focus {
        border-color: #2979FF !important;
        box-shadow: 0 0 0 1px rgba(41,121,255,0.4) !important;
        outline: none !important;
    }
    .stNumberInput button {
        background-color: #0F2540 !important;
        color: #FFFFFF !important;
        border: none !important;
    }

    /* ---- SELECT ---- */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #070E1C !important;
        border: 1px solid #0F2540 !important;
        color: #FFFFFF !important;
    }
    [data-baseweb="popover"], [data-baseweb="menu"] {
        background-color: #0B1628 !important;
        border: 1px solid #1A3A6A !important;
    }
    [data-baseweb="option"] {
        background-color: #0B1628 !important;
        color: #C8D8E8 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.84rem !important;
    }
    [data-baseweb="option"]:hover,
    li[role="option"]:hover {
        background-color: #1A3A6A !important;
        color: #FFFFFF !important;
    }
    [data-baseweb="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"] {
        background-color: #1A3A6A !important;
        color: #2979FF !important;
        font-weight: 600 !important;
    }
    li[role="option"] {
        background-color: #0B1628 !important;
        color: #C8D8E8 !important;
    }

    /* ---- RADIO ---- */
    .stRadio > div > label {
        color: #C8D8E8 !important;
        text-transform: none !important;
        font-size: 0.9rem !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }

    /* ---- TABLE ---- */
    .dataframe, table {
        background-color: #070E1C !important;
        color: #FFFFFF !important;
        border-collapse: collapse !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.8rem !important;
    }
    thead tr th {
        color: #5A7A9A !important;
        background-color: #03080F !important;
        border-bottom: 1px solid #0F2540 !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        padding: 0.55rem 0.9rem !important;
        font-size: 0.72rem !important;
    }
    tbody tr td {
        color: #C8D8E8 !important;
        border-bottom: 1px solid #080F1E !important;
        padding: 0.45rem 0.9rem !important;
    }
    tbody tr:hover td { background-color: #0F2540 !important; }

    /* ---- DIVIDERS ---- */
    hr { border-color: #0F2540 !important; margin: 1.5rem 0 !important; }

    /* ---- ALERTS ---- */
    .stAlert, .stInfo, [data-testid="stNotification"] {
        background-color: #070E1C !important;
        border: 1px solid #0F2540 !important;
        color: #C8D8E8 !important;
        border-radius: 4px !important;
    }

    /* ---- BUTTONS ---- */
    .stButton > button {
        background-color: #070E1C !important;
        color: #FFFFFF !important;
        border: 1px solid #1A3A6A !important;
        border-radius: 3px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.08em !important;
        transition: all 0.15s ease !important;
        text-transform: uppercase !important;
    }
    .stButton > button:hover {
        background-color: #2979FF !important;
        border-color: #2979FF !important;
        color: #FFFFFF !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #1A3A6A !important;
        border-color: #2979FF !important;
    }

    /* ---- SCROLLBAR ---- */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #03080F; }
    ::-webkit-scrollbar-thumb { background: #0F2540; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: #2979FF; }

    /* ---- PROGRESS ---- */
    .stProgress > div > div > div {
        background-color: #2979FF !important;
    }

    /* ---- SIDEBAR NAV BUTTON ACTIVE ---- */
    .nav-btn-active > button {
        background-color: #0F2540 !important;
        border-left: 3px solid #2979FF !important;
        color: #FFFFFF !important;
    }

    /* ---- CARD COMPONENT ---- */
    .terminal-card {
        background: #070E1C;
        border: 1px solid #0F2540;
        border-radius: 4px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }
    .terminal-card-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: #2979FF;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }

    /* ---- TICKER BADGE ---- */
    .ticker-badge {
        display: inline-block;
        background: #0F2540;
        border: 1px solid #1A3A6A;
        border-radius: 2px;
        padding: 1px 7px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        color: #2979FF;
        letter-spacing: 0.06em;
        font-weight: 600;
    }

    /* ---- STATUS INDICATOR ---- */
    .status-dot-green { display:inline-block; width:7px; height:7px; border-radius:50%; background:#00E676; margin-right:6px; animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #03080F !important;
        border-bottom: 1px solid #0F2540 !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: #5A7A9A !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        padding: 0.6rem 1.2rem !important;
        border-bottom: 2px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom: 2px solid #2979FF !important;
        background-color: rgba(41,121,255,0.05) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #070E1C !important;
        border: 1px solid #0F2540 !important;
        color: #FFFFFF !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.82rem !important;
    }
    </style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("""
        <div style='padding: 1.2rem 0.5rem 1rem; border-bottom: 1px solid #0F2540; margin-bottom: 1.4rem;'>
            <div style='font-family: IBM Plex Mono, monospace; font-size:0.6rem; color:#2979FF;
                        letter-spacing:0.35em; margin-bottom:4px;'>⚓  NAVY</div>
            <div style='font-family: IBM Plex Mono, monospace; font-size:1.4rem; font-weight:700;
                        color:#FFFFFF; letter-spacing:0.08em; line-height:1.1;'>TERMINAL</div>
            <div style='font-family: IBM Plex Mono, monospace; font-size:0.58rem; color:#1A3A6A;
                        letter-spacing:0.4em; margin-top:2px;'>PRO  ·  v2.0</div>
        </div>
    """, unsafe_allow_html=True)

    menu_items = [
        ("01", "🌍", "Global Overview"),
        ("02", "🧮", "Analisi DCF"),
        ("03", "📊", "Multi-Compare"),
        ("04", "🧪", "Portfolio Backtest"),
        ("05", "🔍", "Stock Screener"),
        ("06", "⌨️", "Bloomberg Insights"),
    ]

    if "page" not in st.session_state:
        st.session_state.page = "Global Overview"
    if "screener_selected" not in st.session_state:
        st.session_state.screener_selected = None
    if "screener_results" not in st.session_state:
        st.session_state.screener_results = None
    # Fix: per i peers, usa un dict che mappa ticker -> peers string
    if "peers_map" not in st.session_state:
        st.session_state.peers_map = {}
    if "finviz_df" not in st.session_state:
        st.session_state.finviz_df = None
    if "finviz_selected" not in st.session_state:
        st.session_state.finviz_selected = None

    for num, icon, label in menu_items:
        is_active = st.session_state.page == label
        btn_style = "nav-btn-active" if is_active else ""
        with st.container():
            if is_active:
                st.markdown(f"""
                    <div style='background:#0F2540; border-left:3px solid #2979FF; border-radius:3px;
                                padding:0.55rem 0.8rem; margin-bottom:4px; display:flex; align-items:center; gap:10px;'>
                        <span style='font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#2979FF;'>{num}</span>
                        <span style='font-size:0.88rem; color:#FFFFFF; font-weight:500;'>{icon} {label}</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(f"{num}  {icon}  {label}", key=f"nav_{label}", use_container_width=True):
                    st.session_state.page = label
                    st.rerun()

    st.markdown("""
        <div style='margin-top:2rem; padding-top:1rem; border-top:1px solid #0F2540;'>
            <div style='display:flex; align-items:center; margin-bottom:6px;'>
                <span class='status-dot-green'></span>
                <span style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#2979FF;letter-spacing:0.15em;'>LIVE DATA</span>
            </div>
            <div style='font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#1A3A6A;letter-spacing:0.1em;'>
                POWERED BY YFINANCE + FINVIZ<br>
                CACHE TTL · 300–900s
            </div>
        </div>
    """, unsafe_allow_html=True)

choice = st.session_state.page


# =========================================================
# UTILITY
# =========================================================
def page_title(text, subtitle=""):
    st.markdown(f"<div class='page-title'>{text}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='page-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def section_header(text):
    st.markdown(f"""
        <div style='display:flex; align-items:center; gap:10px; margin: 1.4rem 0 0.8rem;'>
            <div style='width:3px; height:18px; background:#2979FF; border-radius:1px; flex-shrink:0;'></div>
            <div style='font-family:IBM Plex Mono,monospace; font-size:0.78rem; color:#5A7A9A;
                        letter-spacing:0.15em; text-transform:uppercase;'>{text}</div>
            <div style='flex:1; height:1px; background:linear-gradient(90deg,#0F2540,transparent);'></div>
        </div>
    """, unsafe_allow_html=True)


def interactive_xaxis():
    return dict(
        gridcolor='#080F1E', showgrid=True, zeroline=False,
        gridwidth=1,
        rangeslider=dict(visible=True, bgcolor="#03080F", thickness=0.035),
        rangeselector=dict(
            bgcolor="#070E1C", activecolor="#2979FF", bordercolor="#0F2540",
            font=dict(color="#FFFFFF", size=9, family="IBM Plex Mono"),
            buttons=[
                dict(count=1,  label="1M", step="month", stepmode="backward"),
                dict(count=3,  label="3M", step="month", stepmode="backward"),
                dict(count=6,  label="6M", step="month", stepmode="backward"),
                dict(count=1,  label="1A", step="year",  stepmode="backward"),
                dict(count=3,  label="3A", step="year",  stepmode="backward"),
                dict(count=5,  label="5A", step="year",  stepmode="backward"),
                dict(step="all", label="MAX"),
            ]
        )
    )


PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor='rgba(3,8,15,0)',
    plot_bgcolor='rgba(7,14,28,0.6)',
    font=dict(color="#C8D8E8", family="IBM Plex Mono, monospace", size=10),
    legend=dict(bgcolor='rgba(3,8,15,0.85)', bordercolor='#0F2540', borderwidth=1,
                font=dict(size=10, family="IBM Plex Mono")),
    xaxis=dict(gridcolor='#080F1E', showgrid=True, zeroline=False, gridwidth=1),
    yaxis=dict(gridcolor='#080F1E', showgrid=True, zeroline=False, gridwidth=1),
    margin=dict(l=50, r=20, t=50, b=50),
    hovermode="x unified",
    dragmode="zoom",
    hoverlabel=dict(bgcolor="#070E1C", bordercolor="#1A3A6A",
                    font=dict(family="IBM Plex Mono", size=11)),
)

ACCENT_COLORS = ['#2979FF','#00E676','#FF9100','#FF1744','#AA00FF',
                 '#00B8D4','#FFD600','#FF6D00','#69F0AE','#40C4FF']


# =========================================================
# CACHING — yfinance
# =========================================================
@st.cache_data(ttl=300, show_spinner=False)
def get_ticker_info(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info or len(info) <= 3:
            import time; time.sleep(0.4)
            info = t.info
        if not info or len(info) <= 3:
            return {}
        has_price = (info.get('regularMarketPrice') is not None or
                     info.get('currentPrice') is not None or
                     info.get('previousClose') is not None)
        has_name = (info.get('longName') is not None or
                    info.get('shortName') is not None)
        if not has_price and not has_name:
            return {}
        return info
    except Exception:
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def get_ticker_history(ticker, period="2d"):
    try:
        return yf.Ticker(ticker).history(period=period)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def get_ticker_news(ticker):
    try:
        return yf.Ticker(ticker).news
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def download_single(ticker, start_str=None, period=None):
    try:
        if period:
            raw = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        else:
            raw = yf.download(ticker, start=start_str, auto_adjust=True, progress=False)
        if raw.empty:
            return pd.Series(dtype=float, name=ticker)
        if isinstance(raw.columns, pd.MultiIndex):
            close = raw['Close']
            return close.iloc[:, 0].rename(ticker) if isinstance(close, pd.DataFrame) else close.squeeze()
        close = raw['Close']
        return close.iloc[:, 0].rename(ticker) if isinstance(close, pd.DataFrame) else close.squeeze()
    except Exception:
        return pd.Series(dtype=float, name=ticker)


# =========================================================
# FINVIZ MODULE — Screen + cached fetch
# =========================================================
@st.cache_data(ttl=900, show_spinner=False)
def fetch_finviz_screener(url: str) -> pd.DataFrame:
    """
    Scarica risultati da un URL di Finviz Screener (export CSV).
    Applica TTL=900s per evitare IP blocking da parte di Finviz.
    
    Supporta:
    - URL export CSV di Finviz (es. finviz.com/screener.ashx?...&export=1)
    - Tenta finvizfinance come fallback
    """
    try:
        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        # Se l'URL non contiene già export, proviamo a parsare come HTML
        export_url = url
        if "export=" not in url:
            if "?" in url:
                export_url = url + "&ar=10&c=1,2,3,4,5,6,7,25,27,65,66"
            else:
                export_url = url + "?ar=10&c=1,2,3,4,5,6,7,25,27,65,66"

        resp = requests.get(export_url, headers=headers, timeout=15)
        resp.raise_for_status()

        # Prova CSV
        try:
            df = pd.read_csv(StringIO(resp.text))
            if not df.empty and "Ticker" in df.columns:
                return df
        except Exception:
            pass

        # Prova parsing HTML table
        try:
            tables = pd.read_html(resp.text)
            for t in tables:
                if "Ticker" in t.columns or "ticker" in str(t.columns).lower():
                    t.columns = [str(c).strip() for c in t.columns]
                    return t
        except Exception:
            pass

        return pd.DataFrame({"Error": ["URL non ha restituito dati validi. Usa un URL export CSV di Finviz."]})

    except requests.exceptions.RequestException as e:
        return pd.DataFrame({"Error": [f"Errore di rete: {str(e)[:120]}"]})
    except Exception as e:
        return pd.DataFrame({"Error": [f"Errore: {str(e)[:120]}"]})


@st.cache_data(ttl=900, show_spinner=False)
def fetch_finviz_preset(preset: str) -> pd.DataFrame:
    """
    Scarica preset screener predefiniti da Finviz senza chiave API.
    preset: 'top_gainers' | 'top_losers' | 'high_volume' | 'oversold' | 'overbought'
    """
    preset_map = {
        "top_gainers":  "https://finviz.com/screener.ashx?v=111&s=ta_topgainers&ar=10",
        "top_losers":   "https://finviz.com/screener.ashx?v=111&s=ta_toplosers&ar=10",
        "high_volume":  "https://finviz.com/screener.ashx?v=111&s=ta_unusualvolume&ar=10",
        "oversold":     "https://finviz.com/screener.ashx?v=111&s=ta_oversold&ar=10",
        "overbought":   "https://finviz.com/screener.ashx?v=111&s=ta_overbought&ar=10",
    }
    url = preset_map.get(preset, preset_map["top_gainers"])
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://finviz.com/",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        tables = pd.read_html(resp.text)
        for t in tables:
            cols = [str(c).strip().lower() for c in t.columns]
            if "ticker" in cols or "no." in cols:
                t.columns = [str(c).strip() for c in t.columns]
                if "No." in t.columns:
                    t = t.drop(columns=["No."], errors="ignore")
                return t.dropna(how="all")
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)[:120]]})


# =========================================================
# yfinance DEEP MODULE — per ticker selezionato da screener
# =========================================================
@st.cache_data(ttl=600, show_spinner=False)
def get_deep_ticker_data(ticker: str) -> dict:
    """
    Scarica dati storici profondi da yfinance per il ticker selezionato.
    Ritorna: price history 10y, financials, balance_sheet, cashflow, info.
    """
    result = {}
    try:
        t = yf.Ticker(ticker)
        result["info"] = t.info or {}
        result["history_10y"] = t.history(period="10y")
        result["history_1y"]  = t.history(period="1y")

        for attr in ["financials", "income_stmt"]:
            try:
                df = getattr(t, attr)
                if df is not None and not df.empty:
                    result["financials"] = df
                    break
            except Exception:
                pass
        if "financials" not in result:
            result["financials"] = pd.DataFrame()

        for attr in ["balance_sheet"]:
            try:
                df = getattr(t, attr)
                if df is not None and not df.empty:
                    result["balance_sheet"] = df
                    break
            except Exception:
                pass
        if "balance_sheet" not in result:
            result["balance_sheet"] = pd.DataFrame()

        for attr in ["cashflow", "cash_flow"]:
            try:
                df = getattr(t, attr)
                if df is not None and not df.empty:
                    result["cashflow"] = df
                    break
            except Exception:
                pass
        if "cashflow" not in result:
            result["cashflow"] = pd.DataFrame()

        for attr in ["quarterly_financials", "quarterly_income_stmt"]:
            try:
                df = getattr(t, attr)
                if df is not None and not df.empty:
                    result["q_financials"] = df
                    break
            except Exception:
                pass
        if "q_financials" not in result:
            result["q_financials"] = pd.DataFrame()

    except Exception as e:
        result["error"] = str(e)
    return result


# =========================================================
# CACHING — fundamentals
# =========================================================
@st.cache_data(ttl=300, show_spinner=False)
def get_top_movers(n=5):
    watchlist = [
        "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","JPM","V",
        "UNH","XOM","JNJ","PG","MA","HD","ABBV","MRK","CVX","PEP","KO","LIN",
        "TMO","DHR","NEE","AMD","INTC","QCOM","TXN","AMAT","LRCX","MU","PANW",
        "ADBE","CRM","NOW","SNOW","PLTR","COIN","NFLX","DIS","BAC","WFC","GS","MS",
        "COST","WMT","TGT","NKE","SBUX","MCD","ABNB","BKNG","BA","CAT","GE","RTX",
        "RIVN","NIO","BABA","MELI","SQ","PYPL","SHOP","SMCI","ARM","ASML","TSM",
        "CEG","ENPH","FSLR","ENI.MI","ENEL.MI","RACE.MI","MC.PA","TTE.PA","SAP.DE",
    ]
    results = []
    for tkr in watchlist:
        try:
            d = yf.Ticker(tkr).history(period="2d")
            if len(d) >= 2:
                c, p = float(d['Close'].iloc[-1]), float(d['Close'].iloc[-2])
                pct = ((c - p) / p) * 100
                results.append({"ticker": tkr, "price": c, "pct": pct})
        except Exception:
            continue
    results.sort(key=lambda x: x["pct"], reverse=True)
    return results[:n], sorted(results, key=lambda x: x["pct"])[:n]


@st.cache_data(ttl=600, show_spinner=False)
def get_historical_pe(ticker, years_back=10):
    try:
        t = yf.Ticker(ticker)
        price_hist = t.history(period=f"{years_back}y")["Close"]
        if price_hist.empty:
            return pd.Series(dtype=float, name=ticker)
        price_hist.index = price_hist.index.tz_localize(None)
        eps_series = None
        for attr in ["income_stmt", "financials"]:
            try:
                df = getattr(t, attr)
                if df is None or (hasattr(df, 'empty') and df.empty):
                    continue
                if hasattr(df, 'index'):
                    for row in ["Basic EPS", "Diluted EPS", "EPS"]:
                        if row in df.index:
                            s = df.loc[row].copy()
                            s.index = pd.to_datetime(s.index)
                            eps_series = s.sort_index()
                            break
                if eps_series is not None:
                    break
            except Exception:
                continue
        eps_q = None
        for attr in ["quarterly_income_stmt", "quarterly_financials"]:
            try:
                df = getattr(t, attr)
                if df is None or (hasattr(df, 'empty') and df.empty):
                    continue
                if hasattr(df, 'index'):
                    for row in ["Basic EPS", "Diluted EPS", "EPS"]:
                        if row in df.index:
                            s = df.loc[row].copy()
                            s.index = pd.to_datetime(s.index)
                            eps_q = s.sort_index()
                            break
                if eps_q is not None:
                    break
            except Exception:
                continue
        if eps_q is not None and not eps_q.empty:
            if eps_series is not None and not eps_series.empty:
                combined = pd.concat([eps_series / 4, eps_q])
                combined = combined[~combined.index.duplicated(keep='last')]
                eps_combined = combined.sort_index()
            else:
                eps_combined = eps_q
            eps_ttm = eps_combined.rolling(4, min_periods=1).sum()
        elif eps_series is not None and not eps_series.empty:
            eps_ttm = eps_series
        else:
            eps_snap = t.info.get("trailingEps")
            if eps_snap and eps_snap > 0:
                return (price_hist / eps_snap).rename(ticker)
            return pd.Series(dtype=float, name=ticker)
        eps_daily = eps_ttm.reindex(
            eps_ttm.index.union(price_hist.index)
        ).ffill().reindex(price_hist.index)
        pe_hist = price_hist / eps_daily
        pe_hist = pe_hist.replace([float("inf"), float("-inf")], float("nan"))
        pe_hist = pe_hist[(pe_hist > 0) & (pe_hist < 500)]
        return pe_hist.dropna().rename(ticker)
    except Exception:
        return pd.Series(dtype=float, name=ticker)


@st.cache_data(ttl=600, show_spinner=False)
def get_historical_ps(ticker, years_back=10):
    try:
        t = yf.Ticker(ticker)
        price_hist = t.history(period=f"{years_back}y")["Close"]
        if price_hist.empty:
            return pd.Series(dtype=float, name=ticker)
        price_hist.index = price_hist.index.tz_localize(None)
        shares = (t.info.get("sharesOutstanding") or t.info.get("impliedSharesOutstanding"))
        if not shares:
            return pd.Series(dtype=float, name=ticker)
        rev_series = None
        for attr in ["financials", "income_stmt"]:
            try:
                df = getattr(t, attr)
                if df is None or (hasattr(df, 'empty') and df.empty):
                    continue
                if hasattr(df, 'index'):
                    for row in ["Total Revenue", "Revenue", "Net Revenue"]:
                        if row in df.index:
                            rev_series = df.loc[row].copy()
                            rev_series.index = pd.to_datetime(rev_series.index)
                            rev_series = rev_series.sort_index()
                            break
                if rev_series is not None:
                    break
            except Exception:
                continue
        rev_q = None
        for attr in ["quarterly_financials", "quarterly_income_stmt"]:
            try:
                df = getattr(t, attr)
                if df is None or (hasattr(df, 'empty') and df.empty):
                    continue
                for row in ["Total Revenue", "Revenue", "Net Revenue"]:
                    if row in df.index:
                        rev_q = df.loc[row].copy()
                        rev_q.index = pd.to_datetime(rev_q.index)
                        rev_q = rev_q.sort_index()
                        break
                if rev_q is not None:
                    break
            except Exception:
                continue
        if rev_q is not None and not rev_q.empty:
            if rev_series is not None and not rev_series.empty:
                combined = pd.concat([rev_series / 4, rev_q])
                combined = combined[~combined.index.duplicated(keep='last')]
                rev_combined = combined.sort_index()
            else:
                rev_combined = rev_q
            rev_ttm = rev_combined.rolling(4, min_periods=1).sum()
        elif rev_series is not None and not rev_series.empty:
            rev_ttm = rev_series
        else:
            rev_snap = t.info.get("totalRevenue")
            if rev_snap and rev_snap > 0:
                return ((price_hist * shares) / rev_snap).rename(ticker)
            return pd.Series(dtype=float, name=ticker)
        rev_daily = rev_ttm.reindex(
            rev_ttm.index.union(price_hist.index)
        ).ffill().reindex(price_hist.index)
        ps_hist = (price_hist * shares) / rev_daily
        ps_hist = ps_hist.replace([float("inf"), float("-inf")], float("nan"))
        ps_hist = ps_hist[(ps_hist > 0) & (ps_hist < 200)]
        return ps_hist.dropna().rename(ticker)
    except Exception:
        return pd.Series(dtype=float, name=ticker)


@st.cache_data(ttl=600, show_spinner=False)
def get_historical_mktcap(ticker, years_back=10):
    try:
        t = yf.Ticker(ticker)
        price_hist = t.history(period=f"{years_back}y")["Close"]
        if price_hist.empty:
            return pd.Series(dtype=float, name=ticker)
        price_hist.index = price_hist.index.tz_localize(None)
        shares = (t.info.get("sharesOutstanding") or t.info.get("impliedSharesOutstanding"))
        if not shares:
            return pd.Series(dtype=float, name=ticker)
        return (price_hist * shares / 1e9).rename(ticker)
    except Exception:
        return pd.Series(dtype=float, name=ticker)


@st.cache_data(ttl=600, show_spinner=False)
def get_quarterly_metric(ticker, metric_key):
    try:
        t = yf.Ticker(ticker)
        if metric_key == "EPS":
            qrt = None
            for attr in ["quarterly_income_stmt", "quarterly_financials"]:
                try:
                    df = getattr(t, attr)
                    if df is None or df.empty: continue
                    for row in ["Basic EPS", "Diluted EPS", "EPS"]:
                        if hasattr(df, 'index') and row in df.index:
                            s = df.loc[row].copy()
                            s.index = pd.to_datetime(s.index)
                            qrt = s.sort_index()
                            break
                    if qrt is not None: break
                except Exception:
                    continue
            return qrt.rename(ticker) if qrt is not None and not qrt.empty else pd.Series(dtype=float, name=ticker)
        else:
            row_map = {
                "Total Revenue": ["Total Revenue", "Revenue", "Net Revenue"],
                "Gross Profit":  ["Gross Profit", "GrossProfit"],
                "Net Income":    ["Net Income", "Net Income Common Stockholders"],
                "EBITDA":        ["EBITDA", "Normalized EBITDA", "Operating Income"],
                "Free Cash Flow":["Free Cash Flow", "FreeCashFlow"],
            }
            candidates = row_map.get(metric_key, [metric_key])
            for attr in ["quarterly_financials", "quarterly_income_stmt",
                         "quarterly_cashflow", "financials", "income_stmt"]:
                try:
                    df = getattr(t, attr)
                    if df is None or df.empty: continue
                    for row in candidates:
                        if row in df.index:
                            s = df.loc[row].copy()
                            s.index = pd.to_datetime(s.index)
                            return (s.sort_index() / 1e9).rename(ticker)
                except Exception:
                    continue
            return pd.Series(dtype=float, name=ticker)
    except Exception:
        return pd.Series(dtype=float, name=ticker)


# =========================================================
# SUPPLY CHAIN MAP
# =========================================================
SUPPLY_CHAIN_MAP = {
    "Technology": {
        "suppliers": ["Taiwan Semiconductor (TSM)", "Samsung Electronics", "ASML (ASML.AS)",
                      "Applied Materials (AMAT)", "Lam Research (LRCX)"],
        "customers": ["Apple (AAPL)", "Microsoft (MSFT)", "Meta (META)",
                      "Amazon AWS (AMZN)", "Alphabet (GOOGL)"],
        "notes": "La supply chain tech è dominata dai foundry asiatici e dai big tech USA come clienti finali."
    },
    "Semiconductors": {
        "suppliers": ["ASML (ASML.AS)", "Applied Materials (AMAT)", "Air Products (APD)", "Shin-Etsu Chemical"],
        "customers": ["Apple (AAPL)", "Nvidia (NVDA)", "AMD", "Qualcomm (QCOM)", "Data center hyperscalers"],
        "notes": "Capital-intensive con altissime barriere. I fornitori di litografia (ASML) sono monopolisti de facto."
    },
    "Communication Services": {
        "suppliers": ["Ericsson (ERIC)", "Nokia (NOK)", "Akamai (AKAM)", "Infrastrutture cloud"],
        "customers": ["Advertiser B2B", "Consumatori B2C", "PMI globali"],
        "notes": "Ricavi prevalentemente da pubblicità digitale e abbonamenti."
    },
    "Financial Services": {
        "suppliers": ["Bloomberg LP", "Refinitiv/LSEG", "Broadridge (BR)", "Fiserv (FISV)"],
        "customers": ["Retail banking", "Investitori istituzionali", "Aziende corporate"],
        "notes": "Il settore si affida a fornitori di dati e infrastrutture IT finanziarie."
    },
    "Healthcare": {
        "suppliers": ["Thermo Fisher (TMO)", "Danaher (DHR)", "Lonza Group", "Wuxi Biologics"],
        "customers": ["Ospedali", "Assicurazioni sanitarie", "Governi", "Distributori farmaceutici"],
        "notes": "Pipeline R&D lunga e costosa; i CDMO sono fornitori critici."
    },
    "Energy": {
        "suppliers": ["Halliburton (HAL)", "Baker Hughes (BKR)", "SLB (SLB)", "Caterpillar (CAT)"],
        "customers": ["Utility elettriche", "Raffinerie", "Industria chimica", "Governi"],
        "notes": "Ciclico, fortemente legato al prezzo del petrolio e alle politiche energetiche."
    },
    "Industrials": {
        "suppliers": ["3M (MMM)", "Honeywell (HON)", "Parker Hannifin (PH)", "Eaton (ETN)"],
        "customers": ["Aerospaziale", "Automotive", "Costruzioni", "Difesa"],
        "notes": "Ampio spettro B2B; sensibile al ciclo economico e agli ordini governativi."
    },
    "Consumer Defensive": {
        "suppliers": ["Archer-Daniels (ADM)", "Bunge (BG)", "Packaging Corp (PKG)", "IFF (IFF)"],
        "customers": ["Grande distribuzione (WMT, COST)", "Consumatori finali B2C"],
        "notes": "Settore anticiclico con pricing power nei brand premium."
    },
    "Consumer Cyclical": {
        "suppliers": ["Li & Fung", "Produttori asiatici OEM", "Fornitori materie prime"],
        "customers": ["Consumatori finali", "E-commerce", "Retail fisico"],
        "notes": "Fortemente correlato al ciclo del credito al consumo."
    },
    "Real Estate": {
        "suppliers": ["Costruttori", "Gestori immobiliari", "Property management"],
        "customers": ["Tenant retail", "Tenant uffici", "Residenziale"],
        "notes": "Sensibile ai tassi d'interesse. I REIT distribuiscono almeno il 90% degli utili."
    },
    "Utilities": {
        "suppliers": ["GE Vernova (GEV)", "Siemens Energy", "NextEra (NEE)", "Fuel suppliers"],
        "customers": ["Residenziale", "Industria", "Data center (domanda in forte crescita)"],
        "notes": "Settore regolato. La crescente domanda da AI/data center è un catalizzatore strutturale."
    },
    "Basic Materials": {
        "suppliers": ["Minatori di materie prime", "Produttori chimici di base"],
        "customers": ["Manifatturiero", "Costruzioni", "Automotive", "Farmaceutico"],
        "notes": "Altamente ciclico, dipendente da domanda cinese e prezzi delle commodity."
    },
}


# =========================================================
# BLOOMBERG INSIGHTS — funzione riutilizzabile (FIX peers)
# =========================================================
def show_bloomberg_insights(target, peers_key=None):
    """
    peers_key: stringa univoca per rendere il widget peers specifico per ticker
    """
    if peers_key is None:
        peers_key = target

    with st.spinner(f"Recupero dati per {target}..."):
        inf = get_ticker_info(target)
        if not inf:
            try:
                import time; time.sleep(0.5)
                inf = yf.Ticker(target).info
                if not inf or len(inf) <= 3:
                    inf = {}
            except Exception:
                inf = {}

        if not inf:
            st.error(f"Ticker **{target}** non trovato o dati non disponibili.")
            st.markdown("Esempi: USA `AAPL` `MSFT` `NVDA` · Italia `ENI.MI` `ENEL.MI` · Francia `MC.PA` · ETF `VWCE.DE`")
            return

        company_name  = inf.get('longName') or inf.get('shortName') or target
        current_price = (inf.get('currentPrice') or inf.get('regularMarketPrice')
                         or inf.get('previousClose'))

    # Header card
    prev_close = inf.get('previousClose') or inf.get('regularMarketPrice') or current_price
    delta_pct = ((current_price - prev_close) / prev_close * 100) if (current_price and prev_close and prev_close != 0) else None
    delta_color = "#00E676" if (delta_pct and delta_pct >= 0) else "#FF1744"
    delta_str = f"{delta_pct:+.2f}%" if delta_pct is not None else "—"

    st.markdown(f"""
        <div style='background:linear-gradient(135deg,#070E1C 0%,#0A1525 100%);
                    border:1px solid #0F2540; border-top:2px solid #2979FF; border-radius:4px;
                    padding:1.5rem 1.8rem; margin-bottom:1.5rem;'>
            <div style='display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;'>
                <div>
                    <div style='font-family:IBM Plex Mono,monospace; font-size:0.6rem;
                                color:#2979FF; letter-spacing:0.3em; margin-bottom:5px;'>EQUITY · LIVE</div>
                    <div style='font-size:1.7rem; font-weight:700; color:#FFFFFF;
                                font-family:IBM Plex Mono,monospace; letter-spacing:0.02em;'>{company_name}</div>
                    <div style='font-family:IBM Plex Mono,monospace; font-size:0.8rem; color:#5A7A9A; margin-top:5px;'>
                        <span class='ticker-badge'>{target}</span>&nbsp;
                        {inf.get('exchange','')}&nbsp;·&nbsp;{inf.get('currency','')}&nbsp;·&nbsp;{inf.get('sector','')}
                    </div>
                </div>
                <div style='text-align:right;'>
                    <div style='font-family:IBM Plex Mono,monospace; font-size:2.2rem;
                                font-weight:700; color:#FFFFFF;'>{f"{current_price:,.2f}" if current_price else "N/A"}</div>
                    <div style='font-family:IBM Plex Mono,monospace; font-size:1rem;
                                color:{delta_color}; font-weight:600;'>{delta_str} oggi</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.metric("P/E Forward",  f"{inf.get('forwardPE'):.1f}"          if inf.get('forwardPE')      else "N/A")
    k2.metric("EPS Forward",  f"{inf.get('forwardEps'):.2f}"         if inf.get('forwardEps')     else "N/A")
    k3.metric("Beta",         f"{inf.get('beta'):.2f}"               if inf.get('beta')           else "N/A")
    k4.metric("Market Cap",   f"${inf.get('marketCap',0)/1e9:.1f}B"  if inf.get('marketCap')      else "N/A")
    k5.metric("52W High",     f"{inf.get('fiftyTwoWeekHigh'):.2f}"   if inf.get('fiftyTwoWeekHigh') else "N/A")
    k6.metric("Dividend %",   f"{(inf.get('dividendYield') or 0)*100:.2f}%")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["📋  OVERVIEW", "📈  CHARTS", "🏢  PEERS", "🔗  SUPPLY CHAIN"])

    with tab1:
        col_desc, col_news = st.columns([3, 2])
        with col_desc:
            section_header("Business Summary")
            st.write(inf.get('longBusinessSummary') or "Descrizione non disponibile.")

            section_header("Key Financials")
            fin_rows = [
                {"Metrica": "Revenue TTM",       "Valore": f"${inf.get('totalRevenue',0)/1e9:.2f}B"         if inf.get('totalRevenue')         else "N/A"},
                {"Metrica": "EBITDA",             "Valore": f"${inf.get('ebitda',0)/1e9:.2f}B"              if inf.get('ebitda')               else "N/A"},
                {"Metrica": "Free Cash Flow",     "Valore": f"${inf.get('freeCashflow',0)/1e9:.2f}B"        if inf.get('freeCashflow')         else "N/A"},
                {"Metrica": "Gross Margin",       "Valore": f"{inf.get('grossMargins',0)*100:.1f}%"         if inf.get('grossMargins')         else "N/A"},
                {"Metrica": "Operating Margin",   "Valore": f"{inf.get('operatingMargins',0)*100:.1f}%"     if inf.get('operatingMargins')     else "N/A"},
                {"Metrica": "Net Margin",         "Valore": f"{inf.get('profitMargins',0)*100:.1f}%"        if inf.get('profitMargins')        else "N/A"},
                {"Metrica": "ROE",                "Valore": f"{inf.get('returnOnEquity',0)*100:.1f}%"       if inf.get('returnOnEquity')       else "N/A"},
                {"Metrica": "Debt/Equity",        "Valore": f"{inf.get('debtToEquity',0)/100:.2f}x"        if inf.get('debtToEquity')         else "N/A"},
                {"Metrica": "P/E Trailing",       "Valore": f"{inf.get('trailingPE'):.1f}"                  if inf.get('trailingPE')           else "N/A"},
                {"Metrica": "P/B",                "Valore": f"{inf.get('priceToBook'):.2f}"                 if inf.get('priceToBook')          else "N/A"},
            ]
            st.dataframe(pd.DataFrame(fin_rows).set_index("Metrica"), use_container_width=True)

        with col_news:
            section_header("Latest News")
            yahoo_url = f"https://finance.yahoo.com/quote/{target}/news/"
            st.markdown(f"""
                <div class='terminal-card'>
                    <div class='terminal-card-header'>live feed</div>
                    <a href='{yahoo_url}' target='_blank'
                       style='display:inline-flex;align-items:center;gap:6px;background:#0F2540;color:#FFFFFF;
                              border:1px solid #2979FF;border-radius:3px;padding:7px 14px;
                              font-family:IBM Plex Mono,monospace;font-size:0.75rem;text-decoration:none;
                              letter-spacing:0.08em;'>
                        📰&nbsp;Yahoo Finance News →
                    </a>
                </div>
            """, unsafe_allow_html=True)
            try:
                news_items = get_ticker_news(target)
                if news_items:
                    for n in news_items[:5]:
                        title = n.get('title', '')
                        link  = n.get('link', yahoo_url)
                        if title:
                            st.markdown(f"""
                                <div style='border-left:2px solid #1A3A6A;padding:0.4rem 0.7rem;
                                            margin-bottom:0.5rem;font-size:0.82rem;color:#C8D8E8;'>
                                    <a href='{link}' target='_blank'
                                       style='color:#C8D8E8;text-decoration:none;'>{title}</a>
                                </div>
                            """, unsafe_allow_html=True)
            except Exception:
                pass

    with tab2:
        section_header("Storico Prezzi")
        hist = get_ticker_history(target, period="5y")
        if not hist.empty:
            hist.index = hist.index.tz_localize(None)
            fig_price = go.Figure()
            fig_price.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'], high=hist['High'],
                low=hist['Low'],   close=hist['Close'],
                name=target,
                increasing=dict(line=dict(color='#00E676'), fillcolor='rgba(0,230,118,0.3)'),
                decreasing=dict(line=dict(color='#FF1744'), fillcolor='rgba(255,23,68,0.3)'),
            ))
            vol = hist['Volume'] if 'Volume' in hist.columns else None
            if vol is not None:
                fig_price.add_trace(go.Bar(
                    x=hist.index, y=vol,
                    name="Volume", yaxis="y2",
                    marker_color='rgba(41,121,255,0.25)',
                    showlegend=False,
                ))
            fig_price.update_layout(
                **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                yaxis2=dict(overlaying='y', side='right', showgrid=False, color='#5A7A9A'),
                title=f"{company_name} — Candlestick + Volume",
                height=500,
            )
            st.plotly_chart(fig_price, use_container_width=True)
        else:
            st.info("Dati storici prezzi non disponibili.")

    with tab3:
        # FIX: peers specifici per ticker, non condivisi tra sessioni
        section_header("Fundamental Peer Analysis")
        
        # Chiave unica per questo ticker
        peer_input_key = f"peers_input_{peers_key}"
        
        # Carica peers salvati per questo ticker (o default)
        default_peers = st.session_state.peers_map.get(peers_key, "AMD, INTC, AVGO")
        
        peers_in = st.text_input(
            f"Competitors per {target} (separati da virgola)",
            value=default_peers,
            key=peer_input_key,
            help="Questi peers sono specifici per questo ticker e vengono ricordati."
        )
        
        # Salva nel dict per questo ticker
        if peers_in != st.session_state.peers_map.get(peers_key, ""):
            st.session_state.peers_map[peers_key] = peers_in

        p_list = [target] + [x.strip().upper() for x in peers_in.split(",") if x.strip()]

        with st.spinner("Caricamento peers..."):
            rows = []
            for p in p_list:
                try:
                    pi = get_ticker_info(p)
                    price_p = (pi.get('currentPrice') or pi.get('regularMarketPrice')
                               or pi.get('previousClose') or 0)
                    rows.append({
                        "Ticker":   p,
                        "Price":    f"{price_p:,.2f}"                          if price_p                      else "N/A",
                        "P/E Fwd":  f"{pi.get('forwardPE'):.1f}"               if pi.get('forwardPE')          else "N/A",
                        "P/E Ttm":  f"{pi.get('trailingPE'):.1f}"              if pi.get('trailingPE')         else "N/A",
                        "EPS Fwd":  f"{pi.get('forwardEps'):.2f}"              if pi.get('forwardEps')         else "N/A",
                        "Beta":     f"{pi.get('beta'):.2f}"                    if pi.get('beta')               else "N/A",
                        "P/B":      f"{pi.get('priceToBook'):.1f}"             if pi.get('priceToBook')        else "N/A",
                        "Cap (B$)": f"{pi.get('marketCap',0)/1e9:.1f}"         if pi.get('marketCap')          else "N/A",
                        "Div %":    f"{(pi.get('dividendYield') or 0)*100:.2f}%",
                        "Op.Mgn":   f"{pi.get('operatingMargins',0)*100:.1f}%" if pi.get('operatingMargins')   else "N/A",
                        "ROE":      f"{pi.get('returnOnEquity',0)*100:.1f}%"   if pi.get('returnOnEquity')     else "N/A",
                        "52W Hi":   f"{pi.get('fiftyTwoWeekHigh'):.2f}"        if pi.get('fiftyTwoWeekHigh')   else "N/A",
                    })
                except Exception:
                    rows.append({"Ticker": p, "Price":"ERR"})
            if rows:
                st.dataframe(pd.DataFrame(rows).set_index("Ticker"), use_container_width=True)

        section_header("Relative Performance — 12 Mesi")
        peer_tickers = [target] + [x.strip().upper() for x in peers_in.split(",") if x.strip()]
        try:
            frames = {}
            for tkr in peer_tickers:
                s = download_single(tkr, period="1y")
                if not s.empty: frames[tkr] = s
            if frames:
                peer_data = pd.DataFrame(frames).dropna(how='all').ffill()
                peer_norm = ((peer_data / peer_data.iloc[0]) - 1) * 100
                fig_peer = go.Figure()
                for idx, col in enumerate(peer_norm.columns):
                    is_main = col == target
                    fig_peer.add_trace(go.Scatter(
                        x=peer_norm.index, y=peer_norm[col], name=col,
                        line=dict(width=3 if is_main else 1.5,
                                  color=ACCENT_COLORS[idx % len(ACCENT_COLORS)]),
                        hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>" + col + "</extra>"
                    ))
                fig_peer.add_hline(y=0, line_dash="dot", line_color="#1A3A6A", line_width=1)
                fig_peer.update_layout(
                    **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                    yaxis_title="Rendimento % (norm.)", height=420,
                    title=f"Performance relativa: {target} vs peers (1 anno)"
                )
                st.plotly_chart(fig_peer, use_container_width=True)
        except Exception:
            st.info("Grafico peers non disponibile.")

    with tab4:
        section_header("Supply Chain & Ecosystem")
        sector = inf.get('sector', 'N/A')
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Settore",   sector)
        sc2.metric("Industria", inf.get('industry', 'N/A'))
        sc3.metric("Paese",     inf.get('country', 'N/A'))
        sc4.metric("Exchange",  inf.get('exchange', 'N/A'))

        sc_data = SUPPLY_CHAIN_MAP.get(sector)
        if sc_data:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### 🔼 Fornitori chiave")
                for s in sc_data["suppliers"]:
                    st.markdown(f"""
                        <div style='border-left:2px solid #1A3A6A;padding:0.3rem 0.6rem;
                                    margin-bottom:0.3rem;font-size:0.85rem;color:#C8D8E8;'>{s}</div>
                    """, unsafe_allow_html=True)
            with c2:
                st.markdown("##### 🔽 Clienti / Sbocchi")
                for c in sc_data["customers"]:
                    st.markdown(f"""
                        <div style='border-left:2px solid #2979FF;padding:0.3rem 0.6rem;
                                    margin-bottom:0.3rem;font-size:0.85rem;color:#C8D8E8;'>{c}</div>
                    """, unsafe_allow_html=True)
            st.info(f"💡 {sc_data['notes']}")
        else:
            st.info(f"Mappa supply chain non disponibile per '{sector}'.")


# =========================================================
# 1. GLOBAL OVERVIEW
# =========================================================
if choice == "Global Overview":
    page_title("🌍  Global Market Overview", "Snapshot in tempo reale · Indici · Titoli · Top Movers")

    section_header("Indici Globali")
    indices = {
        "S&P 500": "^GSPC", "Nasdaq 100": "^IXIC", "Dow Jones": "^DJI",
        "Nikkei 225": "^N225", "FTSE MIB": "FTSEMIB.MI", "DAX 40": "^GDAXI",
        "CAC 40": "^FCHI", "Hang Seng": "^HSI", "Shanghai": "000001.SS",
        "Euro Stoxx 50": "^STOXX50E", "Russell 2000": "^RUT", "Nifty 50": "^NSEI",
    }
    with st.spinner("Caricamento indici..."):
        cols = st.columns(4)
        for i, (name, ticker) in enumerate(indices.items()):
            try:
                d = get_ticker_history(ticker, "2d")
                if len(d) >= 2:
                    c, p = d['Close'].iloc[-1], d['Close'].iloc[-2]
                    delta = f"{((c-p)/p)*100:+.2f}%"
                    cols[i%4].metric(name, f"{c:,.2f}", delta)
                else:
                    cols[i%4].metric(name, "N/A", "—")
            except Exception:
                cols[i%4].metric(name, "N/A", "—")

    st.markdown("---")
    section_header("Titoli di Riferimento")
    stocks = {
        "Apple": "AAPL", "Microsoft": "MSFT", "Nvidia": "NVDA", "Google": "GOOGL",
        "Tesla": "TSLA", "Amazon": "AMZN", "Meta": "META", "LVMH": "MC.PA",
        "ASML": "ASML.AS", "SAP": "SAP.DE", "ENI": "ENI.MI", "Ferrari": "RACE.MI",
    }
    with st.spinner("Caricamento titoli..."):
        cols2 = st.columns(4)
        for i, (name, ticker) in enumerate(stocks.items()):
            try:
                d = get_ticker_history(ticker, "2d")
                if len(d) >= 2:
                    c, p = d['Close'].iloc[-1], d['Close'].iloc[-2]
                    cols2[i%4].metric(f"{name} ({ticker})", f"{c:,.2f}", f"{((c-p)/p)*100:+.2f}%")
                else:
                    cols2[i%4].metric(f"{name} ({ticker})", "N/A", "—")
            except Exception:
                cols2[i%4].metric(f"{name} ({ticker})", "N/A", "—")

    st.markdown("---")
    section_header("Top Movers del Giorno")

    with st.spinner("Calcolo top movers..."):
        try:
            gainers, losers = get_top_movers(n=5)
            col_g, col_l = st.columns(2)
            for mover_col, mover_data, label, color, icon in [
                (col_g, gainers, "Top Gainers", "#00E676", "▲"),
                (col_l, losers,  "Top Losers",  "#FF1744", "▼"),
            ]:
                with mover_col:
                    st.markdown(f"""
                        <div style='font-family:IBM Plex Mono,monospace;font-size:0.7rem;
                                    color:{color};letter-spacing:0.2em;margin-bottom:8px;'>{icon} {label.upper()}</div>
                    """, unsafe_allow_html=True)
                    for m in mover_data:
                        st.markdown(f"""
                            <div style='background:#070E1C;border:1px solid #0F2540;
                                        border-left:3px solid {color};border-radius:3px;
                                        padding:0.65rem 1rem;margin-bottom:6px;
                                        display:flex;justify-content:space-between;align-items:center;'>
                                <div>
                                    <div style='font-family:IBM Plex Mono,monospace;font-size:0.9rem;
                                                color:#FFFFFF;font-weight:600;'>{m['ticker']}</div>
                                    <div style='font-size:0.72rem;color:#5A7A9A;'>${m['price']:,.2f}</div>
                                </div>
                                <div style='font-family:IBM Plex Mono,monospace;font-size:1.05rem;
                                            color:{color};font-weight:700;'>{m['pct']:+.2f}%</div>
                            </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Top movers non disponibili: {e}")


# =========================================================
# 2. ANALISI DCF
# =========================================================
elif choice == "Analisi DCF":
    page_title("🧮  Discounted Cash Flow", "Stima il fair value tramite il modello DCF")

    col1, col2 = st.columns([1, 1])
    with col1:
        section_header("Parametri di Input")
        fcf             = st.number_input("Free Cash Flow Attuale ($)", value=1_000_000_000, step=50_000_000, format="%d")
        growth          = st.slider("Tasso di Crescita (%)", 1, 50, 10)
        wacc            = st.slider("WACC (%)", 5, 20, 9)
        terminal_growth = st.slider("Terminal Growth Rate (%)", 0, 5, 2)
        years_dcf       = st.slider("Anni di Proiezione", 3, 15, 10)
        shares          = st.number_input("Azioni in Circolazione", value=1_000_000_000, step=10_000_000, format="%d")

    g, w, tg = growth/100, wacc/100, terminal_growth/100
    cash_flows, pv_flows = [], []
    for yr in range(1, years_dcf+1):
        cf = fcf * ((1+g)**yr)
        pv = cf / ((1+w)**yr)
        cash_flows.append(cf); pv_flows.append(pv)
    tv   = (cash_flows[-1]*(1+tg))/(w-tg) if w > tg else 0
    pvtv = tv / ((1+w)**years_dcf)
    ev   = sum(pv_flows) + pvtv
    fvs  = ev / shares if shares > 0 else 0

    with col2:
        section_header("Risultati")
        r1, r2 = st.columns(2)
        r1.metric("Enterprise Value",        f"${ev/1e9:,.2f}B")
        r2.metric("Fair Value per Azione",   f"${fvs:,.2f}")
        r3, r4 = st.columns(2)
        r3.metric("Terminal Value (PV)",     f"${pvtv/1e9:,.2f}B")
        r4.metric("PV Cash Flows operativi", f"${sum(pv_flows)/1e9:,.2f}B")

        tv_weight = (pvtv / ev * 100) if ev > 0 else 0
        st.markdown(f"""
            <div class='terminal-card' style='margin-top:1rem;'>
                <div class='terminal-card-header'>Terminal Value Weight</div>
                <div style='height:8px;background:#0F2540;border-radius:4px;overflow:hidden;margin-top:8px;'>
                    <div style='width:{tv_weight:.1f}%;height:100%;background:linear-gradient(90deg,#2979FF,#AA00FF);border-radius:4px;'></div>
                </div>
                <div style='font-family:IBM Plex Mono,monospace;font-size:0.85rem;color:#FFFFFF;margin-top:6px;'>
                    {tv_weight:.1f}% del valore totale è nel Terminal Value
                </div>
                <div style='font-size:0.78rem;color:#5A7A9A;margin-top:3px;'>
                    {"⚠️ Alta dipendenza dal terminal value — sensibile alle assunzioni." if tv_weight > 70 else "✅ Bilanciamento accettabile tra cash flows operativi e terminal value."}
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"Y{i+1}" for i in range(years_dcf)],
        y=[v/1e6 for v in cash_flows], name="FCF Proiettato",
        marker_color='#2979FF', opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        x=[f"Y{i+1}" for i in range(years_dcf)],
        y=[v/1e6 for v in pv_flows], name="PV dei Cash Flows",
        marker_color='#00E676', opacity=0.7,
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, yaxis_title="$ Milioni", barmode='group',
        title="Cash Flow Proiettato vs Present Value",
    )
    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# 3. MULTI-COMPARE
# =========================================================
elif choice == "Multi-Compare":
    page_title("📊  Multi-Asset Comparison", "Confronto rendimenti, inflazione e fondamentali aziendali")

    tab_r, tab_i, tab_f = st.tabs(["📈  RENDIMENTO ASSET", "📉  INFLAZIONE / TIPS", "🏢  FONDAMENTALI"])

    with tab_r:
        section_header("Rendimento % Normalizzato")
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1: tk_in   = st.text_input("Ticker (separati da virgola)", "AAPL, MSFT, TSLA, NVDA")
        with col2: horizon = st.selectbox("Orizzonte", ["Mesi", "Anni"])
        with col3: val     = st.slider("Durata", 1, 24 if horizon == "Mesi" else 10, 12)
        tk_list   = [x.strip().upper() for x in tk_in.split(",") if x.strip()]
        start_str = (datetime.now()-timedelta(days=val*30 if horizon == "Mesi" else val*365)).strftime("%Y-%m-%d")
        if tk_list:
            with st.spinner("Download..."):
                try:
                    frames = {}
                    for tkr in tk_list:
                        s = download_single(tkr, start_str=start_str)
                        if not s.empty: frames[tkr] = s
                        else: st.warning(f"Nessun dato per {tkr}")
                    if frames:
                        data = pd.DataFrame(frames).dropna(how="all").ffill()
                        rets = ((data / data.iloc[0]) - 1) * 100
                        fig = go.Figure()
                        for idx, col in enumerate(rets.columns):
                            fig.add_trace(go.Scatter(
                                x=rets.index, y=rets[col], name=col,
                                line=dict(width=2, color=ACCENT_COLORS[idx % len(ACCENT_COLORS)]),
                                hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>" + col + "</extra>"
                            ))
                        fig.add_hline(y=0, line_dash="dot", line_color="#1A3A6A", line_width=1)
                        fig.update_layout(
                            **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                            title="Rendimento % Normalizzato", yaxis_title="Rendimento (%)", height=460
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.dataframe(pd.DataFrame({
                            "Rendimento Totale (%)": rets.iloc[-1].round(2),
                            "Max (%)": rets.max().round(2),
                            "Min (%)": rets.min().round(2),
                        }), use_container_width=True)
                except Exception as e:
                    st.error(f"Errore: {e}")

    with tab_i:
        section_header("Proxy Inflazione — ETF TIPS")
        st.info("L'inflazione ufficiale (CPI) non è disponibile via yfinance. Usiamo proxy: **TIP**, **RINF**, **ITIP**, **STIP**.")
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1: infl_in = st.text_input("Ticker inflazione/TIPS", "TIP, RINF, ITIP, STIP")
        with col2: infl_h  = st.selectbox("Orizzonte", ["Mesi", "Anni"], key="infl_h")
        with col3: infl_v  = st.slider("Durata", 1, 24 if infl_h == "Mesi" else 20, 5, key="infl_v")
        comp_in = st.text_input("Asset da confrontare", "SPY, GLD")
        infl_list = [x.strip().upper() for x in infl_in.split(",") if x.strip()]
        comp_list = [x.strip().upper() for x in comp_in.split(",") if x.strip()]
        all_infl  = list(dict.fromkeys(infl_list + comp_list))
        infl_start = (datetime.now()-timedelta(days=infl_v*30 if infl_h == "Mesi" else infl_v*365)).strftime("%Y-%m-%d")
        with st.spinner("Download..."):
            try:
                frames = {}
                for tkr in all_infl:
                    s = download_single(tkr, start_str=infl_start)
                    if not s.empty: frames[tkr] = s
                if frames:
                    data = pd.DataFrame(frames).dropna(how="all").ffill()
                    rets = ((data / data.iloc[0]) - 1) * 100
                    preset = {"TIP": "#FF9100", "RINF": "#FF1744", "ITIP": "#FF6D00",
                              "STIP": "#FFD600", "SPY": "#2979FF", "GLD": "#00E676"}
                    fig = go.Figure()
                    for idx, col in enumerate(rets.columns):
                        fig.add_trace(go.Scatter(
                            x=rets.index, y=rets[col], name=col,
                            line=dict(width=2.5 if col in infl_list else 1.5,
                                      dash="solid" if col in infl_list else "dot",
                                      color=preset.get(col, ACCENT_COLORS[idx % len(ACCENT_COLORS)])),
                            hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>" + col + "</extra>"
                        ))
                    fig.add_hline(y=0, line_dash="dot", line_color="#1A3A6A", line_width=1)
                    fig.update_layout(
                        **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                        title="Proxy Inflazione vs Asset", yaxis_title="Rendimento %", height=480
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Errore: {e}")

    with tab_f:
        section_header("Andamento Storico dei Fondamentali")
        col1, col2 = st.columns([3, 2])
        with col1: fund_in     = st.text_input("Ticker aziende", "AAPL, MSFT, GOOGL")
        with col2: fund_metric = st.selectbox("Metrica", [
            "P/E Storico (calcolato)", "P/S Storico (calcolato)",
            "EPS Trimestrale", "Revenue Trimestrale", "Gross Profit Trimestrale",
            "Net Income Trimestrale", "EBITDA Trimestrale", "Free Cash Flow Trimestrale",
            "Debt/Equity (snapshot)", "Operating Margin % (snapshot)", "ROE % (snapshot)",
            "Market Cap Storico (B$)",
        ])
        fund_list    = [x.strip().upper() for x in fund_in.split(",") if x.strip()]
        years_back_s = st.slider("Anni di storia", 1, 15, 7, key="fund_years")

        METRIC_TYPE = {
            "P/E Storico (calcolato)":       "pe_hist",
            "P/S Storico (calcolato)":       "ps_hist",
            "Market Cap Storico (B$)":       "mktcap_hist",
            "EPS Trimestrale":               ("quarterly", "EPS", "EPS ($)", 1),
            "Revenue Trimestrale":           ("quarterly", "Total Revenue", "Revenue (B$)", 1),
            "Gross Profit Trimestrale":      ("quarterly", "Gross Profit", "Gross Profit (B$)", 1),
            "Net Income Trimestrale":        ("quarterly", "Net Income", "Net Income (B$)", 1),
            "EBITDA Trimestrale":            ("quarterly", "EBITDA", "EBITDA (B$)", 1),
            "Free Cash Flow Trimestrale":    ("quarterly", "Free Cash Flow", "FCF (B$)", 1),
            "Debt/Equity (snapshot)":        ("snapshot", "debtToEquity", "D/E (x)", 100),
            "Operating Margin % (snapshot)": ("snapshot", "operatingMargins", "Op.Margin %", 0.01),
            "ROE % (snapshot)":              ("snapshot", "returnOnEquity", "ROE %", 0.01),
        }
        mtype = METRIC_TYPE[fund_metric]

        if fund_list:
            with st.spinner("Calcolo fondamentali..."):
                if mtype == "pe_hist":
                    fig = go.Figure()
                    for idx, tkr in enumerate(fund_list):
                        s = get_historical_pe(tkr, years_back=years_back_s)
                        if not s.empty:
                            s_sm = s.rolling(20, min_periods=1).mean()
                            fig.add_trace(go.Scatter(x=s_sm.index, y=s_sm, name=tkr,
                                line=dict(width=2, color=ACCENT_COLORS[idx % len(ACCENT_COLORS)]),
                                hovertemplate="%{x|%d %b %Y}<br>P/E: %{y:.1f}<extra>" + tkr + "</extra>"))
                        else:
                            st.warning(f"P/E storico non disponibile per {tkr}")
                    if fig.data:
                        fig.update_layout(**{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                                          title="P/E Ratio Storico", yaxis_title="P/E", height=480)
                        st.plotly_chart(fig, use_container_width=True)

                elif mtype == "ps_hist":
                    fig = go.Figure()
                    for idx, tkr in enumerate(fund_list):
                        s = get_historical_ps(tkr, years_back=years_back_s)
                        if not s.empty:
                            s_sm = s.rolling(20, min_periods=1).mean()
                            fig.add_trace(go.Scatter(x=s_sm.index, y=s_sm, name=tkr,
                                line=dict(width=2, color=ACCENT_COLORS[idx % len(ACCENT_COLORS)]),
                                hovertemplate="%{x|%d %b %Y}<br>P/S: %{y:.2f}<extra>" + tkr + "</extra>"))
                    if fig.data:
                        fig.update_layout(**{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                                          title="P/S Ratio Storico", yaxis_title="P/S", height=480)
                        st.plotly_chart(fig, use_container_width=True)

                elif mtype == "mktcap_hist":
                    fig = go.Figure()
                    for idx, tkr in enumerate(fund_list):
                        s = get_historical_mktcap(tkr, years_back=years_back_s)
                        if not s.empty:
                            fig.add_trace(go.Scatter(x=s.index, y=s, name=tkr,
                                line=dict(width=2, color=ACCENT_COLORS[idx % len(ACCENT_COLORS)]),
                                hovertemplate="%{x|%d %b %Y}<br>$%{y:.0f}B<extra>" + tkr + "</extra>"))
                    if fig.data:
                        fig.update_layout(**{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                                          title="Market Cap Storico (B$)", yaxis_title="Market Cap (B$)", height=480)
                        st.plotly_chart(fig, use_container_width=True)

                elif isinstance(mtype, tuple) and mtype[0] == "quarterly":
                    _, q_key, y_label, _ = mtype
                    fig = go.Figure(); has_data = False
                    cutoff = datetime.now() - timedelta(days=365 * years_back_s)
                    for idx, tkr in enumerate(fund_list):
                        s = get_quarterly_metric(tkr, q_key)
                        if not s.empty:
                            s = s[s.index >= cutoff]
                            if not s.empty:
                                fig.add_trace(go.Bar(
                                    x=s.index.astype(str), y=s.values, name=tkr,
                                    marker_color=ACCENT_COLORS[idx % len(ACCENT_COLORS)],
                                ))
                                has_data = True
                    if has_data:
                        fig.update_layout(**PLOTLY_LAYOUT, title=y_label,
                                          yaxis_title=y_label, barmode="group", height=480)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Nessun dato disponibile. yfinance limita lo storico trimestrale.")

                elif isinstance(mtype, tuple) and mtype[0] == "snapshot":
                    _, info_key, y_label, divisor = mtype
                    bar_data = {}
                    for tkr in fund_list:
                        info = get_ticker_info(tkr)
                        v = info.get(info_key)
                        if v is not None:
                            try: bar_data[tkr] = float(v) / divisor
                            except Exception: pass
                    if bar_data:
                        fig_bar = go.Figure()
                        fig_bar.add_trace(go.Bar(
                            x=list(bar_data.keys()), y=list(bar_data.values()),
                            marker_color=ACCENT_COLORS[:len(bar_data)],
                            text=[f"{v:.2f}" for v in bar_data.values()],
                            textposition="outside", textfont=dict(color="#FFFFFF"),
                        ))
                        fig_bar.update_layout(**PLOTLY_LAYOUT, title=f"{y_label} — Snapshot",
                                              yaxis_title=y_label, height=420, showlegend=False)
                        st.plotly_chart(fig_bar, use_container_width=True)


# =========================================================
# 4. PORTFOLIO BACKTEST (CON RISK METRICS)
# =========================================================
elif choice == "Portfolio Backtest":
    page_title("🧪  Portfolio Backtest", "Costruisci una strategia · Confronta con benchmark · Analisi rischio completa")

    section_header("Composizione del Portafoglio")
    col1, _ = st.columns([1, 2])
    with col1: n_assets = st.slider("Numero di asset", 2, 8, 3)

    assets_defaults = ["VOO", "GLD", "TLT", "QQQ", "BND", "VNQ", "EEM", "PDBC"]
    asset_list, weight_list = [], []
    st.markdown("**Ticker**")
    cols_a = st.columns(n_assets)
    for i in range(n_assets):
        with cols_a[i]:
            t = st.text_input(f"Asset {i+1}", value=assets_defaults[i] if i < len(assets_defaults) else "", key=f"asset_{i}")
            asset_list.append(t.strip().upper())

    st.markdown("**Pesi (%)**")
    cols_w = st.columns(n_assets)
    dw = round(100 / n_assets)
    for i in range(n_assets):
        with cols_w[i]:
            w = st.slider(f"{asset_list[i] or f'A{i+1}'}", 0, 100, dw, key=f"weight_{i}")
            weight_list.append(w)

    total_weight = sum(weight_list)
    if total_weight != 100:
        st.warning(f"⚠️  Somma pesi: {total_weight}% — deve essere 100%.")
    else:
        st.success(f"✅  Pesi bilanciati: {total_weight}%")

    st.markdown("---")
    section_header("Benchmark e Orizzonte")
    col3, col4, col5 = st.columns(3)
    with col3:
        bench_options = {
            "S&P 500 (^GSPC)": "^GSPC", "MSCI World (VWCE.DE)": "VWCE.DE",
            "Nasdaq 100 (^IXIC)": "^IXIC", "60/40 Custom": None
        }
        bench_label = st.selectbox("Benchmark", list(bench_options.keys()))
        bench = bench_options[bench_label]
    with col4:
        years = st.slider("Orizzonte temporale (anni)", 1, 20, 5, key="bt_years")
    with col5:
        risk_free_rate = st.slider("Risk-Free Rate (%)", 0.0, 8.0, 4.5, step=0.1,
                                   help="Usato per calcolo Sharpe e Sortino. Default: ~T-Bill 4.5%")

    bench_eq, bench_bond = "SPY", "AGG"
    if bench is None:
        bc1, bc2 = st.columns(2)
        with bc1: bench_eq   = st.text_input("Benchmark Equity", "SPY")
        with bc2: bench_bond = st.text_input("Benchmark Bond",   "AGG")

    run = st.button("▶  ESEGUI BACKTEST", use_container_width=True)

    if run and total_weight == 100:
        valid_pairs  = [(a, weight_list[i]) for i, a in enumerate(asset_list) if a]
        valid_assets = [p[0] for p in valid_pairs]
        w_norm       = [p[1]/100 for p in valid_pairs]
        start_str    = (datetime.now() - timedelta(days=365*years)).strftime("%Y-%m-%d")
        bench_tickers = [bench] if bench else [bench_eq.upper(), bench_bond.upper()]
        rf = risk_free_rate / 100

        with st.spinner("Download dati storici..."):
            try:
                frames = {}
                for tkr in valid_assets + bench_tickers:
                    s = download_single(tkr, start_str=start_str)
                    if not s.empty: frames[tkr] = s
                    else: st.warning(f"Nessun dato per {tkr}")

                if not frames:
                    st.error("Nessun dato scaricato.")
                else:
                    data     = pd.DataFrame(frames).dropna(how='all').ffill()
                    norm     = (data / data.iloc[0]) - 1
                    strat_df = pd.DataFrame(index=norm.index)
                    for i, a in enumerate(valid_assets):
                        if a in norm.columns:
                            strat_df[a] = norm[a] * w_norm[i]
                    strategy = strat_df.sum(axis=1)

                    if bench is None:
                        beq, bbd = bench_eq.upper(), bench_bond.upper()
                        if beq in norm.columns and bbd in norm.columns:
                            bench_series = norm[beq]*0.6 + norm[bbd]*0.4
                            bench_name   = f"60% {beq} + 40% {bbd}"
                            bench_col    = None
                        else:
                            bench_series, bench_name, bench_col = None, "", None
                    else:
                        bench_col    = bench
                        bench_name   = bench_label
                        bench_series = None

                    # --- Performance Chart ---
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=strategy.index, y=strategy*100,
                        name="📐 La Tua Strategia",
                        line=dict(width=3, color="#2979FF"),
                        fill='tozeroy', fillcolor='rgba(41,121,255,0.06)',
                        hovertemplate="%{x|%d %b %Y}<br><b>Strategia: %{y:.2f}%</b><extra></extra>"
                    ))
                    if bench_col and bench_col in norm.columns:
                        fig.add_trace(go.Scatter(
                            x=norm.index, y=norm[bench_col]*100,
                            name=f"📌 {bench_name}",
                            line=dict(width=2, dash='dash', color='#5A7A9A'),
                        ))
                    elif bench_series is not None:
                        fig.add_trace(go.Scatter(
                            x=bench_series.index, y=bench_series*100,
                            name=f"📌 {bench_name}",
                            line=dict(width=2, dash='dash', color='#5A7A9A'),
                        ))
                    for idx, a in enumerate(valid_assets):
                        if a in norm.columns:
                            fig.add_trace(go.Scatter(
                                x=norm.index, y=norm[a]*100,
                                name=f"{a} ({valid_pairs[idx][1]}%)",
                                line=dict(width=1.2, color=ACCENT_COLORS[(idx+1) % len(ACCENT_COLORS)]),
                                opacity=0.5,
                            ))
                    fig.add_hline(y=0, line_dash="dot", line_color="#1A3A6A", line_width=1)
                    fig.update_layout(
                        **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                        title="Rendimento Cumulativo (%)", yaxis_title="Rendimento (%)", height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # --- Risk Calculations ---
                    daily_returns  = strategy.pct_change().dropna()
                    total_ret      = strategy.iloc[-1] * 100
                    annual_ret     = ((1 + strategy.iloc[-1])**(1/years) - 1) * 100 if years > 0 else 0
                    vol            = daily_returns.std() * (252**0.5) * 100
                    sharpe         = ((annual_ret/100 - rf) / (vol/100)) if vol > 0 else 0
                    drawdown_series = ((strategy+1) / (strategy+1).cummax() - 1) * 100
                    max_drawdown   = drawdown_series.min()

                    # Sortino
                    downside = daily_returns[daily_returns < 0]
                    downside_vol = downside.std() * (252**0.5) * 100 if len(downside) > 0 else 0
                    sortino = ((annual_ret/100 - rf) / (downside_vol/100)) if downside_vol > 0 else 0

                    # Calmar
                    calmar = (annual_ret / abs(max_drawdown)) if max_drawdown != 0 else 0

                    # VaR e CVaR (95%)
                    var_95  = np.percentile(daily_returns, 5) * 100
                    cvar_95 = daily_returns[daily_returns <= np.percentile(daily_returns, 5)].mean() * 100

                    # Beta vs benchmark
                    beta_val = None
                    if bench_col and bench_col in data.columns:
                        bench_ret = data[bench_col].pct_change().dropna()
                        aligned   = pd.DataFrame({"s": daily_returns, "b": bench_ret}).dropna()
                        if len(aligned) > 20:
                            cov = np.cov(aligned['s'], aligned['b'])
                            beta_val = cov[0, 1] / cov[1, 1] if cov[1, 1] != 0 else None

                    # Alpha vs benchmark
                    delta_vs_bench = None
                    if bench_col and bench_col in norm.columns:
                        bench_total    = norm[bench_col].iloc[-1] * 100
                        delta_vs_bench = total_ret - bench_total
                    elif bench_series is not None:
                        bench_total    = bench_series.iloc[-1] * 100
                        delta_vs_bench = total_ret - bench_total

                    # --- Risk Metrics Panel ---
                    st.markdown("---")
                    section_header("Performance & Risk Metrics")

                    # Row 1 — Performance
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.metric("Rendimento Totale",  f"{total_ret:+.2f}%")
                    m2.metric("CAGR",               f"{annual_ret:+.2f}%")
                    m3.metric("Volatilità Annua",   f"{vol:.2f}%")
                    m4.metric("Max Drawdown",        f"{max_drawdown:.2f}%")
                    m5.metric("Alpha vs Bench",     f"{delta_vs_bench:+.2f}%" if delta_vs_bench is not None else "N/A")

                    # Row 2 — Risk Ratios
                    st.markdown("---")
                    r1, r2, r3, r4, r5 = st.columns(5)
                    r1.metric("Sharpe Ratio",  f"{sharpe:.3f}",
                              delta="Buono" if sharpe >= 1 else ("Accettabile" if sharpe >= 0.5 else "Basso"))
                    r2.metric("Sortino Ratio", f"{sortino:.3f}",
                              delta="Buono" if sortino >= 1.5 else ("Accettabile" if sortino >= 0.8 else "Basso"))
                    r3.metric("Calmar Ratio",  f"{calmar:.3f}",
                              delta="Buono" if calmar >= 1 else ("Accettabile" if calmar >= 0.5 else "Basso"))
                    r4.metric("VaR 95% (1gg)",  f"{var_95:.2f}%",
                              help="Value at Risk: perdita massima giornaliera nel 95% dei giorni")
                    r5.metric("CVaR 95% (1gg)", f"{cvar_95:.2f}%",
                              help="Conditional VaR: perdita media nei giorni peggiori del 5%")
                    if beta_val is not None:
                        b1, b2, *_ = st.columns(5)
                        b1.metric("Beta vs Bench",  f"{beta_val:.2f}",
                                  delta="Difensivo" if beta_val < 0.8 else ("Aggressivo" if beta_val > 1.2 else "Neutro"))
                        b2.metric("Risk-Free Rate",  f"{risk_free_rate:.1f}%")

                    # --- Curvo-style Risk/Return Chart ---
                    st.markdown("---")
                    section_header("Risk / Return Scatter")
                    scatter_data = []
                    for idx, a in enumerate(valid_assets):
                        if a in data.columns:
                            a_ret_d = data[a].pct_change().dropna()
                            a_ann   = ((data[a].iloc[-1]/data[a].iloc[0])**(1/years)-1)*100
                            a_vol   = a_ret_d.std() * (252**0.5) * 100
                            a_sh    = ((a_ann/100 - rf) / (a_vol/100)) if a_vol > 0 else 0
                            scatter_data.append({"name": a, "vol": a_vol, "ret": a_ann, "sharpe": a_sh, "type": "asset"})
                    scatter_data.append({"name": "⬤ Portafoglio", "vol": vol, "ret": annual_ret, "sharpe": sharpe, "type": "portfolio"})
                    if bench_col and bench_col in data.columns:
                        b_ret_d = data[bench_col].pct_change().dropna()
                        b_ann   = ((data[bench_col].iloc[-1]/data[bench_col].iloc[0])**(1/years)-1)*100
                        b_vol   = b_ret_d.std() * (252**0.5) * 100
                        scatter_data.append({"name": "★ Benchmark", "vol": b_vol, "ret": b_ann, "sharpe": None, "type": "benchmark"})

                    fig_sc = go.Figure()
                    # Efficient frontier guideline
                    vols_range = np.linspace(max(0, min(d["vol"] for d in scatter_data)-2),
                                             max(d["vol"] for d in scatter_data)+2, 50)
                    cml_rets = rf*100 + sharpe * vols_range
                    fig_sc.add_trace(go.Scatter(
                        x=vols_range, y=cml_rets,
                        mode='lines', name=f"Capital Market Line (Sharpe={sharpe:.2f})",
                        line=dict(color='rgba(41,121,255,0.35)', width=1.5, dash='dot'),
                        showlegend=True,
                    ))
                    color_map = {"asset": "#5A7A9A", "portfolio": "#2979FF", "benchmark": "#FF9100"}
                    size_map  = {"asset": 10, "portfolio": 18, "benchmark": 14}
                    for d in scatter_data:
                        fig_sc.add_trace(go.Scatter(
                            x=[d["vol"]], y=[d["ret"]],
                            mode='markers+text',
                            name=d["name"],
                            text=[d["name"]], textposition="top center",
                            marker=dict(size=size_map[d["type"]], color=color_map[d["type"]],
                                        line=dict(width=1, color='#FFFFFF')),
                            hovertemplate=f"<b>{d['name']}</b><br>Vol: %{{x:.2f}}%<br>Ret: %{{y:.2f}}%<extra></extra>",
                        ))
                    fig_sc.update_layout(
                        **PLOTLY_LAYOUT,
                        xaxis_title="Volatilità Annua (%)",
                        yaxis_title="Rendimento Annuo CAGR (%)",
                        title="Risk / Return — Capital Market Line",
                        height=420, showlegend=True,
                    )
                    st.plotly_chart(fig_sc, use_container_width=True)

                    # --- Drawdown ---
                    st.markdown("---")
                    section_header("Drawdown nel Tempo")
                    fig_dd = go.Figure()
                    fig_dd.add_trace(go.Scatter(
                        x=drawdown_series.index, y=drawdown_series,
                        name="Drawdown", fill='tozeroy',
                        line=dict(color='#FF1744', width=1.5),
                        fillcolor='rgba(255,23,68,0.12)',
                    ))
                    fig_dd.update_layout(
                        **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                        yaxis_title="Drawdown (%)", height=300,
                        title="Drawdown dalla Massima Equity"
                    )
                    st.plotly_chart(fig_dd, use_container_width=True)

                    # --- Returns Distribution ---
                    section_header("Distribuzione Rendimenti Giornalieri")
                    fig_hist = go.Figure()
                    fig_hist.add_trace(go.Histogram(
                        x=daily_returns * 100,
                        nbinsx=60,
                        name="Rendimenti",
                        marker_color='#2979FF',
                        opacity=0.75,
                    ))
                    fig_hist.add_vline(x=var_95,  line_dash="dash", line_color="#FF9100",
                                       annotation_text=f"VaR 95%: {var_95:.2f}%",
                                       annotation_font_color="#FF9100")
                    fig_hist.add_vline(x=cvar_95, line_dash="dash", line_color="#FF1744",
                                       annotation_text=f"CVaR 95%: {cvar_95:.2f}%",
                                       annotation_font_color="#FF1744")
                    fig_hist.update_layout(
                        **PLOTLY_LAYOUT,
                        title="Distribuzione Rendimenti Giornalieri",
                        xaxis_title="Rendimento Giornaliero (%)",
                        yaxis_title="Frequenza", height=320,
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)

                    # --- Correlation ---
                    available = [a for a in valid_assets if a in norm.columns]
                    avg_corr = None
                    if len(available) >= 2:
                        section_header("Matrice di Correlazione")
                        corr_df = norm[available].pct_change().dropna().corr()
                        fig_corr = go.Figure(go.Heatmap(
                            z=corr_df.values, x=corr_df.columns.tolist(), y=corr_df.index.tolist(),
                            colorscale=[[0, '#FF1744'], [0.5, '#070E1C'], [1, '#00E676']],
                            zmin=-1, zmax=1,
                            text=corr_df.round(2).values, texttemplate="%{text}",
                            hovertemplate="%{x} / %{y}: %{z:.2f}<extra></extra>",
                        ))
                        fig_corr.update_layout(**PLOTLY_LAYOUT, height=350, title="Correlazione tra Asset")
                        st.plotly_chart(fig_corr, use_container_width=True)
                        upper = corr_df.values[np.triu_indices_from(corr_df.values, k=1)]
                        avg_corr = upper.mean() if len(upper) > 0 else None

                    # --- TIR ---
                    try:
                        import numpy_financial as npf
                        n_months = years * 12
                        cf_irr   = [-100] + [0]*(n_months-1) + [100*(1+strategy.iloc[-1])]
                        irr_m    = npf.irr(cf_irr)
                        section_header("TIR — Tasso Interno di Rendimento")
                        st.metric("TIR Annualizzato", f"{((1+irr_m)**12-1)*100:+.2f}%")
                    except ImportError:
                        st.metric("TIR (approx = CAGR)", f"{annual_ret:+.2f}%",
                                  help="pip install numpy-financial per il TIR esatto")
                    except Exception:
                        pass

                    # --- Suggerimenti ---
                    st.markdown("---")
                    section_header("Analisi e Suggerimenti")
                    suggestions = []
                    if sharpe < 0:
                        suggestions.append(f"🔴 <b>Sharpe negativo ({sharpe:.2f})</b> — Rendimento sotto il risk-free ({risk_free_rate}%). Stai assorbendo rischio senza compensazione. Considera ETF a bassa volatilità (USMV, SPLV).")
                    elif sharpe < 0.5:
                        suggestions.append(f"📉 <b>Sharpe inefficiente ({sharpe:.2f})</b> — Asset decorrelati (oro, TIPS, REITs internazionali) potrebbero migliorare il profilo rischio/rendimento.")
                    elif sharpe >= 1.5:
                        suggestions.append(f"🏆 <b>Sharpe eccellente ({sharpe:.2f})</b> — Verifica il survivorship bias. Sharpe così alti tendono a normalizzarsi. Testa su 15-20 anni.")
                    else:
                        suggestions.append(f"✅ <b>Sharpe accettabile ({sharpe:.2f})</b> — Nella norma. Target: superare 1.0 per battere il mercato su base risk-adjusted.")

                    if sortino < 0.8:
                        suggestions.append(f"📊 <b>Sortino basso ({sortino:.2f})</b> — Il rendimento non compensa adeguatamente il rischio di ribasso specifico.")
                    if abs(var_95) > 2.5:
                        suggestions.append(f"⚠️ <b>VaR 95% elevato ({var_95:.2f}%)</b> — In 1 giorno su 20 potresti perdere più del {abs(var_95):.2f}%. Valuta un hedging parziale con opzioni put o asset difensivi.")
                    if vol > 25:
                        suggestions.append(f"📊 <b>Volatilità molto alta ({vol:.1f}%)</b> — In uno scenario 2008 potresti sperimentare drawdown >50%. Considera 15-20% in bond aggregati (AGG).")
                    if max_drawdown < -40:
                        suggestions.append(f"⚠️ <b>Drawdown estremo ({max_drawdown:.1f}%)</b> — Per tornare al pareggio servono {abs(max_drawdown)/(100+max_drawdown)*100:.1f}% dal minimo.")
                    if avg_corr is not None and avg_corr > 0.7:
                        suggestions.append(f"🔗 <b>Correlazione media alta ({avg_corr:.2f})</b> — In un sell-off scenderebbero tutti insieme. Aggiungi asset decorrelati (GLD, TLT, commodities).")
                    if delta_vs_bench is not None and delta_vs_bench < -5:
                        suggestions.append(f"🔴 <b>Sottoperformance vs {bench_name} ({delta_vs_bench:+.1f}%)</b> — Un semplice ETF sul benchmark avrebbe fatto meglio a costo zero.")
                    if not suggestions:
                        suggestions.append("ℹ️ Parametri nella norma. Nessun segnale critico rilevato.")

                    for sg in suggestions:
                        st.markdown(f"""
                            <div style='background:#070E1C;border:1px solid #0F2540;border-left:3px solid #2979FF;
                                        border-radius:3px;padding:0.8rem 1rem;margin-bottom:0.5rem;
                                        font-size:0.86rem;line-height:1.65;color:#C8D8E8;'>{sg}</div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Errore durante il backtest: {e}")
                import traceback
                st.code(traceback.format_exc())

    elif run and total_weight != 100:
        st.error("Correggi i pesi (devono sommare a 100%).")


# =========================================================
# 5. STOCK SCREENER (FINVIZ + yfinance Deep)
# =========================================================
elif choice == "Stock Screener":

    # Se un ticker è stato selezionato per analisi dettagliata
    if st.session_state.screener_selected:
        target = st.session_state.screener_selected
        if st.button("← Torna allo Screener"):
            st.session_state.screener_selected = None
            st.rerun()
        page_title(f"⌨️  Analisi Dettagliata — {target}")

        # --- yfinance DEEP DATA ---
        with st.spinner(f"Download dati storici profondi per {target}..."):
            deep = get_deep_ticker_data(target)

        inf  = deep.get("info", {})
        hist = deep.get("history_10y", pd.DataFrame())

        # Header
        cname = inf.get('longName') or inf.get('shortName') or target
        cprice = inf.get('currentPrice') or inf.get('regularMarketPrice') or inf.get('previousClose')
        st.markdown(f"""
            <div style='background:#070E1C;border:1px solid #0F2540;border-top:2px solid #2979FF;
                        border-radius:4px;padding:1.2rem 1.5rem;margin-bottom:1.2rem;'>
                <div style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#2979FF;letter-spacing:0.3em;'>DEEP ANALYSIS · yfinance</div>
                <div style='font-size:1.5rem;font-weight:700;color:#FFFFFF;font-family:IBM Plex Mono,monospace;'>{cname}</div>
                <div style='font-size:0.8rem;color:#5A7A9A;font-family:IBM Plex Mono,monospace;'>
                    <span class='ticker-badge'>{target}</span>  {inf.get('sector','')} · {inf.get('industry','')} · {inf.get('country','')}
                </div>
            </div>
        """, unsafe_allow_html=True)

        tab_p, tab_fin, tab_bs, tab_cf = st.tabs(["📈  PREZZO 10Y", "📊  INCOME STMT", "🏦  BALANCE SHEET", "💵  CASH FLOW"])

        with tab_p:
            if not hist.empty:
                hist.index = hist.index.tz_localize(None)
                fig_deep = go.Figure()
                fig_deep.add_trace(go.Scatter(
                    x=hist.index, y=hist['Close'], name="Close",
                    line=dict(color='#2979FF', width=2),
                    fill='tozeroy', fillcolor='rgba(41,121,255,0.05)',
                ))
                if 'Volume' in hist.columns:
                    fig_deep.add_trace(go.Bar(
                        x=hist.index, y=hist['Volume'], name="Volume",
                        yaxis="y2", marker_color='rgba(41,121,255,0.2)', showlegend=False,
                    ))
                fig_deep.update_layout(
                    **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                    yaxis2=dict(overlaying='y', side='right', showgrid=False, color='#5A7A9A'),
                    title=f"{cname} — 10 anni di storia", height=500,
                )
                st.plotly_chart(fig_deep, use_container_width=True)

                # Statistiche prezzo
                pc1, pc2, pc3, pc4, pc5 = st.columns(5)
                pc1.metric("Prezzo Attuale", f"{cprice:,.2f}" if cprice else "N/A")
                pc2.metric("Max 10Y", f"{hist['High'].max():,.2f}")
                pc3.metric("Min 10Y", f"{hist['Low'].min():,.2f}")
                ret_10y = ((hist['Close'].iloc[-1]/hist['Close'].iloc[0])-1)*100
                pc4.metric("Rendimento 10Y", f"{ret_10y:+.1f}%")
                vol_10y = hist['Close'].pct_change().dropna().std() * (252**0.5) * 100
                pc5.metric("Vol. Storica", f"{vol_10y:.1f}%")
            else:
                st.info("Dati storici non disponibili.")

        with tab_fin:
            fin_df = deep.get("financials", pd.DataFrame())
            if not fin_df.empty:
                st.markdown("**Income Statement — Pluriennale (yfinance)**")
                st.dataframe(fin_df.fillna("N/A"), use_container_width=True)
                # Chart Revenue + Net Income
                key_rows = {"Total Revenue": "#2979FF", "Net Income": "#00E676",
                            "Gross Profit": "#FF9100", "Operating Income": "#AA00FF"}
                fig_fin = go.Figure()
                for row, color in key_rows.items():
                    if row in fin_df.index:
                        s = fin_df.loc[row].apply(pd.to_numeric, errors='coerce').dropna() / 1e9
                        if not s.empty:
                            fig_fin.add_trace(go.Bar(
                                x=[str(d)[:10] for d in s.index], y=s.values,
                                name=row, marker_color=color, opacity=0.8,
                            ))
                if fig_fin.data:
                    fig_fin.update_layout(**PLOTLY_LAYOUT, title="Income Statement (B$)",
                                          yaxis_title="B$", barmode="group", height=400)
                    st.plotly_chart(fig_fin, use_container_width=True)
            else:
                st.info("Income statement non disponibile.")
                qfin = deep.get("q_financials", pd.DataFrame())
                if not qfin.empty:
                    st.markdown("**Dati Trimestrali**")
                    st.dataframe(qfin.fillna("N/A"), use_container_width=True)

        with tab_bs:
            bs_df = deep.get("balance_sheet", pd.DataFrame())
            if not bs_df.empty:
                st.markdown("**Balance Sheet — Pluriennale**")
                st.dataframe(bs_df.fillna("N/A"), use_container_width=True)
                # Chart Assets / Liabilities
                fig_bs = go.Figure()
                for row, color in [("Total Assets", "#2979FF"),
                                    ("Total Liabilities Net Minority Interest", "#FF1744"),
                                    ("Stockholders Equity", "#00E676")]:
                    if row in bs_df.index:
                        s = bs_df.loc[row].apply(pd.to_numeric, errors='coerce').dropna() / 1e9
                        if not s.empty:
                            fig_bs.add_trace(go.Bar(
                                x=[str(d)[:10] for d in s.index], y=s.values,
                                name=row.replace("Net Minority Interest",""), marker_color=color, opacity=0.8,
                            ))
                if fig_bs.data:
                    fig_bs.update_layout(**PLOTLY_LAYOUT, title="Balance Sheet (B$)",
                                         yaxis_title="B$", barmode="group", height=400)
                    st.plotly_chart(fig_bs, use_container_width=True)
            else:
                st.info("Balance sheet non disponibile.")

        with tab_cf:
            cf_df = deep.get("cashflow", pd.DataFrame())
            if not cf_df.empty:
                st.markdown("**Cash Flow Statement — Pluriennale**")
                st.dataframe(cf_df.fillna("N/A"), use_container_width=True)
                fig_cf = go.Figure()
                for row, color in [("Operating Cash Flow", "#2979FF"),
                                    ("Free Cash Flow", "#00E676"),
                                    ("Capital Expenditure", "#FF1744")]:
                    if row in cf_df.index:
                        s = cf_df.loc[row].apply(pd.to_numeric, errors='coerce').dropna() / 1e9
                        if not s.empty:
                            fig_cf.add_trace(go.Bar(
                                x=[str(d)[:10] for d in s.index], y=s.values,
                                name=row, marker_color=color, opacity=0.8,
                            ))
                if fig_cf.data:
                    fig_cf.update_layout(**PLOTLY_LAYOUT, title="Cash Flow (B$)",
                                         yaxis_title="B$", barmode="group", height=400)
                    st.plotly_chart(fig_cf, use_container_width=True)
            else:
                st.info("Cash flow statement non disponibile.")

        st.markdown("---")
        show_bloomberg_insights(target, peers_key=f"screener_{target}")

    else:
        page_title("🔍  Stock Screener", "Finviz Screener + yfinance Deep Analysis")

        tab_fv, tab_yf = st.tabs(["📡  FINVIZ SCREENER", "🔧  SCREENER yfinance"])

        # ------------------------------------------
        # Tab 1: FINVIZ
        # ------------------------------------------
        with tab_fv:
            section_header("Finviz Screener — URL Import")
            st.markdown("""
                <div class='terminal-card'>
                    <div class='terminal-card-header'>Come usare</div>
                    <div style='font-size:0.82rem;color:#C8D8E8;line-height:1.6;'>
                        1. Vai su <a href='https://finviz.com/screener.ashx' target='_blank' style='color:#2979FF;'>finviz.com/screener.ashx</a>
                        e imposta i tuoi filtri.<br>
                        2. Copia l'URL dalla barra del browser.<br>
                        3. Incollalo qui sotto e clicca "Carica Screener".<br><br>
                        <b>Oppure usa un preset precaricato:</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            preset_col1, preset_col2, preset_col3, preset_col4, preset_col5 = st.columns(5)
            load_preset = None
            with preset_col1:
                if st.button("🟢 Top Gainers",    use_container_width=True): load_preset = "top_gainers"
            with preset_col2:
                if st.button("🔴 Top Losers",     use_container_width=True): load_preset = "top_losers"
            with preset_col3:
                if st.button("📊 High Volume",    use_container_width=True): load_preset = "high_volume"
            with preset_col4:
                if st.button("📉 Oversold (RSI)", use_container_width=True): load_preset = "oversold"
            with preset_col5:
                if st.button("📈 Overbought",     use_container_width=True): load_preset = "overbought"

            if load_preset:
                with st.spinner(f"Caricamento preset Finviz '{load_preset}' (cache 15 min)..."):
                    df_preset = fetch_finviz_preset(load_preset)
                    if not df_preset.empty and "Error" not in df_preset.columns:
                        st.session_state.finviz_df = df_preset
                        st.success(f"✅ {len(df_preset)} risultati caricati.")
                    else:
                        st.warning("Finviz potrebbe bloccare richieste senza browser. Prova con un URL custom o usa lo screener yfinance.")

            st.markdown("---")
            fv_url = st.text_input(
                "URL Finviz Screener (opzionale)",
                placeholder="https://finviz.com/screener.ashx?v=111&f=cap_largeover,fa_pe_u20&ar=10",
                key="finviz_url_input",
            )
            if st.button("📡  Carica da URL Finviz", use_container_width=True) and fv_url.strip():
                with st.spinner("Caricamento da Finviz (cache 15 min)..."):
                    df_fv = fetch_finviz_screener(fv_url.strip())
                    if not df_fv.empty and "Error" not in df_fv.columns:
                        st.session_state.finviz_df = df_fv
                        st.success(f"✅ {len(df_fv)} risultati caricati da Finviz.")
                    else:
                        err = df_fv.get("Error", ["Errore sconosciuto."])[0] if "Error" in df_fv.columns else "Risposta non valida"
                        st.error(f"Errore Finviz: {err}")

            # Mostra tabella Finviz
            if st.session_state.finviz_df is not None and not st.session_state.finviz_df.empty:
                df_show = st.session_state.finviz_df
                st.markdown(f"#### Risultati Finviz ({len(df_show)} righe)")
                st.dataframe(df_show, use_container_width=True, height=350)

                # Selezione ticker da menu a tendina
                st.markdown("---")
                section_header("Analisi Dettagliata — seleziona un ticker")

                ticker_col = None
                for c in ["Ticker", "ticker", "Symbol", "symbol"]:
                    if c in df_show.columns:
                        ticker_col = c
                        break

                if ticker_col:
                    tickers_available = df_show[ticker_col].dropna().astype(str).tolist()
                    selected_fv = st.selectbox(
                        "Seleziona ticker dalla lista Finviz",
                        tickers_available,
                        key="finviz_select",
                    )
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🔍  Apri Analisi Bloomberg Insights", use_container_width=True):
                            st.session_state.screener_selected = selected_fv.strip().upper()
                            st.session_state.finviz_selected   = selected_fv.strip().upper()
                            st.rerun()
                    with col_b:
                        if st.button("📊  Carica Dati yfinance Deep", use_container_width=True):
                            st.session_state.finviz_selected = selected_fv.strip().upper()

                    # Mostra deep data inline se selezionato
                    if st.session_state.finviz_selected and not st.session_state.screener_selected:
                        tkr = st.session_state.finviz_selected
                        with st.spinner(f"Download dati storici profondi per {tkr} (yfinance)..."):
                            deep = get_deep_ticker_data(tkr)
                        hist_d = deep.get("history_1y", pd.DataFrame())
                        if not hist_d.empty:
                            hist_d.index = hist_d.index.tz_localize(None)
                            fig_fv = go.Figure()
                            fig_fv.add_trace(go.Candlestick(
                                x=hist_d.index,
                                open=hist_d['Open'], high=hist_d['High'],
                                low=hist_d['Low'],   close=hist_d['Close'],
                                name=tkr,
                                increasing=dict(line=dict(color='#00E676'), fillcolor='rgba(0,230,118,0.3)'),
                                decreasing=dict(line=dict(color='#FF1744'), fillcolor='rgba(255,23,68,0.3)'),
                            ))
                            fig_fv.update_layout(
                                **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                                title=f"{tkr} — Candlestick 1 Anno (yfinance Deep)", height=420,
                            )
                            st.plotly_chart(fig_fv, use_container_width=True)

                        fin_d = deep.get("financials", pd.DataFrame())
                        if not fin_d.empty:
                            section_header(f"Bilanci {tkr} — yfinance")
                            st.dataframe(fin_d.fillna("N/A"), use_container_width=True)
                else:
                    st.info("Colonna 'Ticker' non trovata nella risposta Finviz. Controlla il formato dei dati.")

        # ------------------------------------------
        # Tab 2: SCREENER yfinance (originale)
        # ------------------------------------------
        with tab_yf:
            section_header("Screener yfinance — Filtri Fondamentali")

            with st.spinner("Caricamento universo ticker..."):
                try:
                    tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
                    sp500  = tables[0]['Symbol'].str.replace('.', '-', regex=False).tolist()
                except Exception:
                    sp500 = []
                europe_tickers = [
                    "MC.PA","TTE.PA","SAN.PA","BNP.PA","AXA.PA","OR.PA","AIR.PA","SAP.DE","BMW.DE",
                    "SIE.DE","BAYN.DE","ASML.AS","ENI.MI","ENEL.MI","UCG.MI","ISP.MI","RACE.MI",
                    "STLAM.MI","ATL.MI","NESN.SW","ROG.SW","NOVN.SW","HSBA.L","BP.L","SHEL.L",
                    "AZN.L","GSK.L","INDITEX.MC","SAN.MC","BBVA.MC","REP.MC",
                ]
                UNIVERSE = list(set(sp500 + europe_tickers))
                st.caption(f"Universo: {len(UNIVERSE)} ticker (S&P 500 + Europa/Italia)")

            c1, c2, c3 = st.columns(3)
            with c1:
                pe_max     = st.slider("P/E massimo",               0, 200, 50, key="yf_pe")
                pb_max     = st.slider("P/B massimo",               0,  30, 10, key="yf_pb")
            with c2:
                cap_min    = st.slider("Market Cap min (B$)",       0, 500, 10, key="yf_cap")
                margin_min = st.slider("Margine Operativo min (%)", -50, 60,  5, key="yf_margin")
            with c3:
                roic_min   = st.slider("ROE min (%)",              -20,  60,  5, key="yf_roe")
                sector_filter = st.selectbox("Settore", [
                    "Tutti","Technology","Healthcare","Financials","Industrials",
                    "Consumer Defensive","Consumer Cyclical","Energy",
                    "Communication Services","Utilities","Real Estate","Basic Materials"
                ], key="yf_sector")

            max_scan_yf = st.selectbox("Ticker da scansionare",
                                       ["300 (veloce)", "600 (medio)", "Tutti"],
                                       key="yf_maxscan")
            run_yf = st.button("▶  ESEGUI SCREENING", use_container_width=True, key="yf_run")

            if run_yf:
                import random
                if max_scan_yf.startswith("300"):
                    scan_list = random.sample(UNIVERSE, min(300, len(UNIVERSE)))
                elif max_scan_yf.startswith("600"):
                    scan_list = random.sample(UNIVERSE, min(600, len(UNIVERSE)))
                else:
                    scan_list = UNIVERSE

                results = []; progress = st.progress(0); status = st.empty()
                for i, tkr in enumerate(scan_list):
                    progress.progress((i+1)/len(scan_list))
                    status.markdown(f"<span style='font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:#5A7A9A;'>Analisi: {tkr} ({i+1}/{len(scan_list)})</span>",
                                   unsafe_allow_html=True)
                    try:
                        info = get_ticker_info(tkr)
                        if not info: continue
                        pe      = info.get('forwardPE') or info.get('trailingPE')
                        pb      = info.get('priceToBook')
                        mcap    = info.get('marketCap')
                        op_mg   = info.get('operatingMargins')
                        roe     = info.get('returnOnEquity')
                        sec     = info.get('sector', '')
                        price   = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
                        if sector_filter != "Tutti" and sec != sector_filter: continue
                        if pe     is not None and pe > pe_max:               continue
                        if pb     is not None and pb > pb_max:               continue
                        if mcap   is not None and mcap/1e9 < cap_min:        continue
                        if op_mg  is not None and op_mg*100 < margin_min:    continue
                        if roe    is not None and roe*100 < roic_min:        continue
                        results.append({
                            "Ticker":    tkr,
                            "Nome":      info.get('shortName', tkr),
                            "Settore":   sec,
                            "Prezzo":    f"{price:.2f}"          if price    else "N/A",
                            "P/E":       f"{pe:.1f}"             if pe       else "N/A",
                            "P/B":       f"{pb:.1f}"             if pb       else "N/A",
                            "Op.Mgn %":  f"{op_mg*100:.1f}"      if op_mg   else "N/A",
                            "ROE %":     f"{roe*100:.1f}"        if roe     else "N/A",
                            "Cap (B$)":  f"{mcap/1e9:.1f}"       if mcap    else "N/A",
                        })
                    except Exception: continue
                progress.empty(); status.empty()
                st.session_state.screener_results = results if results else []

            if st.session_state.screener_results:
                results = st.session_state.screener_results
                st.success(f"✅  {len(results)} aziende trovate")
                st.dataframe(pd.DataFrame(results).set_index("Ticker"), use_container_width=True)
                sel = st.selectbox("Seleziona azienda",
                                   [f"{r['Ticker']} — {r['Nome']}" for r in results],
                                   key="yf_screener_select")
                if st.button("🔎  Apri Analisi Dettagliata", use_container_width=True, key="yf_open"):
                    st.session_state.screener_selected = sel.split(" — ")[0].strip()
                    st.rerun()


# =========================================================
# 6. BLOOMBERG INSIGHTS
# =========================================================
elif choice == "Bloomberg Insights":
    page_title("⌨️  Company Terminal Insights", "Analisi fondamentale · Notizie · Supply Chain · Peer Comparison")
    target = st.text_input(
        "Ticker principale", "NVDA",
        placeholder="Es: AAPL, MSFT, MC.PA, ENI.MI ..."
    ).strip().upper()
    if target:
        show_bloomberg_insights(target, peers_key=f"bloomberg_{target}")

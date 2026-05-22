import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import random
import time

st.set_page_config(page_title="Navy Terminal Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

    html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        background-color: #050D1A !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    [data-testid="stSidebar"] {
        background-color: #030A14 !important;
        border-right: 1px solid #0E2440 !important;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #071220 !important;
        border: 1px solid #0E2440 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stHeader"] {
        background-color: #030A14 !important;
        border-bottom: 1px solid #0E2440 !important;
    }
    h1,h2,h3,h4,h5,h6 {
        color: #FFFFFF !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
    }
    p,span,li,div,label,.stMarkdown {
        color: #D8E4F0 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    .page-title {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.4rem;
        font-weight: 600;
        color: #FFFFFF !important;
        letter-spacing: 0.08em;
        border-left: 3px solid #3B8EF0;
        padding-left: 1rem;
        margin-bottom: 0.4rem;
    }
    .page-subtitle {
        color: #7A9DBE !important;
        font-size: 0.82rem;
        margin-bottom: 1.4rem;
        padding-left: 1.3rem;
        letter-spacing: 0.04em;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #7A9DBE !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #071A30 0%, #0A1E38 100%) !important;
        border: 1px solid #0E2440 !important;
        border-top: 1px solid #163860 !important;
        border-radius: 4px !important;
        padding: 0.9rem 1rem !important;
    }
    .stTextInput label, .stSelectbox label, .stMultiSelect label,
    .stSlider label, .stNumberInput label, .stRadio label, label[data-testid] {
        color: #7A9DBE !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #3B8EF0 !important;
        border-color: #3B8EF0 !important;
    }
    .stSlider [data-baseweb="slider"] div[class*="Track"] div:first-child {
        background-color: #3B8EF0 !important;
    }
    .stSlider span { color: #7A9DBE !important; }
    .stNumberInput input {
        background-color: #071220 !important;
        color: #FFFFFF !important;
        border: 1px solid #0E2440 !important;
        border-radius: 3px !important;
    }
    .stNumberInput button {
        background-color: #0E2440 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    input[type="text"], textarea, .stTextInput input {
        background-color: #071220 !important;
        color: #FFFFFF !important;
        border: 1px solid #0E2440 !important;
        border-radius: 3px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.88rem !important;
    }
    input[type="text"]:focus, textarea:focus {
        border-color: #3B8EF0 !important;
        box-shadow: 0 0 0 1px rgba(59,142,240,0.3) !important;
    }
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #071220 !important;
        border: 1px solid #0E2440 !important;
        color: #FFFFFF !important;
    }
    [data-baseweb="popover"] { background-color: #071220 !important; border: 1px solid #0E2440 !important; }
    [data-baseweb="menu"] { background-color: #071220 !important; border: 1px solid #0E2440 !important; }
    [data-baseweb="option"] {
        background-color: #071220 !important;
        color: #D8E4F0 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.85rem !important;
    }
    [data-baseweb="option"]:hover { background-color: #0E2440 !important; color: #FFFFFF !important; }
    [data-baseweb="option"][aria-selected="true"] {
        background-color: #163860 !important;
        color: #3B8EF0 !important;
        font-weight: 600 !important;
    }
    li[role="option"] { background-color: #071220 !important; color: #D8E4F0 !important; }
    li[role="option"]:hover { background-color: #0E2440 !important; color: #FFFFFF !important; }
    .stRadio > div > label { color: #D8E4F0 !important; text-transform: none !important; font-size: 0.88rem !important; }
    .dataframe, table {
        background-color: #071220 !important;
        color: #FFFFFF !important;
        border-collapse: collapse !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.8rem !important;
    }
    thead tr th {
        color: #7A9DBE !important;
        background-color: #040F1E !important;
        border-bottom: 1px solid #0E2440 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 0.55rem 0.9rem !important;
        font-size: 0.7rem !important;
    }
    tbody tr td {
        color: #D8E4F0 !important;
        border-bottom: 1px solid #0A1A2E !important;
        padding: 0.45rem 0.9rem !important;
    }
    tbody tr:hover td { background-color: #0E2440 !important; }
    hr { border-color: #0E2440 !important; border-style: solid !important; opacity: 0.6; }
    .stAlert,[data-testid="stNotification"] {
        background-color: #071220 !important;
        border: 1px solid #0E2440 !important;
        color: #D8E4F0 !important;
    }
    .stButton > button {
        background-color: #071A30 !important;
        color: #D8E4F0 !important;
        border: 1px solid #163860 !important;
        border-radius: 3px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.06em !important;
        transition: all 0.15s ease;
        padding: 0.4rem 1rem !important;
    }
    .stButton > button:hover {
        background-color: #3B8EF0 !important;
        color: #FFFFFF !important;
        border-color: #3B8EF0 !important;
    }
    .nav-btn-active > button {
        background-color: #163860 !important;
        border-left: 2px solid #3B8EF0 !important;
        color: #FFFFFF !important;
    }
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #030A14; }
    ::-webkit-scrollbar-thumb { background: #0E2440; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: #3B8EF0; }
    .section-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        color: #3B8EF0;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid #0E2440;
        padding-bottom: 0.4rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #071A30 0%, #0A1E38 100%);
        border: 1px solid #0E2440;
        border-top: 1px solid #163860;
        border-radius: 4px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
    }
    .kpi-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: #7A9DBE;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.25rem;
    }
    .kpi-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.3rem;
        font-weight: 600;
        color: #FFFFFF;
    }
    .kpi-delta-pos { color: #2ECC71 !important; font-size: 0.8rem; }
    .kpi-delta-neg { color: #E74C3C !important; font-size: 0.8rem; }
    .tag-blue {
        display: inline-block;
        background: rgba(59,142,240,0.15);
        border: 1px solid rgba(59,142,240,0.4);
        color: #3B8EF0 !important;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        padding: 2px 8px;
        border-radius: 2px;
        letter-spacing: 0.08em;
    }
    .terminal-box {
        background: #030A14;
        border: 1px solid #0E2440;
        border-radius: 4px;
        padding: 1rem 1.2rem;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.82rem;
        color: #D8E4F0;
        margin-bottom: 1rem;
    }
    .stProgress > div > div { background-color: #3B8EF0 !important; }
    </style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 1.2rem 0 1rem 0;'>
            <div style='font-family: IBM Plex Mono, monospace; font-size:1.5rem; font-weight:700;
                        color:#FFFFFF; letter-spacing:0.2em;'>⚓ NAVY</div>
            <div style='font-family: IBM Plex Mono, monospace; font-size:0.6rem; color:#3B8EF0;
                        letter-spacing:0.4em; margin-top:3px;'>TERMINAL PRO</div>
            <div style='height:1px; background: linear-gradient(90deg, transparent, #3B8EF0, transparent);
                        margin-top:1rem;'></div>
        </div>
    """, unsafe_allow_html=True)

    menu_items = [
        ("🌍", "Global Overview"),
        ("🧮", "Analisi DCF"),
        ("📊", "Multi-Compare"),
        ("🧪", "Portfolio Backtest"),
        ("🔍", "Stock Screener"),
        ("⌨️", "Bloomberg Insights"),
    ]

    for k in ["page","screener_selected","screener_results","bi_ticker","bi_peers"]:
        if k not in st.session_state:
            st.session_state[k] = {"page":"Global Overview","screener_selected":None,
                                    "screener_results":None,"bi_ticker":"NVDA","bi_peers":"AMD, INTC, AVGO"}[k]

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    for icon, label in menu_items:
        active = st.session_state.page == label
        btn_style = "nav-btn-active" if active else ""
        with st.container():
            if active:
                st.markdown(f"<div class='nav-btn-active'>", unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                st.session_state.page = label
                st.rerun()
            if active:
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
        <div style='position:absolute; bottom:1.5rem; left:0; right:0; text-align:center;'>
            <div style='height:1px; background: linear-gradient(90deg, transparent, #0E2440, transparent);
                        margin-bottom:0.8rem;'></div>
            <div style='font-family: IBM Plex Mono, monospace; font-size:0.55rem; color:#1E3A5F;
                        letter-spacing:0.15em; line-height:1.8;'>
                LIVE MARKET DATA<br>POWERED BY YFINANCE + FMP
            </div>
        </div>
    """, unsafe_allow_html=True)

choice = st.session_state.page


# =========================================================
# UTILITY / LAYOUT
# =========================================================
def page_title(text, subtitle=""):
    st.markdown(f"<div class='page-title'>{text}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='page-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

def section_header(text):
    st.markdown(f"<div class='section-header'>{text}</div>", unsafe_allow_html=True)

def kpi_card(label, value, delta=None, delta_positive=True):
    delta_html = ""
    if delta is not None:
        cls = "kpi-delta-pos" if delta_positive else "kpi-delta-neg"
        delta_html = f"<div class='{cls}'>{delta}</div>"
    return f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value'>{value}</div>
        {delta_html}
    </div>"""

def interactive_xaxis():
    return dict(
        gridcolor='#0A1A2E', showgrid=True, zeroline=False,
        rangeslider=dict(visible=True, bgcolor="#030A14", thickness=0.04),
        rangeselector=dict(
            bgcolor="#071220", activecolor="#3B8EF0", bordercolor="#0E2440",
            font=dict(color="#FFFFFF", size=10),
            buttons=[
                dict(count=1,  label="1M", step="month", stepmode="backward"),
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
    paper_bgcolor='rgba(3,10,20,0)',
    plot_bgcolor='rgba(7,18,32,0.6)',
    font=dict(color="#D8E4F0", family="IBM Plex Mono, monospace", size=10),
    legend=dict(bgcolor='rgba(3,10,20,0.9)', bordercolor='#0E2440', borderwidth=1,
                font=dict(size=10)),
    xaxis=dict(gridcolor='#0A1A2E', showgrid=True, zeroline=False),
    yaxis=dict(gridcolor='#0A1A2E', showgrid=True, zeroline=False),
    margin=dict(l=50, r=20, t=45, b=40),
    hovermode="x unified",
    dragmode="zoom",
)

COLORS = ["#3B8EF0","#2ECC71","#F39C12","#E74C3C","#9B59B6","#1ABC9C",
          "#E67E22","#3498DB","#EC407A","#AB47BC","#00BCD4","#8BC34A"]


# =========================================================
# CACHING — CORE
# =========================================================
@st.cache_data(ttl=300, show_spinner=False)
def get_ticker_info(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info or len(info) <= 3:
            time.sleep(0.3)
            info = t.info
        if not info or len(info) <= 3:
            return {}
        has_price = any(info.get(k) for k in ['regularMarketPrice','currentPrice','previousClose'])
        has_name  = any(info.get(k) for k in ['longName','shortName'])
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
        close = raw['Close']
        if isinstance(close, pd.DataFrame):
            return close.iloc[:, 0].rename(ticker)
        return close.squeeze().rename(ticker)
    except Exception:
        return pd.Series(dtype=float, name=ticker)

@st.cache_data(ttl=1800, show_spinner=False)
def get_large_universe():
    """
    Multi-source universe: Russell 3000 + S&P500 + NASDAQ + Europa/Italia.
    Fallback a lista curata se le fonti web falliscono.
    """
    tickers = set()

    # 1. iShares Russell 3000 CSV
    try:
        url = "https://www.ishares.com/us/products/239714/ishares-russell-3000-etf/1467271812596.ajax?fileType=csv&fileName=IWV_holdings&dataType=fund"
        df = pd.read_csv(url, skiprows=9, on_bad_lines='skip')
        col = next((c for c in df.columns if 'ticker' in c.lower()), None)
        if col:
            vals = df[col].dropna().astype(str).str.strip()
            tickers.update(v for v in vals if v.isalpha() and 1 <= len(v) <= 5)
    except Exception:
        pass

    # 2. S&P 500 da Wikipedia
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        syms = tables[0]['Symbol'].str.replace('.', '-', regex=False).tolist()
        tickers.update(syms)
    except Exception:
        pass

    # 3. NASDAQ-listed FTP
    try:
        url2 = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        df2 = pd.read_csv(url2, sep="|", on_bad_lines='skip')
        if 'Symbol' in df2.columns:
            vals2 = df2['Symbol'].dropna().astype(str).str.strip()
            tickers.update(v for v in vals2 if v.isalpha() and 1 <= len(v) <= 5)
    except Exception:
        pass

    # 4. Grossa lista curata (fallback / integrazione)
    curated_us = [
        "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","JPM","V",
        "UNH","XOM","JNJ","PG","MA","HD","ABBV","MRK","CVX","PEP","KO","LIN",
        "TMO","DHR","NEE","AMD","INTC","QCOM","TXN","AMAT","LRCX","MU","PANW",
        "ADBE","CRM","NOW","SNOW","PLTR","COIN","RBLX","UBER","NFLX","DIS",
        "CMCSA","BAC","WFC","GS","MS","BLK","SCHW","COST","WMT","TGT","NKE",
        "SBUX","MCD","ABNB","BKNG","BA","CAT","DE","GE","HON","RTX","LMT",
        "F","GM","RIVN","SQ","PYPL","SHOP","SOFI","AFRM","DKNG","GME",
        "SMCI","ARM","ASML","TSM","ENPH","FSLR","CEG","TLN","CCJ","WDAY",
        "ZM","DOCU","BOX","ORCL","IBM","CSCO","DELL","HPQ","WDC","STX",
        "MRNA","PFE","BMY","GILD","REGN","VRTX","BIIB","ILMN","IQV",
        "CB","PGR","TRV","AIG","MET","PRU","AFL","ALL","CINF",
        "AMT","PLD","EQIX","CCI","PSA","SPG","O","WELL","DLR",
        "XLE","XLK","XLF","XLV","XLI","XLP","XLU","XLB","XLRE",
        "SPY","QQQ","IWM","VOO","VTI","VEA","VWO","GLD","SLV","USO",
        "TLT","IEF","SHY","AGG","BND","HYG","LQD","TIPS",
    ]
    curated_eu = [
        "MC.PA","TTE.PA","SAN.PA","BNP.PA","AXA.PA","OR.PA","AIR.PA","SU.PA","DG.PA",
        "SAP.DE","BMW.DE","SIE.DE","BAYN.DE","MBG.DE","ALV.DE","BAS.DE","VOW3.DE","DTE.DE",
        "ASML.AS","PHIA.AS","HEIA.AS","INGA.AS","UNA.AS",
        "ENI.MI","ENEL.MI","UCG.MI","ISP.MI","STLAM.MI","RACE.MI","ATL.MI",
        "TIT.MI","MB.MI","BMED.MI","PRY.MI","REC.MI","PIRC.MI","BPER.MI",
        "NESN.SW","ROG.SW","NOVN.SW","ABB.SW","UBS.SW","ZURN.SW","CFR.SW",
        "HSBA.L","BP.L","SHEL.L","AZN.L","GSK.L","ULVR.L","RIO.L","LGEN.L","BARC.L",
        "INDITEX.MC","SAN.MC","BBVA.MC","REP.MC","TEF.MC",
        "NOVO-B.CO","ORSTED.CO","VWCE.DE","EXS1.DE","IS3N.DE",
    ]
    tickers.update(curated_us)
    tickers.update(curated_eu)

    return sorted(list(tickers))

@st.cache_data(ttl=1800, show_spinner=False)
def get_sp500_tickers():
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        return tables[0]['Symbol'].str.replace('.', '-', regex=False).tolist()
    except Exception:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def get_top_movers(n=5):
    watchlist = [
        "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","JPM","V",
        "UNH","XOM","JNJ","PG","HD","ABBV","MRK","CVX","AMD","INTC","QCOM",
        "PANW","ADBE","CRM","NOW","SNOW","PLTR","COIN","NFLX","DIS","BAC",
        "WFC","GS","COST","WMT","NKE","SBUX","MCD","BA","CAT","GE","HON",
        "F","GM","SQ","PYPL","SHOP","SOFI","SMCI","ARM","ENPH","FSLR",
        "MRNA","PFE","BMY","GILD","REGN","ORCL","DELL","ENI.MI","ENEL.MI",
        "RACE.MI","MC.PA","TTE.PA","SAP.DE","ASML.AS",
    ]
    results = []
    for tkr in watchlist:
        try:
            d = yf.Ticker(tkr).history(period="2d")
            if len(d) >= 2:
                c, p = float(d['Close'].iloc[-1]), float(d['Close'].iloc[-2])
                results.append({"ticker": tkr, "price": c, "pct": ((c-p)/p)*100})
        except Exception:
            continue
    results.sort(key=lambda x: x["pct"], reverse=True)
    return results[:n], sorted(results, key=lambda x: x["pct"])[:n]


# =========================================================
# FONDAMENTALI STORICI
# =========================================================
@st.cache_data(ttl=600, show_spinner=False)
def get_historical_pe(ticker, years_back=10):
    try:
        t = yf.Ticker(ticker)
        price_hist = t.history(period=f"{years_back}y")["Close"]
        if price_hist.empty: return pd.Series(dtype=float, name=ticker)
        price_hist.index = price_hist.index.tz_localize(None)
        eps_series = None
        for attr in ["income_stmt","financials"]:
            try:
                df = getattr(t, attr)
                if df is None or df.empty: continue
                for row in ["Basic EPS","Diluted EPS","EPS"]:
                    if row in df.index:
                        s = df.loc[row].copy(); s.index = pd.to_datetime(s.index)
                        eps_series = s.sort_index(); break
                if eps_series is not None: break
            except: continue
        eps_q = None
        for attr in ["quarterly_income_stmt","quarterly_financials"]:
            try:
                df = getattr(t, attr)
                if df is None or df.empty: continue
                for row in ["Basic EPS","Diluted EPS","EPS"]:
                    if row in df.index:
                        s = df.loc[row].copy(); s.index = pd.to_datetime(s.index)
                        eps_q = s.sort_index(); break
                if eps_q is not None: break
            except: continue
        if eps_q is not None and not eps_q.empty:
            if eps_series is not None and not eps_series.empty:
                combined = pd.concat([eps_series/4, eps_q])
                combined = combined[~combined.index.duplicated(keep='last')].sort_index()
            else:
                combined = eps_q
            eps_ttm = combined.rolling(4, min_periods=1).sum()
        elif eps_series is not None and not eps_series.empty:
            eps_ttm = eps_series
        else:
            eps_snap = t.info.get("trailingEps")
            if eps_snap and eps_snap > 0:
                return (price_hist / eps_snap).rename(ticker)
            return pd.Series(dtype=float, name=ticker)
        eps_daily = eps_ttm.reindex(eps_ttm.index.union(price_hist.index)).ffill().reindex(price_hist.index)
        pe = (price_hist / eps_daily).replace([np.inf,-np.inf], np.nan)
        return pe[(pe>0)&(pe<500)].dropna().rename(ticker)
    except: return pd.Series(dtype=float, name=ticker)

@st.cache_data(ttl=600, show_spinner=False)
def get_historical_ps(ticker, years_back=10):
    try:
        t = yf.Ticker(ticker)
        price_hist = t.history(period=f"{years_back}y")["Close"]
        if price_hist.empty: return pd.Series(dtype=float, name=ticker)
        price_hist.index = price_hist.index.tz_localize(None)
        shares = t.info.get("sharesOutstanding") or t.info.get("impliedSharesOutstanding")
        if not shares: return pd.Series(dtype=float, name=ticker)
        rev_series = None
        for attr in ["financials","income_stmt"]:
            try:
                df = getattr(t, attr)
                if df is None or df.empty: continue
                for row in ["Total Revenue","Revenue","Net Revenue"]:
                    if row in df.index:
                        s = df.loc[row].copy(); s.index = pd.to_datetime(s.index)
                        rev_series = s.sort_index(); break
                if rev_series is not None: break
            except: continue
        rev_q = None
        for attr in ["quarterly_financials","quarterly_income_stmt"]:
            try:
                df = getattr(t, attr)
                if df is None or df.empty: continue
                for row in ["Total Revenue","Revenue","Net Revenue"]:
                    if row in df.index:
                        s = df.loc[row].copy(); s.index = pd.to_datetime(s.index)
                        rev_q = s.sort_index(); break
                if rev_q is not None: break
            except: continue
        if rev_q is not None and not rev_q.empty:
            combined = pd.concat([rev_series/4 if rev_series is not None else pd.Series(dtype=float), rev_q])
            combined = combined[~combined.index.duplicated(keep='last')].sort_index()
            rev_ttm = combined.rolling(4, min_periods=1).sum()
        elif rev_series is not None and not rev_series.empty:
            rev_ttm = rev_series
        else:
            rev_snap = t.info.get("totalRevenue")
            if rev_snap and rev_snap > 0:
                return ((price_hist * shares) / rev_snap).rename(ticker)
            return pd.Series(dtype=float, name=ticker)
        rev_daily = rev_ttm.reindex(rev_ttm.index.union(price_hist.index)).ffill().reindex(price_hist.index)
        ps = ((price_hist * shares) / rev_daily).replace([np.inf,-np.inf], np.nan)
        return ps[(ps>0)&(ps<200)].dropna().rename(ticker)
    except: return pd.Series(dtype=float, name=ticker)

@st.cache_data(ttl=600, show_spinner=False)
def get_historical_mktcap(ticker, years_back=10):
    try:
        t = yf.Ticker(ticker)
        ph = t.history(period=f"{years_back}y")["Close"]
        if ph.empty: return pd.Series(dtype=float, name=ticker)
        ph.index = ph.index.tz_localize(None)
        shares = t.info.get("sharesOutstanding") or t.info.get("impliedSharesOutstanding")
        if not shares: return pd.Series(dtype=float, name=ticker)
        return (ph * shares / 1e9).rename(ticker)
    except: return pd.Series(dtype=float, name=ticker)

@st.cache_data(ttl=600, show_spinner=False)
def get_quarterly_metric(ticker, metric_key):
    try:
        t = yf.Ticker(ticker)
        if metric_key == "EPS":
            for attr in ["quarterly_income_stmt","quarterly_financials","income_stmt","financials"]:
                try:
                    df = getattr(t, attr)
                    if df is None or df.empty: continue
                    for row in ["Basic EPS","Diluted EPS","EPS"]:
                        if row in df.index:
                            s = df.loc[row].copy(); s.index = pd.to_datetime(s.index)
                            return s.sort_index().rename(ticker)
                except: continue
            return pd.Series(dtype=float, name=ticker)
        elif metric_key == "Free Cash Flow":
            for attr in ["quarterly_cashflow","cashflow","quarterly_cash_flow","cash_flow"]:
                try:
                    df = getattr(t, attr)
                    if df is None or df.empty: continue
                    for row in ["Free Cash Flow","FreeCashFlow"]:
                        if row in df.index:
                            s = df.loc[row].copy(); s.index = pd.to_datetime(s.index)
                            return (s.sort_index()/1e9).rename(ticker)
                except: continue
            return pd.Series(dtype=float, name=ticker)
        else:
            row_map = {
                "Total Revenue":  ["Total Revenue","Revenue","TotalRevenue"],
                "Gross Profit":   ["Gross Profit","GrossProfit"],
                "Net Income":     ["Net Income","NetIncome","Net Income Common Stockholders"],
                "EBITDA":         ["EBITDA","Normalized EBITDA","Operating Income","EBIT"],
            }
            candidates = row_map.get(metric_key, [metric_key])
            for attr in ["quarterly_financials","quarterly_income_stmt","financials","income_stmt"]:
                try:
                    df = getattr(t, attr)
                    if df is None or df.empty: continue
                    for row in candidates:
                        if row in df.index:
                            s = df.loc[row].copy(); s.index = pd.to_datetime(s.index)
                            return (s.sort_index()/1e9).rename(ticker)
                except: continue
            return pd.Series(dtype=float, name=ticker)
    except: return pd.Series(dtype=float, name=ticker)


# =========================================================
# SUPPLY CHAIN MAP
# =========================================================
SUPPLY_CHAIN_MAP = {
    "Technology": {
        "suppliers": ["Taiwan Semiconductor (TSM)","Samsung Electronics","ASML (ASML.AS)",
                      "Applied Materials (AMAT)","Lam Research (LRCX)"],
        "customers": ["Apple (AAPL)","Microsoft (MSFT)","Meta (META)",
                      "Amazon AWS (AMZN)","Alphabet (GOOGL)"],
        "notes": "La supply chain tech è dominata dai foundry asiatici. ASML è monopolista de facto nella litografia EUV."
    },
    "Semiconductors": {
        "suppliers": ["ASML (ASML.AS)","Applied Materials (AMAT)","Air Products (APD)","Shin-Etsu Chemical"],
        "customers": ["Apple (AAPL)","Nvidia (NVDA)","AMD","Qualcomm (QCOM)","Data center hyperscalers"],
        "notes": "Capital-intensive con altissime barriere. Ciclo capex multi-anno con forte domanda AI."
    },
    "Communication Services": {
        "suppliers": ["Ericsson (ERIC)","Nokia (NOK)","Akamai (AKAM)","Infrastrutture cloud"],
        "customers": ["Advertiser B2B","Consumatori B2C","PMI globali"],
        "notes": "Ricavi prevalentemente da pubblicità digitale e abbonamenti. Alta leva operativa."
    },
    "Financial Services": {
        "suppliers": ["Bloomberg LP","Refinitiv/LSEG","Broadridge (BR)","Fiserv (FISV)"],
        "customers": ["Retail banking","Investitori istituzionali","Aziende corporate"],
        "notes": "Sensibile ai tassi d'interesse. Fintech sta erodendo margini nel retail."
    },
    "Healthcare": {
        "suppliers": ["Thermo Fisher (TMO)","Danaher (DHR)","Lonza Group","Wuxi Biologics"],
        "customers": ["Ospedali","Assicurazioni sanitarie","Governi","Distributori farmaceutici"],
        "notes": "Pipeline R&D lunga e costosa. I CDMO sono fornitori critici per biotech."
    },
    "Energy": {
        "suppliers": ["Halliburton (HAL)","Baker Hughes (BKR)","SLB","Caterpillar (CAT)"],
        "customers": ["Utility elettriche","Raffinerie","Industria chimica","Governi"],
        "notes": "Ciclico, fortemente legato al prezzo del petrolio e alle politiche energetiche."
    },
    "Industrials": {
        "suppliers": ["3M (MMM)","Honeywell (HON)","Parker Hannifin (PH)","Eaton (ETN)"],
        "customers": ["Aerospaziale","Automotive","Costruzioni","Difesa"],
        "notes": "Ampio spettro B2B; sensibile al ciclo economico e agli ordini governativi."
    },
    "Consumer Defensive": {
        "suppliers": ["Archer-Daniels (ADM)","Bunge (BG)","Packaging Corp (PKG)","IFF"],
        "customers": ["Grande distribuzione (WMT, COST)","Consumatori finali B2C"],
        "notes": "Settore anticiclico con pricing power nei brand premium."
    },
    "Consumer Cyclical": {
        "suppliers": ["Li & Fung","Produttori asiatici OEM","Fornitori materie prime"],
        "customers": ["Consumatori finali","E-commerce","Retail fisico"],
        "notes": "Fortemente correlato al ciclo del credito al consumo."
    },
    "Real Estate": {
        "suppliers": ["Costruttori","Gestori immobiliari","Property management"],
        "customers": ["Tenant retail","Tenant uffici","Residenziale"],
        "notes": "Sensibile ai tassi d'interesse. I REIT distribuiscono almeno il 90% degli utili."
    },
    "Utilities": {
        "suppliers": ["GE Vernova (GEV)","Siemens Energy","NextEra (NEE)","Fuel suppliers"],
        "customers": ["Residenziale","Industria","Data center (forte crescita AI)"],
        "notes": "Settore regolato. Domanda crescente da AI/data center è catalizzatore strutturale."
    },
    "Basic Materials": {
        "suppliers": ["Minatori di materie prime","Produttori chimici di base"],
        "customers": ["Manifatturiero","Costruzioni","Automotive","Farmaceutico"],
        "notes": "Altamente ciclico, dipendente da domanda cinese e prezzi delle commodity."
    },
}


# =========================================================
# BLOOMBERG INSIGHTS — funzione riutilizzabile
# =========================================================
def show_bloomberg_insights(target, peers_default="AMD, INTC, AVGO"):
    with st.spinner(f"Recupero dati per {target}..."):
        inf = get_ticker_info(target)
        if not inf:
            st.error(f"❌  Ticker **{target}** non trovato.")
            st.markdown("**Esempi:** USA: `AAPL` `MSFT` `NVDA` · Italia: `ENI.MI` `ENEL.MI` · Francia: `MC.PA`")
            return

        company_name  = inf.get('longName') or inf.get('shortName') or target
        current_price = inf.get('currentPrice') or inf.get('regularMarketPrice') or inf.get('previousClose')
        prev_close    = inf.get('previousClose') or current_price
        day_change    = ((current_price - prev_close) / prev_close * 100) if (current_price and prev_close and prev_close != 0) else None

    # Header box
    chg_color = "#2ECC71" if (day_change or 0) >= 0 else "#E74C3C"
    chg_html  = f"<span style='color:{chg_color}'>{day_change:+.2f}% oggi</span>" if day_change is not None else ""
    st.markdown(f"""
        <div style='background:linear-gradient(135deg,#071A30,#0A1E38);border:1px solid #0E2440;
                    border-top:2px solid #3B8EF0;border-radius:4px;padding:1.2rem 1.6rem;margin-bottom:1.2rem;'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                <div>
                    <div style='font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#3B8EF0;
                                letter-spacing:0.25em;margin-bottom:5px;'>EQUITY · {inf.get('exchange','N/A')} · {inf.get('currency','USD')}</div>
                    <div style='font-size:1.6rem;font-weight:700;color:#FFFFFF;line-height:1.2;'>{company_name}</div>
                    <div style='font-family:IBM Plex Mono,monospace;font-size:0.82rem;color:#7A9DBE;margin-top:4px;'>
                        {target} &nbsp;|&nbsp; {inf.get('sector','N/A')} &nbsp;|&nbsp; {inf.get('country','N/A')}
                    </div>
                </div>
                <div style='text-align:right;'>
                    <div style='font-family:IBM Plex Mono,monospace;font-size:2rem;font-weight:700;color:#FFFFFF;'>
                        {f"{current_price:,.2f}" if current_price else "N/A"}
                    </div>
                    <div style='font-size:0.85rem;margin-top:2px;'>{chg_html}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # KPI row
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.metric("P/E Fwd",    f"{inf['forwardPE']:.1f}"          if inf.get('forwardPE')        else "N/A")
    k2.metric("P/E Ttm",    f"{inf['trailingPE']:.1f}"         if inf.get('trailingPE')       else "N/A")
    k3.metric("EPS Fwd",    f"{inf['forwardEps']:.2f}"         if inf.get('forwardEps')       else "N/A")
    k4.metric("Beta",       f"{inf['beta']:.2f}"               if inf.get('beta')             else "N/A")
    k5.metric("Market Cap", f"${inf['marketCap']/1e9:.1f}B"    if inf.get('marketCap')        else "N/A")
    k6.metric("52W Range",  f"{inf.get('fiftyTwoWeekLow','?')} – {inf.get('fiftyTwoWeekHigh','?')}")

    st.markdown("---")

    # Description + news
    col_desc, col_news = st.columns([2,1])
    with col_desc:
        section_header("BUSINESS SUMMARY")
        st.write(inf.get('longBusinessSummary') or "Descrizione non disponibile.")

        section_header("FINANCIALS SNAPSHOT")
        fin1,fin2,fin3,fin4 = st.columns(4)
        fin1.metric("Revenue", f"${inf.get('totalRevenue',0)/1e9:.1f}B"  if inf.get('totalRevenue') else "N/A")
        fin2.metric("EBITDA",  f"${inf.get('ebitda',0)/1e9:.1f}B"        if inf.get('ebitda')       else "N/A")
        fin3.metric("FCF",     f"${inf.get('freeCashflow',0)/1e9:.1f}B"  if inf.get('freeCashflow') else "N/A")
        fin4.metric("Div Yield",f"{(inf.get('dividendYield') or 0)*100:.2f}%")

    with col_news:
        section_header("LATEST NEWS")
        yahoo_url = f"https://finance.yahoo.com/quote/{target}/news/"
        st.markdown(f"""
            <div style='background:#030A14;border:1px solid #0E2440;border-radius:4px;padding:0.9rem;margin-bottom:0.8rem;'>
                <div style='font-size:0.68rem;color:#3B8EF0;letter-spacing:0.18em;margin-bottom:6px;'>FONTE LIVE</div>
                <a href='{yahoo_url}' target='_blank'
                   style='display:inline-block;background:#071220;color:#3B8EF0;border:1px solid #163860;
                          border-radius:3px;padding:5px 12px;font-family:IBM Plex Mono,monospace;
                          font-size:0.75rem;text-decoration:none;'>📰 Yahoo Finance News →</a>
            </div>
        """, unsafe_allow_html=True)
        try:
            news_items = get_ticker_news(target)
            for n in (news_items or [])[:5]:
                title = n.get('title','')
                link  = n.get('link', yahoo_url)
                if title:
                    st.markdown(f"<div style='border-left:2px solid #0E2440;padding-left:8px;margin-bottom:8px;"
                                f"font-size:0.8rem;color:#D8E4F0;'><a href='{link}' target='_blank' "
                                f"style='color:#7A9DBE;text-decoration:none;'>{title}</a></div>",
                                unsafe_allow_html=True)
        except Exception:
            pass

    st.markdown("---")

    # Peer comparison — KEY FIX: uses dynamic peers_default based on the current ticker
    section_header("PEER ANALYSIS")
    peers_in = st.text_input(
        "Competitors (separati da virgola)",
        value=peers_default,
        key=f"peers_input_{target}_{int(time.time()*10) % 10000}"
    )
    p_list = [target] + [x.strip().upper() for x in peers_in.split(",") if x.strip()]

    with st.spinner("Caricamento peers..."):
        rows = []
        for p in p_list:
            try:
                pi = get_ticker_info(p)
                price_p = pi.get('currentPrice') or pi.get('regularMarketPrice') or pi.get('previousClose') or 0
                rows.append({
                    "Ticker":    p,
                    "Price":     f"{price_p:,.2f}"                        if price_p                    else "N/A",
                    "P/E Fwd":   f"{pi.get('forwardPE'):.1f}"             if pi.get('forwardPE')        else "N/A",
                    "P/E Ttm":   f"{pi.get('trailingPE'):.1f}"            if pi.get('trailingPE')       else "N/A",
                    "EPS Fwd":   f"{pi.get('forwardEps'):.2f}"            if pi.get('forwardEps')       else "N/A",
                    "Beta":      f"{pi.get('beta'):.2f}"                  if pi.get('beta')             else "N/A",
                    "P/B":       f"{pi.get('priceToBook'):.1f}"           if pi.get('priceToBook')      else "N/A",
                    "P/S":       f"{pi.get('priceToSalesTrailing12Months'):.1f}" if pi.get('priceToSalesTrailing12Months') else "N/A",
                    "EV/EBITDA": f"{pi.get('enterpriseToEbitda'):.1f}"    if pi.get('enterpriseToEbitda') else "N/A",
                    "Cap (B$)":  f"{pi.get('marketCap',0)/1e9:.1f}"       if pi.get('marketCap')        else "N/A",
                    "Div %":     f"{(pi.get('dividendYield') or 0)*100:.2f}%",
                    "ROE %":     f"{pi.get('returnOnEquity',0)*100:.1f}"  if pi.get('returnOnEquity')   else "N/A",
                    "Op.Mgn %":  f"{pi.get('operatingMargins',0)*100:.1f}" if pi.get('operatingMargins') else "N/A",
                    "52W High":  f"{pi.get('fiftyTwoWeekHigh'):.2f}"      if pi.get('fiftyTwoWeekHigh') else "N/A",
                })
            except Exception:
                rows.append({"Ticker":p,"Price":"ERR","P/E Fwd":"—","P/E Ttm":"—","EPS Fwd":"—",
                             "Beta":"—","P/B":"—","P/S":"—","EV/EBITDA":"—","Cap (B$)":"—",
                             "Div %":"—","ROE %":"—","Op.Mgn %":"—","52W High":"—"})
        if rows:
            df_peers = pd.DataFrame(rows).set_index("Ticker")
            st.dataframe(df_peers, use_container_width=True)

    st.markdown("---")

    # Relative performance chart
    section_header("PERFORMANCE RELATIVA VS PEERS (12M)")
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
                fig_peer.add_trace(go.Scatter(
                    x=peer_norm.index, y=peer_norm[col], name=col,
                    line=dict(width=2.5 if col==target else 1.5, color=COLORS[idx % len(COLORS)]),
                    hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>"+col+"</extra>"
                ))
            fig_peer.add_hline(y=0, line_dash="dot", line_color="#163860", line_width=1)
            fig_peer.update_layout(
                **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                yaxis_title="Rendimento % (normalizzato)", height=400,
                title=f"Performance relativa 12M — {target} vs peers"
            )
            st.plotly_chart(fig_peer, use_container_width=True)
    except Exception:
        st.info("Grafico peers non disponibile.")

    st.markdown("---")

    # Sector & Supply Chain
    col_sc1, col_sc2 = st.columns(2)
    with col_sc1:
        section_header("SECTOR & GEOGRAPHY")
        sc1,sc2 = st.columns(2)
        sc1.metric("Settore",   inf.get('sector','N/A'))
        sc2.metric("Industria", inf.get('industry','N/A'))
        sc3,sc4 = st.columns(2)
        sc3.metric("Paese",    inf.get('country','N/A'))
        sc4.metric("Exchange", inf.get('exchange','N/A'))
    with col_sc2:
        section_header("SUPPLY CHAIN ECOSYSTEM")
        sc_data = SUPPLY_CHAIN_MAP.get(inf.get('sector',''))
        if sc_data:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**🔼 Fornitori chiave**")
                for s in sc_data["suppliers"]: st.markdown(f"<div style='font-size:0.8rem;color:#7A9DBE;'>· {s}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("**🔽 Clienti / Sbocchi**")
                for c in sc_data["customers"]: st.markdown(f"<div style='font-size:0.8rem;color:#7A9DBE;'>· {c}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='margin-top:0.6rem;font-size:0.8rem;color:#3B8EF0;'>💡 {sc_data['notes']}</div>", unsafe_allow_html=True)
        else:
            st.info(f"Supply chain map non disponibile per '{inf.get('sector','questo settore')}'.")


# =========================================================
# 1. GLOBAL OVERVIEW
# =========================================================
if choice == "Global Overview":
    page_title("🌍  GLOBAL MARKET OVERVIEW", "Snapshot in tempo reale · Indici · Titoli · Top Movers")

    section_header("INDICI GLOBALI")
    indices = {
        "S&P 500":"^GSPC","Nasdaq 100":"^IXIC","Dow Jones":"^DJI","Nikkei 225":"^N225",
        "FTSE MIB":"FTSEMIB.MI","DAX 40":"^GDAXI","CAC 40":"^FCHI","Hang Seng":"^HSI",
        "Euro Stoxx 50":"^STOXX50E","Russell 2000":"^RUT","MSCI EM (EEM)":"EEM","VIX":"^VIX",
    }
    with st.spinner("Caricamento indici..."):
        cols = st.columns(4)
        for i, (name, ticker) in enumerate(indices.items()):
            try:
                d = get_ticker_history(ticker, "2d")
                if len(d) >= 2:
                    c,p = d['Close'].iloc[-1], d['Close'].iloc[-2]
                    cols[i%4].metric(name, f"{c:,.2f}", f"{((c-p)/p)*100:+.2f}%")
                else:
                    cols[i%4].metric(name,"N/A","—")
            except: cols[i%4].metric(name,"N/A","—")

    st.markdown("---")
    section_header("TITOLI DI RIFERIMENTO")
    stocks = {
        "Apple":"AAPL","Microsoft":"MSFT","Nvidia":"NVDA","Google":"GOOGL",
        "Tesla":"TSLA","Amazon":"AMZN","Meta":"META","ASML":"ASML.AS",
        "SAP":"SAP.DE","ENI":"ENI.MI","LVMH":"MC.PA","Ferrari":"RACE.MI",
    }
    with st.spinner("Caricamento titoli..."):
        cols2 = st.columns(4)
        for i,(name,ticker) in enumerate(stocks.items()):
            try:
                d = get_ticker_history(ticker,"2d")
                if len(d) >= 2:
                    c,p = d['Close'].iloc[-1], d['Close'].iloc[-2]
                    cols2[i%4].metric(f"{name} ({ticker})", f"{c:,.2f}", f"{((c-p)/p)*100:+.2f}%")
                else:
                    cols2[i%4].metric(f"{name} ({ticker})","N/A","—")
            except: cols2[i%4].metric(f"{name} ({ticker})","N/A","—")

    st.markdown("---")
    section_header("TOP MOVERS DEL GIORNO")
    with st.spinner("Calcolo movers..."):
        try:
            gainers, losers = get_top_movers(n=5)
            col_g, col_l = st.columns(2)
            for col_data, color, label in [(gainers,"#2ECC71","🟢 TOP GAINERS"),(losers,"#E74C3C","🔴 TOP LOSERS")]:
                with (col_g if color=="#2ECC71" else col_l):
                    st.markdown(f"<div class='section-header' style='color:{color};'>{label}</div>", unsafe_allow_html=True)
                    for m in col_data:
                        st.markdown(f"""
                            <div style='background:linear-gradient(135deg,#071A30,#0A1E38);border:1px solid #0E2440;
                                        border-left:3px solid {color};border-radius:3px;padding:0.65rem 1rem;
                                        margin-bottom:0.4rem;display:flex;justify-content:space-between;align-items:center;'>
                                <div>
                                    <div style='font-family:IBM Plex Mono,monospace;font-size:0.92rem;color:#FFFFFF;font-weight:600;'>{m['ticker']}</div>
                                    <div style='font-size:0.72rem;color:#7A9DBE;margin-top:2px;'>${m['price']:,.2f}</div>
                                </div>
                                <div style='font-family:IBM Plex Mono,monospace;font-size:1.1rem;color:{color};font-weight:700;'>{m['pct']:+.2f}%</div>
                            </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Top movers non disponibili: {e}")


# =========================================================
# 2. ANALISI DCF
# =========================================================
elif choice == "Analisi DCF":
    page_title("🧮  DISCOUNTED CASH FLOW", "Stima il fair value tramite il modello DCF — Wacc, Terminal Value, Sensitivity")

    col1,col2 = st.columns([1,1])
    with col1:
        section_header("PARAMETRI DI INPUT")
        fcf             = st.number_input("Free Cash Flow Attuale ($)",value=1_000_000_000,step=50_000_000,format="%d")
        growth          = st.slider("Tasso di Crescita (%)",1,50,10)
        wacc            = st.slider("WACC (%)",5,20,9)
        terminal_growth = st.slider("Terminal Growth Rate (%)",0,5,2)
        years_dcf       = st.slider("Anni di Proiezione",3,15,10)
        shares          = st.number_input("Azioni in Circolazione",value=1_000_000_000,step=10_000_000,format="%d")
        net_debt        = st.number_input("Net Debt ($, pos=debito)",value=0,step=100_000_000,format="%d")

    g,w,tg = growth/100, wacc/100, terminal_growth/100
    cash_flows,pv_flows = [],[]
    for yr in range(1,years_dcf+1):
        cf = fcf*((1+g)**yr); pv = cf/((1+w)**yr)
        cash_flows.append(cf); pv_flows.append(pv)
    tv   = (cash_flows[-1]*(1+tg))/(w-tg) if w>tg else 0
    pvtv = tv/((1+w)**years_dcf)
    ev   = sum(pv_flows)+pvtv
    eq   = ev - net_debt
    fvs  = eq/shares if shares>0 else 0

    with col2:
        section_header("RISULTATI DCF")
        r1,r2 = st.columns(2)
        r1.metric("Enterprise Value",      f"${ev/1e9:,.2f}B")
        r2.metric("Equity Value",          f"${eq/1e9:,.2f}B")
        r3,r4 = st.columns(2)
        r3.metric("Fair Value per Azione", f"${fvs:,.2f}")
        r4.metric("Terminal Value (PV)",   f"${pvtv/1e9:,.2f}B")
        r5,r6 = st.columns(2)
        r5.metric("PV FCF Operativi",      f"${sum(pv_flows)/1e9:,.2f}B")
        r6.metric("% Terminal Value",      f"{pvtv/ev*100:.1f}%" if ev else "N/A")

    st.markdown("---")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[f"Y{i+1}" for i in range(years_dcf)], y=[v/1e6 for v in cash_flows],
                         name="FCF Proiettato", marker_color='#3B8EF0', opacity=0.85))
    fig.add_trace(go.Bar(x=[f"Y{i+1}" for i in range(years_dcf)], y=[v/1e6 for v in pv_flows],
                         name="PV dei FCF", marker_color='#2ECC71', opacity=0.85))
    fig.update_layout(**PLOTLY_LAYOUT, yaxis_title="$ Milioni", barmode='group',
                      title="Cash Flow Proiettato vs Present Value", height=380)
    st.plotly_chart(fig, use_container_width=True)

    # Sensitivity table
    st.markdown("---")
    section_header("SENSITIVITY ANALYSIS — Fair Value vs WACC e Growth")
    wacc_range   = [w-0.02, w-0.01, w, w+0.01, w+0.02]
    growth_range = [g-0.02, g-0.01, g, g+0.01, g+0.02]
    rows_s = {}
    for gr in growth_range:
        row = {}
        for wc in wacc_range:
            if wc <= tg: row[f"WACC {wc*100:.0f}%"] = "N/A"; continue
            cfs = [fcf*((1+gr)**yr)/((1+wc)**yr) for yr in range(1,years_dcf+1)]
            tv_s = (fcf*((1+gr)**years_dcf)*(1+tg))/(wc-tg) / ((1+wc)**years_dcf)
            ev_s = sum(cfs)+tv_s
            eq_s = ev_s - net_debt
            row[f"WACC {wc*100:.0f}%"] = f"${eq_s/shares:,.0f}" if shares else "N/A"
        rows_s[f"Growth {gr*100:.0f}%"] = row
    df_sens = pd.DataFrame(rows_s).T
    st.dataframe(df_sens, use_container_width=True)


# =========================================================
# 3. MULTI-COMPARE
# =========================================================
elif choice == "Multi-Compare":
    page_title("📊  MULTI-ASSET COMPARISON", "Rendimenti · Inflazione · Fondamentali · Correlazioni")

    mode = st.radio("Modalità:",
                    ["📈 Rendimento % Asset","📉 Inflazione","🏢 Fondamentali Aziendali"],
                    horizontal=True)
    st.markdown("---")

    if mode == "📈 Rendimento % Asset":
        col1,col2,col3 = st.columns([3,1,1])
        with col1: tk_in   = st.text_input("Ticker (separati da virgola)","AAPL, MSFT, TSLA, NVDA, SPY")
        with col2: horizon = st.selectbox("Orizzonte",["Mesi","Anni"])
        with col3: val     = st.slider("Durata",1,24 if horizon=="Mesi" else 20,12)
        tk_list   = [x.strip().upper() for x in tk_in.split(",") if x.strip()]
        start_str = (datetime.now()-timedelta(days=val*30 if horizon=="Mesi" else val*365)).strftime("%Y-%m-%d")
        if tk_list:
            with st.spinner("Download..."):
                try:
                    frames = {tkr: s for tkr in tk_list for s in [download_single(tkr, start_str=start_str)] if not s.empty}
                    if frames:
                        data  = pd.DataFrame(frames).dropna(how="all").ffill()
                        rets  = ((data/data.iloc[0])-1)*100
                        fig   = go.Figure()
                        for idx,col in enumerate(rets.columns):
                            last_val = rets[col].iloc[-1]
                            fig.add_trace(go.Scatter(x=rets.index, y=rets[col], name=f"{col} ({last_val:+.1f}%)",
                                line=dict(width=2, color=COLORS[idx%len(COLORS)]),
                                hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>"+col+"</extra>"))
                        fig.add_hline(y=0,line_dash="dot",line_color="#163860",line_width=1)
                        fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                          title="Rendimento % Normalizzato",yaxis_title="Rendimento (%)",height=480)
                        st.plotly_chart(fig, use_container_width=True)

                        section_header("STATISTICHE")
                        daily_rets = data.pct_change().dropna()
                        stats_rows = []
                        for col in rets.columns:
                            dr = daily_rets[col].dropna()
                            ann_ret = rets[col].iloc[-1]
                            ann_vol = dr.std() * np.sqrt(252) * 100
                            sharpe  = (ann_ret / ann_vol) if ann_vol > 0 else 0
                            dd      = ((data[col]/data[col].cummax())-1).min()*100
                            stats_rows.append({
                                "Ticker": col,
                                "Rendimento %": f"{ann_ret:+.2f}%",
                                "Volatilità Annua": f"{ann_vol:.2f}%",
                                "Sharpe (approx)": f"{sharpe:.2f}",
                                "Max Drawdown": f"{dd:.2f}%",
                                "Max (%)": f"{rets[col].max():+.2f}%",
                                "Min (%)": f"{rets[col].min():+.2f}%",
                            })
                        st.dataframe(pd.DataFrame(stats_rows).set_index("Ticker"), use_container_width=True)

                        if len(frames) >= 2:
                            section_header("MATRICE DI CORRELAZIONE")
                            corr_df = daily_rets.corr()
                            fig_c = go.Figure(go.Heatmap(
                                z=corr_df.values, x=corr_df.columns.tolist(), y=corr_df.index.tolist(),
                                colorscale=[[0,'#E74C3C'],[0.5,'#071220'],[1,'#2ECC71']],
                                zmin=-1, zmax=1,
                                text=corr_df.round(2).values, texttemplate="%{text}",
                                hovertemplate="%{x} / %{y}: %{z:.2f}<extra></extra>"))
                            fig_c.update_layout(**PLOTLY_LAYOUT, height=350, title="Correlazione Asset")
                            st.plotly_chart(fig_c, use_container_width=True)
                except Exception as e: st.error(f"Errore: {e}")

    elif mode == "📉 Inflazione":
        st.markdown("#### Inflazione — Proxy tramite ETF TIPS")
        st.info("Usiamo proxy di mercato: **TIP** (TIPS USA), **RINF** (inflation expectations), **ITIP** (internazionale), **STIP** (short-term).")
        col1,col2,col3 = st.columns([3,1,1])
        with col1: infl_in = st.text_input("Ticker inflazione/TIPS","TIP, RINF, ITIP, STIP")
        with col2: infl_h  = st.selectbox("Orizzonte",["Mesi","Anni"],key="infl_h")
        with col3: infl_v  = st.slider("Durata",1,24 if infl_h=="Mesi" else 20,5,key="infl_v")
        comp_in = st.text_input("Confronto con altri asset","SPY, GLD, BND")
        all_infl = list(dict.fromkeys(
            [x.strip().upper() for x in infl_in.split(",") if x.strip()] +
            [x.strip().upper() for x in comp_in.split(",") if x.strip()]
        ))
        infl_list = [x.strip().upper() for x in infl_in.split(",") if x.strip()]
        infl_start = (datetime.now()-timedelta(days=infl_v*30 if infl_h=="Mesi" else infl_v*365)).strftime("%Y-%m-%d")
        with st.spinner("Download..."):
            try:
                frames = {tkr: s for tkr in all_infl for s in [download_single(tkr,start_str=infl_start)] if not s.empty}
                if frames:
                    data = pd.DataFrame(frames).dropna(how="all").ffill()
                    rets = ((data/data.iloc[0])-1)*100
                    preset = {"TIP":"#F39C12","RINF":"#E74C3C","ITIP":"#E67E22","STIP":"#F1C40F",
                              "SPY":"#3B8EF0","GLD":"#2ECC71","BND":"#9B59B6"}
                    fig = go.Figure()
                    for idx,col in enumerate(rets.columns):
                        fig.add_trace(go.Scatter(x=rets.index, y=rets[col], name=col,
                            line=dict(width=2.5 if col in infl_list else 1.5,
                                      dash="solid" if col in infl_list else "dot",
                                      color=preset.get(col, COLORS[idx%len(COLORS)])),
                            hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>"+col+"</extra>"))
                    fig.add_hline(y=0,line_dash="dot",line_color="#163860",line_width=1)
                    fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                      title="Proxy Inflazione vs Asset",yaxis_title="Rendimento % (base 100)",height=480)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e: st.error(f"Errore: {e}")

    elif mode == "🏢 Fondamentali Aziendali":
        section_header("ANDAMENTO STORICO DEI FONDAMENTALI")
        col1,col2 = st.columns([3,2])
        with col1: fund_in     = st.text_input("Ticker aziende","AAPL, MSFT, GOOGL")
        with col2: fund_metric = st.selectbox("Metrica",[
            "P/E Storico (calcolato)","P/S Storico (calcolato)",
            "EPS Trimestrale","Revenue Trimestrale","Gross Profit Trimestrale",
            "Net Income Trimestrale","EBITDA Trimestrale","Free Cash Flow Trimestrale",
            "Debt/Equity (snapshot)","Operating Margin % (snapshot)","ROE % (snapshot)",
            "Market Cap Storico (B$)",
        ])
        fund_list    = [x.strip().upper() for x in fund_in.split(",") if x.strip()]
        years_back_s = st.slider("Anni di storia",1,15,7,key="fund_years")

        METRIC_TYPE = {
            "P/E Storico (calcolato)":       "pe_hist",
            "P/S Storico (calcolato)":       "ps_hist",
            "Market Cap Storico (B$)":       "mktcap_hist",
            "EPS Trimestrale":               ("quarterly","EPS","EPS ($)"),
            "Revenue Trimestrale":           ("quarterly","Total Revenue","Revenue (B$)"),
            "Gross Profit Trimestrale":      ("quarterly","Gross Profit","Gross Profit (B$)"),
            "Net Income Trimestrale":        ("quarterly","Net Income","Net Income (B$)"),
            "EBITDA Trimestrale":            ("quarterly","EBITDA","EBITDA (B$)"),
            "Free Cash Flow Trimestrale":    ("quarterly","Free Cash Flow","FCF (B$)"),
            "Debt/Equity (snapshot)":        ("snapshot","debtToEquity","D/E (x)",100),
            "Operating Margin % (snapshot)": ("snapshot","operatingMargins","Op.Margin %",0.01),
            "ROE % (snapshot)":              ("snapshot","returnOnEquity","ROE %",0.01),
        }
        mtype = METRIC_TYPE[fund_metric]

        if fund_list:
            with st.spinner("Calcolo fondamentali storici..."):
                fig = go.Figure()
                has_data = False

                if mtype == "pe_hist":
                    for idx,tkr in enumerate(fund_list):
                        s = get_historical_pe(tkr, years_back=years_back_s)
                        if not s.empty:
                            s_sm = s.rolling(20, min_periods=1).mean()
                            fig.add_trace(go.Scatter(x=s_sm.index, y=s_sm, name=tkr,
                                line=dict(width=2, color=COLORS[idx%len(COLORS)]),
                                hovertemplate="%{x|%d %b %Y}<br>P/E: %{y:.1f}<extra>"+tkr+"</extra>"))
                            has_data = True
                    if has_data:
                        fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                          title="P/E Ratio Storico", yaxis_title="P/E", height=480)
                        st.plotly_chart(fig, use_container_width=True)

                elif mtype == "ps_hist":
                    for idx,tkr in enumerate(fund_list):
                        s = get_historical_ps(tkr, years_back=years_back_s)
                        if not s.empty:
                            s_sm = s.rolling(20, min_periods=1).mean()
                            fig.add_trace(go.Scatter(x=s_sm.index, y=s_sm, name=tkr,
                                line=dict(width=2, color=COLORS[idx%len(COLORS)]),
                                hovertemplate="%{x|%d %b %Y}<br>P/S: %{y:.2f}<extra>"+tkr+"</extra>"))
                            has_data = True
                    if has_data:
                        fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                          title="P/S Ratio Storico", yaxis_title="P/S", height=480)
                        st.plotly_chart(fig, use_container_width=True)

                elif mtype == "mktcap_hist":
                    for idx,tkr in enumerate(fund_list):
                        s = get_historical_mktcap(tkr, years_back=years_back_s)
                        if not s.empty:
                            fig.add_trace(go.Scatter(x=s.index, y=s, name=tkr,
                                line=dict(width=2, color=COLORS[idx%len(COLORS)]),
                                hovertemplate="%{x|%d %b %Y}<br>${%{y:.0f}}B<extra>"+tkr+"</extra>"))
                            has_data = True
                    if has_data:
                        fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                          title="Market Cap Storico (B$)", yaxis_title="Market Cap (B$)", height=480)
                        st.plotly_chart(fig, use_container_width=True)

                elif isinstance(mtype,tuple) and mtype[0]=="quarterly":
                    _,q_key,y_label = mtype
                    cutoff = datetime.now()-timedelta(days=365*years_back_s)
                    for idx,tkr in enumerate(fund_list):
                        s = get_quarterly_metric(tkr, q_key)
                        if not s.empty:
                            s = s[s.index >= cutoff]
                            if not s.empty:
                                fig.add_trace(go.Bar(x=s.index.astype(str), y=s.values, name=tkr,
                                    marker_color=COLORS[idx%len(COLORS)],
                                    hovertemplate="%{x}<br>"+y_label+": %{y:.2f}<extra>"+tkr+"</extra>"))
                                has_data = True
                    if has_data:
                        fig.update_layout(**PLOTLY_LAYOUT, title=f"Storico — {y_label}",
                                          yaxis_title=y_label, barmode="group", height=480)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Nessun dato disponibile per questa metrica.")

                elif isinstance(mtype,tuple) and mtype[0]=="snapshot":
                    _,info_key,y_label,divisor = mtype
                    bar_data = {}
                    for tkr in fund_list:
                        v = get_ticker_info(tkr).get(info_key)
                        if v is not None:
                            try: bar_data[tkr] = float(v)/divisor
                            except: pass
                    if bar_data:
                        fig.add_trace(go.Bar(
                            x=list(bar_data.keys()), y=list(bar_data.values()),
                            marker_color=COLORS[:len(bar_data)],
                            text=[f"{v:.2f}" for v in bar_data.values()],
                            textposition="outside", textfont=dict(color="#FFFFFF")))
                        fig.update_layout(**PLOTLY_LAYOUT, title=f"{y_label} — Valore recente",
                                          yaxis_title=y_label, height=420, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)

                # Full table
                st.markdown("---")
                section_header("TABELLA FONDAMENTALI COMPLETA")
                rows = []
                for tkr in fund_list:
                    info = get_ticker_info(tkr)
                    if not info: continue
                    rows.append({
                        "Ticker":      tkr,
                        "P/E Ttm":     f"{info.get('trailingPE'):.1f}"                    if info.get('trailingPE') else "N/A",
                        "P/E Fwd":     f"{info.get('forwardPE'):.1f}"                     if info.get('forwardPE')  else "N/A",
                        "P/B":         f"{info.get('priceToBook'):.1f}"                   if info.get('priceToBook') else "N/A",
                        "P/S":         f"{info.get('priceToSalesTrailing12Months'):.1f}"  if info.get('priceToSalesTrailing12Months') else "N/A",
                        "EV/EBITDA":   f"{info.get('enterpriseToEbitda'):.1f}"            if info.get('enterpriseToEbitda') else "N/A",
                        "EPS Fwd":     f"{info.get('forwardEps'):.2f}"                    if info.get('forwardEps') else "N/A",
                        "Rev (B$)":    f"{info.get('totalRevenue',0)/1e9:.1f}"            if info.get('totalRevenue') else "N/A",
                        "EBITDA (B$)": f"{info.get('ebitda',0)/1e9:.1f}"                 if info.get('ebitda') else "N/A",
                        "FCF (B$)":    f"{info.get('freeCashflow',0)/1e9:.1f}"            if info.get('freeCashflow') else "N/A",
                        "D/E":         f"{info.get('debtToEquity',0)/100:.2f}"            if info.get('debtToEquity') else "N/A",
                        "Op.Mgn %":    f"{info.get('operatingMargins',0)*100:.1f}"        if info.get('operatingMargins') else "N/A",
                        "ROE %":       f"{info.get('returnOnEquity',0)*100:.1f}"          if info.get('returnOnEquity') else "N/A",
                        "ROA %":       f"{info.get('returnOnAssets',0)*100:.1f}"          if info.get('returnOnAssets') else "N/A",
                    })
                if rows:
                    st.dataframe(pd.DataFrame(rows).set_index("Ticker"), use_container_width=True)


# =========================================================
# 4. PORTFOLIO BACKTEST
# =========================================================
elif choice == "Portfolio Backtest":
    page_title("🧪  PORTFOLIO BACKTEST", "Costruisci la tua strategia e analizza rischio, rendimento e metriche avanzate")

    # ── Asset allocation ──
    section_header("COMPOSIZIONE PORTAFOGLIO")
    n_assets = st.slider("Numero di asset",2,10,4)
    defaults = ["VOO","GLD","TLT","QQQ","BND","VNQ","EEM","PDBC","IAU","VWCE.DE"]

    col_t = st.columns(n_assets)
    col_w = st.columns(n_assets)
    asset_list, weight_list = [], []
    dw = round(100/n_assets)
    for i in range(n_assets):
        with col_t[i]:
            t = st.text_input(f"Asset {i+1}", value=defaults[i] if i<len(defaults) else "", key=f"a_{i}")
            asset_list.append(t.strip().upper())
        with col_w[i]:
            w = st.slider(f"{asset_list[i] or f'A{i+1}'}",0,100,dw,key=f"w_{i}")
            weight_list.append(w)

    total_weight = sum(weight_list)
    if total_weight != 100:
        st.warning(f"⚠️  Somma pesi: {total_weight}% — deve essere 100%")
    else:
        st.success("✅  Pesi bilanciati al 100%")

    st.markdown("---")
    section_header("BENCHMARK E PARAMETRI")
    b1,b2,b3 = st.columns(3)
    with b1:
        bench_options = {"S&P 500 (^GSPC)":"^GSPC","Nasdaq 100 (^IXIC)":"^IXIC",
                         "MSCI World (VWCE.DE)":"VWCE.DE","60/40 Custom":None}
        bench_label = st.selectbox("Benchmark", list(bench_options.keys()))
        bench = bench_options[bench_label]
    with b2:
        years = st.slider("Orizzonte (anni)",1,25,7,key="bt_years")
    with b3:
        risk_free = st.slider("Risk-free rate (%)",0.0,6.0,4.2,step=0.1)

    bench_eq, bench_bond = "SPY", "AGG"
    if bench is None:
        bc1,bc2 = st.columns(2)
        with bc1: bench_eq   = st.text_input("Benchmark Equity","SPY")
        with bc2: bench_bond = st.text_input("Benchmark Bond","AGG")

    run = st.button("▶  ESEGUI BACKTEST", use_container_width=True)

    if run and total_weight == 100:
        valid_pairs  = [(a, weight_list[i]) for i,a in enumerate(asset_list) if a]
        valid_assets = [p[0] for p in valid_pairs]
        w_norm       = [p[1]/100 for p in valid_pairs]
        start_str    = (datetime.now()-timedelta(days=365*years)).strftime("%Y-%m-%d")
        bench_tickers = [bench] if bench else [bench_eq.upper(), bench_bond.upper()]
        rf = risk_free / 100

        with st.spinner("Download dati storici..."):
            try:
                frames = {}
                for tkr in valid_assets + bench_tickers:
                    s = download_single(tkr, start_str=start_str)
                    if not s.empty: frames[tkr] = s
                    else: st.warning(f"⚠️ Nessun dato per {tkr}")

                if not frames:
                    st.error("Nessun dato scaricato.")
                else:
                    data = pd.DataFrame(frames).dropna(how='all').ffill()
                    norm = (data / data.iloc[0]) - 1

                    strat_df = pd.DataFrame(index=norm.index)
                    for i,a in enumerate(valid_assets):
                        if a in norm.columns: strat_df[a] = norm[a] * w_norm[i]
                    strategy = strat_df.sum(axis=1)

                    if bench is None:
                        beq, bbd = bench_eq.upper(), bench_bond.upper()
                        if beq in norm.columns and bbd in norm.columns:
                            bench_series = norm[beq]*0.6 + norm[bbd]*0.4
                            bench_name   = f"60% {beq} + 40% {bbd}"
                            bench_col    = None
                        else:
                            bench_series, bench_name, bench_col = None,"",None
                    else:
                        bench_col, bench_name, bench_series = bench, bench_label, None

                    # ── Metriche core ──
                    total_ret  = strategy.iloc[-1] * 100
                    ann_ret    = ((1 + strategy.iloc[-1])**(1/years) - 1) * 100 if years > 0 else 0
                    daily_rets = strategy.diff().dropna()
                    vol        = daily_rets.std() * np.sqrt(252) * 100
                    sharpe     = ((ann_ret/100 - rf) / (vol/100)) if vol > 0 else 0
                    drawdown_s = ((strategy + 1) / (strategy + 1).cummax()) - 1
                    max_dd     = drawdown_s.min() * 100
                    calmar     = (ann_ret / abs(max_dd)) if max_dd != 0 else 0

                    # Sortino
                    neg_rets  = daily_rets[daily_rets < 0]
                    down_vol  = neg_rets.std() * np.sqrt(252) * 100 if len(neg_rets) > 0 else 0
                    sortino   = ((ann_ret/100 - rf) / (down_vol/100)) if down_vol > 0 else 0

                    # VaR & CVaR
                    dr_arr  = daily_rets.dropna().values
                    var_95  = np.percentile(dr_arr, 5) * 100 if len(dr_arr) > 0 else 0
                    cvar_95 = dr_arr[dr_arr <= np.percentile(dr_arr, 5)].mean() * 100 if len(dr_arr) > 0 else 0

                    # Win rate
                    win_rate = (daily_rets > 0).mean() * 100

                    # Omega ratio (simplified)
                    threshold = rf / 252
                    gains  = daily_rets[daily_rets > threshold] - threshold
                    losses = threshold - daily_rets[daily_rets < threshold]
                    omega  = gains.sum() / losses.sum() if losses.sum() > 0 else 999

                    # Beta / Alpha vs benchmark
                    bench_rets_series = None
                    bench_ann_ret = None
                    if bench_col and bench_col in norm.columns:
                        bench_series_data = norm[bench_col]
                        bench_rets_series = bench_series_data.diff().dropna()
                        bench_total  = bench_series_data.iloc[-1] * 100
                        bench_ann_ret = ((1+bench_series_data.iloc[-1])**(1/years)-1)*100
                        delta_bench  = total_ret - bench_total
                    elif bench_series is not None:
                        bench_series_data = bench_series
                        bench_rets_series = bench_series_data.diff().dropna()
                        bench_total  = bench_series_data.iloc[-1] * 100
                        bench_ann_ret = ((1+bench_series_data.iloc[-1])**(1/years)-1)*100
                        delta_bench  = total_ret - bench_total
                    else:
                        delta_bench = None
                        bench_ann_ret = None

                    beta_val = alpha_val = None
                    if bench_rets_series is not None:
                        try:
                            aligned = pd.DataFrame({"s": daily_rets, "b": bench_rets_series}).dropna()
                            if len(aligned) > 10:
                                cov  = aligned.cov().iloc[0,1]
                                vb   = aligned["b"].var()
                                beta_val  = cov / vb if vb != 0 else None
                                alpha_val = ann_ret - (risk_free + (beta_val or 0) * ((bench_ann_ret or 0) - risk_free))
                        except: pass

                    # ── KPI Dashboard ──
                    st.markdown("---")
                    section_header("PERFORMANCE SUMMARY")

                    k1,k2,k3,k4 = st.columns(4)
                    k1.metric("Rendimento Totale", f"{total_ret:+.2f}%")
                    k2.metric("CAGR",              f"{ann_ret:+.2f}%")
                    k3.metric("Volatilità Annua",  f"{vol:.2f}%")
                    k4.metric("Max Drawdown",      f"{max_dd:.2f}%")

                    k5,k6,k7,k8 = st.columns(4)
                    k5.metric("Sharpe Ratio",      f"{sharpe:.3f}")
                    k6.metric("Sortino Ratio",     f"{sortino:.3f}")
                    k7.metric("Calmar Ratio",      f"{calmar:.3f}")
                    k8.metric("Omega Ratio",       f"{omega:.2f}")

                    k9,k10,k11,k12 = st.columns(4)
                    k9.metric("VaR 95% (giorn.)", f"{var_95:.2f}%")
                    k10.metric("CVaR 95% (giorn.)",f"{cvar_95:.2f}%")
                    k11.metric("Win Rate",          f"{win_rate:.1f}%")
                    k12.metric("Beta vs Bench",     f"{beta_val:.2f}" if beta_val is not None else "N/A")

                    if delta_bench is not None:
                        a1,a2 = st.columns(2)
                        a1.metric(f"Alpha vs {bench_name}", f"{alpha_val:+.2f}%" if alpha_val is not None else "N/A")
                        a2.metric(f"Delta vs {bench_name}", f"{delta_bench:+.2f}%",
                                  delta="Sovraperforma" if delta_bench > 0 else "Sottoperforma")

                    # ── Main chart ──
                    st.markdown("---")
                    section_header("EQUITY CURVE")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=strategy.index, y=strategy*100,
                        name="📐 Strategia",
                        line=dict(width=3, color="#3B8EF0"),
                        fill='tozeroy', fillcolor='rgba(59,142,240,0.06)',
                        hovertemplate="%{x|%d %b %Y}<br><b>Strategia: %{y:.2f}%</b><extra></extra>"))
                    if bench_col and bench_col in norm.columns:
                        fig.add_trace(go.Scatter(x=norm.index, y=norm[bench_col]*100,
                            name=f"📌 {bench_name}", line=dict(width=2, dash='dash', color='#7A9DBE'),
                            hovertemplate="%{x|%d %b %Y}<br>Bench: %{y:.2f}%<extra></extra>"))
                    elif bench_series is not None:
                        fig.add_trace(go.Scatter(x=bench_series.index, y=bench_series*100,
                            name=f"📌 {bench_name}", line=dict(width=2, dash='dash', color='#7A9DBE')))
                    for idx,a in enumerate(valid_assets):
                        if a in norm.columns:
                            fig.add_trace(go.Scatter(x=norm.index, y=norm[a]*100,
                                name=f"{a} ({valid_pairs[idx][1]}%)",
                                line=dict(width=1.2, color=COLORS[(idx+2)%len(COLORS)]), opacity=0.55))
                    fig.add_hline(y=0, line_dash="dot", line_color="#163860", line_width=1)
                    fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                      yaxis_title="Rendimento (%)", height=500,
                                      title="Equity Curve — Rendimento Cumulativo")
                    st.plotly_chart(fig, use_container_width=True)

                    # ── Rolling Sharpe ──
                    section_header("ROLLING SHARPE (252 GIORNI)")
                    roll_vol    = daily_rets.rolling(252).std() * np.sqrt(252)
                    roll_ret    = daily_rets.rolling(252).mean() * 252
                    roll_sharpe = (roll_ret - rf) / roll_vol
                    fig_rs = go.Figure()
                    fig_rs.add_trace(go.Scatter(x=roll_sharpe.index, y=roll_sharpe,
                        name="Rolling Sharpe", line=dict(color="#3B8EF0", width=1.8),
                        hovertemplate="%{x|%d %b %Y}<br>Sharpe: %{y:.2f}<extra></extra>"))
                    fig_rs.add_hline(y=0, line_dash="dot", line_color="#163860")
                    fig_rs.add_hline(y=1, line_dash="dot", line_color="#2ECC71", annotation_text="Sharpe=1")
                    fig_rs.update_layout(**PLOTLY_LAYOUT, height=280, title="Rolling Sharpe Ratio (1 anno)")
                    st.plotly_chart(fig_rs, use_container_width=True)

                    # ── Drawdown ──
                    section_header("DRAWDOWN ANALYSIS")
                    dd = drawdown_s * 100
                    fig_dd = go.Figure()
                    fig_dd.add_trace(go.Scatter(x=dd.index, y=dd, name="Drawdown",
                        fill='tozeroy', line=dict(color='#E74C3C', width=1.5),
                        fillcolor='rgba(231,76,60,0.12)',
                        hovertemplate="%{x|%d %b %Y}<br>Drawdown: %{y:.2f}%<extra></extra>"))
                    fig_dd.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                         yaxis_title="Drawdown (%)", height=280,
                                         title="Drawdown dalla Massima Equity")
                    st.plotly_chart(fig_dd, use_container_width=True)

                    # ── Monthly returns heatmap ──
                    section_header("MONTHLY RETURNS HEATMAP")
                    try:
                        monthly = (strategy.resample('ME').last().pct_change().dropna() * 100)
                        monthly_df = pd.DataFrame({
                            'Year': monthly.index.year,
                            'Month': monthly.index.month,
                            'Return': monthly.values
                        })
                        pivot = monthly_df.pivot(index='Year', columns='Month', values='Return')
                        month_names = ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic']
                        pivot.columns = [month_names[m-1] for m in pivot.columns]
                        fig_mth = go.Figure(go.Heatmap(
                            z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                            colorscale=[[0,'#E74C3C'],[0.5,'#071220'],[1,'#2ECC71']],
                            zmid=0,
                            text=[[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in pivot.values],
                            texttemplate="%{text}",
                            hovertemplate="Anno %{y} · %{x}<br>Rendimento: %{z:.2f}%<extra></extra>"))
                        fig_mth.update_layout(**PLOTLY_LAYOUT, height=max(200, len(pivot)*28+80),
                                              title="Rendimenti Mensili (%)")
                        st.plotly_chart(fig_mth, use_container_width=True)
                    except Exception:
                        st.info("Heatmap mensile non disponibile.")

                    # ── Return distribution ──
                    section_header("DISTRIBUZIONE DEI RENDIMENTI GIORNALIERI")
                    fig_hist = go.Figure()
                    fig_hist.add_trace(go.Histogram(x=dr_arr*100, nbinsx=80,
                        marker_color='#3B8EF0', opacity=0.75, name="Distribuzione"))
                    fig_hist.add_vline(x=var_95, line_dash="dash", line_color="#E74C3C",
                                       annotation_text=f"VaR 95% ({var_95:.2f}%)")
                    fig_hist.add_vline(x=0, line_dash="dot", line_color="#7A9DBE")
                    fig_hist.update_layout(**PLOTLY_LAYOUT, height=300,
                                           xaxis_title="Rendimento Giornaliero (%)",
                                           yaxis_title="Frequenza",
                                           title="Distribuzione Rendimenti Giornalieri")
                    st.plotly_chart(fig_hist, use_container_width=True)

                    # ── Correlation matrix ──
                    available = [a for a in valid_assets if a in norm.columns]
                    if len(available) >= 2:
                        section_header("MATRICE DI CORRELAZIONE")
                        corr_df = norm[available].pct_change().dropna().corr()
                        fig_corr = go.Figure(go.Heatmap(
                            z=corr_df.values, x=corr_df.columns.tolist(), y=corr_df.index.tolist(),
                            colorscale=[[0,'#E74C3C'],[0.5,'#071220'],[1,'#2ECC71']],
                            zmin=-1, zmax=1,
                            text=corr_df.round(2).values, texttemplate="%{text}",
                            hovertemplate="%{x} / %{y}: %{z:.2f}<extra></extra>"))
                        fig_corr.update_layout(**PLOTLY_LAYOUT, height=350, title="Correlazione tra Asset")
                        st.plotly_chart(fig_corr, use_container_width=True)

                    # ── Smart analysis ──
                    st.markdown("---")
                    section_header("ANALISI AUTOMATICA E SUGGERIMENTI")
                    suggestions = []

                    if sharpe < 0:
                        suggestions.append(f"🔴 <b>Sharpe negativo ({sharpe:.2f})</b> — Rendimento inferiore al risk-free ({risk_free:.1f}%). "
                                           f"Valuta la sostituzione dell'asset con il peggior contributo con ETF difensivi (USMV, SPLV).")
                    elif sharpe < 0.5:
                        suggestions.append(f"🟡 <b>Sharpe basso ({sharpe:.2f})</b> — Per ogni punto di volatilità ottieni rendimento insufficiente. "
                                           f"Asset decorrelati (GLD, TLT, REITs) potrebbero migliorare l'efficienza.")
                    elif sharpe >= 1.5:
                        suggestions.append(f"🏆 <b>Sharpe eccellente ({sharpe:.2f})</b> — Attenzione al survivorship bias: "
                                           f"Sharpe > 1.5 su periodi brevi tendono a normalizzarsi. Verifica su 15+ anni.")
                    else:
                        suggestions.append(f"✅ <b>Sharpe accettabile ({sharpe:.2f})</b> — Nella norma per un portafoglio diversificato. "
                                           f"Obiettivo: superare 1.0 per generare alfa costante.")

                    if sortino > sharpe * 1.3:
                        suggestions.append(f"📊 <b>Sortino > Sharpe ({sortino:.2f} vs {sharpe:.2f})</b> — "
                                           f"I rendimenti negativi sono moderati rispetto alla volatilità totale. Segno di asimmetria positiva.")

                    if vol > 25:
                        suggestions.append(f"⚡ <b>Volatilità molto alta ({vol:.1f}%)</b> — Superiore al doppio della media storica S&P 500 (~15%). "
                                           f"In uno stress-test 2008 potresti sperimentare drawdown >55%. Considera 15-25% in bond aggregati.")
                    elif vol < 8:
                        suggestions.append(f"🛡️ <b>Volatilità molto bassa ({vol:.1f}%)</b> — Portafoglio ultra-difensivo. "
                                           f"Potresti aumentare l'esposizione azionaria per migliorare il rendimento atteso nel lungo periodo.")

                    if max_dd < -40:
                        suggestions.append(f"💥 <b>Drawdown estremo ({max_dd:.1f}%)</b> — Per recuperare dal minimo servono "
                                           f"{abs(max_dd)/(100+max_dd)*100:.0f}% di guadagno. Implementa un position sizing risk-parity.")
                    elif max_dd < -20:
                        suggestions.append(f"⚠️ <b>Drawdown significativo ({max_dd:.1f}%)</b> — Un ribilanciamento trimestrale riduce "
                                           f"il drawdown medio del 15-25% su orizzonti lunghi.")

                    if len(valid_assets) < 3:
                        suggestions.append(f"🔀 <b>Bassa diversificazione ({len(valid_assets)} asset)</b> — "
                                           f"Fama-French suggerisce 8-15 asset decorrelati. Considera small-cap value, EM, commodities.")

                    if var_95 < -3:
                        suggestions.append(f"📉 <b>VaR 95% elevato ({var_95:.2f}%/giorno)</b> — In un giorno su 20 potresti perdere oltre il {abs(var_95):.1f}%. "
                                           f"Monitora il CVaR ({cvar_95:.2f}%) per le code di distribuzione.")

                    if not suggestions:
                        suggestions.append("ℹ️ Parametri nella norma. Nessun segnale critico rilevato.")

                    for sg in suggestions:
                        st.markdown(f"""
                            <div style='background:linear-gradient(135deg,#071A30,#0A1E38);
                                        border-left:3px solid #3B8EF0;border-radius:3px;
                                        padding:0.8rem 1rem;margin-bottom:0.5rem;
                                        font-size:0.86rem;line-height:1.7;color:#D8E4F0;'>{sg}</div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Errore durante il backtest: {e}")

    elif run and total_weight != 100:
        st.error("Correggi i pesi (devono sommare a 100%).")


# =========================================================
# 5. STOCK SCREENER
# =========================================================
elif choice == "Stock Screener":

    if st.session_state.screener_selected:
        target = st.session_state.screener_selected
        col_back, _ = st.columns([1,6])
        with col_back:
            if st.button("← Torna allo Screener"):
                st.session_state.screener_selected = None
                st.rerun()
        page_title(f"⌨️  ANALISI DETTAGLIATA — {target}")

        # Derive smart peer defaults based on sector
        info_check = get_ticker_info(target)
        sector_check = info_check.get('sector','') if info_check else ''
        sector_peer_defaults = {
            "Technology":             "AAPL, MSFT, GOOGL",
            "Semiconductors":         "NVDA, AMD, INTC, AVGO",
            "Consumer Cyclical":      "AMZN, TSLA, NKE, MCD",
            "Consumer Defensive":     "PG, KO, PEP, WMT",
            "Healthcare":             "JNJ, PFE, ABBV, MRK",
            "Financials":             "JPM, BAC, GS, MS",
            "Energy":                 "XOM, CVX, TTE.PA, BP.L",
            "Industrials":            "GE, CAT, HON, BA",
            "Communication Services": "META, GOOGL, NFLX, DIS",
            "Utilities":              "NEE, CEG, DUK, SO",
            "Real Estate":            "PLD, AMT, EQIX, SPG",
            "Basic Materials":        "LIN, APD, NEM, FCX",
        }
        peers_default = sector_peer_defaults.get(sector_check, "SPY, QQQ, IWM")
        show_bloomberg_insights(target, peers_default=peers_default)

    else:
        page_title("🔍  STOCK SCREENER", "Filtra aziende per fondamentali — universo Russell 3000 + Europa + Italia")

        with st.spinner("Caricamento universo ticker..."):
            UNIVERSE = get_large_universe()
            st.markdown(f"<div class='terminal-box'>✅  Universo caricato: <b style='color:#3B8EF0'>{len(UNIVERSE)} ticker</b> · Russell 3000 + NASDAQ + S&P500 + Europa + Italia</div>", unsafe_allow_html=True)

        section_header("FILTRI FONDAMENTALI")
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            pe_max       = st.slider("P/E massimo",              0,200,50)
            pb_max       = st.slider("P/B massimo",              0, 30,10)
            ps_max       = st.slider("P/S massimo",              0, 50,15)
        with c2:
            cap_min      = st.slider("Market Cap min (B$)",      0,500, 1)
            cap_max      = st.slider("Market Cap max (B$)",      0,5000,3000)
            de_max       = st.slider("Debt/Equity massimo",      0, 10, 5)
        with c3:
            margin_min   = st.slider("Margine Operativo min (%)",-50,60,0)
            roic_min     = st.slider("ROE min (%)",             -20,60,-20)
            evebitda_max = st.slider("EV/EBITDA massimo",         0,80,40)
        with c4:
            div_min      = st.slider("Dividend Yield min (%)",   0.0,10.0,0.0,step=0.1)
            beta_max     = st.slider("Beta massimo",             0.0, 5.0, 5.0,step=0.1)
            sector_filter = st.selectbox("Settore",[
                "Tutti","Technology","Healthcare","Financials","Industrials",
                "Consumer Defensive","Consumer Cyclical","Energy",
                "Communication Services","Utilities","Real Estate","Basic Materials","Semiconductors"
            ])

        section_header("FILTRI AVANZATI")
        adv1, adv2 = st.columns(2)
        with adv1:
            product_filter = st.text_input("Keyword business/settore","",
                placeholder="Es: cloud, semiconductor, oil, insurance, pharma, AI, defense ...")
        with adv2:
            custom_in = st.text_input("Ticker extra da aggiungere all'universo","")
        if custom_in.strip():
            extra = [x.strip().upper() for x in custom_in.split(",") if x.strip()]
            UNIVERSE = list(set(UNIVERSE + extra))

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            max_scan = st.selectbox("Ticker da scansionare",
                ["300 (veloce ~1.5min)","600 (medio ~3min)","1000 (completo ~5min)","Tutti (lento ~12min+)"])
        with col_r2:
            sort_by = st.selectbox("Ordina per",["Market Cap","P/E","EV/EBITDA","ROE %","Op.Margin %","Div %"])

        run_screen = st.button("▶  ESEGUI SCREENING", use_container_width=True)

        if run_screen:
            n_map = {"300 (veloce ~1.5min)":300,"600 (medio ~3min)":600,
                     "1000 (completo ~5min)":1000,"Tutti (lento ~12min+)":len(UNIVERSE)}
            n_scan = n_map.get(max_scan, 300)
            scan_list = random.sample(UNIVERSE, min(n_scan, len(UNIVERSE)))

            results = []
            progress = st.progress(0)
            status   = st.empty()
            for i, tkr in enumerate(scan_list):
                progress.progress((i+1)/len(scan_list))
                status.markdown(f"<span style='color:#7A9DBE;font-size:0.78rem;font-family:IBM Plex Mono,monospace;'>"
                                f"Scansione: {tkr} ({i+1}/{len(scan_list)})</span>", unsafe_allow_html=True)
                try:
                    info = get_ticker_info(tkr)
                    if not info: continue

                    pe        = info.get('forwardPE') or info.get('trailingPE')
                    pb        = info.get('priceToBook')
                    ps        = info.get('priceToSalesTrailing12Months')
                    mcap      = info.get('marketCap')
                    de        = info.get('debtToEquity')
                    op_margin = info.get('operatingMargins')
                    roe       = info.get('returnOnEquity')
                    ev_ebitda = info.get('enterpriseToEbitda')
                    sector_v  = info.get('sector','')
                    div_yield = (info.get('dividendYield') or 0) * 100
                    beta_v    = info.get('beta')
                    name      = info.get('shortName', tkr)
                    price     = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')

                    # Filters
                    if sector_filter != "Tutti" and sector_v != sector_filter: continue
                    if product_filter.strip():
                        kw  = product_filter.strip().lower()
                        txt = " ".join(filter(None,[info.get('longBusinessSummary',''),
                                                     info.get('industry',''),info.get('longName',''),info.get('sector','')])).lower()
                        if kw not in txt: continue
                    if pe        is not None and pe > pe_max:           continue
                    if pb        is not None and pb > pb_max:           continue
                    if ps        is not None and ps > ps_max:           continue
                    if de        is not None and de/100 > de_max:       continue
                    if ev_ebitda is not None and ev_ebitda > evebitda_max: continue
                    if mcap      is not None and mcap/1e9 < cap_min:    continue
                    if mcap      is not None and mcap/1e9 > cap_max:    continue
                    if op_margin is not None and op_margin*100 < margin_min: continue
                    if roe       is not None and roe*100 < roic_min:    continue
                    if div_yield < div_min:                             continue
                    if beta_v    is not None and beta_v > beta_max:     continue

                    results.append({
                        "Ticker":    tkr,
                        "Nome":      name,
                        "Settore":   sector_v,
                        "Prezzo":    f"{price:.2f}"           if price      else "N/A",
                        "P/E":       f"{pe:.1f}"              if pe         else "N/A",
                        "P/B":       f"{pb:.1f}"              if pb         else "N/A",
                        "P/S":       f"{ps:.1f}"              if ps         else "N/A",
                        "EV/EBITDA": f"{ev_ebitda:.1f}"       if ev_ebitda  else "N/A",
                        "Op.Mgn %":  f"{op_margin*100:.1f}"   if op_margin  else "N/A",
                        "ROE %":     f"{roe*100:.1f}"         if roe        else "N/A",
                        "Div %":     f"{div_yield:.2f}",
                        "Beta":      f"{beta_v:.2f}"          if beta_v     else "N/A",
                        "D/E":       f"{de/100:.2f}"          if de         else "N/A",
                        "Cap (B$)":  f"{mcap/1e9:.1f}"        if mcap       else "N/A",
                        "_cap_num":  mcap/1e9 if mcap else 0,
                        "_pe_num":   pe if pe else 999,
                        "_ev_num":   ev_ebitda if ev_ebitda else 999,
                        "_roe_num":  roe*100 if roe else 0,
                        "_mgn_num":  op_margin*100 if op_margin else 0,
                        "_div_num":  div_yield,
                    })
                except: continue

            progress.empty(); status.empty()

            # Sort
            sort_key_map = {
                "Market Cap":  ("_cap_num", True),
                "P/E":         ("_pe_num",  False),
                "EV/EBITDA":   ("_ev_num",  False),
                "ROE %":       ("_roe_num", True),
                "Op.Margin %": ("_mgn_num", True),
                "Div %":       ("_div_num", True),
            }
            sk, rev = sort_key_map.get(sort_by, ("_cap_num", True))
            results.sort(key=lambda x: x.get(sk, 0), reverse=rev)

            st.session_state.screener_results = results if results else []

        if st.session_state.screener_results:
            results = st.session_state.screener_results
            st.success(f"✅  {len(results)} aziende trovate")
            display_cols = ["Nome","Settore","Prezzo","P/E","P/B","P/S","EV/EBITDA","Op.Mgn %","ROE %","Div %","Beta","Cap (B$)"]
            df_show = pd.DataFrame(results)[["Ticker"]+display_cols].set_index("Ticker")
            st.dataframe(df_show, use_container_width=True)

            section_header("ANALISI DETTAGLIATA")
            sel = st.selectbox("Seleziona azienda",
                               [f"{r['Ticker']} — {r['Nome']}" for r in results],
                               key="screener_select_box")
            if st.button("🔎  APRI ANALISI BLOOMBERG", use_container_width=True):
                st.session_state.screener_selected = sel.split(" — ")[0].strip()
                st.rerun()

        elif st.session_state.screener_results is not None and len(st.session_state.screener_results) == 0:
            st.warning("Nessuna azienda trovata. Prova ad allargare i parametri di filtro.")


# =========================================================
# 6. BLOOMBERG INSIGHTS
# =========================================================
elif choice == "Bloomberg Insights":
    page_title("⌨️  COMPANY TERMINAL", "Analisi fondamentale · Supply chain · Peer comparison · News")

    col_inp, col_btn = st.columns([4,1])
    with col_inp:
        new_target = st.text_input("Ticker",
                                   value=st.session_state.get("bi_ticker","NVDA"),
                                   placeholder="Es: AAPL, MSFT, MC.PA, ENI.MI, ASML.AS ...").strip().upper()
    with col_btn:
        st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
        search_btn = st.button("🔍  ANALIZZA", use_container_width=True)

    if search_btn or new_target:
        if new_target != st.session_state.get("bi_ticker",""):
            st.session_state.bi_ticker = new_target
            # Reset peers when ticker changes
            info_new = get_ticker_info(new_target)
            sector_new = info_new.get('sector','') if info_new else ''
            peer_map = {
                "Technology":             "AMD, INTC, AVGO, QCOM",
                "Semiconductors":         "NVDA, AMD, INTC, AVGO, TSM",
                "Consumer Cyclical":      "AMZN, TSLA, NKE, MCD, BKNG",
                "Consumer Defensive":     "PG, KO, PEP, WMT, COST",
                "Healthcare":             "JNJ, PFE, ABBV, MRK, LLY",
                "Financials":             "JPM, BAC, GS, MS, V",
                "Energy":                 "XOM, CVX, TTE.PA, BP.L, ENI.MI",
                "Industrials":            "GE, CAT, HON, BA, MMM",
                "Communication Services": "META, GOOGL, NFLX, DIS, CMCSA",
                "Utilities":              "NEE, CEG, DUK, SO, AEP",
                "Real Estate":            "PLD, AMT, EQIX, SPG, O",
                "Basic Materials":        "LIN, APD, NEM, FCX, DD",
            }
            st.session_state.bi_peers = peer_map.get(sector_new, "SPY, QQQ, IWM, GLD")

        target = st.session_state.bi_ticker or new_target
        if target:
            show_bloomberg_insights(target, peers_default=st.session_state.get("bi_peers","AMD, INTC, AVGO"))

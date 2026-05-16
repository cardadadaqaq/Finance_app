import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Navy Terminal Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
    html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        background-color: #0A1628 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    [data-testid="stSidebar"] {
        background-color: #060E1E !important;
        border-right: 1px solid #1E3A5F !important;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #0D1F38 !important;
        border: 1px solid #1E3A5F !important;
        color: #FFFFFF !important;
    }
    [data-testid="stHeader"] {
        background-color: #060E1E !important;
        border-bottom: 1px solid #1E3A5F !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
    }
    p, span, li, div, label, .stMarkdown {
        color: #E8EDF5 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    .page-title {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.6rem;
        font-weight: 600;
        color: #FFFFFF !important;
        letter-spacing: 0.08em;
        border-left: 3px solid #4A9EFF;
        padding-left: 1rem;
        margin-bottom: 1.8rem;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 1.3rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #A8BDD4 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    [data-testid="metric-container"] {
        background-color: #0D1F38 !important;
        border: 1px solid #1E3A5F !important;
        border-radius: 6px !important;
        padding: 0.8rem 1rem !important;
    }
    .stTextInput label, .stSelectbox label, .stMultiSelect label,
    .stSlider label, .stNumberInput label, .stRadio label, label[data-testid] {
        color: #FFFFFF !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #4A9EFF !important;
        border-color: #4A9EFF !important;
    }
    .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
        color: #FFFFFF !important;
        background-color: #4A9EFF !important;
    }
    .stSlider [data-baseweb="slider"] div[class*="Track"] div:first-child {
        background-color: #4A9EFF !important;
    }
    .stSlider span { color: #A8BDD4 !important; }
    .stNumberInput input {
        background-color: #0D1F38 !important;
        color: #FFFFFF !important;
        border: 1px solid #1E3A5F !important;
        border-radius: 4px !important;
    }
    .stNumberInput button {
        background-color: #1E3A5F !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    input[type="text"], textarea, .stTextInput input {
        background-color: #0D1F38 !important;
        color: #FFFFFF !important;
        border: 1px solid #1E3A5F !important;
        border-radius: 4px !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    input[type="text"]:focus, textarea:focus {
        border-color: #4A9EFF !important;
        box-shadow: 0 0 0 1px #4A9EFF !important;
    }
    /* Selectbox chiuso */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #0D1F38 !important;
        border: 1px solid #1E3A5F !important;
        color: #FFFFFF !important;
    }
    /* Valore selezionato visibile nel box chiuso */
    .stSelectbox [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div {
        color: #FFFFFF !important;
    }
    /* Dropdown aperto: sfondo bianco, testo nero */
    [data-baseweb="popover"] {
        background-color: #FFFFFF !important;
        border: 1px solid #1E3A5F !important;
    }
    [data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        border: 1px solid #1E3A5F !important;
    }
    [data-baseweb="option"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.88rem !important;
    }
    [data-baseweb="option"]:hover {
        background-color: #DDEEFF !important;
        color: #000000 !important;
    }
    [data-baseweb="option"][aria-selected="true"] {
        background-color: #BBDDFF !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    li[role="option"]:hover {
        background-color: #DDEEFF !important;
        color: #000000 !important;
    }
    /* Radio buttons */
    .stRadio > div > label {
        color: #FFFFFF !important;
        text-transform: none !important;
        font-size: 0.9rem !important;
    }
    .dataframe, table {
        background-color: #0D1F38 !important;
        color: #FFFFFF !important;
        border-collapse: collapse !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.82rem !important;
    }
    thead tr th {
        color: #A8BDD4 !important;
        background-color: #060E1E !important;
        border-bottom: 1px solid #1E3A5F !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.6rem 1rem !important;
    }
    tbody tr td {
        color: #FFFFFF !important;
        border-bottom: 1px solid #111E33 !important;
        padding: 0.5rem 1rem !important;
    }
    tbody tr:hover td { background-color: #1E3A5F !important; }
    hr { border-color: #1E3A5F !important; }
    .stAlert, .stInfo, [data-testid="stNotification"] {
        background-color: #0D1F38 !important;
        border: 1px solid #1E3A5F !important;
        color: #E8EDF5 !important;
    }
    .stButton > button {
        background-color: #1E3A5F !important;
        color: #FFFFFF !important;
        border: 1px solid #4A9EFF !important;
        border-radius: 4px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.06em !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover { background-color: #4A9EFF !important; color: #000 !important; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #060E1E; }
    ::-webkit-scrollbar-thumb { background: #1E3A5F; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #4A9EFF; }
    </style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; margin-bottom:1.5rem;'>
            <div style='font-family: IBM Plex Mono, monospace; font-size:1.3rem; font-weight:700;
                        color:#FFFFFF; letter-spacing:0.15em;'>⚓ NAVY</div>
            <div style='font-family: IBM Plex Mono, monospace; font-size:0.65rem; color:#4A9EFF;
                        letter-spacing:0.3em; margin-top:2px;'>TERMINAL PRO</div>
        </div>
        <div style='height:1px; background: linear-gradient(90deg, transparent, #4A9EFF, transparent);
                    margin-bottom:1.5rem;'></div>
    """, unsafe_allow_html=True)

    menu_items = [
        ("🌍", "Global Overview"),
        ("🧮", "Analisi DCF"),
        ("📊", "Multi-Compare"),
        ("🧪", "Portfolio Backtest"),
        ("🔍", "Stock Screener"),
        ("⌨️", "Bloomberg Insights"),
    ]

    if "page" not in st.session_state:
        st.session_state.page = "Global Overview"
    if "screener_selected" not in st.session_state:
        st.session_state.screener_selected = None
    if "screener_results" not in st.session_state:
        st.session_state.screener_results = None

    for icon, label in menu_items:
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label

    st.markdown("""
        <div style='height:1px; background: linear-gradient(90deg, transparent, #1E3A5F, transparent);
                    margin-top:2rem; margin-bottom:1rem;'></div>
        <div style='font-family: IBM Plex Mono, monospace; font-size:0.6rem; color:#2E4A6E;
                    text-align:center; letter-spacing:0.12em;'>
            MARKET DATA · REAL-TIME<br>POWERED BY YFINANCE
        </div>
    """, unsafe_allow_html=True)

choice = st.session_state.page


# =========================================================
# UTILITY
# =========================================================
def page_title(text, subtitle=""):
    sub_html = (f'<p style="color:#A8BDD4; font-size:0.88rem; margin-top:-1rem; '
                f'margin-bottom:1.5rem;">{subtitle}</p>') if subtitle else ""
    st.markdown(f"<div class='page-title'>{text}</div>{sub_html}", unsafe_allow_html=True)


def interactive_xaxis():
    return dict(
        gridcolor='#111E33', showgrid=True, zeroline=False,
        rangeslider=dict(visible=True, bgcolor="#060E1E", thickness=0.04),
        rangeselector=dict(
            bgcolor="#0D1F38", activecolor="#4A9EFF",
            bordercolor="#1E3A5F",
            font=dict(color="#FFFFFF", size=10),
            buttons=[
                dict(count=1,  label="1M", step="month", stepmode="backward"),
                dict(count=6,  label="6M", step="month", stepmode="backward"),
                dict(count=1,  label="1A", step="year",  stepmode="backward"),
                dict(count=3,  label="3A", step="year",  stepmode="backward"),
                dict(step="all", label="Tutto"),
            ]
        )
    )


PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor='rgba(6,14,30,0.0)',
    plot_bgcolor='rgba(13,31,56,0.5)',
    font=dict(color="#E8EDF5", family="IBM Plex Mono, monospace", size=11),
    legend=dict(bgcolor='rgba(6,14,30,0.8)', bordercolor='#1E3A5F', borderwidth=1),
    xaxis=dict(gridcolor='#111E33', showgrid=True, zeroline=False),
    yaxis=dict(gridcolor='#111E33', showgrid=True, zeroline=False),
    margin=dict(l=40, r=20, t=40, b=40),
    hovermode="x unified",
    dragmode="zoom",
)


# =========================================================
# CACHING
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
            if isinstance(close, pd.DataFrame):
                return close.iloc[:, 0].rename(ticker)
            return close.squeeze()
        close = raw['Close']
        if isinstance(close, pd.DataFrame):
            return close.iloc[:, 0].rename(ticker)
        return close.squeeze()
    except Exception:
        return pd.Series(dtype=float, name=ticker)


# =========================================================
# FONDAMENTALI STORICI — funzioni robuste
# =========================================================
@st.cache_data(ttl=600, show_spinner=False)
def get_historical_pe(ticker, years_back=10):
    try:
        t = yf.Ticker(ticker)
        price_hist = t.history(period=f"{years_back}y")["Close"]
        if price_hist.empty:
            return pd.Series(dtype=float, name=ticker)
        price_hist.index = price_hist.index.tz_localize(None)

        eps_q = None
        for attr in ["quarterly_earnings", "earnings", "quarterly_income_stmt",
                     "income_stmt", "quarterly_financials", "financials"]:
            try:
                df = getattr(t, attr)
                if df is None or (hasattr(df, "empty") and df.empty):
                    continue
                if hasattr(df, "columns") and "EPS" in df.columns:
                    eps_q = df["EPS"].copy()
                    eps_q.index = pd.to_datetime(eps_q.index)
                    eps_q = eps_q.sort_index()
                    break
                if hasattr(df, "index"):
                    for row_name in ["Basic EPS", "Diluted EPS", "EPS",
                                     "Basic Earnings Per Share"]:
                        if row_name in df.index:
                            eps_q = df.loc[row_name].copy()
                            eps_q.index = pd.to_datetime(eps_q.index)
                            eps_q = eps_q.sort_index()
                            break
                if eps_q is not None:
                    break
            except Exception:
                continue

        if eps_q is None or eps_q.empty:
            eps_snap = t.info.get("trailingEps")
            if eps_snap and eps_snap > 0:
                return (price_hist / eps_snap).rename(ticker)
            return pd.Series(dtype=float, name=ticker)

        eps_ttm = eps_q.rolling(4, min_periods=1).sum()
        eps_daily = eps_ttm.reindex(
            eps_ttm.index.union(price_hist.index)
        ).ffill().reindex(price_hist.index)
        pe_hist = price_hist / eps_daily
        pe_hist = pe_hist.replace([float("inf"), float("-inf")], float("nan"))
        return pe_hist[eps_daily > 0].dropna().rename(ticker)
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
        shares = (t.info.get("sharesOutstanding") or
                  t.info.get("impliedSharesOutstanding"))
        if not shares:
            return pd.Series(dtype=float, name=ticker)

        rev_q = None
        for attr in ["quarterly_financials", "financials",
                     "quarterly_income_stmt", "income_stmt"]:
            try:
                df = getattr(t, attr)
                if df is None or (hasattr(df, "empty") and df.empty):
                    continue
                for row_name in ["Total Revenue", "Revenue",
                                 "TotalRevenue", "Net Revenue"]:
                    if row_name in df.index:
                        rev_q = df.loc[row_name].copy()
                        rev_q.index = pd.to_datetime(rev_q.index)
                        rev_q = rev_q.sort_index()
                        break
                if rev_q is not None:
                    break
            except Exception:
                continue

        if rev_q is None or rev_q.empty:
            rev_snap = t.info.get("totalRevenue")
            if rev_snap and rev_snap > 0:
                return ((price_hist * shares) / rev_snap).rename(ticker)
            return pd.Series(dtype=float, name=ticker)

        rev_ttm = rev_q.rolling(4, min_periods=1).sum()
        rev_daily = rev_ttm.reindex(
            rev_ttm.index.union(price_hist.index)
        ).ffill().reindex(price_hist.index)
        ps_hist = (price_hist * shares) / rev_daily
        ps_hist = ps_hist.replace([float("inf"), float("-inf")], float("nan"))
        return ps_hist[rev_daily > 0].dropna().rename(ticker)
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
        shares = (t.info.get("sharesOutstanding") or
                  t.info.get("impliedSharesOutstanding"))
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
            for attr in ["quarterly_earnings", "earnings"]:
                try:
                    df = getattr(t, attr)
                    if df is not None and not df.empty and "EPS" in df.columns:
                        s = df["EPS"].copy()
                        s.index = pd.to_datetime(s.index)
                        return s.sort_index().rename(ticker)
                except Exception:
                    continue
            for attr in ["quarterly_income_stmt", "income_stmt",
                         "quarterly_financials", "financials"]:
                try:
                    df = getattr(t, attr)
                    if df is None or df.empty:
                        continue
                    for row in ["Basic EPS", "Diluted EPS", "EPS"]:
                        if row in df.index:
                            s = df.loc[row].copy()
                            s.index = pd.to_datetime(s.index)
                            return s.sort_index().rename(ticker)
                except Exception:
                    continue
            return pd.Series(dtype=float, name=ticker)

        elif metric_key == "Free Cash Flow":
            for attr in ["quarterly_cashflow", "cashflow",
                         "quarterly_cash_flow", "cash_flow"]:
                try:
                    df = getattr(t, attr)
                    if df is None or df.empty:
                        continue
                    for row in ["Free Cash Flow", "FreeCashFlow",
                                "Free Cash Flow From Operations"]:
                        if row in df.index:
                            s = df.loc[row].copy()
                            s.index = pd.to_datetime(s.index)
                            return (s.sort_index() / 1e9).rename(ticker)
                except Exception:
                    continue
            return pd.Series(dtype=float, name=ticker)

        else:
            row_map = {
                "Total Revenue": ["Total Revenue", "Revenue",
                                  "TotalRevenue", "Net Revenue"],
                "Gross Profit":  ["Gross Profit", "GrossProfit"],
                "Net Income":    ["Net Income", "NetIncome",
                                  "Net Income Common Stockholders"],
                "EBITDA":        ["EBITDA", "Normalized EBITDA",
                                  "Operating Income", "EBIT"],
            }
            candidates = row_map.get(metric_key, [metric_key])
            for attr in ["quarterly_financials", "financials",
                         "quarterly_income_stmt", "income_stmt"]:
                try:
                    df = getattr(t, attr)
                    if df is None or df.empty:
                        continue
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
        "suppliers": ["Taiwan Semiconductor (TSM)", "Samsung Electronics",
                      "ASML (ASML.AS)", "Applied Materials (AMAT)", "Lam Research (LRCX)"],
        "customers": ["Apple (AAPL)", "Microsoft (MSFT)", "Meta (META)",
                      "Amazon AWS (AMZN)", "Alphabet (GOOGL)"],
        "notes": "La supply chain tech è dominata dai foundry asiatici per la produzione di chip e dai big tech USA come clienti finali."
    },
    "Consumer Electronics": {
        "suppliers": ["Foxconn (2317.TW)", "Qualcomm (QCOM)", "Corning (GLW)", "Murata Manufacturing"],
        "customers": ["Retailer globali", "Operatori telecom", "Consumatori B2C"],
        "notes": "Fortemente dipendente da componentistica asiatica e da cicli di upgrade dei consumatori."
    },
    "Semiconductors": {
        "suppliers": ["ASML (ASML.AS)", "Applied Materials (AMAT)",
                      "Air Products (APD)", "Shin-Etsu Chemical"],
        "customers": ["Apple (AAPL)", "Nvidia (NVDA)", "AMD",
                      "Qualcomm (QCOM)", "Data center hyperscalers"],
        "notes": "Settore capital-intensive con altissime barriere d'ingresso. I fornitori di litografia (ASML) sono monopolisti de facto."
    },
    "Communication Services": {
        "suppliers": ["Ericsson (ERIC)", "Nokia (NOK)", "Akamai (AKAM)", "Infrastrutture cloud"],
        "customers": ["Advertiser B2B", "Consumatori B2C", "PMI globali"],
        "notes": "I ricavi dipendono prevalentemente dalla pubblicità digitale e dagli abbonamenti."
    },
    "Financial Services": {
        "suppliers": ["Bloomberg LP", "Refinitiv/LSEG", "Broadridge (BR)", "Fiserv (FISV)"],
        "customers": ["Retail banking clienti", "Investitori istituzionali", "Aziende corporate"],
        "notes": "Il settore si affida a fornitori di dati e infrastrutture IT finanziarie specializzate."
    },
    "Healthcare": {
        "suppliers": ["Thermo Fisher (TMO)", "Danaher (DHR)", "Lonza Group", "Wuxi Biologics"],
        "customers": ["Ospedali", "Assicurazioni sanitarie", "Governi", "Distributori farmaceutici"],
        "notes": "Pipeline R&D lunga e costosa; i CDMO (contract manufacturers) sono fornitori critici."
    },
    "Energy": {
        "suppliers": ["Halliburton (HAL)", "Baker Hughes (BKR)", "SLB (SLB)", "Caterpillar (CAT)"],
        "customers": ["Utility elettriche", "Raffinerie", "Industria chimica", "Governi"],
        "notes": "Ciclico, fortemente legato al prezzo del petrolio e alle politiche energetiche governative."
    },
    "Industrials": {
        "suppliers": ["3M (MMM)", "Honeywell (HON)", "Parker Hannifin (PH)", "Eaton (ETN)"],
        "customers": ["Settore aerospaziale", "Automotive", "Costruzioni", "Difesa"],
        "notes": "Ampio spettro B2B; molto sensibile al ciclo economico e agli ordini governativi."
    },
    "Consumer Defensive": {
        "suppliers": ["Archer-Daniels (ADM)", "Bunge (BG)", "Packaging Corp (PKG)", "IFF (IFF)"],
        "customers": ["Grande distribuzione (WMT, COST)", "Consumatori finali B2C"],
        "notes": "Settore anticiclico con pricing power nei brand premium. Margini sotto pressione per inflazione input."
    },
    "Consumer Cyclical": {
        "suppliers": ["Li & Fung", "Produttori asiatici OEM", "Fornitori materie prime"],
        "customers": ["Consumatori finali", "E-commerce", "Retail fisico"],
        "notes": "Fortemente correlato al ciclo del credito al consumo e alla fiducia dei consumatori."
    },
    "Real Estate": {
        "suppliers": ["Costruttori", "Gestori immobiliari", "Società di property management"],
        "customers": ["Tenant retail", "Tenant uffici", "Residenziale"],
        "notes": "Sensibile ai tassi d'interesse. I REIT distribuiscono almeno il 90% degli utili come dividendi."
    },
    "Utilities": {
        "suppliers": ["GE Vernova (GEV)", "Siemens Energy", "NextEra (NEE)", "Fuel suppliers"],
        "customers": ["Residenziale", "Industria", "Data center (domanda in forte crescita)"],
        "notes": "Settore regolato, cash flow stabile. La crescente domanda da AI/data center è un catalizzatore strutturale."
    },
    "Basic Materials": {
        "suppliers": ["Minatori di materie prime", "Produttori chimici di base"],
        "customers": ["Manifatturiero", "Costruzioni", "Automotive", "Farmaceutico"],
        "notes": "Altamente ciclico, dipendente da domanda cinese e prezzi delle commodity globali."
    },
}


# =========================================================
# BLOOMBERG INSIGHTS — funzione riutilizzabile
# =========================================================
def show_bloomberg_insights(target):
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
            st.error(f"❌  Ticker **{target}** non trovato. Verifica il simbolo.")
            st.markdown("""
                **Esempi di formato corretto:**
                - USA: `AAPL`, `MSFT`, `NVDA`
                - Italia: `ENI.MI`, `ENEL.MI`
                - Francia: `MC.PA`, `TTE.PA`
                - Germania: `SAP.DE`, `BMW.DE`
                - ETF: `VWCE.DE`, `SWDA.MI`
            """)
            return

        company_name = inf.get('longName') or inf.get('shortName') or inf.get('symbol')
        current_price = (inf.get('currentPrice') or inf.get('regularMarketPrice')
                         or inf.get('previousClose'))
        display_name = company_name if company_name else target

        st.markdown(f"""
            <div style='background:#0D1F38; border:1px solid #1E3A5F; border-radius:8px;
                        padding:1.2rem 1.5rem; margin-bottom:1.5rem;'>
                <div style='font-family: IBM Plex Mono, monospace; font-size:0.7rem;
                            color:#4A9EFF; letter-spacing:0.2em; margin-bottom:4px;'>EQUITY</div>
                <div style='font-size:1.6rem; font-weight:700; color:#FFFFFF;'>{display_name}</div>
                <div style='font-family: IBM Plex Mono, monospace; font-size:0.85rem;
                            color:#A8BDD4; margin-top:4px;'>
                    {target} · {inf.get('exchange','N/A')} · {inf.get('currency','N/A')}
                </div>
            </div>
        """, unsafe_allow_html=True)

        k1,k2,k3,k4,k5 = st.columns(5)
        k1.metric("Prezzo",      f"{current_price:,.2f}"              if current_price          else "N/A")
        k2.metric("P/E Forward", f"{inf.get('forwardPE'):.1f}"        if inf.get('forwardPE')   else "N/A")
        k3.metric("EPS Forward", f"{inf.get('forwardEps'):.2f}"       if inf.get('forwardEps')  else "N/A")
        k4.metric("Beta",        f"{inf.get('beta'):.2f}"             if inf.get('beta')        else "N/A")
        k5.metric("Market Cap",  f"${inf.get('marketCap',0)/1e9:.1f}B" if inf.get('marketCap') else "N/A")

        st.markdown("---")
        col_desc, col_news = st.columns([2, 1])
        with col_desc:
            st.markdown("#### Business Summary")
            st.write(inf.get('longBusinessSummary') or "Descrizione non disponibile.")

        with col_news:
            st.markdown("#### Latest News")
            yahoo_url = f"https://finance.yahoo.com/quote/{target}/news/"
            st.markdown(f"""
                <div style='background:#0D1F38; border:1px solid #1E3A5F; border-radius:6px;
                            padding:1rem; margin-bottom:0.8rem;'>
                    <div style='font-family: IBM Plex Mono, monospace; font-size:0.7rem;
                                color:#4A9EFF; letter-spacing:0.15em; margin-bottom:6px;'>FONTE ESTERNA</div>
                    <div style='font-size:0.88rem; color:#E8EDF5; margin-bottom:10px;'>
                        Notizie in tempo reale su <b>{target}</b> disponibili su Yahoo Finance.
                    </div>
                    <a href='{yahoo_url}' target='_blank'
                       style='display:inline-block; background:#1E3A5F; color:#FFFFFF;
                              border:1px solid #4A9EFF; border-radius:4px;
                              padding:6px 14px; font-family: IBM Plex Mono, monospace;
                              font-size:0.78rem; letter-spacing:0.06em; text-decoration:none;'>
                        📰 Apri News su Yahoo Finance →
                    </a>
                </div>
            """, unsafe_allow_html=True)
            try:
                news_items = get_ticker_news(target)
                if news_items:
                    st.markdown("**Titoli recenti:**")
                    for n in news_items[:4]:
                        title = n.get('title','')
                        link  = n.get('link', yahoo_url)
                        if title:
                            st.markdown(f"→ [{title}]({link})")
            except Exception:
                pass

        st.markdown("---")
        st.markdown("#### Fundamental Peer Analysis")
        peers_in = st.text_input("Competitors (separati da virgola)", "AMD, INTC, AVGO",
                                 key=f"peers_{target}")
        p_list = [target] + [x.strip().upper() for x in peers_in.split(",") if x.strip()]

        with st.spinner("Caricamento dati peers..."):
            rows = []
            for p in p_list:
                try:
                    pi = get_ticker_info(p)
                    price_p = (pi.get('currentPrice') or pi.get('regularMarketPrice')
                               or pi.get('previousClose') or 0)
                    rows.append({
                        "Ticker":    p,
                        "Price":     f"{price_p:,.2f}"                         if price_p                      else "N/A",
                        "P/E Fwd":   f"{pi.get('forwardPE'):.1f}"              if pi.get('forwardPE')          else "N/A",
                        "EPS Fwd":   f"{pi.get('forwardEps'):.2f}"             if pi.get('forwardEps')         else "N/A",
                        "Beta":      f"{pi.get('beta'):.2f}"                   if pi.get('beta')               else "N/A",
                        "P/B":       f"{pi.get('priceToBook'):.1f}"            if pi.get('priceToBook')        else "N/A",
                        "Cap (B$)":  f"{pi.get('marketCap',0)/1e9:.1f}"        if pi.get('marketCap')          else "N/A",
                        "Div Yield": f"{(pi.get('dividendYield') or 0)*100:.2f}%",
                        "52W High":  f"{pi.get('fiftyTwoWeekHigh'):.2f}"       if pi.get('fiftyTwoWeekHigh')   else "N/A",
                    })
                except Exception:
                    rows.append({"Ticker":p,"Price":"ERR","P/E Fwd":"—","EPS Fwd":"—",
                                 "Beta":"—","P/B":"—","Cap (B$)":"—","Div Yield":"—","52W High":"—"})
            if rows:
                st.dataframe(pd.DataFrame(rows).set_index("Ticker"), use_container_width=True)

        st.markdown("---")
        st.markdown("#### Sector & Industry")
        sector = inf.get('sector','N/A')
        sc1,sc2,sc3,sc4 = st.columns(4)
        sc1.metric("Settore",   sector)
        sc2.metric("Industria", inf.get('industry','N/A'))
        sc3.metric("Paese",     inf.get('country','N/A'))
        sc4.metric("Exchange",  inf.get('exchange','N/A'))

        st.markdown("---")
        st.markdown("#### Supply Chain & Ecosystem")
        sc_data = SUPPLY_CHAIN_MAP.get(sector)
        if sc_data:
            c1,c2 = st.columns(2)
            with c1:
                st.markdown("##### 🔼 Da chi acquista — Fornitori chiave")
                for s in sc_data["suppliers"]: st.markdown(f"- {s}")
            with c2:
                st.markdown("##### 🔽 A chi vende — Clienti / Sbocchi")
                for c in sc_data["customers"]: st.markdown(f"- {c}")
            st.info(f"💡 {sc_data['notes']}")
        else:
            st.info(f"Mappa supply chain non disponibile per il settore '{sector}'.")

        st.markdown("---")
        st.markdown("#### Andamento relativo vs Peers (12 mesi)")
        peer_tickers = [target] + [x.strip().upper() for x in peers_in.split(",") if x.strip()]
        try:
            frames = {}
            for tkr in peer_tickers:
                s = download_single(tkr, period="1y")
                if not s.empty:
                    frames[tkr] = s
            if frames:
                peer_data = pd.DataFrame(frames).dropna(how='all').ffill()
                peer_norm = ((peer_data / peer_data.iloc[0]) - 1) * 100
                peer_colors = ['#4A9EFF','#2ECC71','#F39C12','#E74C3C','#9B59B6','#1ABC9C']
                fig_peer = go.Figure()
                for idx, col in enumerate(peer_norm.columns):
                    fig_peer.add_trace(go.Scatter(
                        x=peer_norm.index, y=peer_norm[col], name=col,
                        line=dict(width=2.5 if col==target else 1.5,
                                  color=peer_colors[idx % len(peer_colors)]),
                        hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>"+col+"</extra>"
                    ))
                fig_peer.add_hline(y=0, line_dash="dot", line_color="#2E4A6E", line_width=1)
                fig_peer.update_layout(
                    **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                    yaxis_title="Rendimento % (norm.)", height=420,
                    title=f"Performance relativa: {target} vs peers (1 anno)"
                )
                st.plotly_chart(fig_peer, use_container_width=True)
        except Exception:
            st.info("Grafico peers non disponibile.")


# =========================================================
# 1. GLOBAL OVERVIEW
# =========================================================
if choice == "Global Overview":
    page_title("🌍  Global Market Overview", "Snapshot in tempo reale dei principali indici e titoli globali")
    titles = {
        "S&P 500":"^GSPC","Nasdaq 100":"^IXIC","Dow Jones":"^DJI","Nikkei 225":"^N225",
        "FTSE MIB":"FTSEMIB.MI","DAX 40":"^GDAXI","CAC 40":"^FCHI","Hang Seng":"^HSI",
        "Shanghai":"000001.SS","Euro Stoxx 50":"^STOXX50E","Russell 2000":"^RUT","Nifty 50":"^NSEI",
        "Apple":"AAPL","Microsoft":"MSFT","Nvidia":"NVDA","Google":"GOOGL",
        "Tesla":"TSLA","Amazon":"AMZN","LVMH":"MC.PA","ASML":"ASML.AS"
    }
    with st.spinner("Caricamento dati di mercato..."):
        cols = st.columns(4)
        for i, (name, ticker) in enumerate(titles.items()):
            try:
                d = get_ticker_history(ticker, "2d")
                if len(d) >= 2:
                    c, p = d['Close'].iloc[-1], d['Close'].iloc[-2]
                    cols[i%4].metric(name, f"{c:,.2f}", f"{((c-p)/p)*100:+.2f}%")
                else:
                    cols[i%4].metric(name, "N/A", "—")
            except Exception:
                cols[i%4].metric(name, "N/A", "—")


# =========================================================
# 2. ANALISI DCF
# =========================================================
elif choice == "Analisi DCF":
    page_title("🧮  Discounted Cash Flow", "Stima il fair value di un'azienda tramite il modello DCF")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Parametri di Input")
        fcf            = st.number_input("Free Cash Flow Attuale ($)", value=1_000_000_000, step=50_000_000, format="%d")
        growth         = st.slider("Tasso di Crescita (%)", 1, 50, 10)
        wacc           = st.slider("WACC (%)", 5, 20, 9)
        terminal_growth= st.slider("Terminal Growth Rate (%)", 0, 5, 2)
        years_dcf      = st.slider("Anni di Proiezione", 3, 15, 10)
        shares         = st.number_input("Azioni in Circolazione", value=1_000_000_000, step=10_000_000, format="%d")

    g, w, tg = growth/100, wacc/100, terminal_growth/100
    cash_flows, pv_flows = [], []
    for yr in range(1, years_dcf+1):
        cf = fcf * ((1+g)**yr); pv = cf / ((1+w)**yr)
        cash_flows.append(cf); pv_flows.append(pv)
    terminal_value     = (cash_flows[-1]*(1+tg))/(w-tg) if w>tg else 0
    pv_terminal        = terminal_value / ((1+w)**years_dcf)
    enterprise_value   = sum(pv_flows) + pv_terminal
    fair_value_share   = enterprise_value / shares if shares > 0 else 0

    with col2:
        st.markdown("#### Risultati")
        st.metric("Enterprise Value",          f"${enterprise_value/1e9:,.2f}B")
        st.metric("Fair Value per Azione",     f"${fair_value_share:,.2f}")
        st.metric("Terminal Value (PV)",       f"${pv_terminal/1e9:,.2f}B")
        st.metric("PV Cash Flows operativi",   f"${sum(pv_flows)/1e9:,.2f}B")

    st.markdown("---")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[f"Anno {i+1}" for i in range(years_dcf)],
                         y=[v/1e6 for v in cash_flows], name="FCF Proiettato",
                         marker_color='#4A9EFF', opacity=0.8))
    fig.add_trace(go.Bar(x=[f"Anno {i+1}" for i in range(years_dcf)],
                         y=[v/1e6 for v in pv_flows], name="PV dei Cash Flows",
                         marker_color='#2ECC71', opacity=0.8))
    fig.update_layout(**PLOTLY_LAYOUT, yaxis_title="$ Milioni", barmode='group',
                      title="Cash Flow Proiettato vs Present Value")
    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# 3. MULTI-COMPARE
# =========================================================
elif choice == "Multi-Compare":
    page_title("📊  Multi-Asset Comparison", "Confronto rendimenti, inflazione e fondamentali aziendali")

    mode = st.radio("Cosa vuoi visualizzare?",
                    ["📈 Rendimento % Asset", "📉 Inflazione", "🏢 Fondamentali Aziendali"],
                    horizontal=True)
    st.markdown("---")

    # --- MODALITÀ 1: Rendimento ---
    if mode == "📈 Rendimento % Asset":
        col1, col2, col3 = st.columns([3,1,1])
        with col1: tk_in    = st.text_input("Ticker (separati da virgola)", "AAPL, MSFT, TSLA, NVDA")
        with col2: horizon  = st.selectbox("Orizzonte", ["Mesi","Anni"])
        with col3: val      = st.slider("Durata", 1, 24 if horizon=="Mesi" else 10, 12)

        tk_list   = [x.strip().upper() for x in tk_in.split(",") if x.strip()]
        start_str = (datetime.now()-timedelta(days=val*30 if horizon=="Mesi" else val*365)).strftime("%Y-%m-%d")

        if tk_list:
            with st.spinner("Download dati..."):
                try:
                    frames = {}
                    for tkr in tk_list:
                        s = download_single(tkr, start_str=start_str)
                        if not s.empty: frames[tkr] = s
                        else: st.warning(f"⚠️ Nessun dato per {tkr}")
                    if frames:
                        data = pd.DataFrame(frames).dropna(how="all").ffill()
                        rets = ((data/data.iloc[0])-1)*100
                        colors = ["#4A9EFF","#2ECC71","#F39C12","#E74C3C","#9B59B6",
                                  "#1ABC9C","#E67E22","#3498DB","#EC407A","#AB47BC"]
                        fig = go.Figure()
                        for idx, col in enumerate(rets.columns):
                            fig.add_trace(go.Scatter(
                                x=rets.index, y=rets[col], name=col,
                                line=dict(width=2, color=colors[idx%len(colors)]),
                                hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>"+col+"</extra>"
                            ))
                        fig.add_hline(y=0, line_dash="dot", line_color="#2E4A6E", line_width=1)
                        fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                          title="Rendimento % Normalizzato",
                                          yaxis_title="Rendimento (%)", height=460)
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown("#### Riepilogo")
                        st.dataframe(pd.DataFrame({
                            "Rendimento Totale (%)": rets.iloc[-1].round(2),
                            "Max (%)": rets.max().round(2),
                            "Min (%)": rets.min().round(2),
                        }), use_container_width=True)
                except Exception as e:
                    st.error(f"Errore: {e}")

    # --- MODALITÀ 2: Inflazione ---
    elif mode == "📉 Inflazione":
        st.markdown("#### Inflazione — Proxy tramite ETF")
        st.info("L'inflazione ufficiale (CPI) non è disponibile via yfinance. "
                "Usiamo proxy di mercato: **TIP**, **RINF**, **ITIP**, **STIP**.")
        col1,col2,col3 = st.columns([3,1,1])
        with col1: infl_in  = st.text_input("Ticker inflazione/TIPS", "TIP, RINF, ITIP, STIP")
        with col2: infl_h   = st.selectbox("Orizzonte", ["Mesi","Anni"], key="infl_h")
        with col3: infl_v   = st.slider("Durata", 1, 24 if infl_h=="Mesi" else 20, 5, key="infl_v")
        comp_in = st.text_input("Aggiungi asset da confrontare", "SPY, GLD")

        infl_list = [x.strip().upper() for x in infl_in.split(",") if x.strip()]
        comp_list = [x.strip().upper() for x in comp_in.split(",") if x.strip()]
        all_infl  = list(dict.fromkeys(infl_list+comp_list))
        infl_start= (datetime.now()-timedelta(days=infl_v*30 if infl_h=="Mesi" else infl_v*365)).strftime("%Y-%m-%d")

        with st.spinner("Download..."):
            try:
                frames = {}
                for tkr in all_infl:
                    s = download_single(tkr, start_str=infl_start)
                    if not s.empty: frames[tkr] = s
                if frames:
                    data = pd.DataFrame(frames).dropna(how="all").ffill()
                    rets = ((data/data.iloc[0])-1)*100
                    preset = {"TIP":"#F39C12","RINF":"#E74C3C","ITIP":"#E67E22","STIP":"#F1C40F",
                              "SPY":"#4A9EFF","GLD":"#2ECC71","BTC-USD":"#9B59B6"}
                    def_c  = ["#4A9EFF","#2ECC71","#F39C12","#E74C3C","#9B59B6","#1ABC9C"]
                    fig = go.Figure()
                    for idx, col in enumerate(rets.columns):
                        fig.add_trace(go.Scatter(
                            x=rets.index, y=rets[col], name=col,
                            line=dict(width=2.5 if col in infl_list else 1.5,
                                      dash="solid" if col in infl_list else "dot",
                                      color=preset.get(col, def_c[idx%len(def_c)])),
                            hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>"+col+"</extra>"
                        ))
                    fig.add_hline(y=0, line_dash="dot", line_color="#2E4A6E", line_width=1)
                    fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                      title="Proxy Inflazione vs Asset",
                                      yaxis_title="Rendimento % (base 100)", height=480)
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("""
                    | Ticker | Cosa rappresenta |
                    |--------|-----------------|
                    | **TIP** | iShares TIPS Bond ETF — obbligazioni USA indicizzate all'inflazione |
                    | **RINF** | ProShares Inflation Expectations ETF |
                    | **ITIP** | iShares International Inflation-Linked Bond ETF |
                    | **STIP** | iShares 0-5 Year TIPS — inflazione breve termine |
                    | **GLD** | Oro — hedge tradizionale contro l'inflazione |
                    """)
            except Exception as e:
                st.error(f"Errore: {e}")

    # --- MODALITÀ 3: Fondamentali storici ---
    elif mode == "🏢 Fondamentali Aziendali":
        st.markdown("#### Andamento Storico dei Fondamentali")
        col1, col2 = st.columns([3,2])
        with col1: fund_in   = st.text_input("Ticker aziende", "AAPL, MSFT, GOOGL")
        with col2: fund_metric = st.selectbox("Metrica storica", [
            "P/E Storico (calcolato)",
            "P/S Storico (calcolato)",
            "EPS Trimestrale",
            "Revenue Trimestrale",
            "Gross Profit Trimestrale",
            "Net Income Trimestrale",
            "EBITDA Trimestrale",
            "Free Cash Flow Trimestrale",
            "Debt/Equity (snapshot)",
            "Operating Margin % (snapshot)",
            "ROE % (snapshot)",
            "Market Cap Storico (B$)",
        ])

        fund_list    = [x.strip().upper() for x in fund_in.split(",") if x.strip()]
        colors_f     = ["#4A9EFF","#2ECC71","#F39C12","#E74C3C",
                        "#9B59B6","#1ABC9C","#E67E22","#AB47BC"]
        years_back_s = st.slider("Anni di storia", 1, 15, 5, key="fund_years")

        METRIC_TYPE = {
            "P/E Storico (calcolato)":       "pe_hist",
            "P/S Storico (calcolato)":       "ps_hist",
            "Market Cap Storico (B$)":       "mktcap_hist",
            "EPS Trimestrale":               ("quarterly","EPS",          "EPS ($)",        1),
            "Revenue Trimestrale":           ("quarterly","Total Revenue", "Revenue (B$)",   1),
            "Gross Profit Trimestrale":      ("quarterly","Gross Profit",  "Gross Profit (B$)",1),
            "Net Income Trimestrale":        ("quarterly","Net Income",    "Net Income (B$)",  1),
            "EBITDA Trimestrale":            ("quarterly","EBITDA",        "EBITDA (B$)",      1),
            "Free Cash Flow Trimestrale":    ("quarterly","Free Cash Flow","FCF (B$)",         1),
            "Debt/Equity (snapshot)":        ("snapshot","debtToEquity",   "D/E (x)",        100),
            "Operating Margin % (snapshot)": ("snapshot","operatingMargins","Op.Margin %",  0.01),
            "ROE % (snapshot)":              ("snapshot","returnOnEquity", "ROE %",          0.01),
        }
        mtype = METRIC_TYPE[fund_metric]

        if fund_list:
            with st.spinner("Calcolo fondamentali storici..."):

                if mtype == "pe_hist":
                    st.info("**P/E storico** = Prezzo giornaliero ÷ EPS TTM rolling (4 trimestri). "
                            "Se i dati trimestrali non sono disponibili viene usato l'EPS snapshot come approssimazione.")
                    fig = go.Figure()
                    for idx, tkr in enumerate(fund_list):
                        s = get_historical_pe(tkr, years_back=years_back_s)
                        if not s.empty:
                            s_sm = s.rolling(20, min_periods=1).mean()
                            fig.add_trace(go.Scatter(
                                x=s_sm.index, y=s_sm, name=tkr,
                                line=dict(width=2, color=colors_f[idx%len(colors_f)]),
                                hovertemplate="%{x|%d %b %Y}<br>P/E: %{y:.1f}<extra>"+tkr+"</extra>"
                            ))
                        else:
                            st.warning(f"⚠️ P/E storico non disponibile per {tkr}")
                    if fig.data:
                        fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                          title="P/E Ratio Storico", yaxis_title="P/E", height=480)
                        st.plotly_chart(fig, use_container_width=True)

                elif mtype == "ps_hist":
                    st.info("**P/S storico** = Market Cap giornaliero ÷ Revenue TTM rolling (4 trimestri).")
                    fig = go.Figure()
                    for idx, tkr in enumerate(fund_list):
                        s = get_historical_ps(tkr, years_back=years_back_s)
                        if not s.empty:
                            s_sm = s.rolling(20, min_periods=1).mean()
                            fig.add_trace(go.Scatter(
                                x=s_sm.index, y=s_sm, name=tkr,
                                line=dict(width=2, color=colors_f[idx%len(colors_f)]),
                                hovertemplate="%{x|%d %b %Y}<br>P/S: %{y:.2f}<extra>"+tkr+"</extra>"
                            ))
                        else:
                            st.warning(f"⚠️ P/S storico non disponibile per {tkr}")
                    if fig.data:
                        fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                          title="P/S Ratio Storico", yaxis_title="P/S", height=480)
                        st.plotly_chart(fig, use_container_width=True)

                elif mtype == "mktcap_hist":
                    fig = go.Figure()
                    for idx, tkr in enumerate(fund_list):
                        s = get_historical_mktcap(tkr, years_back=years_back_s)
                        if not s.empty:
                            fig.add_trace(go.Scatter(
                                x=s.index, y=s, name=tkr,
                                line=dict(width=2, color=colors_f[idx%len(colors_f)]),
                                hovertemplate="%{x|%d %b %Y}<br>Mkt Cap: $%{y:.0f}B<extra>"+tkr+"</extra>"
                            ))
                        else:
                            st.warning(f"⚠️ Dati non disponibili per {tkr}")
                    if fig.data:
                        fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                          title="Market Cap Storico (B$)",
                                          yaxis_title="Market Cap (B$)", height=480)
                        st.plotly_chart(fig, use_container_width=True)

                elif isinstance(mtype, tuple) and mtype[0] == "quarterly":
                    _, q_key, y_label, _ = mtype
                    fig = go.Figure()
                    has_data = False
                    cutoff = datetime.now() - timedelta(days=365*years_back_s)
                    for idx, tkr in enumerate(fund_list):
                        s = get_quarterly_metric(tkr, q_key)
                        if not s.empty:
                            s = s[s.index >= cutoff]
                            if not s.empty:
                                fig.add_trace(go.Bar(
                                    x=s.index.astype(str), y=s.values, name=tkr,
                                    marker_color=colors_f[idx%len(colors_f)],
                                    hovertemplate="%{x}<br>"+y_label+": %{y:.2f}<extra>"+tkr+"</extra>"
                                ))
                                has_data = True
                        else:
                            st.warning(f"⚠️ Dati trimestrali non disponibili per {tkr}")
                    if has_data:
                        fig.update_layout(**PLOTLY_LAYOUT,
                                          title=f"Storico Trimestrale — {y_label}",
                                          yaxis_title=y_label, barmode="group", height=480)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Nessun dato trimestrale disponibile. "
                                   "yfinance limita lo storico a ~8-12 trimestri.")

                elif isinstance(mtype, tuple) and mtype[0] == "snapshot":
                    _, info_key, y_label, divisor = mtype
                    st.info(f"**{y_label}** è un valore puntuale (ultimo report). "
                            "Per la serie storica completa considera Macrotrends o Tikr.")
                    bar_data = {}
                    for tkr in fund_list:
                        info = get_ticker_info(tkr)
                        v = info.get(info_key)
                        if v is not None:
                            try: bar_data[tkr] = float(v)/divisor
                            except Exception: pass
                    if bar_data:
                        fig_bar = go.Figure()
                        fig_bar.add_trace(go.Bar(
                            x=list(bar_data.keys()), y=list(bar_data.values()),
                            marker_color=colors_f[:len(bar_data)],
                            text=[f"{v:.2f}" for v in bar_data.values()],
                            textposition="outside", textfont=dict(color="#FFFFFF"),
                            hovertemplate="%{x}<br>"+y_label+": %{y:.2f}<extra></extra>"
                        ))
                        fig_bar.update_layout(**PLOTLY_LAYOUT,
                                              title=f"{y_label} — Valore più recente",
                                              yaxis_title=y_label, height=420, showlegend=False)
                        st.plotly_chart(fig_bar, use_container_width=True)

                # Tabella snapshot sempre visibile
                st.markdown("---")
                st.markdown("#### Tabella Fondamentali Completa (snapshot)")
                rows = []
                for tkr in fund_list:
                    info = get_ticker_info(tkr)
                    if not info: continue
                    rows.append({
                        "Ticker":      tkr,
                        "P/E Ttm":     f"{info.get('trailingPE'):.1f}"                       if info.get('trailingPE')                else "N/A",
                        "P/E Fwd":     f"{info.get('forwardPE'):.1f}"                        if info.get('forwardPE')                 else "N/A",
                        "P/B":         f"{info.get('priceToBook'):.1f}"                      if info.get('priceToBook')               else "N/A",
                        "P/S":         f"{info.get('priceToSalesTrailing12Months'):.1f}"     if info.get('priceToSalesTrailing12Months') else "N/A",
                        "EPS Ttm":     f"{info.get('trailingEps'):.2f}"                      if info.get('trailingEps')               else "N/A",
                        "EPS Fwd":     f"{info.get('forwardEps'):.2f}"                       if info.get('forwardEps')                else "N/A",
                        "Rev (B$)":    f"{info.get('totalRevenue',0)/1e9:.1f}"               if info.get('totalRevenue')              else "N/A",
                        "EBITDA (B$)": f"{info.get('ebitda',0)/1e9:.1f}"                     if info.get('ebitda')                    else "N/A",
                        "FCF (B$)":    f"{info.get('freeCashflow',0)/1e9:.1f}"               if info.get('freeCashflow')              else "N/A",
                        "D/E (x)":     f"{info.get('debtToEquity',0)/100:.2f}"               if info.get('debtToEquity')              else "N/A",
                        "Op.Mgn %":    f"{info.get('operatingMargins',0)*100:.1f}"           if info.get('operatingMargins')          else "N/A",
                        "ROE %":       f"{info.get('returnOnEquity',0)*100:.1f}"             if info.get('returnOnEquity')            else "N/A",
                    })
                if rows:
                    st.dataframe(pd.DataFrame(rows).set_index("Ticker"), use_container_width=True)


# =========================================================
# 4. PORTFOLIO BACKTEST
# =========================================================
elif choice == "Portfolio Backtest":
    page_title("🧪  Portfolio Backtest", "Costruisci una strategia composita e confrontala con un benchmark")

    st.markdown("---")
    st.markdown("#### 1 · Composizione del Portafoglio")
    col1, _ = st.columns([1,2])
    with col1:
        n_assets = st.slider("Numero di asset", 2, 8, 3)

    assets_defaults = ["VOO","GLD","TLT","QQQ","BND","VNQ","EEM","PDBC"]
    asset_list, weight_list = [], []

    st.markdown("##### Ticker")
    cols_a = st.columns(n_assets)
    for i in range(n_assets):
        with cols_a[i]:
            t = st.text_input(f"Asset {i+1}",
                              value=assets_defaults[i] if i < len(assets_defaults) else "",
                              key=f"asset_{i}")
            asset_list.append(t.strip().upper())

    st.markdown("##### Pesi (%)")
    cols_w = st.columns(n_assets)
    dw = round(100/n_assets)
    for i in range(n_assets):
        with cols_w[i]:
            w = st.slider(f"{asset_list[i] or f'Asset {i+1}'}",
                          0, 100, dw, key=f"weight_{i}")
            weight_list.append(w)

    total_weight = sum(weight_list)
    if total_weight != 100:
        st.warning(f"⚠️  La somma dei pesi è {total_weight}% — deve essere 100%.")
    else:
        st.success(f"✅  Pesi bilanciati: {total_weight}%")

    st.markdown("---")
    st.markdown("#### 2 · Benchmark e Orizzonte")
    col3, _ = st.columns(2)
    with col3:
        bench_options = {
            "S&P 500 (^GSPC)":"^GSPC",
            "MSCI World (VWCE.DE)":"VWCE.DE",
            "Nasdaq 100 (^IXIC)":"^IXIC",
            "60/40 Custom":None
        }
        bench_label = st.selectbox("Benchmark", list(bench_options.keys()))
        bench = bench_options[bench_label]

    years = st.slider("Orizzonte temporale (anni)", 1, 20, 5, key="bt_years")

    bench_eq, bench_bond = "SPY","AGG"
    if bench is None:
        bc1, bc2 = st.columns(2)
        with bc1: bench_eq   = st.text_input("Benchmark Equity", "SPY")
        with bc2: bench_bond = st.text_input("Benchmark Bond",   "AGG")

    run = st.button("▶  Esegui Backtest", use_container_width=True)

    if run and total_weight == 100:
        valid_pairs  = [(a, weight_list[i]) for i, a in enumerate(asset_list) if a]
        valid_assets = [p[0] for p in valid_pairs]
        w_norm       = [p[1]/100 for p in valid_pairs]
        start_str    = (datetime.now()-timedelta(days=365*years)).strftime("%Y-%m-%d")
        bench_tickers= [bench] if bench else [bench_eq.upper(), bench_bond.upper()]

        with st.spinner("Download dati storici (ticker per ticker)..."):
            try:
                frames = {}
                for tkr in valid_assets + bench_tickers:
                    s = download_single(tkr, start_str=start_str)
                    if not s.empty: frames[tkr] = s
                    else: st.warning(f"⚠️ Nessun dato per {tkr}")

                if not frames:
                    st.error("Nessun dato scaricato.")
                else:
                    data     = pd.DataFrame(frames).dropna(how='all').ffill()
                    norm     = (data/data.iloc[0])-1
                    strat_df = pd.DataFrame(index=norm.index)
                    for i, a in enumerate(valid_assets):
                        if a in norm.columns: strat_df[a] = norm[a]*w_norm[i]
                        else: st.warning(f"⚠️ {a} non presente — peso ignorato.")
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
                        bench_col    = bench
                        bench_name   = bench_label
                        bench_series = None

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=strategy.index, y=strategy*100,
                        name="📐 La Tua Strategia",
                        line=dict(width=3,color="#4A9EFF"),
                        fill='tozeroy', fillcolor='rgba(74,158,255,0.07)',
                        hovertemplate="%{x|%d %b %Y}<br><b>Strategia: %{y:.2f}%</b><extra></extra>"
                    ))
                    if bench_col and bench_col in norm.columns:
                        fig.add_trace(go.Scatter(
                            x=norm.index, y=norm[bench_col]*100,
                            name=f"📌 {bench_name}",
                            line=dict(width=2,dash='dash',color='#FFFFFF'),
                            hovertemplate="%{x|%d %b %Y}<br>Benchmark: %{y:.2f}%<extra></extra>"
                        ))
                    elif bench_series is not None:
                        fig.add_trace(go.Scatter(
                            x=bench_series.index, y=bench_series*100,
                            name=f"📌 {bench_name}",
                            line=dict(width=2,dash='dash',color='#FFFFFF'),
                            hovertemplate="%{x|%d %b %Y}<br>Benchmark: %{y:.2f}%<extra></extra>"
                        ))
                    ac = ['#2ECC71','#F39C12','#E74C3C','#9B59B6','#1ABC9C','#E67E22','#EC407A','#AB47BC']
                    for idx, a in enumerate(valid_assets):
                        if a in norm.columns:
                            fig.add_trace(go.Scatter(
                                x=norm.index, y=norm[a]*100,
                                name=f"  {a} ({valid_pairs[idx][1]}%)",
                                line=dict(width=1.2,color=ac[idx%len(ac)]),
                                opacity=0.5,
                                hovertemplate="%{x|%d %b %Y}<br>"+a+": %{y:.2f}%<extra></extra>"
                            ))
                    fig.add_hline(y=0,line_dash="dot",line_color="#2E4A6E",line_width=1)
                    fig.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                      title="Rendimento Cumulativo (%)",
                                      yaxis_title="Rendimento (%)", height=500)
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("#### Statistiche di Performance")
                    s1,s2,s3,s4 = st.columns(4)
                    total_ret  = strategy.iloc[-1]*100
                    annual_ret = ((1+strategy.iloc[-1])**(1/years)-1)*100 if years>0 else 0
                    vol        = strategy.diff().dropna().std()*(252**0.5)*100
                    sharpe     = (annual_ret/vol) if vol>0 else 0
                    drawdown   = ((strategy+1)/(strategy+1).cummax()-1).min()*100

                    s1.metric("Rendimento Totale",  f"{total_ret:+.2f}%")
                    s2.metric("CAGR",               f"{annual_ret:+.2f}%")
                    s3.metric("Volatilità Annua",   f"{vol:.2f}%")
                    s4.metric("Max Drawdown",        f"{drawdown:.2f}%")
                    st.metric("Sharpe Ratio",        f"{sharpe:.2f}")

                    delta_vs_bench = None
                    if bench_col and bench_col in norm.columns:
                        bench_total    = norm[bench_col].iloc[-1]*100
                        delta_vs_bench = total_ret - bench_total
                        st.metric(f"Alpha vs {bench_name}", f"{delta_vs_bench:+.2f}%",
                                  delta="Sovraperforma" if delta_vs_bench>0 else "Sottoperforma")

                    st.markdown("---")
                    st.markdown("#### Tasso Interno di Rendimento (TIR)")
                    try:
                        import numpy_financial as npf
                        n_months = years*12
                        cf_irr   = [-100]+[0]*(n_months-1)+[100*(1+strategy.iloc[-1])]
                        irr_m    = npf.irr(cf_irr)
                        st.metric("TIR Annualizzato", f"{((1+irr_m)**12-1)*100:+.2f}%")
                    except ImportError:
                        st.metric("TIR (approx = CAGR)", f"{annual_ret:+.2f}%",
                                  help="pip install numpy-financial per il TIR esatto")
                    except Exception:
                        st.info("TIR non calcolabile.")

                    st.markdown("---")
                    st.markdown("#### Drawdown nel Tempo")
                    dd = ((strategy+1)/(strategy+1).cummax()-1)*100
                    fig_dd = go.Figure()
                    fig_dd.add_trace(go.Scatter(
                        x=dd.index, y=dd, name="Drawdown",
                        fill='tozeroy', line=dict(color='#E74C3C',width=1.5),
                        fillcolor='rgba(231,76,60,0.15)',
                        hovertemplate="%{x|%d %b %Y}<br>Drawdown: %{y:.2f}%<extra></extra>"
                    ))
                    fig_dd.update_layout(**{**PLOTLY_LAYOUT,"xaxis":interactive_xaxis()},
                                         yaxis_title="Drawdown (%)", height=300,
                                         title="Drawdown dalla Massima Equity")
                    st.plotly_chart(fig_dd, use_container_width=True)

                    st.markdown("---")
                    st.markdown("#### Matrice di Correlazione")
                    available = [a for a in valid_assets if a in norm.columns]
                    if len(available) >= 2:
                        import numpy as np
                        corr_df = norm[available].pct_change().dropna().corr()
                        fig_corr = go.Figure(go.Heatmap(
                            z=corr_df.values,
                            x=corr_df.columns.tolist(),
                            y=corr_df.index.tolist(),
                            colorscale=[[0,'#E74C3C'],[0.5,'#0D1F38'],[1,'#2ECC71']],
                            zmin=-1, zmax=1,
                            text=corr_df.round(2).values,
                            texttemplate="%{text}",
                            hovertemplate="%{x} / %{y}: %{z:.2f}<extra></extra>"
                        ))
                        fig_corr.update_layout(**PLOTLY_LAYOUT, height=350,
                                               title="Correlazione tra Asset")
                        st.plotly_chart(fig_corr, use_container_width=True)
                        upper    = corr_df.values[np.triu_indices_from(corr_df.values,k=1)]
                        avg_corr = upper.mean() if len(upper)>0 else 0
                    else:
                        avg_corr = None

                    st.markdown("---")
                    st.markdown("#### 💡 Analisi e Suggerimenti Specifici")
                    suggestions = []

                    if sharpe < 0:
                        suggestions.append(
                            f"🔴 <b>Sharpe negativo ({sharpe:.2f})</b> — Il portafoglio sta distruggendo valore "
                            f"rispetto al risk-free. Con volatilità {vol:.1f}% e rendimento negativo stai assumendo "
                            f"rischio senza compensazione. Individua l'asset con il peggior contributo dal grafico "
                            f"e considera di sostituirlo con un ETF a bassa volatilità (USMV, SPLV)."
                        )
                    elif sharpe < 0.5:
                        suggestions.append(
                            f"📉 <b>Sharpe inefficiente ({sharpe:.2f})</b> — Per ogni punto di volatilità ottieni "
                            f"solo {sharpe*vol/100:.2f}% di rendimento extra. Aggiungere asset decorrelati come "
                            f"oro (correlazione storica con S&P ~0.0), TIPS inflation-linked o REITs internazionali "
                            f"potrebbe migliorare lo Sharpe senza ridurre il rendimento atteso."
                        )
                    elif sharpe >= 1.5:
                        suggestions.append(
                            f"🏆 <b>Sharpe eccellente ({sharpe:.2f})</b> — Attenzione al survivorship bias: "
                            f"Sharpe così alti tendono a normalizzarsi. Verifica se il periodo include il bull "
                            f"market 2020-2024. Testa la strategia su 15-20 anni per una stima più robusta."
                        )
                    else:
                        suggestions.append(
                            f"✅ <b>Sharpe accettabile ({sharpe:.2f})</b> — Profilo rischio/rendimento nella norma. "
                            f"Obiettivo ottimale: superare 1.0 per battere costantemente il mercato su base risk-adjusted."
                        )

                    if vol > 25:
                        suggestions.append(
                            f"📊 <b>Volatilità molto alta ({vol:.1f}% vs ~16% S&P storico)</b> — "
                            f"In uno scenario stress tipo 2008 potresti sperimentare drawdown >50%. "
                            f"Ogni 1% di vol extra rispetto al benchmark richiede +0.1 Sharpe per giustificarsi. "
                            f"Valuta 15-20% in obbligazioni aggregate (AGG) o asset reali."
                        )
                    elif vol > 15:
                        suggestions.append(
                            f"📊 <b>Volatilità in linea con l'azionario ({vol:.1f}%)</b> — "
                            f"Con orizzonte <7 anni considera un buffer 20-30% in bond. "
                            f"Con orizzonte >10 anni la volatilità attuale è accettabile."
                        )

                    if drawdown < -40:
                        suggestions.append(
                            f"⚠️ <b>Drawdown estremo ({drawdown:.1f}%)</b> — Per tornare al pareggio dal minimo "
                            f"servono {abs(drawdown)/(100+drawdown)*100:.1f}%. Il Nasdaq ha impiegato 15 anni "
                            f"a recuperare dal -78% del 2000-2002. Analizza quale asset ha generato il drawdown "
                            f"maggiore e considera un position sizing proporzionale al rischio (Kelly Criterion)."
                        )
                    elif drawdown < -20:
                        suggestions.append(
                            f"⚠️ <b>Drawdown significativo ({drawdown:.1f}%)</b> — "
                            f"Per recuperare servono {abs(drawdown)/(100+drawdown)*100:.1f}% dal minimo. "
                            f"Un ribilanciamento trimestrale sistematico riduce il drawdown medio del 15-25% "
                            f"su orizzonti lunghi senza sacrificare rendimento."
                        )

                    if len(valid_assets) < 3:
                        suggestions.append(
                            f"🔀 <b>Concentrazione elevata ({len(valid_assets)} asset)</b> — "
                            f"Con 2 soli asset il rischio idiosincratico pesa ancora molto. "
                            f"Fama-French mostra che gran parte dei benefici si ottiene con 8-15 asset non correlati. "
                            f"Considera small-cap value (VBR), mercati emergenti (VWO) o commodities (PDBC) "
                            f"per catturare premi di rischio aggiuntivi."
                        )

                    if avg_corr is not None and avg_corr > 0.7:
                        suggestions.append(
                            f"🔗 <b>Correlazione media alta ({avg_corr:.2f})</b> — Gli asset si muovono in modo "
                            f"molto simile, riducendo i benefici della diversificazione. In un sell-off generalizzato "
                            f"scenderebbero tutti insieme. Considera oro (GLD), Treasury lunghi (TLT) o volatilità (VXX) "
                            f"per asset con correlazione negativa o nulla."
                        )
                    elif avg_corr is not None and avg_corr < 0.2:
                        suggestions.append(
                            f"🌐 <b>Ottima decorrelazione (corr. media: {avg_corr:.2f})</b> — "
                            f"Il portafoglio è ben diversificato in termini di correlazione, "
                            f"uno dei fattori più importanti per la resilienza in fasi di stress."
                        )

                    if delta_vs_bench is not None and delta_vs_bench < -5:
                        suggestions.append(
                            f"🔴 <b>Sottoperformance rilevante vs {bench_name} ({delta_vs_bench:+.1f}%)</b> — "
                            f"Stai pagando un costo opportunità significativo. Prima di modificare la strategia "
                            f"verifica se la sottoperformance è concentrata in un periodo specifico o è strutturale. "
                            f"Se strutturale, un semplice ETF sul benchmark avrebbe fatto meglio a costo zero."
                        )
                    elif delta_vs_bench is not None and delta_vs_bench > 10:
                        suggestions.append(
                            f"🟢 <b>Alpha forte vs {bench_name} ({delta_vs_bench:+.1f}%)</b> — "
                            f"Ottimo risultato, ma alfa così elevati tendono a ridursi per mean reversion. "
                            f"Considera di cristallizzare parte dei guadagni aumentando la quota difensiva, "
                            f"o implementa un trailing stop sull'asset che ha contribuito di più."
                        )

                    if not suggestions:
                        suggestions.append("ℹ️ Parametri nella norma. Nessun segnale critico rilevato.")

                    for sg in suggestions:
                        st.markdown(
                            f"<div style='background:#0D1F38; border-left:3px solid #4A9EFF; "
                            f"border-radius:4px; padding:0.8rem 1rem; margin-bottom:0.6rem; "
                            f"font-size:0.88rem; line-height:1.6;'>{sg}</div>",
                            unsafe_allow_html=True
                        )

            except Exception as e:
                st.error(f"Errore durante il backtest: {e}")

    elif run and total_weight != 100:
        st.error("Correggi i pesi prima di eseguire il backtest (devono sommare a 100%).")


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
        page_title(f"⌨️  Analisi Dettagliata — {target}")
        show_bloomberg_insights(target)

    else:
        page_title("🔍  Stock Screener", "Filtra aziende per fondamentali e identifica opportunità")

        UNIVERSE = [
            "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","BRK-B","JPM","V",
            "UNH","XOM","JNJ","PG","MA","HD","ABBV","MRK","CVX","PEP","KO","AVGO",
            "COST","WMT","BAC","MCD","CSCO","ACN","LIN","TMO","DHR","NEE","AMD",
            "INTC","QCOM","TXN","AMAT","LRCX","ASML","TSM","NVO",
            "MC.PA","TTE.PA","SAN.PA","SAP.DE","BMW.DE","SIE.DE",
            "ENI.MI","ENEL.MI","UCG.MI","ISP.MI","STLAM.MI","RACE.MI","ATL.MI"
        ]

        st.markdown("#### Parametri di Filtro")
        c1,c2,c3 = st.columns(3)
        with c1:
            pe_max       = st.slider("P/E massimo",               0,200,50)
            pb_max       = st.slider("P/B massimo",               0, 30,10)
            ps_max       = st.slider("P/S massimo",               0, 50,15)
        with c2:
            cap_min      = st.slider("Market Cap min (B$)",       0,500,10)
            de_max       = st.slider("Debt/Equity massimo",       0, 10, 3)
            margin_min   = st.slider("Margine Operativo min (%)",-50, 60, 5)
        with c3:
            roic_min     = st.slider("ROIC min (%)",             -20, 60, 5)
            evebitda_max = st.slider("EV/EBITDA massimo",          0, 80,25)
            sector_filter= st.selectbox("Settore",[
                "Tutti","Technology","Healthcare","Financials","Industrials",
                "Consumer Defensive","Consumer Cyclical","Energy",
                "Communication Services","Utilities","Real Estate","Basic Materials"
            ])

        product_filter = st.text_input(
            "Filtra per prodotto / servizio / business (lascia vuoto per ignorare)", "",
            placeholder="Es: cloud, semiconductor, oil, insurance, electric vehicle, pharma..."
        )
        custom_in = st.text_input("Aggiungi ticker custom all'universo (separati da virgola)", "")
        if custom_in.strip():
            UNIVERSE = list(set(UNIVERSE+[x.strip().upper() for x in custom_in.split(",") if x.strip()]))

        run_screen = st.button("▶  Esegui Screening", use_container_width=True)

        if run_screen:
            results  = []
            progress = st.progress(0)
            status   = st.empty()
            for i, tkr in enumerate(UNIVERSE):
                progress.progress((i+1)/len(UNIVERSE))
                status.markdown(f"<span style='color:#A8BDD4;font-size:0.8rem;'>Analisi: {tkr} ({i+1}/{len(UNIVERSE)})</span>",
                                unsafe_allow_html=True)
                try:
                    info = get_ticker_info(tkr)
                    if not info: continue
                    pe        = info.get('forwardPE') or info.get('trailingPE')
                    pb        = info.get('priceToBook')
                    ps        = info.get('priceToSalesTrailing12Months')
                    mcap      = info.get('marketCap')
                    de        = info.get('debtToEquity')
                    op_margin = info.get('operatingMargins')
                    roic      = info.get('returnOnEquity')
                    ev_ebitda = info.get('enterpriseToEbitda')
                    sector_v  = info.get('sector','')
                    name      = info.get('shortName', tkr)
                    price     = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')

                    if sector_filter != "Tutti" and sector_v != sector_filter: continue
                    if product_filter.strip():
                        kw = product_filter.strip().lower()
                        txt= ((info.get('longBusinessSummary') or '')+" "+
                              (info.get('industry') or '')+" "+
                              (info.get('longName') or '')+" "+
                              (info.get('sector') or '')).lower()
                        if kw not in txt: continue
                    if pe        is not None and pe           > pe_max:       continue
                    if pb        is not None and pb           > pb_max:       continue
                    if ps        is not None and ps           > ps_max:       continue
                    if de        is not None and de/100       > de_max:       continue
                    if ev_ebitda is not None and ev_ebitda    > evebitda_max: continue
                    if mcap      is not None and mcap/1e9     < cap_min:      continue
                    if op_margin is not None and op_margin*100< margin_min:   continue
                    if roic      is not None and roic*100     < roic_min:     continue

                    results.append({
                        "Ticker":      tkr,
                        "Nome":        name,
                        "Settore":     sector_v,
                        "Prezzo":      f"{price:.2f}"         if price     else "N/A",
                        "P/E":         f"{pe:.1f}"            if pe        else "N/A",
                        "P/B":         f"{pb:.1f}"            if pb        else "N/A",
                        "P/S":         f"{ps:.1f}"            if ps        else "N/A",
                        "EV/EBITDA":   f"{ev_ebitda:.1f}"     if ev_ebitda else "N/A",
                        "Op.Margin %": f"{op_margin*100:.1f}" if op_margin else "N/A",
                        "ROE %":       f"{roic*100:.1f}"      if roic      else "N/A",
                        "D/E (x)":     f"{de/100:.2f}"        if de        else "N/A",
                        "Cap (B$)":    f"{mcap/1e9:.1f}"      if mcap      else "N/A",
                    })
                except Exception:
                    continue
            progress.empty(); status.empty()
            st.session_state.screener_results = results if results else []

        if st.session_state.screener_results:
            results = st.session_state.screener_results
            st.success(f"✅  {len(results)} aziende trovate")
            st.markdown("---")
            st.dataframe(pd.DataFrame(results).set_index("Ticker"), use_container_width=True)
            st.markdown("#### Analizza un'azienda in dettaglio")
            sel = st.selectbox("Seleziona azienda",
                               [f"{r['Ticker']} — {r['Nome']}" for r in results],
                               key="screener_select_box")
            if st.button("🔎  Apri Analisi Dettagliata", use_container_width=True):
                st.session_state.screener_selected = sel.split(" — ")[0].strip()
                st.rerun()
        elif st.session_state.screener_results is not None and len(st.session_state.screener_results)==0:
            st.warning("Nessuna azienda trovata. Prova ad allargare i parametri.")


# =========================================================
# 6. BLOOMBERG INSIGHTS
# =========================================================
elif choice == "Bloomberg Insights":
    page_title("⌨️  Company Terminal Insights", "Analisi fondamentale, notizie, supply chain e peer comparison")
    target = st.text_input("Ticker principale", "NVDA",
                           placeholder="Es: AAPL, MSFT, MC.PA, ENI.MI ...").strip().upper()
    if target:
        show_bloomberg_insights(target)

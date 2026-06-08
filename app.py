"""
╔══════════════════════════════════════════════════════════╗
║        NAVY TERMINAL PRO  v5.0  ·  Bloomberg-Grade       ║
║  Full-stack financial intelligence platform              ║
╚══════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings, math, json
warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NAVY TERMINAL PRO",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚓",
)

# ══════════════════════════════════════════════════════════
#  GLOBAL CSS — Bloomberg dark with amber accent
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

/* ── BASE ── */
html,body,.stApp,[data-testid="stAppViewContainer"],.main,.block-container {
  background-color:#050D1A!important;
  font-family:'IBM Plex Sans',sans-serif!important;
}
.block-container{padding-top:1rem!important;padding-bottom:2rem!important;max-width:100%!important}

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{background-color:#030A14!important;border-right:1px solid #0D2137!important;min-height:100vh!important}
[data-testid="stSidebar"] *{color:#C8D8EC!important}
[data-testid="stHeader"]{background-color:#020810!important;border-bottom:1px solid #0D2137!important}

/* ── TYPOGRAPHY ── */
h1,h2,h3,h4,h5,h6{color:#FFFFFF!important;font-family:'IBM Plex Mono',monospace!important;font-weight:600!important;letter-spacing:0.04em!important}
p,span,li,.stMarkdown{color:#C8D8EC!important;font-family:'IBM Plex Sans',sans-serif!important}

/* ── METRICS ── */
[data-testid="stMetricValue"]{color:#FFFFFF!important;font-family:'IBM Plex Mono',monospace!important;font-weight:700!important;font-size:1.1rem!important}
[data-testid="stMetricLabel"]{color:#5A88B0!important;font-size:0.65rem!important;text-transform:uppercase;letter-spacing:0.12em!important;font-family:'IBM Plex Mono',monospace!important}
[data-testid="metric-container"]{background:linear-gradient(160deg,#061528 0%,#091E35 100%)!important;border:1px solid #0D2137!important;border-top:2px solid #1E4976!important;border-radius:2px!important;padding:0.75rem 1rem!important}
[data-testid="stMetricDelta"] svg{display:none!important}
[data-testid="stMetricDelta"]{font-family:'IBM Plex Mono',monospace!important;font-size:0.72rem!important;font-weight:600!important}

/* ── INPUTS ── */
.stTextInput label,.stSelectbox label,.stMultiSelect label,.stSlider label,.stNumberInput label,.stRadio label,.stCheckbox label,label[data-testid]{
  color:#5A88B0!important;font-size:0.66rem!important;font-weight:600!important;
  letter-spacing:0.1em!important;text-transform:uppercase!important;
  font-family:'IBM Plex Mono',monospace!important;
}
input[type="text"],textarea,.stTextInput input,.stNumberInput input{
  background-color:#06111F!important;color:#E8F0F8!important;
  border:1px solid #0D2137!important;border-radius:2px!important;
  font-family:'IBM Plex Mono',monospace!important;font-size:0.84rem!important;
}
input[type="text"]:focus,.stTextInput input:focus{border-color:#F5A623!important;box-shadow:0 0 0 1px rgba(245,166,35,0.25)!important}
.stSelectbox [data-baseweb="select"]>div{background-color:#06111F!important;border:1px solid #0D2137!important;color:#E8F0F8!important;border-radius:2px!important}
[data-baseweb="popover"]{background-color:#06111F!important;border:1px solid #0D2137!important}
[data-baseweb="menu"]{background-color:#06111F!important}
[data-baseweb="option"]{background-color:#06111F!important;color:#C8D8EC!important;font-size:0.82rem!important}
[data-baseweb="option"]:hover{background-color:#0D2137!important;color:#FFFFFF!important}
[data-baseweb="option"][aria-selected="true"]{background-color:#122A47!important;color:#F5A623!important;font-weight:600!important}
li[role="option"]{background-color:#06111F!important;color:#C8D8EC!important}
li[role="option"]:hover{background-color:#0D2137!important;color:#FFFFFF!important}
.stRadio>div>label{color:#C8D8EC!important;text-transform:none!important;font-size:0.84rem!important}

/* ── SLIDER ── */
.stSlider [data-baseweb="slider"] [role="slider"]{background-color:#F5A623!important;border-color:#F5A623!important}
.stSlider [data-baseweb="slider"] div[class*="Track"] div:first-child{background-color:#F5A623!important}
.stSlider span{color:#5A88B0!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.68rem!important}

/* ── BUTTONS ── */
.stButton>button{
  background-color:#061528!important;color:#C8D8EC!important;
  border:1px solid #1E4976!important;border-radius:2px!important;
  font-family:'IBM Plex Mono',monospace!important;font-size:0.72rem!important;
  letter-spacing:0.1em!important;transition:all 0.12s ease;padding:0.4rem 1rem!important;
  text-transform:uppercase!important;
}
.stButton>button:hover{background-color:#F5A623!important;color:#050D1A!important;border-color:#F5A623!important;font-weight:700!important}

/* ── TABLES ── */
.dataframe,table{background-color:#06111F!important;color:#E8F0F8!important;border-collapse:collapse!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.76rem!important}
thead tr th{color:#5A88B0!important;background-color:#030A14!important;border-bottom:1px solid #0D2137!important;text-transform:uppercase;letter-spacing:0.08em;padding:0.45rem 0.8rem!important;font-size:0.62rem!important}
tbody tr td{color:#C8D8EC!important;border-bottom:1px solid #091827!important;padding:0.38rem 0.8rem!important}
tbody tr:hover td{background-color:#0D2137!important;color:#FFFFFF!important}
tbody tr:first-child td{color:#F5A623!important}

/* ── SCROLLBAR ── */
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:#020810}
::-webkit-scrollbar-thumb{background:#0D2137;border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:#F5A623}

/* ── CUSTOM COMPONENTS ── */
.nav-title{font-family:'IBM Plex Mono',monospace;font-size:1.5rem;font-weight:700;color:#FFFFFF;letter-spacing:0.3em;text-align:center}
.nav-sub{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:#F5A623;letter-spacing:0.55em;text-align:center;margin-top:2px}
.nav-divider{height:1px;background:linear-gradient(90deg,transparent,#F5A623,transparent);margin:0.9rem 0}

.page-title{font-family:'IBM Plex Mono',monospace!important;font-size:1.25rem;font-weight:700;color:#FFFFFF!important;letter-spacing:0.06em;border-left:3px solid #F5A623;padding-left:1rem;margin-bottom:0.2rem}
.page-sub{color:#5A88B0!important;font-size:0.72rem;margin-bottom:1.2rem;padding-left:1.3rem;letter-spacing:0.06em;font-family:'IBM Plex Mono',monospace}

.sec-hdr{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#F5A623;letter-spacing:0.3em;text-transform:uppercase;margin:1.2rem 0 0.6rem 0;border-bottom:1px solid #0D2137;padding-bottom:0.3rem}

.ticker-card{background:linear-gradient(160deg,#061528,#091E35);border:1px solid #0D2137;border-top:2px solid #F5A623;border-radius:2px;padding:1.2rem 1.6rem;margin-bottom:1rem}
.ticker-tag{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#F5A623;letter-spacing:0.32em;margin-bottom:6px}
.ticker-name{font-size:1.45rem;font-weight:700;color:#FFFFFF;line-height:1.2;font-family:'IBM Plex Sans',sans-serif}
.ticker-meta{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#5A88B0;margin-top:4px}
.ticker-price{font-family:'IBM Plex Mono',monospace;font-size:1.85rem;font-weight:700;color:#FFFFFF;text-align:right}

.mover-card{background:linear-gradient(160deg,#061528,#091E35);border:1px solid #0D2137;border-radius:2px;padding:0.55rem 0.9rem;margin-bottom:0.3rem;display:flex;justify-content:space-between;align-items:center}

.term-box{background:#020810;border:1px solid #0D2137;border-radius:2px;padding:0.85rem 1.1rem;font-family:'IBM Plex Mono',monospace;font-size:0.78rem;color:#C8D8EC;margin-bottom:0.75rem}

.alert-box{background:linear-gradient(160deg,#061528,#091E35);border-left:3px solid #F5A623;border-radius:2px;padding:0.7rem 1rem;margin-bottom:0.4rem;font-size:0.83rem;color:#C8D8EC;line-height:1.7}

.kpi-positive{color:#2ECC71!important;font-weight:700!important}
.kpi-negative{color:#E74C3C!important;font-weight:700!important}
.kpi-neutral{color:#F5A623!important;font-weight:700!important}

.kbd{background:#0D2137;border:1px solid #1E4976;border-radius:2px;padding:1px 5px;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#C8D8EC}

.stProgress>div>div{background-color:#F5A623!important}

/* ── TABS ── */
[data-testid="stTabs"] [role="tab"]{font-family:'IBM Plex Mono',monospace!important;font-size:0.68rem!important;letter-spacing:0.12em!important;text-transform:uppercase!important;color:#5A88B0!important;background:transparent!important;border:none!important;padding:0.5rem 1rem!important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{color:#F5A623!important;border-bottom:2px solid #F5A623!important}
[data-testid="stTabsContent"]{padding-top:1rem!important}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════
_NOT_RUN = "__NOT_RUN__"
_DEFAULTS = dict(
    page="Market Overview",
    screener_selected=None,
    screener_results=_NOT_RUN,
    terminal_ticker="NVDA",
    terminal_peers="AMD, INTC, AVGO, QCOM, SMCI",
    watchlist=["AAPL","NVDA","ASML.AS","ENI.MI","MC.PA","RACE.MI","MSFT","AMZN"],
    alerts=[],
    portfolio_notes="",
)
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:1.2rem 0 0.8rem 0'>
      <div class='nav-title'>⚓ NAVY</div>
      <div class='nav-sub'>TERMINAL PRO · v5.0</div>
      <div class='nav-divider'></div>
    </div>""", unsafe_allow_html=True)

    MENU = [
        ("MKT","Market Overview"),
        ("WL", "Watchlist"),
        ("TRM","Company Terminal"),
        ("CRT","Charts & Technical"),
        ("DCF","DCF Valuation"),
        ("CMP","Multi-Compare"),
        ("BKT","Portfolio Backtest"),
        ("SCR","Stock Screener"),
        ("MAC","Macro & Fixed Income"),
        ("OPT","Options & Derivatives"),
        ("FX", "FX & Commodities"),
        ("ECO","Economic Calendar"),
    ]

    for code, label in MENU:
        active = st.session_state.page == label
        style  = "background:#0F2A47!important;border-left:2px solid #F5A623;" if active else ""
        st.markdown(f"<style>#nav_{code} button{{{style}}}</style>", unsafe_allow_html=True)
        st.markdown(f"<span id='nav_{code}'></span>", unsafe_allow_html=True)
        if st.button(
            f"{'▶' if active else '·'}  {code}  {label}",
            key=f"nav_btn_{code}",
            use_container_width=True,
        ):
            st.session_state.page = label
            st.rerun()

    st.markdown("""
    <div style='margin-top:2rem;padding:0 0.5rem'>
      <div style='height:1px;background:linear-gradient(90deg,transparent,#0D2137,transparent);margin-bottom:0.7rem'></div>
      <div style='font-family:IBM Plex Mono,monospace;font-size:0.48rem;color:#1A3A5C;text-align:center;letter-spacing:0.14em;line-height:2'>
        LIVE DATA · YFINANCE API<br>
        v5.0 · NAVY TERMINAL PRO<br>
        ⚓ PROFESSIONAL EDITION
      </div>
    </div>""", unsafe_allow_html=True)

choice = st.session_state.page

# ══════════════════════════════════════════════════════════
#  LAYOUT HELPERS
# ══════════════════════════════════════════════════════════
def ptitle(text: str, sub: str = ""):
    st.markdown(f"<div class='page-title'>{text}</div>", unsafe_allow_html=True)
    if sub:
        st.markdown(f"<div class='page-sub'>{sub}</div>", unsafe_allow_html=True)

def sec(text: str):
    st.markdown(f"<div class='sec-hdr'>{text}</div>", unsafe_allow_html=True)

def alert(html: str):
    st.markdown(f"<div class='alert-box'>{html}</div>", unsafe_allow_html=True)

def colored(val, positive_above=0, fmt="{:.2f}%"):
    if val is None: return "<span style='color:#5A88B0'>N/A</span>"
    col = "#2ECC71" if val > positive_above else ("#E74C3C" if val < positive_above else "#F5A623")
    return f"<span style='color:{col};font-weight:700'>{fmt.format(val)}</span>"

COLORS = [
    "#F5A623","#3B8EF0","#2ECC71","#E74C3C","#9B59B6","#1ABC9C",
    "#E67E22","#EC407A","#00BCD4","#8BC34A","#FF7043","#AB47BC",
    "#26C6DA","#66BB6A","#FFA726","#EF5350","#7E57C2","#26A69A",
]

def _deep_merge(base, over):
    r = dict(base)
    for k, v in over.items():
        r[k] = _deep_merge(r[k], v) if isinstance(v, dict) and isinstance(r.get(k), dict) else v
    return r

PLOTLY_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(2,8,16,0)",
    plot_bgcolor="rgba(6,17,31,0.85)",
    font=dict(color="#C8D8EC", family="IBM Plex Mono, monospace", size=10),
    legend=dict(bgcolor="rgba(3,10,20,0.92)", bordercolor="#0D2137", borderwidth=1, font=dict(size=9)),
    margin=dict(l=52, r=20, t=44, b=40),
    hovermode="x unified",
    dragmode="zoom",
    hoverlabel=dict(bgcolor="#06111F", bordercolor="#F5A623", font=dict(family="IBM Plex Mono", color="#E8F0F8")),
)

def pla(overrides=None):
    return _deep_merge(PLOTLY_BASE, overrides) if overrides else dict(PLOTLY_BASE)

def xaxis_time(bar=False):
    d = dict(
        gridcolor="#091827", showgrid=True, zeroline=False,
        rangeselector=dict(
            bgcolor="#06111F", activecolor="#F5A623", bordercolor="#0D2137",
            font=dict(color="#FFFFFF", size=9),
            buttons=[
                dict(count=5,  label="5D",  step="day",   stepmode="backward"),
                dict(count=1,  label="1M",  step="month", stepmode="backward"),
                dict(count=3,  label="3M",  step="month", stepmode="backward"),
                dict(count=6,  label="6M",  step="month", stepmode="backward"),
                dict(count=1,  label="1Y",  step="year",  stepmode="backward"),
                dict(count=3,  label="3Y",  step="year",  stepmode="backward"),
                dict(count=5,  label="5Y",  step="year",  stepmode="backward"),
                dict(count=10, label="10Y", step="year",  stepmode="backward"),
                dict(count=20, label="20Y", step="year",  stepmode="backward"),
                dict(step="all", label="MAX"),
            ],
        ),
    )
    if not bar:
        d["rangeslider"] = dict(visible=True, bgcolor="#020810", thickness=0.035)
    return d

def yaxis_plain():
    return dict(gridcolor="#091827", showgrid=True, zeroline=False)

# ══════════════════════════════════════════════════════════
#  DATA LAYER  (all cached)
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=180, show_spinner=False)
def get_info(tkr: str) -> dict:
    try:
        info = yf.Ticker(tkr).info
        if not info or len(info) < 4:
            return {}
        if not any(info.get(k) for k in ["regularMarketPrice","currentPrice","previousClose","longName","shortName"]):
            return {}
        return info
    except Exception:
        return {}

@st.cache_data(ttl=180, show_spinner=False)
def get_close(tkr: str, start=None, period=None) -> pd.Series:
    try:
        t = yf.Ticker(tkr)
        raw = t.history(period=period) if period else t.history(start=start)
        if raw.empty: return pd.Series(dtype=float, name=tkr)
        s = raw["Close"].squeeze()
        if hasattr(s.index,"tz") and s.index.tz:
            s.index = s.index.tz_localize(None)
        return s.rename(tkr)
    except Exception:
        return pd.Series(dtype=float, name=tkr)

@st.cache_data(ttl=90, show_spinner=False)
def get_ohlcv(tkr: str, period="1y", interval="1d") -> pd.DataFrame:
    try:
        df = yf.Ticker(tkr).history(period=period, interval=interval)
        if hasattr(df.index,"tz") and df.index.tz:
            df.index = df.index.tz_localize(None)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=90, show_spinner=False)
def get_price_chg(tkr: str):
    try:
        d = yf.Ticker(tkr).history(period="2d")
        if len(d) >= 2:
            c,p = float(d["Close"].iloc[-1]), float(d["Close"].iloc[-2])
            return c, (c-p)/p*100
        elif len(d) == 1:
            return float(d["Close"].iloc[-1]), None
        return None, None
    except Exception:
        return None, None

@st.cache_data(ttl=600, show_spinner=False)
def get_financials(tkr: str) -> dict:
    """Returns dict of DataFrames: income, balance, cashflow (annual+quarterly)"""
    try:
        t = yf.Ticker(tkr)
        return {
            "income_a":   getattr(t, "income_stmt",         pd.DataFrame()),
            "income_q":   getattr(t, "quarterly_income_stmt",pd.DataFrame()),
            "balance_a":  getattr(t, "balance_sheet",        pd.DataFrame()),
            "balance_q":  getattr(t, "quarterly_balance_sheet",pd.DataFrame()),
            "cashflow_a": getattr(t, "cashflow",             pd.DataFrame()),
            "cashflow_q": getattr(t, "quarterly_cashflow",   pd.DataFrame()),
        }
    except Exception:
        return {}

@st.cache_data(ttl=600, show_spinner=False)
def get_options_chain(tkr: str):
    try:
        t = yf.Ticker(tkr)
        exps = t.options
        if not exps: return None, None, []
        exp = exps[0]
        chain = t.option_chain(exp)
        return chain.calls, chain.puts, list(exps[:12])
    except Exception:
        return None, None, []

@st.cache_data(ttl=300, show_spinner=False)
def get_institutional_holders(tkr: str) -> pd.DataFrame:
    try:
        return yf.Ticker(tkr).institutional_holders or pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_recommendations(tkr: str) -> pd.DataFrame:
    try:
        return yf.Ticker(tkr).recommendations or pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_earnings_dates(tkr: str) -> pd.DataFrame:
    try:
        return yf.Ticker(tkr).earnings_dates or pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def _first_row(df, candidates):
    if df is None or df.empty: return pd.Series(dtype=float)
    for r in candidates:
        if r in df.index:
            s = df.loc[r].dropna()
            s.index = pd.to_datetime(s.index)
            return s.sort_index()
    return pd.Series(dtype=float)

# ══════════════════════════════════════════════════════════
#  TECHNICAL INDICATORS
# ══════════════════════════════════════════════════════════
def add_sma(df, w): return df["Close"].rolling(w).mean()
def add_ema(df, w): return df["Close"].ewm(span=w).mean()

def add_bbands(df, w=20):
    m = df["Close"].rolling(w).mean()
    s = df["Close"].rolling(w).std()
    return m+2*s, m, m-2*s

def add_rsi(df, w=14):
    d = df["Close"].diff()
    g = d.clip(lower=0).rolling(w).mean()
    l = (-d.clip(upper=0)).rolling(w).mean()
    return 100 - 100/(1 + g/l.replace(0, np.nan))

def add_macd(df, fast=12, slow=26, sig=9):
    f = df["Close"].ewm(span=fast).mean()
    s = df["Close"].ewm(span=slow).mean()
    macd = f - s
    signal = macd.ewm(span=sig).mean()
    return macd, signal, macd - signal

def add_stoch(df, k=14, d=3):
    lo = df["Low"].rolling(k).min()
    hi = df["High"].rolling(k).max()
    ks = 100*(df["Close"]-lo)/(hi-lo+1e-10)
    ds = ks.rolling(d).mean()
    return ks, ds

def add_atr(df, w=14):
    hl = df["High"] - df["Low"]
    hc = (df["High"] - df["Close"].shift()).abs()
    lc = (df["Low"]  - df["Close"].shift()).abs()
    tr = pd.concat([hl,hc,lc],axis=1).max(axis=1)
    return tr.rolling(w).mean()

def add_obv(df):
    sign = np.sign(df["Close"].diff().fillna(0))
    return (sign * df["Volume"]).cumsum()

def add_vwap(df):
    tp = (df["High"]+df["Low"]+df["Close"])/3
    return (tp * df["Volume"]).cumsum() / df["Volume"].cumsum()

def add_ichimoku(df):
    h9  = df["High"].rolling(9).max();  l9  = df["Low"].rolling(9).min()
    h26 = df["High"].rolling(26).max(); l26 = df["Low"].rolling(26).min()
    h52 = df["High"].rolling(52).max(); l52 = df["Low"].rolling(52).min()
    tenkan  = (h9 + l9)/2
    kijun   = (h26+l26)/2
    span_a  = ((tenkan+kijun)/2).shift(26)
    span_b  = ((h52+l52)/2).shift(26)
    chikou  = df["Close"].shift(-26)
    return tenkan, kijun, span_a, span_b, chikou

def add_fibonacci(df):
    hi, lo = df["High"].max(), df["Low"].min()
    diff = hi - lo
    levels = {
        "0.0%": hi, "23.6%": hi-0.236*diff, "38.2%": hi-0.382*diff,
        "50.0%": hi-0.5*diff, "61.8%": hi-0.618*diff, "78.6%": hi-0.786*diff, "100%": lo,
    }
    return levels

# ══════════════════════════════════════════════════════════
#  UNIVERSE — ~1500 tickers
# ══════════════════════════════════════════════════════════
CURATED = list(dict.fromkeys([
    # ─── US MEGA CAP ───
    "AAPL","MSFT","NVDA","GOOGL","GOOG","AMZN","META","TSLA","AVGO","JPM",
    "V","UNH","XOM","JNJ","PG","MA","HD","ABBV","MRK","CVX",
    "PEP","KO","LIN","TMO","DHR","AMD","INTC","QCOM","TXN","AMAT",
    "LRCX","MU","ORCL","IBM","CSCO","DELL","ACN","NOW","CRM","ADBE",

    # ─── US TECH ───
    "PANW","FTNT","CRWD","ZS","SNPS","CDNS","ANSS","PTC","EPAM","INTU",
    "NFLX","SPOT","RBLX","UBER","LYFT","ABNB","BKNG","EXPE","TRIP",
    "SNOW","PLTR","COIN","HOOD","SOFI","AFRM","UPST","LC",
    "ARM","SMCI","MRVL","KLAC","MPWR","ONTO","FORM","ACLS","ENTG",
    "DDOG","MDB","GTLB","ESTC","HUBS","TTD","ROKU","SNAP","PINS","DUOL",
    "TWLO","DOCN","CFLT","NET","NTNX","PSTG","ZM","ZI","ASAN","MNDY",
    "APPF","PCTY","PAYC","WEX","BRZE","PATH","AI","SOUN","IONQ","RGTI",
    "VEEV","CSGP","VNET","WK","NCNO","AVDX","RDDT","OKTA","SAIL","CYBR",
    "TENB","QLYS","RBRK","S","RPD","FIVN","NICE","CIEN","VIAV","COHR",
    "GDDY","TWTR","FSLY","ESTC","BIGC","VMEO","TASK","AMPL","DOMO","NCNO",
    "SAMSF","KLIC","LSCC","ALGM","AMBA","CRUS","DIOD","IIVI","IMOS","IPGP",
    "MKSI","OLED","PI","SLAB","UCTT","WOLF","XPERI","SYNA","RMBS","XLNX",

    # ─── US FINANCE ───
    "BAC","WFC","GS","MS","BLK","SCHW","C","USB","PNC","TFC",
    "AXP","COF","DFS","SYF","ALLY","OMF","BX","KKR","APO","CG",
    "ARES","TPG","HLI","LAZ","EVR","PJT","CB","PGR","TRV","AIG",
    "MET","PRU","AFL","ALL","CINF","HIG","FITB","HBAN","RF","CFG",
    "KEY","ZION","CMA","WAL","WBS","BOKF","NDAQ","ICE","CME","CBOE",
    "MKTX","LPLA","RJF","PYPL","SQ","GPN","FIS","FISV","WU","MQ",
    "FOUR","VOYA","LNC","GL","RGA","CNO","AIZ","EQH","EWBC","FFIN",
    "IBOC","CVBF","UBSI","FULT","GBCI","SDFG","PACW","SIVB","NYCB","FRBK",
    "NTRS","STT","BK","TROW","IVZ","AMG","FHN","HOMB","BPOP","INDB",
    "SFNC","SBCF","TOWN","SRCE","MGRC","MCO","SPGI","VRSK","MSCI","FactSet",

    # ─── US HEALTHCARE ───
    "LLY","ABBV","JNJ","MRK","PFE","BMY","AMGN","GILD","REGN","VRTX",
    "BIIB","ILMN","IQV","TMO","DHR","A","BDX","BSX","MDT","SYK",
    "EW","ZBH","BAX","IDXX","HOLX","ISRG","ALGN","DXCM","PODD","INSP",
    "MRNA","NVAX","BNTX","ARCT","CRSP","EDIT","NTLA","BEAM","FATE","BLUE",
    "ALNY","IONS","SRPT","RARE","BMRN","NBIX","JAZZ","ACAD","SAGE","INVA",
    "EXAS","NTRA","SDGR","RXRX","RVMD","KYMR","KROS","MCK","ABC","CAH",
    "CVS","CI","HUM","ELV","MOH","CNC","RMD","OMCL","MASI","MMSI",
    "NVCR","GKOS","QDEL","PRGO","LMNX","AXNX","OFIX","HALO","LGND",
    "RGEN","TDOC","ACMR","ACST","AKBA","ALDX","ALLO","ALRN","AMRN","ARWR",

    # ─── US CONSUMER ───
    "COST","WMT","TGT","DG","DLTR","KR","SFM","BJ","GO","FIVE",
    "NKE","LULU","UAA","PVH","RL","TPR","CPRI","VFC","HBI","SKX",
    "MCD","SBUX","YUM","CMG","DPZ","QSR","WEN","TXRH","SHAK","JACK",
    "CL","CHD","CLX","EL","KHC","GIS","CPB","CAG","MKC","SJM",
    "KO","PEP","MNST","CELH","KDP","FIZZ","STZ","TAP","BF-B","DEO",
    "PG","KVUE","F","GM","RIVN","LCID","STLA","HOG","LKQ","DORMAN",
    "LOW","HD","SHW","MAS","FBHS","TREX","AZEK","BECN","BLDR","IBP",
    "BBY","ETSY","EBAY","CHWY","W","RH","PTON","CROX","ONON","DECK",
    "MAR","HLT","IHG","WH","H","APLE","PK","RHP","SHO","HST",
    "RACE","LCNB","AN","PAG","KMX","LAD","ABG","CVNA","DRVN","RUSHA",

    # ─── US INDUSTRIALS ───
    "GE","HON","MMM","EMR","ETN","PH","ROK","AME","FTV","XYL",
    "BA","RTX","LMT","NOC","GD","LHX","HII","TDG","HWM","CW",
    "CAT","DE","PCAR","AGCO","CNH","OSK","TEX","GNRC","ALLE","CARR",
    "OTIS","IR","JCI","TT","VRT","AAON","BWXT","AXON","CACI","LDOS",
    "BAH","SAIC","DRS","KTOS","MRCY","MOOG","UPS","FDX","CHRW","EXPD",
    "XPO","SAIA","ODFL","JBHT","HUBG","WERN","WM","RSG","CWST","SRCL",
    "CLH","ECOLAB","IDEX","GRACO","WATTS","HEICO","TXT","AVAV","JOBY","ACHR",
    "SPCE","MAXN","RRX","NPO","GNSS","VSEC","DRS","WMS","DNOW","ITRI",
    "AZZ","ACCO","NWPX","ARIS","GFF","ESE","ESAB","FLOW","FELE","REXNORD",
    "SPR","KFRC","MAN","KELYA","HSII","DHX","HURN","FWRD","ECHO","MRTN",

    # ─── US ENERGY ───
    "XOM","CVX","COP","EOG","OXY","DVN","MRO","APA","FANG","PR",
    "SLB","HAL","BKR","NOV","HP","RIG","VAL","NE","PD","WHD",
    "MPC","PSX","VLO","DKL","HFC","DINO","PARR","KMI","WMB","ET",
    "MPLX","PAA","OKE","LNG","CQP","TRGP","AM","CEG","TLN","CCJ",
    "NNE","OKLO","SMR","VST","NRG","AES","ENPH","FSLR","SEDG","RUN",
    "NOVA","ARRY","SHLS","STEM","CVE","SU","CNQ","TRP","ENB","CTRA",
    "PXD","HES","MTDR","CIVI","PDCE","SM","CPE","ESTE","BATL","REI",
    "TALO","VTLE","DMLP","SBOW","ERF","BTE","ARX","WCP","POU","TVE",

    # ─── US REAL ESTATE & UTILITIES ───
    "AMT","PLD","EQIX","CCI","PSA","SPG","O","WELL","DLR","VTR",
    "AVB","EQR","INVH","AMH","NNN","WPC","STAG","VICI","GLPI","HST",
    "NEE","DUK","SO","AEP","EXC","XEL","ED","WEC","DTE","PPL",
    "AWK","CMS","LNT","EVRG","AVA","NWE","OGE","PNW","SRE","D",
    "PCG","EIX","ETR","CNP","NI","WTRG","SJW","MSEX","YORW","ARTNA",
    "NLY","AGNC","TWO","RITM","ACRE","GPMT","ABR","RC","KREF","TRTX",

    # ─── US MATERIALS ───
    "NEM","GOLD","AEM","KGC","FNV","WPM","PAAS","CDE","HL","EXK",
    "FCX","SCCO","AA","CENX","MP","ALB","SQM","LTHM","LIVENT","NOVS",
    "DD","DOW","LYB","CE","OLN","WLK","EMN","HUN","AXTA","PPG",
    "NUE","STLD","CLF","X","CMC","ATI","HAYN","KALU","RYI","ZEUS",
    "APD","LIN","ECL","IFF","RPM","SHW","BALL","PKG","IP","SEE",
    "SLGN","SON","IOSP","MTRN","TROX","HXL","CRS","ASIX","BERY","GEF",

    # ─── US MEDIA & GAMING ───
    "DIS","CMCSA","NFLX","WBD","PARA","FOX","FOXA","NYT","NWSA","IAC",
    "EA","TTWO","RBLX","DKNG","PENN","MGM","WYNN","LVS","CZR","BYD",
    "CHDN","SRAD","GENI","HIMS","ONON","SPOT","SONO","CARG","CARS",
    "IACI","SSTK","GCI","FUBO","AMC","CNK","IMAX","IPG","OMC","WPP",
    "PUBM","MGNI","DV","IAS","DoubleVerify","ZETA","ACXM","TBLA","OUTBRAIN",

    # ─── US ETF CORE ───
    "SPY","QQQ","IWM","VOO","VTI","VEA","VWO","VXUS","EFA","EEM",
    "GLD","SLV","IAU","GDX","GDXJ","USO","UNG","DBA","PDBC","DBB",
    "TLT","IEF","SHY","AGG","BND","HYG","JNK","LQD","MBB","BNDX",
    "TIP","EMB","VGIT","VCIT","VCSH","BSV","IGIB","IGSB","FLOT","NEAR",
    "XLK","XLF","XLV","XLE","XLI","XLP","XLU","XLB","XLRE","XLC","XLY",
    "ARKK","ARKQ","ARKG","ARKW","SOXL","SOXS","TQQQ","UVXY","VXX","UVXY",
    "VIG","SCHD","DVY","VYM","NOBL","QUAL","MTUM","VLUE","USMV","SIZE",
    "IBIT","GBTC","BITO","ARKB","BTCO","EZBC","HODL",

    # ─── US CRYPTO ───
    "BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD","ADA-USD",
    "DOGE-USD","AVAX-USD","DOT-USD","LINK-USD","LTC-USD",
    "MATIC-USD","UNI-USD","ATOM-USD","FIL-USD","NEAR-USD",
    "ALGO-USD","VET-USD","ICP-USD","FTM-USD","SAND-USD","MANA-USD",
    "MARA","RIOT","CLSK","CORZ","IREN","BTBT","HUT","CIFR",

    # ─── GERMANY ───
    "SAP.DE","SIE.DE","BAYN.DE","BMW.DE","MBG.DE","ALV.DE","BAS.DE",
    "VOW3.DE","DTE.DE","RWE.DE","HEN3.DE","DBK.DE","ADS.DE","AIR.DE",
    "FRE.DE","HAG.DE","MTX.DE","PUM.DE","ZAL.DE","1COV.DE","IFX.DE",
    "DHER.DE","QGEN.DE","EVK.DE","SHL.DE","PAH3.DE","MRK.DE","SRT3.DE",
    "DWS.DE","LEG.DE","VNA.DE","FNTN.DE","NDA.DE","ENR.DE","HLAG.DE",
    "TUI1.DE","LHA.DE","FRA.DE","DPW.DE","MTU.DE","HEI.DE","HOT.DE",
    "KBX.DE","DKGR.DE","AIXA.DE","EVNK.DE","NDX1.DE","XONA.DE",

    # ─── FRANCE ───
    "MC.PA","TTE.PA","SAN.PA","BNP.PA","AXA.PA","OR.PA","SU.PA",
    "DG.PA","EL.PA","KER.PA","RMS.PA","STMPA.PA","AIR.PA","CAP.PA",
    "VIE.PA","DSY.PA","SGO.PA","SW.PA","URW.PA","BN.PA","EN.PA",
    "ML.PA","SK.PA","LR.PA","CS.PA","ATO.PA","BOL.PA","RNO.PA",
    "STM.PA","FP.PA","ERF.PA","ENGI.PA","ORA.PA","PUB.PA","RI.PA",
    "GBT.PA","EDEN.PA","MERY.PA","NK.PA","FNAC.PA","EURO.PA","CGG.PA",

    # ─── UK ───
    "HSBA.L","BP.L","SHEL.L","AZN.L","GSK.L","ULVR.L","RIO.L",
    "BARC.L","LLOY.L","NWG.L","BT-A.L","VOD.L","REL.L","EXPN.L",
    "CRH.L","DGE.L","IMB.L","ABF.L","WTB.L","SMT.L","LSEG.L",
    "STAN.L","HLMA.L","RKT.L","MNDI.L","BATS.L","FERG.L","AUTO.L",
    "OCDO.L","JET2.L","IAG.L","EZJ.L","RR.L","BA.L","GFS.L",
    "IHG.L","BNZL.L","SGRO.L","LAND.L","BLND.L","LRE.L","RSA.L",
    "PRU.L","LGEN.L","AVST.L","MNG.L","JUP.L","SLA.L","STJ.L",
    "SMWH.L","WPP.L","IPG.L","SPT.L","BRBY.L","MULB.L","BOO.L",

    # ─── NETHERLANDS & SWITZERLAND ───
    "ASML.AS","PHIA.AS","HEIA.AS","INGA.AS","UNA.AS","WKL.AS","ADYEN.AS",
    "KPN.AS","RAND.AS","NN.AS","BESI.AS","IMCD.AS","AGN.AS","ASM.AS",
    "AKZO.AS","WRT.AS","TKWY.AS","SBMO.AS","NSG.AS","OCI.AS",
    "NESN.SW","ROG.SW","NOVN.SW","ABB.SW","UBS.SW","ZURN.SW","CFR.SW",
    "LOGN.SW","SIKA.SW","GIVN.SW","BARN.SW","SOON.SW","ALC.SW","CSGN.SW",
    "SCMN.SW","PGHN.SW","STMN.SW","VACN.SW","KNIN.SW","LONN.SW","BALN.SW",
    "GEBN.SW","SLHN.SW","SREN.SW","TEMN.SW","DUFN.SW","HOLN.SW","LISP.SW",

    # ─── SPAIN & NORDICS ───
    "ITX.MC","SAN.MC","BBVA.MC","REP.MC","TEF.MC","IBE.MC","CABK.MC",
    "ENG.MC","ACS.MC","FER.MC","NTGY.MC","GRF.MC","AMS.MC","CLNX.MC",
    "EQNR.OL","DNB.OL","MOWI.OL","YAR.OL","TGS.OL","AKER.OL","NHY.OL",
    "ORK.OL","SCATC.OL","SUBC.OL","PGS.OL","BWO.OL","SALM.OL",
    "ERIC-B.ST","SAND.ST","ATCO-A.ST","EVO.ST","SWED-A.ST","SHB-A.ST",
    "SKF-B.ST","VOLV-B.ST","HEXA-B.ST","TEL2-B.ST","INVE-B.ST","SEB-A.ST",
    "NOVO-B.CO","DSV.CO","MAERSK-B.CO","ORSTED.CO","CARL-B.CO","TRYG.CO",
    "NOKIA.HE","NESTE.HE","FORTUM.HE","UPM.HE","KNEBV.HE","STERV.HE",

    # ─── ITALY ───
    "ENI.MI","ENEL.MI","UCG.MI","ISP.MI","STLAM.MI","RACE.MI","ATL.MI",
    "TIT.MI","MB.MI","BMED.MI","PRY.MI","REC.MI","BPER.MI","G.MI",
    "SPM.MI","TEN.MI","A2A.MI","CNHI.MI","LDO.MI","MONC.MI","NEXI.MI",
    "POSTE.MI","ERG.MI","IREN.MI","RECORDATI.MI","REPLY.MI","MAIRE.MI",
    "SFER.MI","AZIMUT.MI","OVS.MI","FINECOBANK.MI","BMPS.MI","PIRC.MI",
    "UNI.MI","BPE.MI","CASS.MI","MFB.MI","IVG.MI","CALT.MI","DIA.MI",

    # ─── JAPAN ───
    "SONY","TM","HMC","MUFG","SMFG","MFG","NTT","NTDOY","ITOCY","MSBHY",
    "TOELY","FUJIY","HTHIY","FANUY","KYOCY","DSNKY","SSDOY","OTSKY","PCRFY",
    "7203.T","6758.T","9984.T","6861.T","8306.T","8316.T","9432.T","6954.T",
    "7267.T","4063.T","6367.T","6501.T","7751.T","8031.T","9433.T","6702.T",
    "4543.T","2802.T","7741.T","4901.T","6971.T","7733.T","4523.T","2914.T",

    # ─── CHINA ───
    "BABA","JD","PDD","BIDU","NIO","LI","XPEV","NTES","TME","IQ",
    "FUTU","TIGR","HTHT","TAL","EDU","RLX","YUMC","SE","GRAB","LAIX",
    "QFIN","LU","NOAH","VNET","CANG","UXIN","RETO","BTCM","FINV","LKCO",
    "0700.HK","9988.HK","3690.HK","0941.HK","2318.HK","1299.HK","0939.HK",
    "1398.HK","3988.HK","0005.HK","2388.HK","0011.HK","1044.HK","0016.HK",

    # ─── INDIA & EMERGING ───
    "INFY","WIT","HDB","IBN","TTM","VEDL","MMYT","RELIANCE.NS","TCS.NS",
    "HDFC.NS","ICICIBANK.NS","HINDUNILVR.NS","ITC.NS","BAJFINANCE.NS",
    "TSM","2330.TW","2317.TW","2454.TW","3008.TW","2308.TW",
    "KB","SHG","055550.KS","005380.KS","000660.KS","035420.KS","051910.KS",
    "VALE","PBR","ITUB","BBDC4.SA","PETR4.SA","MGLU3.SA","MELI","NU",
    "GLOB","PAGS","STNE","CASH3.SA","BPAC11.SA","RENT3.SA","LREN3.SA",
    "SAMSUNG","SAMSF","SSNLF","HMNNF","LGEIY","KSIDF","DSYTF",

    # ─── CANADA ───
    "SHOP","RY","TD","BNS","BMO","CM","ENB","CNQ","SU","TRP",
    "CP","CNR","WCN","CCO","AGI","KL","IMG","FM","TECK","LUN",
    "NTR","MG","ABX","G","OR","WPM","FNV","AEM","SGSVF","ERF",
    "PWT","CVE","MEG","HWX","SOY","ATH","PEY","SPB","VRX","LSPD",

    # ─── AUSTRALIA ───
    "BHP","RIO","FMG","WDS","WBC","CBA","ANZ","NAB","MQG","CSL",
    "XRO","WOW","COL","ALL.AX","QAN.AX","REA.AX","SEK.AX","CAR.AX",
    "WTC.AX","PME.AX","CPU.AX","ASX.AX","STO.AX","ORG.AX","WPL.AX",
    "S32.AX","NCM.AX","OZL.AX","IGO.AX","LYC.AX","MIN.AX","PLS.AX",

    # ─── FX & COMMODITIES (yfinance) ───
    "EURUSD=X","GBPUSD=X","USDJPY=X","USDCHF=X","AUDUSD=X",
    "USDCAD=X","NZDUSD=X","USDCNY=X","USDINR=X","USDBRL=X",
    "GC=F","SI=F","HG=F","CL=F","BZ=F","NG=F","ZC=F","ZS=F","ZW=F",
    "PL=F","PA=F","ALI=F","HG=F","LBS=F","OJ=F","KC=F","CT=F",

    # ─── BONDS & RATES ───
    "^TNX","^TYX","^FVX","^IRX","^MOVE",
    "TLT","IEF","SHY","AGG","BND","LQD","HYG","EMB","TIP","STIP",
    "RINF","VTIP","LTPZ","SCHP","WIP","LEMB","PICB","HYEM",

    # ─── VOLATILITY & FEAR ───
    "^VIX","^VXN","^GVZ","^OVX","^RVX","UVXY","SVXY","VXX","VIXM",
]))

SECTOR_PEERS = {
    "Technology":             "AAPL,MSFT,GOOGL,META,ORCL",
    "Semiconductors":         "NVDA,AMD,INTC,AVGO,TSM,KLAC,LRCX",
    "Consumer Cyclical":      "AMZN,TSLA,NKE,MCD,BKNG,ABNB",
    "Consumer Defensive":     "PG,KO,PEP,WMT,COST,CL",
    "Healthcare":             "JNJ,PFE,ABBV,MRK,LLY,AMGN,GILD",
    "Financials":             "JPM,BAC,GS,MS,V,MA,BLK",
    "Energy":                 "XOM,CVX,TTE.PA,BP.L,SLB,COP",
    "Industrials":            "GE,CAT,HON,BA,MMM,RTX,ETN",
    "Communication Services": "META,GOOGL,NFLX,DIS,CMCSA,SPOT",
    "Utilities":              "NEE,CEG,DUK,SO,AEP,XEL",
    "Real Estate":            "PLD,AMT,EQIX,SPG,O,WELL",
    "Basic Materials":        "LIN,APD,NEM,FCX,DD,DOW",
}

SC_MAP = {
    "Technology":    {"sup":["TSM","ASML.AS","AMAT","LRCX","KLAC"],"cust":["AAPL","MSFT","META","AMZN","GOOGL"],"note":"Foundry asiatici + hyperscaler USA"},
    "Semiconductors":{"sup":["ASML.AS","AMAT","LRCX","KLAC","MPWR"],"cust":["AAPL","NVDA","AMD","QCOM","AVGO"],"note":"ASML monopoly EUV · AI structural demand"},
    "Healthcare":    {"sup":["TMO","DHR","Lonza","WuXi"],"cust":["Ospedali","Assicurazioni","Governi"],"note":"Long R&D pipeline · CDMO critical"},
    "Energy":        {"sup":["SLB","HAL","BKR","CAT"],"cust":["Utility","Raffinerie","Industria"],"note":"Cyclical · oil price driven"},
    "Industrials":   {"sup":["MMM","HON","PH","ETN"],"cust":["Aerospace","Auto","Construction","Defense"],"note":"B2B · economic cycle sensitive"},
    "Consumer Defensive":{"sup":["ADM","BG","PKG","IFF"],"cust":["WMT","COST","B2C"],"note":"Anticyclical · premium pricing power"},
    "Financials":    {"sup":["Bloomberg LP","LSEG","Fiserv","Broadridge"],"cust":["Retail banks","Institutional","SME"],"note":"Fintech eroding retail margins"},
    "Utilities":     {"sup":["GEV","Siemens Energy","NEE"],"cust":["Residential","Industry","AI data centers"],"note":"Regulated · AI is structural catalyst"},
    "Basic Materials":{"sup":["Miners RM","Chemical producers"],"cust":["Manufacturing","Auto","Pharma"],"note":"Highly cyclical · China demand driven"},
    "Communication Services":{"sup":["ERIC","NOK","AKAM"],"cust":["Advertisers B2B","SME","Consumers"],"note":"Revenue from digital ads + subscriptions"},
    "Real Estate":   {"sup":["Builders","Property mgmt"],"cust":["Office tenants","Retail","Residential"],"note":"Rate sensitive · REIT 90% payout"},
    "Consumer Cyclical":{"sup":["OEM Asia","Raw materials"],"cust":["Consumers","E-commerce","Physical retail"],"note":"Correlated to consumer credit cycle"},
}

# ══════════════════════════════════════════════════════════
#  CANDLE CHART BUILDER
# ══════════════════════════════════════════════════════════
def build_candle_chart(tkr, df, indicators, period_label=""):
    rows = 2 + ("MACD" in indicators) + ("RSI" in indicators) + ("Stochastic" in indicators)
    heights = [0.5, 0.15] + [0.12]*(rows-2)
    heights_norm = [h/sum(heights) for h in heights]

    fig = make_subplots(
        rows=rows, cols=1, shared_xaxes=True,
        vertical_spacing=0.025, row_heights=heights_norm,
    )

    # ── Candlestick ──
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name=tkr, increasing_line_color="#2ECC71", decreasing_line_color="#E74C3C",
        increasing_fillcolor="#2ECC71", decreasing_fillcolor="#E74C3C",
        line_width=1.2,
    ), row=1, col=1)

    # ── Overlays ──
    if "SMA 20" in indicators:
        fig.add_trace(go.Scatter(x=df.index,y=add_sma(df,20),name="SMA20",line=dict(color="#F5A623",width=1.2)),row=1,col=1)
    if "SMA 50" in indicators:
        fig.add_trace(go.Scatter(x=df.index,y=add_sma(df,50),name="SMA50",line=dict(color="#3B8EF0",width=1.2)),row=1,col=1)
    if "SMA 200" in indicators:
        fig.add_trace(go.Scatter(x=df.index,y=add_sma(df,200),name="SMA200",line=dict(color="#9B59B6",width=1.5)),row=1,col=1)
    if "EMA 20" in indicators:
        fig.add_trace(go.Scatter(x=df.index,y=add_ema(df,20),name="EMA20",line=dict(color="#F39C12",width=1.2,dash="dot")),row=1,col=1)
    if "EMA 50" in indicators:
        fig.add_trace(go.Scatter(x=df.index,y=add_ema(df,50),name="EMA50",line=dict(color="#2ECC71",width=1.2,dash="dot")),row=1,col=1)
    if "Bollinger Bands" in indicators:
        u,m,l = add_bbands(df)
        fig.add_trace(go.Scatter(x=df.index,y=u,name="BB Up",line=dict(color="rgba(245,166,35,0.5)",width=1)),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=m,name="BB Mid",line=dict(color="rgba(245,166,35,0.3)",width=1,dash="dot")),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=l,name="BB Low",line=dict(color="rgba(245,166,35,0.5)",width=1),fill="tonexty",fillcolor="rgba(245,166,35,0.04)"),row=1,col=1)
    if "VWAP" in indicators:
        fig.add_trace(go.Scatter(x=df.index,y=add_vwap(df),name="VWAP",line=dict(color="#00BCD4",width=1.5,dash="dash")),row=1,col=1)
    if "Ichimoku" in indicators:
        tk,kj,sa,sb,ch = add_ichimoku(df)
        fig.add_trace(go.Scatter(x=df.index,y=tk,name="Tenkan",line=dict(color="#E74C3C",width=1)),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=kj,name="Kijun",line=dict(color="#3B8EF0",width=1)),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=sa,name="SpanA",line=dict(color="rgba(46,204,113,0.5)",width=1)),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=sb,name="SpanB",line=dict(color="rgba(231,76,60,0.5)",width=1),fill="tonexty",fillcolor="rgba(100,100,100,0.06)"),row=1,col=1)
    if "Fibonacci" in indicators:
        levels = add_fibonacci(df)
        for lbl, val in levels.items():
            fig.add_hline(y=val,line_dash="dot",line_color="rgba(245,166,35,0.4)",
                         annotation_text=f"Fib {lbl}",annotation_font_color="#F5A623",annotation_font_size=9,row=1,col=1)

    # ── Volume ──
    colors = ["#2ECC71" if df["Close"].iloc[i]>=df["Open"].iloc[i] else "#E74C3C" for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index,y=df["Volume"],name="Vol",marker_color=colors,opacity=0.7),row=2,col=1)
    if "OBV" in indicators:
        fig.add_trace(go.Scatter(x=df.index,y=add_obv(df),name="OBV",line=dict(color="#F5A623",width=1.2)),row=2,col=1)

    # ── Sub-panes ──
    sub_row = 3
    if "MACD" in indicators:
        macd,signal,hist = add_macd(df)
        hcol = ["#2ECC71" if v>=0 else "#E74C3C" for v in hist]
        fig.add_trace(go.Bar(x=df.index,y=hist,name="MACD Hist",marker_color=hcol,opacity=0.8),row=sub_row,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=macd,name="MACD",line=dict(color="#3B8EF0",width=1.2)),row=sub_row,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=signal,name="Signal",line=dict(color="#F5A623",width=1.2)),row=sub_row,col=1)
        fig.update_yaxes(title_text="MACD",row=sub_row,col=1,gridcolor="#091827",zeroline=True,zerolinecolor="#1E4976")
        sub_row += 1
    if "RSI" in indicators:
        rsi = add_rsi(df)
        fig.add_trace(go.Scatter(x=df.index,y=rsi,name="RSI",line=dict(color="#F5A623",width=1.5)),row=sub_row,col=1)
        fig.add_hline(y=70,line_dash="dot",line_color="rgba(231,76,60,0.6)",row=sub_row,col=1)
        fig.add_hline(y=30,line_dash="dot",line_color="rgba(46,204,113,0.6)",row=sub_row,col=1)
        fig.add_hrect(y0=70,y1=100,fillcolor="rgba(231,76,60,0.04)",row=sub_row,col=1,line_width=0)
        fig.add_hrect(y0=0,y1=30,fillcolor="rgba(46,204,113,0.04)",row=sub_row,col=1,line_width=0)
        fig.update_yaxes(title_text="RSI",range=[0,100],row=sub_row,col=1,gridcolor="#091827")
        sub_row += 1
    if "Stochastic" in indicators:
        ks,ds = add_stoch(df)
        fig.add_trace(go.Scatter(x=df.index,y=ks,name="%K",line=dict(color="#F5A623",width=1.2)),row=sub_row,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=ds,name="%D",line=dict(color="#3B8EF0",width=1.2)),row=sub_row,col=1)
        fig.add_hline(y=80,line_dash="dot",line_color="rgba(231,76,60,0.6)",row=sub_row,col=1)
        fig.add_hline(y=20,line_dash="dot",line_color="rgba(46,204,113,0.6)",row=sub_row,col=1)
        fig.update_yaxes(title_text="Stoch",range=[0,100],row=sub_row,col=1,gridcolor="#091827")

    fig.update_layout(**pla({
        "height": 600 + 100*max(0,rows-2),
        "title": f"{tkr} — {period_label}",
        "xaxis": xaxis_time(),
        "showlegend": True,
        "xaxis_rangeslider_visible": False,
    }))
    for i in range(1, rows+1):
        fig.update_xaxes(gridcolor="#091827", showgrid=True, row=i, col=1)
    return fig

# ══════════════════════════════════════════════════════════
#  COMPANY TERMINAL (Bloomberg-style)
# ══════════════════════════════════════════════════════════
def show_terminal(tkr: str, peers_str: str = "SPY,QQQ,IWM"):
    inf = get_info(tkr)
    if not inf:
        st.error(f"❌ Ticker **{tkr}** not found. Examples: `AAPL` `NVDA` `ENI.MI` `MC.PA` `ASML.AS`")
        return

    name   = inf.get("longName") or inf.get("shortName") or tkr
    price  = inf.get("currentPrice") or inf.get("regularMarketPrice") or inf.get("previousClose")
    prev   = inf.get("previousClose") or price
    chg    = (price-prev)/prev*100 if price and prev and prev!=0 else None
    sector = inf.get("sector","N/A")
    cur    = inf.get("currency","USD")

    chg_col = "#2ECC71" if (chg or 0)>=0 else "#E74C3C"
    chg_str = f"<span style='color:{chg_col};font-weight:700'>{chg:+.2f}%</span>" if chg else ""
    hi52 = inf.get("fiftyTwoWeekHigh","—"); lo52 = inf.get("fiftyTwoWeekLow","—")
    vs_hi = (price/hi52-1)*100 if price and hi52 and hi52!="—" else None

    st.markdown(f"""
    <div class='ticker-card'>
      <div style='display:flex;justify-content:space-between;align-items:flex-start'>
        <div>
          <div class='ticker-tag'>EQUITY · {inf.get('exchange','N/A')} · {cur} · {inf.get('quoteType','EQUITY')}</div>
          <div class='ticker-name'>{name}</div>
          <div class='ticker-meta'>{tkr} &nbsp;·&nbsp; {sector} &nbsp;·&nbsp; {inf.get('industry','N/A')[:30]} &nbsp;·&nbsp; {inf.get('country','N/A')}</div>
          <div style='margin-top:10px;font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#5A88B0'>
            52W Lo: <b style='color:#E74C3C'>{lo52}</b> &nbsp;&nbsp;
            52W Hi: <b style='color:#2ECC71'>{hi52}</b> &nbsp;&nbsp;
            {'vs Hi: <b style=color:#F5A623>' + f'{vs_hi:+.1f}%' + '</b>' if vs_hi else ''}
          </div>
        </div>
        <div style='text-align:right'>
          <div class='ticker-price'>{f"{price:,.2f}" if price else "N/A"} <span style='font-size:0.85rem;color:#5A88B0'>{cur}</span></div>
          <div style='font-size:0.88rem;margin-top:4px'>{chg_str}</div>
          <div style='font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#5A88B0;margin-top:6px'>
            Vol: {f"{inf.get('volume',0):,}" if inf.get('volume') else "—"} &nbsp;·&nbsp;
            Avg: {f"{inf.get('averageVolume',0):,}" if inf.get('averageVolume') else "—"}
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── KPIs row 1 ──
    kpis1 = [
        ("P/E Fwd",   f"{inf['forwardPE']:.1f}"                    if inf.get("forwardPE")            else "N/A"),
        ("P/E TTM",   f"{inf['trailingPE']:.1f}"                   if inf.get("trailingPE")           else "N/A"),
        ("EPS Fwd",   f"{inf['forwardEps']:.2f}"                   if inf.get("forwardEps")           else "N/A"),
        ("EPS TTM",   f"{inf.get('trailingEps','N/A'):.2f}"        if inf.get("trailingEps")          else "N/A"),
        ("P/B",       f"{inf['priceToBook']:.2f}"                  if inf.get("priceToBook")          else "N/A"),
        ("P/S",       f"{inf['priceToSalesTrailing12Months']:.2f}" if inf.get("priceToSalesTrailing12Months") else "N/A"),
        ("Beta",      f"{inf['beta']:.2f}"                         if inf.get("beta")                 else "N/A"),
        ("Market Cap",f"${inf['marketCap']/1e9:.1f}B"             if inf.get("marketCap")            else "N/A"),
    ]
    cols = st.columns(8)
    for i,(lb,v) in enumerate(kpis1): cols[i].metric(lb,v)

    kpis2 = [
        ("EV/EBITDA",  f"{inf['enterpriseToEbitda']:.1f}"         if inf.get("enterpriseToEbitda")   else "N/A"),
        ("EV/Rev",     f"{inf['enterpriseToRevenue']:.2f}"        if inf.get("enterpriseToRevenue")  else "N/A"),
        ("Div Yield",  f"{(inf.get('dividendYield') or 0)*100:.2f}%"),
        ("Payout",     f"{(inf.get('payoutRatio') or 0)*100:.1f}%"),
        ("ROE",        f"{inf.get('returnOnEquity',0)*100:.1f}%"  if inf.get("returnOnEquity")       else "N/A"),
        ("ROA",        f"{inf.get('returnOnAssets',0)*100:.1f}%"  if inf.get("returnOnAssets")       else "N/A"),
        ("Op Margin",  f"{inf.get('operatingMargins',0)*100:.1f}%"if inf.get("operatingMargins")     else "N/A"),
        ("Net Margin", f"{inf.get('profitMargins',0)*100:.1f}%"   if inf.get("profitMargins")        else "N/A"),
    ]
    cols2 = st.columns(8)
    for i,(lb,v) in enumerate(kpis2): cols2[i].metric(lb,v)

    st.markdown("---")

    # ── TABS ──
    t1,t2,t3,t4,t5,t6,t7 = st.tabs([
        "📋 Overview","📊 Financials","📈 Performance","👥 Peers",
        "🏦 Holders","📰 News & Rec","⛓️ Supply Chain"
    ])

    with t1:
        c1,c2 = st.columns([3,2])
        with c1:
            sec("BUSINESS SUMMARY")
            st.write(inf.get("longBusinessSummary","Description not available.")[:1500])
        with c2:
            sec("FINANCIAL HIGHLIGHTS")
            fl = [
                ("Revenue",   f"${inf.get('totalRevenue',0)/1e9:.2f}B" if inf.get("totalRevenue") else "N/A"),
                ("EBITDA",    f"${inf.get('ebitda',0)/1e9:.2f}B"       if inf.get("ebitda")       else "N/A"),
                ("FCF",       f"${inf.get('freeCashflow',0)/1e9:.2f}B" if inf.get("freeCashflow") else "N/A"),
                ("Gross Mgn", f"{inf.get('grossMargins',0)*100:.1f}%"  if inf.get("grossMargins") else "N/A"),
                ("D/E Ratio", f"{inf.get('debtToEquity',0)/100:.2f}"   if inf.get("debtToEquity") else "N/A"),
                ("Cash",      f"${inf.get('totalCash',0)/1e9:.2f}B"    if inf.get("totalCash")    else "N/A"),
                ("Debt",      f"${inf.get('totalDebt',0)/1e9:.2f}B"    if inf.get("totalDebt")    else "N/A"),
                ("Employees", f"{inf.get('fullTimeEmployees',0):,}"     if inf.get("fullTimeEmployees") else "N/A"),
            ]
            r1,r2 = st.columns(2)
            for i,(lb,v) in enumerate(fl):
                (r1 if i%2==0 else r2).metric(lb,v)
            sec("GROWTH METRICS")
            g1,g2 = st.columns(2)
            g1.metric("Rev Growth QoQ", f"{inf.get('revenueGrowth',0)*100:.1f}%" if inf.get("revenueGrowth") else "N/A")
            g2.metric("Earnings Growth", f"{inf.get('earningsGrowth',0)*100:.1f}%" if inf.get("earningsGrowth") else "N/A")
            g1.metric("Qtrly Rev Growth", f"{inf.get('revenueQuarterlyGrowth',0)*100:.1f}%" if inf.get("revenueQuarterlyGrowth") else "N/A")
            g2.metric("Rev/Share", f"{inf.get('revenuePerShare','N/A')}")

    with t2:
        fin = get_financials(tkr)
        if fin:
            mode_f = st.radio("Period:", ["Annual","Quarterly"], horizontal=True, key=f"fin_mode_{tkr}")
            suffix = "_a" if mode_f=="Annual" else "_q"
            st_tabs = st.tabs(["Income Statement","Balance Sheet","Cash Flow"])
            for tab_w, key in zip(st_tabs, ["income","balance","cashflow"]):
                with tab_w:
                    df_f = fin.get(key+suffix, pd.DataFrame())
                    if not df_f.empty:
                        df_disp = df_f.copy()
                        def fmt_bn(x):
                            try:
                                v = float(x)
                                if abs(v)>=1e9: return f"${v/1e9:.2f}B"
                                if abs(v)>=1e6: return f"${v/1e6:.1f}M"
                                return f"${v:,.0f}"
                            except: return str(x)
                        df_disp.columns = [str(c)[:10] for c in df_disp.columns]
                        for col in df_disp.columns:
                            df_disp[col] = df_disp[col].apply(fmt_bn)
                        st.dataframe(df_disp, use_container_width=True)
                    else:
                        st.info("Financial data not available.")

    with t3:
        periods_map = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","2Y":"2y","5Y":"5y","10Y":"10y","MAX":"max"}
        per_lbl = st.select_slider("Period:", list(periods_map.keys()), value="1Y", key=f"perf_per_{tkr}")
        s_data = get_close(tkr, period=periods_map[per_lbl])
        if not s_data.empty:
            fig_p = go.Figure()
            ret = ((s_data / s_data.iloc[0])-1)*100
            fig_p.add_trace(go.Scatter(
                x=ret.index, y=ret, name=tkr,
                line=dict(width=2.5,color="#F5A623"),
                fill="tozeroy", fillcolor="rgba(245,166,35,0.06)",
                hovertemplate="%{x|%d %b %Y}<br><b>%{y:+.2f}%</b><extra></extra>",
            ))
            fig_p.add_hline(y=0,line_dash="dot",line_color="#1E4976")
            fig_p.update_layout(**pla({"xaxis":xaxis_time(),"yaxis":dict(title="Return %",**yaxis_plain()),"height":380,"title":f"{tkr} Performance — {per_lbl}"}))
            st.plotly_chart(fig_p, use_container_width=True)
            dr = s_data.pct_change().dropna()
            ay = max((s_data.index[-1]-s_data.index[0]).days/365.25,0.1)
            tr = float(ret.iloc[-1])
            car = ((1+tr/100)**(1/ay)-1)*100
            vol = dr.std()*np.sqrt(252)*100
            dd = ((s_data/s_data.cummax())-1).min()*100
            m1,m2,m3,m4,m5 = st.columns(5)
            m1.metric("Total Return",f"{tr:+.2f}%"); m2.metric("CAGR",f"{car:+.2f}%")
            m3.metric("Ann. Vol",f"{vol:.2f}%"); m4.metric("Max DD",f"{dd:.2f}%")
            m5.metric("Sharpe",f"{car/vol:.2f}" if vol>0 else "N/A")

    with t4:
        peers_key = f"peers_{tkr}"
        if peers_key not in st.session_state: st.session_state[peers_key]=peers_str
        peers_in = st.text_input("Peers (comma separated)", value=st.session_state[peers_key], key=f"peers_inp_{tkr}")
        st.session_state[peers_key]=peers_in
        p_list = [tkr]+[x.strip().upper() for x in peers_in.split(",") if x.strip()]
        rows_p=[]
        for p in p_list:
            pi=get_info(p)
            if not pi:
                rows_p.append({"Ticker":p,**{k:"ERR" for k in ["Price","P/E Fwd","P/E TTM","EPS Fwd","P/B","P/S","EV/EBITDA","Beta","Cap $B","Div %","ROE %","Op.Mgn %","Net.Mgn %","Rev $B","FCF $B"]}})
                continue
            pr=pi.get("currentPrice") or pi.get("regularMarketPrice") or pi.get("previousClose") or 0
            rows_p.append({
                "Ticker":p,
                "Price":    f"{pr:,.2f}"                                            if pr  else "N/A",
                "P/E Fwd":  f"{pi.get('forwardPE'):.1f}"                           if pi.get("forwardPE") else "N/A",
                "P/E TTM":  f"{pi.get('trailingPE'):.1f}"                          if pi.get("trailingPE") else "N/A",
                "EPS Fwd":  f"{pi.get('forwardEps'):.2f}"                          if pi.get("forwardEps") else "N/A",
                "P/B":      f"{pi.get('priceToBook'):.2f}"                         if pi.get("priceToBook") else "N/A",
                "P/S":      f"{pi.get('priceToSalesTrailing12Months'):.2f}"        if pi.get("priceToSalesTrailing12Months") else "N/A",
                "EV/EBITDA":f"{pi.get('enterpriseToEbitda'):.1f}"                  if pi.get("enterpriseToEbitda") else "N/A",
                "Beta":     f"{pi.get('beta'):.2f}"                                if pi.get("beta") else "N/A",
                "Cap $B":   f"{pi.get('marketCap',0)/1e9:.1f}"                     if pi.get("marketCap") else "N/A",
                "Div %":    f"{(pi.get('dividendYield') or 0)*100:.2f}%",
                "ROE %":    f"{pi.get('returnOnEquity',0)*100:.1f}"                if pi.get("returnOnEquity") else "N/A",
                "Op.Mgn %": f"{pi.get('operatingMargins',0)*100:.1f}"              if pi.get("operatingMargins") else "N/A",
                "Net.Mgn %":f"{pi.get('profitMargins',0)*100:.1f}"                 if pi.get("profitMargins") else "N/A",
                "Rev $B":   f"{pi.get('totalRevenue',0)/1e9:.1f}"                  if pi.get("totalRevenue") else "N/A",
                "FCF $B":   f"{pi.get('freeCashflow',0)/1e9:.1f}"                  if pi.get("freeCashflow") else "N/A",
            })
        if rows_p:
            st.dataframe(pd.DataFrame(rows_p).set_index("Ticker"), use_container_width=True)
        sec("RELATIVE PERFORMANCE 1Y")
        fr = {p:s for p in p_list for s in [get_close(p,period="1y")] if not s.empty}
        if fr:
            pd_data = pd.DataFrame(fr).dropna(how="all").ffill()
            pn = ((pd_data/pd_data.iloc[0])-1)*100
            fig_peers = go.Figure()
            for idx,col in enumerate(pn.columns):
                fig_peers.add_trace(go.Scatter(
                    x=pn.index,y=pn[col],name=col,
                    line=dict(width=2.8 if col==tkr else 1.5,color=COLORS[idx%len(COLORS)]),
                ))
            fig_peers.add_hline(y=0,line_dash="dot",line_color="#1E4976")
            fig_peers.update_layout(**pla({"xaxis":xaxis_time(),"yaxis":dict(title="Return %",**yaxis_plain()),"height":360,"title":f"Relative Performance 1Y — {tkr} vs Peers"}))
            st.plotly_chart(fig_peers,use_container_width=True)

    with t5:
        ihold = get_institutional_holders(tkr)
        if not ihold.empty:
            sec("TOP INSTITUTIONAL HOLDERS")
            st.dataframe(ihold.head(15), use_container_width=True)
        maj = get_info(tkr)
        sec("INSIDER / MAJOR HOLDERS SNAPSHOT")
        i1,i2,i3,i4 = st.columns(4)
        i1.metric("Float %", f"{inf.get('floatShares',0)/inf.get('sharesOutstanding',1)*100:.1f}%" if inf.get("sharesOutstanding") else "N/A")
        i2.metric("Inst. Held", f"{inf.get('heldPercentInstitutions',0)*100:.1f}%" if inf.get("heldPercentInstitutions") else "N/A")
        i3.metric("Insider Held", f"{inf.get('heldPercentInsiders',0)*100:.1f}%" if inf.get("heldPercentInsiders") else "N/A")
        i4.metric("Short Float", f"{inf.get('shortPercentOfFloat',0)*100:.1f}%" if inf.get("shortPercentOfFloat") else "N/A")

    with t6:
        c_news, c_rec = st.columns([3,2])
        with c_news:
            sec("LATEST NEWS")
            try:
                for n in (yf.Ticker(tkr).news or [])[:8]:
                    title=n.get("title",""); link=n.get("link",f"https://finance.yahoo.com/quote/{tkr}")
                    pub=n.get("providerPublishTime","")
                    if title:
                        dt_str=""
                        try: dt_str=datetime.fromtimestamp(pub).strftime("%d %b %H:%M") if pub else ""
                        except: pass
                        st.markdown(
                            f"<div style='border-left:2px solid #1E4976;padding-left:8px;margin-bottom:8px;font-size:0.79rem'>"
                            f"<a href='{link}' target='_blank' style='color:#C8D8EC;text-decoration:none;font-weight:500'>{title[:90]}</a>"
                            f"<div style='font-size:0.62rem;color:#5A88B0;margin-top:2px'>{dt_str}</div></div>",
                            unsafe_allow_html=True)
            except: st.info("News not available.")
        with c_rec:
            sec("ANALYST RECOMMENDATIONS")
            recs = get_recommendations(tkr)
            if not recs.empty:
                try:
                    recent = recs.head(10)[["Firm","To Grade","Action"]].reset_index(drop=True) if "Firm" in recs.columns else recs.head(10)
                    st.dataframe(recent, use_container_width=True)
                except: st.dataframe(recs.head(10), use_container_width=True)
            rec_hist = inf.get("recommendationMean")
            if rec_hist:
                rec_label = {1:"Strong Buy",2:"Buy",3:"Hold",4:"Sell",5:"Strong Sell"}.get(round(rec_hist),"N/A")
                st.metric("Consensus Rating", f"{rec_label} ({rec_hist:.2f})")
                st.metric("# Analysts", str(inf.get("numberOfAnalystOpinions","N/A")))
                st.metric("Target Price", f"${inf.get('targetMeanPrice','N/A')}")
                st.metric("Upside", f"{(inf.get('targetMeanPrice',0)/price-1)*100:.1f}%" if price and inf.get('targetMeanPrice') else "N/A")

    with t7:
        sc = SC_MAP.get(sector)
        if sc:
            s1,s2,s3 = st.columns(3)
            with s1:
                sec("🔼 KEY SUPPLIERS")
                for s in sc["sup"]: st.markdown(f"<div style='font-size:0.82rem;color:#C8D8EC;padding:2px 0'>· {s}</div>",unsafe_allow_html=True)
            with s2:
                sec("🔽 KEY CUSTOMERS")
                for c in sc["cust"]: st.markdown(f"<div style='font-size:0.82rem;color:#C8D8EC;padding:2px 0'>· {c}</div>",unsafe_allow_html=True)
            with s3:
                sec("💡 SECTOR NOTE")
                st.markdown(f"<div class='term-box'>{sc['note']}</div>",unsafe_allow_html=True)
        else:
            st.info("Supply chain map not available for this sector.")
        sec("SECTOR & GEOGRAPHY METADATA")
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Sector",sector); m2.metric("Industry",inf.get("industry","N/A")[:22])
        m3.metric("Country",inf.get("country","N/A")); m4.metric("Exchange",inf.get("exchange","N/A"))

# ══════════════════════════════════════════════════════════
#  PAGE: MARKET OVERVIEW
# ══════════════════════════════════════════════════════════
if choice == "Market Overview":
    ptitle("GLOBAL MARKET OVERVIEW","Real-time snapshot · Indices · Top movers · Fear & Greed")

    INDICES = {
        "S&P 500":"^GSPC","Nasdaq 100":"^IXIC","Dow Jones":"^DJI","Russell 2000":"^RUT",
        "VIX":"^VIX","Nikkei 225":"^N225","FTSE MIB":"FTSEMIB.MI","DAX 40":"^GDAXI",
        "CAC 40":"^FCHI","STOXX 50":"^STOXX50E","Hang Seng":"^HSI","MSCI EM":"EEM",
    }
    sec("GLOBAL INDICES")
    idx_cols = st.columns(4)
    for i,(name,tkr) in enumerate(INDICES.items()):
        p,c = get_price_chg(tkr)
        idx_cols[i%4].metric(name, f"{p:,.2f}" if p else "N/A", f"{c:+.2f}%" if c else "—")

    st.markdown("---")
    BOND_FUTURES = {"10Y Yield":"^TNX","30Y Yield":"^TYX","5Y Yield":"^FVX","2Y Yield":"^IRX","MOVE":"^MOVE"}
    sec("RATES & FIXED INCOME")
    bnd_cols = st.columns(5)
    for i,(nm,tk) in enumerate(BOND_FUTURES.items()):
        p,c = get_price_chg(tk)
        bnd_cols[i].metric(nm, f"{p:.3f}" if p else "N/A", f"{c:+.2f}%" if c else "—")

    st.markdown("---")
    FX = {"EUR/USD":"EURUSD=X","GBP/USD":"GBPUSD=X","USD/JPY":"USDJPY=X","USD/CHF":"USDCHF=X","AUD/USD":"AUDUSD=X","DXY":"DX-Y.NYB"}
    COMMS = {"Gold":"GC=F","Silver":"SI=F","Crude WTI":"CL=F","Brent":"BZ=F","Nat Gas":"NG=F","Copper":"HG=F"}
    c_fx, c_cm = st.columns(2)
    with c_fx:
        sec("FOREIGN EXCHANGE")
        fc = st.columns(3)
        for i,(nm,tk) in enumerate(FX.items()):
            p,c = get_price_chg(tk)
            fc[i%3].metric(nm, f"{p:.4f}" if p else "N/A", f"{c:+.2f}%" if c else "—")
    with c_cm:
        sec("COMMODITIES")
        cc = st.columns(3)
        for i,(nm,tk) in enumerate(COMMS.items()):
            p,c = get_price_chg(tk)
            cc[i%3].metric(nm, f"{p:,.2f}" if p else "N/A", f"{c:+.2f}%" if c else "—")

    st.markdown("---")
    STOCKS = {
        "Apple":"AAPL","Microsoft":"MSFT","NVIDIA":"NVDA","Alphabet":"GOOGL",
        "Tesla":"TSLA","Amazon":"AMZN","Meta":"META","ASML":"ASML.AS",
        "SAP":"SAP.DE","ENI":"ENI.MI","LVMH":"MC.PA","Ferrari":"RACE.MI",
        "Berkshire":"BRK-B","JPMorgan":"JPM","TSMC":"TSM","Samsung":"SAMSF",
    }
    sec("KEY EQUITIES")
    stk_cols = st.columns(4)
    for i,(nm,tk) in enumerate(STOCKS.items()):
        p,c = get_price_chg(tk)
        stk_cols[i%4].metric(f"{nm} ({tk})", f"{p:,.2f}" if p else "N/A", f"{c:+.2f}%" if c else "—")

    st.markdown("---")
    sec("TOP MOVERS")
    WATCH = ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","JPM","V",
             "AMD","INTC","PANW","ADBE","CRM","SNOW","PLTR","COIN","NFLX","DIS",
             "BAC","WFC","GS","COST","WMT","NKE","MCD","BA","CAT","GE",
             "F","GM","SQ","PYPL","SMCI","ARM","ENPH","MRNA","PFE","GILD",
             "ENI.MI","ENEL.MI","RACE.MI","MC.PA","TTE.PA","SAP.DE","ASML.AS",
             "BTC-USD","ETH-USD","SOL-USD","GC=F","CL=F"]
    mv_results=[]
    prog = st.progress(0)
    for i,tk in enumerate(WATCH):
        prog.progress((i+1)/len(WATCH))
        p,c = get_price_chg(tk)
        if p and c: mv_results.append({"Ticker":tk,"Price":p,"Change%":c})
    prog.empty()
    mv_results.sort(key=lambda x:x["Change%"],reverse=True)
    cg,cl = st.columns(2)
    for col_w, data, color, label in [(cg,mv_results[:7],"#2ECC71","🟢 TOP GAINERS"),(cl,sorted(mv_results,key=lambda x:x["Change%"])[:7],"#E74C3C","🔴 TOP LOSERS")]:
        with col_w:
            st.markdown(f"<div class='sec-hdr' style='color:{color}'>{label}</div>",unsafe_allow_html=True)
            for m in data:
                st.markdown(f"""
                <div class='mover-card' style='border-left:3px solid {color}'>
                  <div><div style='font-family:IBM Plex Mono,monospace;font-size:0.88rem;color:#FFF;font-weight:700'>{m['Ticker']}</div>
                       <div style='font-size:0.68rem;color:#5A88B0'>${m['Price']:,.3f}</div></div>
                  <div style='font-family:IBM Plex Mono,monospace;font-size:1rem;color:{color};font-weight:700'>{m['Change%']:+.2f}%</div>
                </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  PAGE: WATCHLIST
# ══════════════════════════════════════════════════════════
elif choice == "Watchlist":
    ptitle("WATCHLIST","Personal portfolio tracker · Real-time prices · Alerts")

    wl_input = st.text_input("Add tickers (comma separated)","",placeholder="NVDA, ASML.AS, ENI.MI, BTC-USD ...")
    if wl_input.strip():
        new = [x.strip().upper() for x in wl_input.split(",") if x.strip()]
        before = len(st.session_state.watchlist)
        st.session_state.watchlist = list(dict.fromkeys(st.session_state.watchlist+new))
        if len(st.session_state.watchlist)>before: st.rerun()

    wl = st.session_state.watchlist
    if not wl:
        st.info("Watchlist empty. Add tickers above.")
    else:
        with st.form("wl_remove"):
            rem = st.multiselect("Remove from watchlist", wl)
            if st.form_submit_button("Remove selected") and rem:
                st.session_state.watchlist=[t for t in wl if t not in rem]; st.rerun()

        sec("REAL-TIME PRICES")
        rows_wl=[]
        prog_wl=st.progress(0)
        for i,tkr in enumerate(wl):
            prog_wl.progress((i+1)/len(wl))
            inf=get_info(tkr); p,c=get_price_chg(tkr)
            if inf:
                rows_wl.append({
                    "Ticker":tkr,"Name":(inf.get("shortName") or tkr)[:28],
                    "Price":f"{p:,.4f}" if p else "N/A",
                    "Chg %":f"{c:+.2f}%" if c else "—",
                    "52W Lo":str(inf.get("fiftyTwoWeekLow","—")),"52W Hi":str(inf.get("fiftyTwoWeekHigh","—")),
                    "P/E":f"{inf['forwardPE']:.1f}" if inf.get("forwardPE") else "N/A",
                    "Cap $B":f"{inf.get('marketCap',0)/1e9:.1f}" if inf.get("marketCap") else "N/A",
                    "Beta":f"{inf['beta']:.2f}" if inf.get("beta") else "N/A",
                    "Div%":f"{(inf.get('dividendYield') or 0)*100:.2f}%",
                    "Sector":(inf.get("sector") or "")[:18],
                })
        prog_wl.empty()
        if rows_wl:
            st.dataframe(pd.DataFrame(rows_wl).set_index("Ticker"),use_container_width=True)

        sec("COMPARATIVE PERFORMANCE")
        h_opts={"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","3Y":"3y","5Y":"5y","10Y":"10y","MAX":"max"}
        h_lbl=st.selectbox("Horizon",list(h_opts.keys()),index=3)
        fr={tk:s for tk in wl for s in [get_close(tk,period=h_opts[h_lbl])] if not s.empty}
        if fr:
            d=pd.DataFrame(fr).dropna(how="all").ffill()
            r=((d/d.iloc[0])-1)*100
            fig_wl=go.Figure()
            for idx,col in enumerate(r.columns):
                fig_wl.add_trace(go.Scatter(x=r.index,y=r[col],name=f"{col} ({r[col].iloc[-1]:+.1f}%)",line=dict(width=2,color=COLORS[idx%len(COLORS)])))
            fig_wl.add_hline(y=0,line_dash="dot",line_color="#1E4976")
            fig_wl.update_layout(**pla({"xaxis":xaxis_time(),"yaxis":dict(title="Return %",**yaxis_plain()),"height":440,"title":f"Watchlist Performance — {h_lbl}"}))
            st.plotly_chart(fig_wl,use_container_width=True)

            if len(fr)>=2:
                sec("CORRELATION MATRIX")
                corr=d.pct_change().dropna().corr()
                fig_co=go.Figure(go.Heatmap(z=corr.values,x=corr.columns.tolist(),y=corr.index.tolist(),
                    colorscale=[[0,"#E74C3C"],[0.5,"#071220"],[1,"#2ECC71"]],zmid=0,zmin=-1,zmax=1,
                    text=corr.round(2).values,texttemplate="%{text}",hovertemplate="%{x} vs %{y}: %{z:.2f}<extra></extra>"))
                fig_co.update_layout(**pla({"height":340,"title":"Return Correlation"}))
                st.plotly_chart(fig_co,use_container_width=True)

        # ── Quick terminal jump ──
        sec("OPEN IN TERMINAL")
        sel_wl = st.selectbox("Select ticker",wl)
        if st.button("⌨  OPEN COMPANY TERMINAL",use_container_width=True):
            st.session_state.page="Company Terminal"
            st.session_state.terminal_ticker=sel_wl
            st.rerun()

# ══════════════════════════════════════════════════════════
#  PAGE: COMPANY TERMINAL
# ══════════════════════════════════════════════════════════
elif choice == "Company Terminal":
    ptitle("COMPANY TERMINAL","Fundamental · Technical · Peers · Supply Chain · News")
    ci,cb = st.columns([5,1])
    with ci:
        new_t=st.text_input("Ticker",value=st.session_state.terminal_ticker,
            placeholder="AAPL · NVDA · ENI.MI · ASML.AS · BTC-USD ...").strip().upper()
    with cb:
        st.markdown("<div style='height:28px'></div>",unsafe_allow_html=True)
        go_btn=st.button("▶ GO",use_container_width=True)
    if new_t:
        if new_t!=st.session_state.terminal_ticker or go_btn:
            st.session_state.terminal_ticker=new_t
            inf_tmp=get_info(new_t)
            s_tmp=inf_tmp.get("sector","") if inf_tmp else ""
            st.session_state.terminal_peers=SECTOR_PEERS.get(s_tmp,"SPY,QQQ,IWM,GLD")
        show_terminal(st.session_state.terminal_ticker, st.session_state.terminal_peers)

# ══════════════════════════════════════════════════════════
#  PAGE: CHARTS & TECHNICAL
# ══════════════════════════════════════════════════════════
elif choice == "Charts & Technical":
    ptitle("CHARTS & TECHNICAL ANALYSIS","Candlestick · Overlays · RSI · MACD · Ichimoku · Fibonacci")

    ct1,ct2,ct3 = st.columns([3,2,2])
    with ct1:
        chart_tkr=st.text_input("Ticker","NVDA",key="chart_tkr")
    with ct2:
        chart_per=st.selectbox("Period",["1mo","3mo","6mo","1y","2y","5y","10y","max"],index=3,key="chart_per")
    with ct3:
        chart_int=st.selectbox("Interval",["1d","1wk","1mo"],index=0,key="chart_int")

    ind_opts=["SMA 20","SMA 50","SMA 200","EMA 20","EMA 50","Bollinger Bands","VWAP","Ichimoku","Fibonacci","MACD","RSI","Stochastic","OBV"]
    sel_ind=st.multiselect("Indicators",ind_opts,default=["SMA 20","SMA 50","Bollinger Bands","MACD","RSI"])

    if chart_tkr.strip():
        tkr_c=chart_tkr.strip().upper()
        df_c=get_ohlcv(tkr_c,period=chart_per,interval=chart_int)
        if not df_c.empty:
            fig_c=build_candle_chart(tkr_c,df_c,sel_ind,f"{chart_per} · {chart_int}")
            st.plotly_chart(fig_c,use_container_width=True)

            sec("PRICE STATISTICS")
            dr_c=df_c["Close"].pct_change().dropna()
            s1,s2,s3,s4,s5,s6,s7,s8 = st.columns(8)
            s1.metric("Current",f"{df_c['Close'].iloc[-1]:,.2f}")
            s2.metric("Open",f"{df_c['Open'].iloc[-1]:,.2f}")
            s3.metric("High",f"{df_c['High'].iloc[-1]:,.2f}")
            s4.metric("Low",f"{df_c['Low'].iloc[-1]:,.2f}")
            s5.metric("Volume",f"{df_c['Volume'].iloc[-1]:,.0f}" if 'Volume' in df_c else "—")
            s6.metric("Ann. Vol",f"{dr_c.std()*np.sqrt(252)*100:.1f}%")
            s7.metric("ATR(14)",f"{add_atr(df_c).iloc[-1]:,.2f}" if len(df_c)>14 else "—")
            s8.metric("RSI(14)",f"{add_rsi(df_c).iloc[-1]:.1f}" if len(df_c)>14 else "—")

            sec("SUPPORT & RESISTANCE — FIBONACCI LEVELS")
            levels=add_fibonacci(df_c)
            lev_cols=st.columns(7)
            for i,(lbl,val) in enumerate(levels.items()):
                lev_cols[i%7].metric(f"Fib {lbl}",f"{val:,.2f}")
        else:
            st.warning(f"No data for **{tkr_c}**.")

# ══════════════════════════════════════════════════════════
#  PAGE: DCF VALUATION
# ══════════════════════════════════════════════════════════
elif choice == "DCF Valuation":
    ptitle("DCF VALUATION","WACC · Terminal Value · Sensitivity · Reverse DCF · Monte Carlo")

    mode_dcf = st.radio("Mode:",["Manual DCF","Auto-fill from Ticker","Reverse DCF","Monte Carlo Simulation"],horizontal=True)
    st.markdown("---")

    if mode_dcf in ("Manual DCF","Auto-fill from Ticker"):
        if mode_dcf=="Auto-fill from Ticker":
            af_tkr=st.text_input("Ticker for auto-fill","AAPL")
            if af_tkr.strip():
                af_inf=get_info(af_tkr.strip().upper())
                af_fcf=af_inf.get("freeCashflow",1_000_000_000) if af_inf else 1_000_000_000
                af_shr=af_inf.get("sharesOutstanding",1_000_000_000) if af_inf else 1_000_000_000
                af_nd=(af_inf.get("totalDebt",0) or 0)-(af_inf.get("totalCash",0) or 0) if af_inf else 0
                af_eg=min(max((af_inf.get("earningsGrowth",0.1) or 0.1)*100,1),50) if af_inf else 10
            else:
                af_fcf,af_shr,af_nd,af_eg = 1_000_000_000,1_000_000_000,0,10
        else:
            af_fcf,af_shr,af_nd,af_eg = 1_000_000_000,1_000_000_000,0,10

        c1,c2=st.columns(2)
        with c1:
            sec("DCF INPUTS")
            fcf   = st.number_input("Base FCF ($)",value=int(af_fcf),step=50_000_000,format="%d")
            g_r   = st.slider("FCF Growth Rate (%)",1,60,int(af_eg))
            wacc  = st.slider("WACC (%)",4,20,9)
            tg    = st.slider("Terminal Growth (%)",0,5,2)
            yrs   = st.slider("Projection Years",3,20,10)
            shr   = st.number_input("Shares Outstanding",value=int(af_shr),step=10_000_000,format="%d")
            nd    = st.number_input("Net Debt (positive=debt)",value=int(af_nd),step=100_000_000,format="%d")
            disc_phases = st.checkbox("Two-stage growth model",value=False)
            if disc_phases:
                g_r2=st.slider("Phase 2 Growth (%)",1,30,5)
                phase_yr=st.slider("Phase 1 Duration (years)",1,10,5)
            else:
                g_r2,phase_yr=tg*100,yrs

        g,w,t=g_r/100,wacc/100,tg/100
        cfs,pvs=[],[]
        for yr in range(1,yrs+1):
            if disc_phases and yr>phase_yr:
                cf=cfs[-1]*(1+g_r2/100) if cfs else fcf*(1+g)**phase_yr*(1+g_r2/100)
            else:
                cf=fcf*((1+g)**yr)
            pv=cf/((1+w)**yr)
            cfs.append(cf); pvs.append(pv)

        tv   =(cfs[-1]*(1+t))/(w-t) if w>t else 0
        pvtv =tv/((1+w)**yrs)
        ev   =sum(pvs)+pvtv
        eq   =ev-nd
        fvs  =eq/shr if shr>0 else 0

        with c2:
            sec("VALUATION RESULTS")
            r1,r2=st.columns(2); r1.metric("Enterprise Value",f"${ev/1e9:,.2f}B"); r2.metric("Equity Value",f"${eq/1e9:,.2f}B")
            r3,r4=st.columns(2); r3.metric("Fair Value/Share",f"${fvs:,.2f}"); r4.metric("TV % of EV",f"{pvtv/ev*100:.1f}%" if ev else "N/A")
            r5,r6=st.columns(2); r5.metric("PV Operating FCF",f"${sum(pvs)/1e9:,.2f}B"); r6.metric("Terminal Value PV",f"${pvtv/1e9:,.2f}B")
            if mode_dcf=="Auto-fill from Ticker" and af_tkr.strip():
                cur_p=get_info(af_tkr.strip().upper()).get("currentPrice") if get_info(af_tkr.strip().upper()) else None
                if cur_p and fvs>0:
                    margin=(fvs/cur_p-1)*100
                    mc=st.columns(2)
                    mc[0].metric("Current Price",f"${cur_p:,.2f}")
                    mc[1].metric("Margin of Safety",f"{margin:+.1f}%")

        st.markdown("---")
        fig_dcf=go.Figure()
        fig_dcf.add_trace(go.Bar(x=[f"Y{i+1}" for i in range(yrs)],y=[v/1e6 for v in cfs],name="Projected FCF",marker_color="#F5A623",opacity=0.85))
        fig_dcf.add_trace(go.Bar(x=[f"Y{i+1}" for i in range(yrs)],y=[v/1e6 for v in pvs],name="PV of FCF",marker_color="#3B8EF0",opacity=0.85))
        fig_dcf.update_layout(**pla({"xaxis":yaxis_plain(),"yaxis":dict(title="$ Millions",**yaxis_plain()),"barmode":"group","height":320,"title":"Projected FCF vs Present Value"}))
        st.plotly_chart(fig_dcf,use_container_width=True)

        sec("SENSITIVITY — FAIR VALUE vs WACC × FCF GROWTH")
        wacc_range=[w-0.03,w-0.015,w,w+0.015,w+0.03]
        grow_range=[g-0.03,g-0.015,g,g+0.015,g+0.03]
        tbl={}
        for gr in grow_range:
            if gr<=0: continue
            rl=f"G {gr*100:.1f}%"
            row={}
            for wc in wacc_range:
                cl=f"W {wc*100:.1f}%"
                if wc<=t or wc<=0:row[cl]="N/A";continue
                cs=[fcf*((1+gr)**yr)/((1+wc)**yr) for yr in range(1,yrs+1)]
                tv_s=(fcf*((1+gr)**yrs)*(1+t))/(wc-t)/((1+wc)**yrs)
                ev_s=sum(cs)+tv_s
                row[cl]=f"${(ev_s-nd)/shr:,.0f}" if shr else "N/A"
            tbl[rl]=row
        if tbl: st.dataframe(pd.DataFrame(tbl).T,use_container_width=True)

    elif mode_dcf=="Reverse DCF":
        sec("REVERSE DCF — IMPLIED GROWTH RATE")
        rev_tkr=st.text_input("Ticker","AAPL",key="rev_tkr")
        if rev_tkr.strip():
            ri=get_info(rev_tkr.strip().upper())
            if ri:
                mkt_cap=ri.get("marketCap",0); nd_r=(ri.get("totalDebt",0) or 0)-(ri.get("totalCash",0) or 0)
                mkt_ev=mkt_cap+nd_r; fcf_r=ri.get("freeCashflow",0) or 0
                wacc_r=st.slider("WACC (%)",4,20,9,key="wacc_r")/100
                tg_r=st.slider("Terminal Growth (%)",0,5,2,key="tg_r")/100
                yrs_r=st.slider("Years",5,20,10,key="yrs_r")
                m1,m2,m3=st.columns(3)
                m1.metric("Market Cap",f"${mkt_cap/1e9:.1f}B")
                m2.metric("FCF (TTM)",f"${fcf_r/1e9:.2f}B")
                m3.metric("EV",f"${mkt_ev/1e9:.1f}B")
                if fcf_r>0 and mkt_ev>0:
                    from scipy.optimize import brentq
                    def dcf_ev(g):
                        cs=[fcf_r*((1+g)**yr)/((1+wacc_r)**yr) for yr in range(1,yrs_r+1)]
                        tv=(fcf_r*((1+g)**yrs_r)*(1+tg_r))/(wacc_r-tg_r)/((1+wacc_r)**yrs_r) if wacc_r>tg_r else 0
                        return sum(cs)+tv
                    try:
                        implied_g=brentq(lambda g:dcf_ev(g)-mkt_ev,-0.3,1.0,maxiter=200)
                        st.success(f"📊 **Implied Growth Rate: {implied_g*100:+.2f}% p.a.** (to justify current EV of ${mkt_ev/1e9:.1f}B with WACC={wacc_r*100:.1f}%, TG={tg_r*100:.1f}%)")
                    except Exception as e:
                        st.warning(f"Could not solve: {e}")

    else:  # Monte Carlo
        sec("MONTE CARLO SIMULATION — DCF DISTRIBUTION")
        mc_fcf=st.number_input("Base FCF ($)",value=1_000_000_000,step=50_000_000,format="%d",key="mc_fcf")
        mc1,mc2,mc3=st.columns(3)
        with mc1:
            g_mu=st.slider("Growth μ (%)",1,40,10,key="mc_gmu"); g_std=st.slider("Growth σ (%)",1,20,5,key="mc_gstd")
        with mc2:
            w_mu=st.slider("WACC μ (%)",5,18,9,key="mc_wmu"); w_std=st.slider("WACC σ (%)",1,5,1,key="mc_wstd")
        with mc3:
            mc_yrs=st.slider("Years",5,20,10,key="mc_yrs"); mc_n=st.select_slider("Simulations",[1000,5000,10000,50000],value=10000,key="mc_n")
        mc_shr=st.number_input("Shares",value=1_000_000_000,step=10_000_000,format="%d",key="mc_shr")
        mc_nd=st.number_input("Net Debt",value=0,step=100_000_000,format="%d",key="mc_nd")

        if st.button("▶ RUN MONTE CARLO",use_container_width=True):
            np.random.seed(42)
            g_s=np.random.normal(g_mu/100,g_std/100,mc_n).clip(-0.5,2)
            w_s=np.random.normal(w_mu/100,w_std/100,mc_n).clip(0.02,0.4)
            tg_mc=0.025
            fvs_s=[]
            for g,w in zip(g_s,w_s):
                if w<=tg_mc: fvs_s.append(np.nan); continue
                cs=[mc_fcf*((1+g)**yr)/((1+w)**yr) for yr in range(1,mc_yrs+1)]
                tv=(mc_fcf*((1+g)**mc_yrs)*(1+tg_mc))/(w-tg_mc)/((1+w)**mc_yrs)
                ev=sum(cs)+tv; fvs_s.append((ev-mc_nd)/mc_shr if mc_shr else np.nan)
            fvs_arr=np.array(fvs_s); fvs_arr=fvs_arr[~np.isnan(fvs_arr) & (fvs_arr>0) & (fvs_arr<1e6)]
            fig_mc=go.Figure()
            fig_mc.add_trace(go.Histogram(x=fvs_arr,nbinsx=100,marker_color="#F5A623",opacity=0.8,name="Fair Value"))
            for pct,col,lbl in [(5,"#E74C3C","P5"),(50,"#FFFFFF","Median"),(95,"#2ECC71","P95")]:
                v=np.percentile(fvs_arr,pct)
                fig_mc.add_vline(x=v,line_dash="dash",line_color=col,annotation_text=f"{lbl}: ${v:,.0f}",annotation_font_color=col)
            fig_mc.update_layout(**pla({"height":360,"title":f"Monte Carlo Distribution — {mc_n:,} Simulations","xaxis":dict(title="Fair Value / Share",**yaxis_plain()),"yaxis":dict(title="Frequency",**yaxis_plain())}))
            st.plotly_chart(fig_mc,use_container_width=True)
            mc_cols=st.columns(5)
            for col_w,pct,label in zip(mc_cols,[5,25,50,75,95],["P5","P25","Median","P75","P95"]):
                col_w.metric(label,f"${np.percentile(fvs_arr,pct):,.0f}")

# ══════════════════════════════════════════════════════════
#  PAGE: MULTI-COMPARE
# ══════════════════════════════════════════════════════════
elif choice == "Multi-Compare":
    ptitle("MULTI-ASSET COMPARISON","Returns · Fundamentals · Correlation · Risk-adjusted metrics")

    mode_mc=st.radio("Mode:",["📈 Returns","🏢 Fundamentals","📉 Inflation Proxy","⚡ Risk Metrics"],horizontal=True)
    st.markdown("---")

    if mode_mc=="📈 Returns":
        c1,c2=st.columns([4,2])
        with c1: tk_in=st.text_input("Tickers (comma)","AAPL,MSFT,NVDA,TSLA,SPY,QQQ")
        with c2:
            h_map={"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","2Y":"2y","3Y":"3y","5Y":"5y","10Y":"10y","20Y":"20y","MAX":"max"}
            h_lbl=st.selectbox("Horizon",list(h_map.keys()),index=6)
        tk_list=[x.strip().upper() for x in tk_in.split(",") if x.strip()]
        if tk_list:
            fr={t:s for t in tk_list for s in [get_close(t,period=h_map[h_lbl])] if not s.empty}
            if fr:
                d=pd.DataFrame(fr).dropna(how="all").ffill()
                r=((d/d.iloc[0])-1)*100
                fig_r=go.Figure()
                for idx,col in enumerate(r.columns):
                    fig_r.add_trace(go.Scatter(x=r.index,y=r[col],name=f"{col} ({r[col].iloc[-1]:+.1f}%)",line=dict(width=2,color=COLORS[idx%len(COLORS)])))
                fig_r.add_hline(y=0,line_dash="dot",line_color="#1E4976")
                fig_r.update_layout(**pla({"xaxis":xaxis_time(),"yaxis":dict(title="Return %",**yaxis_plain()),"height":480,"title":f"Normalized Returns — {h_lbl}"}))
                st.plotly_chart(fig_r,use_container_width=True)
                dr=d.pct_change().dropna(); ay=max((d.index[-1]-d.index[0]).days/365.25,0.1)
                stats=[{"Ticker":col,"Total Return":f"{r[col].iloc[-1]:+.1f}%",
                        "CAGR":f"{((1+r[col].iloc[-1]/100)**(1/ay)-1)*100:+.2f}%",
                        "Ann. Vol":f"{dr[col].std()*np.sqrt(252)*100:.1f}%",
                        "Sharpe":f"{((1+r[col].iloc[-1]/100)**(1/ay)-1)/max(dr[col].std()*np.sqrt(252),0.001):.2f}",
                        "Max DD":f"{((d[col]/d[col].cummax())-1).min()*100:.1f}%",
                        "Years":f"{ay:.1f}"} for col in r.columns]
                st.dataframe(pd.DataFrame(stats).set_index("Ticker"),use_container_width=True)
                if len(fr)>=2:
                    sec("CORRELATION")
                    cr=dr.corr()
                    fc=go.Figure(go.Heatmap(z=cr.values,x=cr.columns.tolist(),y=cr.index.tolist(),colorscale=[[0,"#E74C3C"],[0.5,"#06111F"],[1,"#2ECC71"]],zmid=0,zmin=-1,zmax=1,text=cr.round(2).values,texttemplate="%{text}"))
                    fc.update_layout(**pla({"height":340,"title":"Return Correlation Matrix"}))
                    st.plotly_chart(fc,use_container_width=True)

    elif mode_mc=="🏢 Fundamentals":
        c1,c2=st.columns([3,2])
        with c1: fund_in=st.text_input("Tickers","AAPL,MSFT,GOOGL,AMZN,META")
        with c2: fund_m=st.selectbox("Metric",["P/E Historical","P/S Historical","Market Cap ($B)","EPS","Revenue ($B)","Gross Profit ($B)","Net Income ($B)","EBITDA ($B)","FCF ($B)","D/E Snapshot","Op.Margin % Snap","ROE % Snap"])
        fund_list=[x.strip().upper() for x in fund_in.split(",") if x.strip()]
        yrs_b=st.slider("Years of history",1,25,10,key="fyb")
        if fund_list:
            sec("FUNDAMENTAL SNAPSHOT TABLE")
            snap=[]
            for tkr in fund_list:
                inf=get_info(tkr)
                if not inf: continue
                snap.append({"Ticker":tkr,
                    "P/E TTM":f"{inf.get('trailingPE'):.1f}" if inf.get("trailingPE") else "N/A",
                    "P/E Fwd":f"{inf.get('forwardPE'):.1f}" if inf.get("forwardPE") else "N/A",
                    "P/B":f"{inf.get('priceToBook'):.2f}" if inf.get("priceToBook") else "N/A",
                    "P/S":f"{inf.get('priceToSalesTrailing12Months'):.1f}" if inf.get("priceToSalesTrailing12Months") else "N/A",
                    "EV/EBITDA":f"{inf.get('enterpriseToEbitda'):.1f}" if inf.get("enterpriseToEbitda") else "N/A",
                    "Rev $B":f"{inf.get('totalRevenue',0)/1e9:.1f}" if inf.get("totalRevenue") else "N/A",
                    "EBITDA $B":f"{inf.get('ebitda',0)/1e9:.1f}" if inf.get("ebitda") else "N/A",
                    "FCF $B":f"{inf.get('freeCashflow',0)/1e9:.1f}" if inf.get("freeCashflow") else "N/A",
                    "ROE %":f"{inf.get('returnOnEquity',0)*100:.1f}" if inf.get("returnOnEquity") else "N/A",
                    "Op.Mgn %":f"{inf.get('operatingMargins',0)*100:.1f}" if inf.get("operatingMargins") else "N/A",
                    "D/E":f"{inf.get('debtToEquity',0)/100:.2f}" if inf.get("debtToEquity") else "N/A",
                    "Beta":f"{inf.get('beta'):.2f}" if inf.get("beta") else "N/A",
                })
            if snap: st.dataframe(pd.DataFrame(snap).set_index("Ticker"),use_container_width=True)

    elif mode_mc=="📉 Inflation Proxy":
        st.info("TIPS proxy: **TIP** · **RINF** · **STIP** · **VTIP** · **SCHP**")
        c1,c2=st.columns([4,2])
        with c1: infl_in=st.text_input("TIPS Tickers","TIP,RINF,STIP,SCHP")
        with c2:
            ih_map={"1Y":"1y","3Y":"3y","5Y":"5y","10Y":"10y","20Y":"20y","MAX":"max"}
            ih_lbl=st.selectbox("Horizon",list(ih_map.keys()),index=3,key="ih3")
        comp_in=st.text_input("Compare with","SPY,GLD,BND,IEF")
        all_t=list(dict.fromkeys([x.strip().upper() for x in infl_in.split(",") if x.strip()]+[x.strip().upper() for x in comp_in.split(",") if x.strip()]))
        infl_lst=[x.strip().upper() for x in infl_in.split(",") if x.strip()]
        fr_i={t:s for t in all_t for s in [get_close(t,period=ih_map[ih_lbl])] if not s.empty}
        if fr_i:
            d=pd.DataFrame(fr_i).dropna(how="all").ffill()
            r=((d/d.iloc[0])-1)*100
            fig_i=go.Figure()
            preset={"TIP":"#F5A623","RINF":"#E74C3C","STIP":"#F39C12","VTIP":"#E67E22","SCHP":"#FFA726","SPY":"#3B8EF0","GLD":"#2ECC71","BND":"#9B59B6","IEF":"#00BCD4"}
            for idx,col in enumerate(r.columns):
                fig_i.add_trace(go.Scatter(x=r.index,y=r[col],name=col,line=dict(width=2.5 if col in infl_lst else 1.5,dash="solid" if col in infl_lst else "dot",color=preset.get(col,COLORS[idx%len(COLORS)]))))
            fig_i.add_hline(y=0,line_dash="dot",line_color="#1E4976")
            fig_i.update_layout(**pla({"xaxis":xaxis_time(),"yaxis":dict(title="Return % (base 100)",**yaxis_plain()),"height":480,"title":f"Inflation Proxy vs Assets — {ih_lbl}"}))
            st.plotly_chart(fig_i,use_container_width=True)

    else:  # Risk Metrics
        c1,c2=st.columns([4,2])
        with c1: rm_in=st.text_input("Tickers","AAPL,NVDA,TSLA,SPY,GLD,TLT")
        with c2: rm_per=st.selectbox("Period",["1y","3y","5y","10y"],index=2,key="rm_per")
        rm_list=[x.strip().upper() for x in rm_in.split(",") if x.strip()]
        rf_rm=st.slider("Risk-free (%)",0.0,7.0,4.0,step=0.1,key="rf_rm")/100
        if rm_list:
            fr_r={t:s for t in rm_list for s in [get_close(t,period=rm_per)] if not s.empty}
            if fr_r:
                d=pd.DataFrame(fr_r).dropna(how="all").ffill()
                dr=d.pct_change().dropna(); ay=max((d.index[-1]-d.index[0]).days/365.25,0.1)
                rm_rows=[]
                for col in dr.columns:
                    r_tot=((d[col].iloc[-1]/d[col].iloc[0])-1)*100
                    r_ann=((1+r_tot/100)**(1/ay)-1)*100
                    vol=dr[col].std()*np.sqrt(252)*100
                    dd=((d[col]/d[col].cummax())-1).min()*100
                    sharpe=(r_ann/100-rf_rm)/(vol/100) if vol>0 else np.nan
                    neg=dr[col][dr[col]<0]; dv=neg.std()*np.sqrt(252)*100 if len(neg)>1 else 0
                    sortino=(r_ann/100-rf_rm)/(dv/100) if dv>0 else np.nan
                    calmar=r_ann/abs(dd) if dd<0 else np.nan
                    var95=np.percentile(dr[col].values,5)*100
                    rm_rows.append({"Ticker":col,"CAGR":f"{r_ann:+.2f}%","Ann.Vol":f"{vol:.1f}%","MaxDD":f"{dd:.1f}%","Sharpe":f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A","Sortino":f"{sortino:.2f}" if not np.isnan(sortino) else "N/A","Calmar":f"{calmar:.2f}" if not np.isnan(calmar) else "N/A","VaR95":f"{var95:.2f}%","Beta vs SPY":"—"})
                if rm_rows: st.dataframe(pd.DataFrame(rm_rows).set_index("Ticker"),use_container_width=True)

# ══════════════════════════════════════════════════════════
#  PAGE: PORTFOLIO BACKTEST
# ══════════════════════════════════════════════════════════
elif choice == "Portfolio Backtest":
    ptitle("PORTFOLIO BACKTEST","Equity curve · Risk metrics · Drawdown · Factor exposure · Optimization")

    sec("PORTFOLIO COMPOSITION")
    n_a=st.slider("Number of assets",2,12,4)
    defs=["VOO","GLD","TLT","QQQ","BND","VNQ","EEM","PDBC","IAU","VWCE.DE","AAPL","NVDA"]
    ct=st.columns(n_a); cw=st.columns(n_a)
    assets,weights=[],[]
    dw=round(100/n_a)
    for i in range(n_a):
        with ct[i]: a=st.text_input(f"Asset {i+1}",defs[i] if i<len(defs) else "",key=f"at_{i}"); assets.append(a.strip().upper())
        with cw[i]: w=st.slider(assets[i] or f"A{i+1}",0,100,dw,key=f"aw_{i}"); weights.append(w)

    tw=sum(weights)
    st.warning(f"⚠ Weights sum: {tw}%") if tw!=100 else st.success("✅ Weights at 100%")

    st.markdown("---")
    sec("PARAMETERS")
    p1,p2,p3,p4=st.columns(4)
    with p1:
        bench_map={"S&P 500 (^GSPC)":"^GSPC","Nasdaq (^IXIC)":"^IXIC","MSCI World (VWCE.DE)":"VWCE.DE","60/40 Custom":None}
        bench_lbl=st.selectbox("Benchmark",list(bench_map.keys()))
        bench=bench_map[bench_lbl]
    with p2: years=st.slider("Horizon (years)",1,30,10,key="bt_yrs")
    with p3: rf_bt=st.slider("Risk-free (%)",0.0,7.0,4.2,step=0.1)
    with p4: rebal=st.selectbox("Rebalancing",["None","Monthly","Quarterly","Annually"])

    if bench is None:
        bc1,bc2=st.columns(2)
        with bc1: be=st.text_input("Equity","SPY")
        with bc2: bb=st.text_input("Bond","AGG")
    else: be,bb="SPY","AGG"

    run_bt=st.button("▶  RUN BACKTEST",use_container_width=True)

    if run_bt and tw==100:
        vp=[(a,weights[i]) for i,a in enumerate(assets) if a]
        va=[p[0] for p in vp]; wn=[p[1]/100 for p in vp]
        start_s=(datetime.now()-timedelta(days=365*years)).strftime("%Y-%m-%d")
        rf=rf_bt/100; b_tks=[bench] if bench else [be.upper(),bb.upper()]

        with st.spinner("Downloading data..."):
            fr={}
            for tk in va+b_tks:
                s=get_close(tk,start=start_s)
                if not s.empty: fr[tk]=s
                else: st.warning(f"⚠ No data: {tk}")

        if fr:
            data=pd.DataFrame(fr).dropna(how="all").ffill().bfill().dropna(axis=1,how="all")
            norm=(data/data.iloc[0])-1

            # Build strategy
            sdf=pd.DataFrame(index=data.index); tw2=0.0
            for i,a in enumerate(va):
                if a in data.columns: sdf[a]=norm[a]*wn[i]; tw2+=wn[i]
            if tw2>0 and abs(tw2-1)>0.01: sdf=sdf/tw2
            strat=sdf.sum(axis=1).ffill().dropna()

            if len(strat)>=2:
                ay=max((strat.index[-1]-strat.index[0]).days/365.25,0.1)
                dr=strat.pct_change().dropna(); dr=dr[dr.abs()<0.5]
                tot_ret=float(strat.iloc[-1])*100
                ann_ret=((1+tot_ret/100)**(1/ay)-1)*100
                vol=float(dr.std())*np.sqrt(252)*100 if not np.isnan(dr.std()) else 0
                sharpe=(ann_ret/100-rf)/(vol/100) if vol>0 else 0
                pc=(1+strat); rm=pc.cummax(); dd_s=(pc/rm)-1; max_dd=float(dd_s.min())*100
                calmar=ann_ret/abs(max_dd) if max_dd<0 else float('inf')
                neg=dr[dr<0]; dv=float(neg.std())*np.sqrt(252)*100 if len(neg)>1 else 0
                sortino=(ann_ret/100-rf)/(dv/100) if dv>0 else 0
                arr=dr.dropna().values
                var95=float(np.percentile(arr,5))*100 if len(arr)>20 else 0
                cvar95=float(arr[arr<=np.percentile(arr,5)].mean())*100 if len(arr)>20 else 0
                win_r=float((dr>0).mean())*100
                thr=rf/252; go_=dr[dr>thr]-thr; lo_=thr-dr[dr<thr]
                omega=float(go_.sum()/lo_.sum()) if float(lo_.sum())>0 else 999

                # Benchmark
                if bench is None:
                    beq2,bbd2=be.upper(),bb.upper()
                    if beq2 in norm.columns and bbd2 in norm.columns: bench_s=norm[beq2]*0.6+norm[bbd2]*0.4
                    elif beq2 in norm.columns: bench_s=norm[beq2]
                    else: bench_s=None
                    bench_name=f"60%{beq2}+40%{bbd2}"
                else:
                    bench_s=norm[bench] if bench in norm.columns else None
                    bench_name=bench_lbl

                beta_v=alpha_v=delta_b=bench_ann=None
                if bench_s is not None and len(bench_s.dropna())>10:
                    bsc=bench_s.dropna(); bay=max((bsc.index[-1]-bsc.index[0]).days/365.25,0.1)
                    bench_ann=((1+float(bsc.iloc[-1]))**(1/bay)-1)*100
                    delta_b=tot_ret-float(bsc.iloc[-1])*100
                    try:
                        br=bench_s.pct_change().dropna(); br=br[br.abs()<0.5]
                        al=pd.concat([dr,br],axis=1,join="inner").dropna(); al.columns=["s","b"]
                        if len(al)>30:
                            cv=float(al.cov().iloc[0,1]); vb=float(al["b"].var())
                            beta_v=cv/vb if vb>1e-10 else None
                            if beta_v and bench_ann: alpha_v=ann_ret-(rf_bt+beta_v*(bench_ann-rf_bt))
                    except: pass

                def _f(v,s="%",d=2):
                    if v is None or (isinstance(v,float) and (np.isnan(v) or np.isinf(v))): return "N/A"
                    fmt=f"{{:+.{d}f}}{s}" if s=="%" else f"{{:.{d}f}}{s}"
                    return fmt.format(v)

                sec("PERFORMANCE DASHBOARD")
                k1,k2,k3,k4=st.columns(4)
                k1.metric("Total Return",_f(tot_ret)); k2.metric("CAGR",_f(ann_ret))
                k3.metric("Ann. Volatility",f"{vol:.2f}%"); k4.metric("Max Drawdown",_f(max_dd))
                k5,k6,k7,k8=st.columns(4)
                k5.metric("Sharpe",f"{sharpe:.3f}"); k6.metric("Sortino",f"{sortino:.3f}")
                k7.metric("Calmar",f"{calmar:.3f}" if not np.isinf(calmar) else "∞"); k8.metric("Omega",f"{omega:.2f}" if omega<999 else ">999")
                k9,k10,k11,k12=st.columns(4)
                k9.metric("VaR 95%",f"{var95:.2f}%"); k10.metric("CVaR 95%",f"{cvar95:.2f}%")
                k11.metric("Win Rate",f"{win_r:.1f}%"); k12.metric("Beta",f"{beta_v:.2f}" if beta_v else "N/A")
                k13,k14,k15,k16=st.columns(4)
                k13.metric(f"Alpha vs {bench_name}",_f(alpha_v) if alpha_v else "N/A")
                k14.metric(f"Delta vs {bench_name}",_f(delta_b) if delta_b else "N/A")
                k15.metric("Backtest Years",f"{ay:.1f}"); k16.metric("Trading Days",str(len(dr)))

                sec("EQUITY CURVE")
                fig_eq=go.Figure()
                fig_eq.add_trace(go.Scatter(x=strat.index,y=strat*100,name="Strategy",line=dict(width=3,color="#F5A623"),fill="tozeroy",fillcolor="rgba(245,166,35,0.05)"))
                if bench_s is not None and len(bench_s.dropna())>2:
                    fig_eq.add_trace(go.Scatter(x=bench_s.index,y=bench_s*100,name=bench_name,line=dict(width=2,dash="dash",color="#5A88B0")))
                for idx,a in enumerate(va):
                    if a in norm.columns:
                        fig_eq.add_trace(go.Scatter(x=norm.index,y=norm[a]*100,name=f"{a}({vp[idx][1]}%)",line=dict(width=1,color=COLORS[(idx+2)%len(COLORS)]),opacity=0.45))
                fig_eq.add_hline(y=0,line_dash="dot",line_color="#1E4976")
                fig_eq.update_layout(**pla({"xaxis":xaxis_time(),"yaxis":dict(title="Return %",**yaxis_plain()),"height":500,"title":f"Portfolio Equity Curve — {ay:.0f}Y · {len(dr)} days"}))
                st.plotly_chart(fig_eq,use_container_width=True)

                c_dd,c_rs=st.columns(2)
                with c_dd:
                    sec("DRAWDOWN")
                    fig_dd=go.Figure()
                    fig_dd.add_trace(go.Scatter(x=dd_s.index,y=dd_s*100,name="DD",fill="tozeroy",line=dict(color="#E74C3C",width=1.5),fillcolor="rgba(231,76,60,0.1)"))
                    fig_dd.update_layout(**pla({"xaxis":xaxis_time(),"yaxis":dict(title="Drawdown %",**yaxis_plain()),"height":280,"title":"Drawdown from Peak"}))
                    st.plotly_chart(fig_dd,use_container_width=True)

                mr=min(252,max(30,len(dr)//4))
                with c_rs:
                    sec(f"ROLLING SHARPE ({mr}d)")
                    rvol=dr.rolling(mr,min_periods=mr//2).std()*np.sqrt(252)
                    rret=dr.rolling(mr,min_periods=mr//2).mean()*252
                    rsh=((rret-rf)/rvol).replace([np.inf,-np.inf],np.nan)
                    fig_rs=go.Figure()
                    fig_rs.add_trace(go.Scatter(x=rsh.index,y=rsh,name="Rolling Sharpe",line=dict(color="#F5A623",width=1.5)))
                    fig_rs.add_hline(y=0,line_dash="dot",line_color="#1E4976")
                    fig_rs.add_hline(y=1,line_dash="dot",line_color="#2ECC71",annotation_text="Sharpe=1",annotation_font_color="#2ECC71")
                    fig_rs.update_layout(**pla({"height":280,"title":f"Rolling Sharpe ({mr}d)"}))
                    st.plotly_chart(fig_rs,use_container_width=True)

                sec("MONTHLY RETURNS HEATMAP")
                try:
                    mth=strat.resample("ME").last().pct_change().dropna()*100
                    mth=mth[mth.abs()<50]
                    mdf=pd.DataFrame({"Y":mth.index.year,"M":mth.index.month,"R":mth.values})
                    pvt=mdf.pivot(index="Y",columns="M",values="R")
                    mn=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                    pvt.columns=[mn[m-1] for m in pvt.columns]
                    fig_mth=go.Figure(go.Heatmap(z=pvt.values,x=pvt.columns.tolist(),y=pvt.index.tolist(),colorscale=[[0,"#E74C3C"],[0.5,"#06111F"],[1,"#2ECC71"]],zmid=0,text=[[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in pvt.values],texttemplate="%{text}"))
                    fig_mth.update_layout(**pla({"height":max(220,len(pvt)*28+80),"title":"Monthly Returns (%)"}))
                    st.plotly_chart(fig_mth,use_container_width=True)
                except Exception as e:
                    st.info(f"Heatmap unavailable: {e}")

                c_hist,c_corr=st.columns(2)
                with c_hist:
                    sec("RETURN DISTRIBUTION")
                    fig_h=go.Figure()
                    fig_h.add_trace(go.Histogram(x=arr*100,nbinsx=80,marker_color="#F5A623",opacity=0.75,name="Returns"))
                    if var95: fig_h.add_vline(x=var95,line_dash="dash",line_color="#E74C3C",annotation_text=f"VaR95: {var95:.2f}%",annotation_font_color="#E74C3C")
                    fig_h.add_vline(x=0,line_dash="dot",line_color="#5A88B0")
                    fig_h.update_layout(**pla({"xaxis":dict(title="Daily Return %",**yaxis_plain()),"yaxis":dict(title="Frequency",**yaxis_plain()),"height":280,"title":"Return Distribution"}))
                    st.plotly_chart(fig_h,use_container_width=True)
                with c_corr:
                    avail=[a for a in va if a in norm.columns]
                    if len(avail)>=2:
                        sec("ASSET CORRELATION")
                        cor_d=norm[avail].pct_change().dropna().corr()
                        fig_co=go.Figure(go.Heatmap(z=cor_d.values,x=cor_d.columns.tolist(),y=cor_d.index.tolist(),colorscale=[[0,"#E74C3C"],[0.5,"#06111F"],[1,"#2ECC71"]],zmid=0,text=cor_d.round(2).values,texttemplate="%{text}"))
                        fig_co.update_layout(**pla({"height":280,"title":"Asset Correlation"}))
                        st.plotly_chart(fig_co,use_container_width=True)

                sec("ANALYSIS & RECOMMENDATIONS")
                tips=[]
                if not np.isnan(sharpe):
                    if sharpe<0: tips.append(f"🔴 <b>Negative Sharpe ({sharpe:.2f})</b> — Return below risk-free ({rf_bt:.1f}%). Identify the worst contributor.")
                    elif sharpe<0.5: tips.append(f"🟡 <b>Low Sharpe ({sharpe:.2f})</b> — Consider adding uncorrelated assets: GLD, TLT, REITs.")
                    elif sharpe>=1.5: tips.append(f"🏆 <b>High Sharpe ({sharpe:.2f})</b> — Excellent. Verify over longer period for survivorship bias.")
                    else: tips.append(f"✅ <b>Acceptable Sharpe ({sharpe:.2f})</b> — Target >1.0 for consistent alpha.")
                if vol>25: tips.append(f"⚡ <b>High Volatility ({vol:.1f}%)</b> — Consider 15-25% in aggregate bonds.")
                if max_dd<-40: tips.append(f"💥 <b>Extreme Drawdown ({max_dd:.1f}%)</b> — Implement risk parity or Kelly position sizing.")
                if var95<-3: tips.append(f"📉 <b>High VaR95 ({var95:.2f}%/day)</b> — 1 in 20 days risks >{abs(var95):.1f}% loss.")
                if len(va)<3: tips.append(f"🔀 <b>Low diversification ({len(va)} assets)</b> — 8-15 uncorrelated assets is optimal.")
                if not tips: tips.append("ℹ️ Parameters within normal range. No critical signals.")
                for tip in tips: alert(tip)

    elif run_bt and tw!=100:
        st.error("Weights must sum to 100%.")

# ══════════════════════════════════════════════════════════
#  PAGE: STOCK SCREENER
# ══════════════════════════════════════════════════════════
elif choice == "Stock Screener":
    if st.session_state.screener_selected:
        target=st.session_state.screener_selected
        with st.columns([1,8])[0]:
            if st.button("← Back to Screener"):
                st.session_state.screener_selected=None; st.rerun()
        ptitle(f"TERMINAL — {target}")
        inf_s=get_info(target); sec_s=inf_s.get("sector","") if inf_s else ""
        show_terminal(target,SECTOR_PEERS.get(sec_s,"SPY,QQQ,IWM"))
    else:
        ptitle("STOCK SCREENER",f"Filter across {len(CURATED):,}+ global tickers")

        with st.expander("⚙ FUNDAMENTAL FILTERS", expanded=True):
            c1,c2,c3,c4,c5=st.columns(5)
            with c1:
                pe_max=st.slider("P/E max",0,300,80); pb_max=st.slider("P/B max",0,50,15)
                ps_max=st.slider("P/S max",0,60,20)
            with c2:
                cap_min=st.slider("MktCap min ($B)",0,500,0); cap_max=st.slider("MktCap max ($B)",0,5000,5000)
                de_max=st.slider("D/E max",0,30,20)
            with c3:
                mgn_min=st.slider("Op.Margin min %",-100,80,-100); roe_min=st.slider("ROE min %",-50,100,-50)
                ev_max=st.slider("EV/EBITDA max",0,200,200)
            with c4:
                div_min=st.slider("Div Yield min %",0.0,15.0,0.0,step=0.1)
                beta_min=st.slider("Beta min",-2.0,5.0,-2.0,step=0.1)
                beta_max=st.slider("Beta max",-2.0,10.0,10.0,step=0.1)
            with c5:
                sec_f=st.selectbox("Sector",["All","Technology","Healthcare","Financials","Industrials","Consumer Defensive","Consumer Cyclical","Energy","Communication Services","Utilities","Real Estate","Basic Materials"])
                country_f=st.selectbox("Country",["All","United States","Germany","France","United Kingdom","Switzerland","Italy","Japan","China","Canada","Australia"])
                kw_f=st.text_input("Business keyword","",placeholder="AI, cloud, defense...")

        with st.expander("⚙ PERFORMANCE FILTERS"):
            c1p,c2p,c3p=st.columns(3)
            with c1p:
                rev_g_min=st.slider("Rev Growth min %",-100,200,-100,key="rg_min")
                earn_g_min=st.slider("Earn Growth min %",-100,200,-100,key="eg_min")
            with c2p:
                extra_tickers=st.text_input("Add extra tickers","",placeholder="AMZN, TSLA ...")
            with c3p:
                n_scan=st.selectbox("Tickers to scan",["100 (fast)","300","500","1000","2000","All (~20min+)"])
                sort_by=st.selectbox("Sort by",["Market Cap","P/E","EV/EBITDA","ROE %","Op.Margin %","Div Yield","Rev Growth"])

        run_sc=st.button("▶  RUN SCREENING",use_container_width=True)

        if run_sc:
            UNIVERSE=list(CURATED)
            if extra_tickers.strip():
                UNIVERSE=list(dict.fromkeys(UNIVERSE+[x.strip().upper() for x in extra_tickers.split(",") if x.strip()]))
            n_map={"100 (fast)":100,"300":300,"500":500,"1000":1000,"2000":2000,"All (~20min+)":len(UNIVERSE)}
            n=n_map.get(n_scan,500); scan=UNIVERSE[:n]
            results=[]
            prog=st.progress(0); stat=st.empty()
            for i,tkr in enumerate(scan):
                prog.progress((i+1)/len(scan))
                stat.markdown(f"<div class='term-box' style='padding:0.4rem 0.8rem;margin:0'>⬛ Scanning: <b>{tkr}</b> ({i+1}/{len(scan)})</div>",unsafe_allow_html=True)
                try:
                    inf=get_info(tkr)
                    if not inf: continue
                    pe=inf.get("forwardPE") or inf.get("trailingPE"); pb=inf.get("priceToBook")
                    ps=inf.get("priceToSalesTrailing12Months"); mc=inf.get("marketCap")
                    de=inf.get("debtToEquity"); om=inf.get("operatingMargins"); roe=inf.get("returnOnEquity")
                    eve=inf.get("enterpriseToEbitda"); dy=(inf.get("dividendYield") or 0)*100
                    bt=inf.get("beta"); sec_v=inf.get("sector",""); cntry=inf.get("country","")
                    pr=inf.get("currentPrice") or inf.get("regularMarketPrice") or inf.get("previousClose")
                    nm=inf.get("shortName",tkr); rg=inf.get("revenueGrowth"); eg=inf.get("earningsGrowth")

                    if sec_f!="All" and sec_v!=sec_f: continue
                    if country_f!="All" and cntry!=country_f: continue
                    if kw_f.strip():
                        kw=kw_f.strip().lower()
                        txt=" ".join(filter(None,[inf.get("longBusinessSummary",""),inf.get("industry",""),inf.get("longName",""),sec_v])).lower()
                        if kw not in txt: continue
                    if pe and pe>pe_max: continue
                    if pb and pb>pb_max: continue
                    if ps and ps>ps_max: continue
                    if de and de/100>de_max: continue
                    if eve and eve>ev_max: continue
                    if mc and mc/1e9<cap_min: continue
                    if mc and mc/1e9>cap_max: continue
                    if om and om*100<mgn_min: continue
                    if roe and roe*100<roe_min: continue
                    if dy<div_min: continue
                    if bt is not None and bt<beta_min: continue
                    if bt is not None and bt>beta_max: continue
                    if rg is not None and rg*100<rev_g_min: continue
                    if eg is not None and eg*100<earn_g_min: continue

                    results.append({
                        "Ticker":tkr,"Name":nm[:26],"Sector":sec_v[:18],"Country":cntry,
                        "Price":f"{pr:.2f}" if pr else "N/A","P/E":f"{pe:.1f}" if pe else "N/A",
                        "P/B":f"{pb:.1f}" if pb else "N/A","P/S":f"{ps:.1f}" if ps else "N/A",
                        "EV/EBITDA":f"{eve:.1f}" if eve else "N/A","Op.Mgn%":f"{om*100:.1f}" if om else "N/A",
                        "ROE%":f"{roe*100:.1f}" if roe else "N/A","Div%":f"{dy:.2f}",
                        "Beta":f"{bt:.2f}" if bt else "N/A","D/E":f"{de/100:.2f}" if de else "N/A",
                        "Cap$B":f"{mc/1e9:.1f}" if mc else "N/A",
                        "RevG%":f"{rg*100:.1f}" if rg else "N/A","EarnG%":f"{eg*100:.1f}" if eg else "N/A",
                        "_mc":mc/1e9 if mc else 0,"_pe":pe if pe else 999,"_ev":eve if eve else 999,
                        "_roe":roe*100 if roe else 0,"_mgn":om*100 if om else 0,"_div":dy,
                        "_rg":rg*100 if rg else 0,
                    })
                except Exception: continue
            prog.empty(); stat.empty()
            sm={"Market Cap":("_mc",True),"P/E":("_pe",False),"EV/EBITDA":("_ev",False),
                "ROE %":("_roe",True),"Op.Margin %":("_mgn",True),"Div Yield":("_div",True),"Rev Growth":("_rg",True)}
            sk,rv=sm.get(sort_by,("_mc",True))
            results.sort(key=lambda x:x.get(sk,0),reverse=rv)
            st.session_state.screener_results=results

        if st.session_state.screener_results is _NOT_RUN:
            pass
        elif not st.session_state.screener_results:
            st.warning("No companies found. Broaden your filters.")
        else:
            res=st.session_state.screener_results
            st.success(f"✅  {len(res)} companies found")
            dcols=["Name","Sector","Country","Price","P/E","P/B","P/S","EV/EBITDA","Op.Mgn%","ROE%","Div%","RevG%","EarnG%","Beta","Cap$B"]
            st.dataframe(pd.DataFrame(res)[["Ticker"]+dcols].set_index("Ticker"),use_container_width=True)
            sec("OPEN IN TERMINAL")
            sel=st.selectbox("Select company",[f"{r['Ticker']} — {r['Name']}" for r in res])
            if st.button("⌨  OPEN COMPANY TERMINAL",use_container_width=True):
                st.session_state.screener_selected=sel.split(" — ")[0].strip(); st.rerun()

# ══════════════════════════════════════════════════════════
#  PAGE: MACRO & FIXED INCOME
# ══════════════════════════════════════════════════════════
elif choice == "Macro & Fixed Income":
    ptitle("MACRO & FIXED INCOME","Yield curve · Treasury rates · Credit spreads · Global rates")

    RATES={"^IRX":"3M","^FVX":"5Y","^TNX":"10Y","^TYX":"30Y"}
    sec("US TREASURY YIELD CURVE")
    rc=st.columns(4)
    yields_data={}
    for i,(tk,lbl) in enumerate(RATES.items()):
        p,c=get_price_chg(tk)
        rc[i].metric(f"{lbl} Treasury",f"{p:.3f}%" if p else "N/A",f"{c:+.3f}bps" if c else "—")
        if p: yields_data[lbl]=p

    if len(yields_data)>=2:
        fig_yc=go.Figure()
        x_lbl=list(yields_data.keys()); y_val=list(yields_data.values())
        fig_yc.add_trace(go.Scatter(x=x_lbl,y=y_val,mode="lines+markers",line=dict(color="#F5A623",width=2.5),marker=dict(size=8,color="#F5A623"),fill="tozeroy",fillcolor="rgba(245,166,35,0.06)",name="Yield Curve"))
        for x,y in zip(x_lbl,y_val): fig_yc.add_annotation(x=x,y=y,text=f"{y:.3f}%",showarrow=False,yshift=12,font=dict(color="#F5A623",size=10,family="IBM Plex Mono"))
        fig_yc.update_layout(**pla({"height":300,"title":"US Treasury Yield Curve (Snapshot)","xaxis":dict(title="Maturity",**yaxis_plain()),"yaxis":dict(title="Yield (%)",**yaxis_plain())}))
        st.plotly_chart(fig_yc,use_container_width=True)

    st.markdown("---")
    sec("HISTORICAL YIELD COMPARISON")
    bond_tickers={"TLT (20Y+)":"TLT","IEF (7-10Y)":"IEF","SHY (1-3Y)":"SHY","TIP (Inflation)":"TIP","HYG (HY Credit)":"HYG","LQD (IG Credit)":"LQD","EMB (EM Bonds)":"EMB"}
    bc2=st.columns(4)
    for i,(nm,tk) in enumerate(list(bond_tickers.items())[:4]):
        p,c=get_price_chg(tk)
        bc2[i%4].metric(nm,f"{p:.2f}" if p else "N/A",f"{c:+.2f}%" if c else "—")

    bon_per=st.selectbox("Period",["1y","3y","5y","10y","max"],index=2,key="bon_per")
    fr_b={nm:s for nm,tk in bond_tickers.items() for s in [get_close(tk,period=bon_per)] if not s.empty}
    if fr_b:
        d_b=pd.DataFrame(fr_b).dropna(how="all").ffill()
        r_b=((d_b/d_b.iloc[0])-1)*100
        fig_b=go.Figure()
        for idx,col in enumerate(r_b.columns):
            fig_b.add_trace(go.Scatter(x=r_b.index,y=r_b[col],name=col,line=dict(width=1.8,color=COLORS[idx%len(COLORS)])))
        fig_b.add_hline(y=0,line_dash="dot",line_color="#1E4976")
        fig_b.update_layout(**pla({"xaxis":xaxis_time(),"yaxis":dict(title="Return %",**yaxis_plain()),"height":420,"title":"Fixed Income ETF Performance"}))
        st.plotly_chart(fig_b,use_container_width=True)

    st.markdown("---")
    sec("GLOBAL CENTRAL BANK RATES & CURRENCIES")
    GLOBAL_FX={"EUR/USD":"EURUSD=X","GBP/USD":"GBPUSD=X","USD/JPY":"USDJPY=X","USD/CNY":"USDCNY=X","USD/CHF":"USDCHF=X","AUD/USD":"AUDUSD=X","USD/BRL":"USDBRL=X","DXY Index":"DX-Y.NYB"}
    gc=st.columns(4)
    for i,(nm,tk) in enumerate(GLOBAL_FX.items()):
        p,c=get_price_chg(tk)
        gc[i%4].metric(nm,f"{p:.4f}" if p else "N/A",f"{c:+.3f}%" if c else "—")

# ══════════════════════════════════════════════════════════
#  PAGE: OPTIONS & DERIVATIVES
# ══════════════════════════════════════════════════════════
elif choice == "Options & Derivatives":
    ptitle("OPTIONS & DERIVATIVES","Option chains · Greeks · Implied volatility · Put/Call ratio")

    opt_tkr=st.text_input("Ticker for options","AAPL",key="opt_tkr")
    if opt_tkr.strip():
        tkr_o=opt_tkr.strip().upper()
        calls,puts,exps=get_options_chain(tkr_o)
        if calls is not None and puts is not None:
            inf_o=get_info(tkr_o)
            cur_p=inf_o.get("currentPrice") or inf_o.get("regularMarketPrice") if inf_o else None

            sec("SELECT EXPIRATION")
            if exps:
                exp_sel=st.selectbox("Expiration Date",exps)
                try:
                    chain=yf.Ticker(tkr_o).option_chain(exp_sel)
                    calls,puts=chain.calls,chain.puts
                except: pass

            m1,m2,m3=st.columns(3)
            if cur_p:
                m1.metric("Current Price",f"${cur_p:,.2f}")
            if not calls.empty:
                m2.metric("Call OI Total",f"{calls['openInterest'].sum():,.0f}" if "openInterest" in calls.columns else "N/A")
            if not puts.empty:
                m3.metric("Put OI Total",f"{puts['openInterest'].sum():,.0f}" if "openInterest" in puts.columns else "N/A")
                if not calls.empty and calls.get("openInterest") is not None and puts.get("openInterest") is not None:
                    pc_ratio=puts["openInterest"].sum()/max(calls["openInterest"].sum(),1)
                    m1.metric("Put/Call Ratio",f"{pc_ratio:.2f}")

            tab_calls,tab_puts,tab_iv=st.tabs(["📈 Call Chain","📉 Put Chain","📊 IV Surface"])
            with tab_calls:
                if not calls.empty:
                    disp_cols=[c for c in ["strike","lastPrice","bid","ask","volume","openInterest","impliedVolatility","delta","gamma","theta"] if c in calls.columns]
                    df_c=calls[disp_cols].copy()
                    if cur_p and "strike" in df_c.columns:
                        df_c=df_c.iloc[(df_c["strike"]-cur_p).abs().argsort()[:30]]
                    if "impliedVolatility" in df_c.columns:
                        df_c["impliedVolatility"]=df_c["impliedVolatility"].apply(lambda x:f"{x*100:.1f}%" if pd.notna(x) else "N/A")
                    st.dataframe(df_c.reset_index(drop=True),use_container_width=True)
            with tab_puts:
                if not puts.empty:
                    disp_cols=[c for c in ["strike","lastPrice","bid","ask","volume","openInterest","impliedVolatility","delta","gamma","theta"] if c in puts.columns]
                    df_p=puts[disp_cols].copy()
                    if cur_p and "strike" in df_p.columns:
                        df_p=df_p.iloc[(df_p["strike"]-cur_p).abs().argsort()[:30]]
                    if "impliedVolatility" in df_p.columns:
                        df_p["impliedVolatility"]=df_p["impliedVolatility"].apply(lambda x:f"{x*100:.1f}%" if pd.notna(x) else "N/A")
                    st.dataframe(df_p.reset_index(drop=True),use_container_width=True)
            with tab_iv:
                if not calls.empty and "impliedVolatility" in calls.columns and "strike" in calls.columns:
                    iv_data=calls[["strike","impliedVolatility"]].dropna()
                    if cur_p: iv_data=iv_data[(iv_data["strike"]>cur_p*0.7)&(iv_data["strike"]<cur_p*1.3)]
                    fig_iv=go.Figure()
                    fig_iv.add_trace(go.Scatter(x=iv_data["strike"],y=iv_data["impliedVolatility"]*100,mode="lines+markers",line=dict(color="#F5A623",width=2),marker=dict(size=5),name="Call IV"))
                    if not puts.empty and "impliedVolatility" in puts.columns:
                        iv_p=puts[["strike","impliedVolatility"]].dropna()
                        if cur_p: iv_p=iv_p[(iv_p["strike"]>cur_p*0.7)&(iv_p["strike"]<cur_p*1.3)]
                        fig_iv.add_trace(go.Scatter(x=iv_p["strike"],y=iv_p["impliedVolatility"]*100,mode="lines+markers",line=dict(color="#3B8EF0",width=2),marker=dict(size=5),name="Put IV"))
                    if cur_p: fig_iv.add_vline(x=cur_p,line_dash="dash",line_color="#2ECC71",annotation_text=f"Spot ${cur_p:.2f}",annotation_font_color="#2ECC71")
                    fig_iv.update_layout(**pla({"height":380,"title":f"Implied Volatility Smile — {tkr_o}","xaxis":dict(title="Strike Price",**yaxis_plain()),"yaxis":dict(title="Implied Volatility (%)",**yaxis_plain())}))
                    st.plotly_chart(fig_iv,use_container_width=True)
        else:
            st.warning(f"No options data available for **{tkr_o}**.")

# ══════════════════════════════════════════════════════════
#  PAGE: FX & COMMODITIES
# ══════════════════════════════════════════════════════════
elif choice == "FX & Commodities":
    ptitle("FX & COMMODITIES","Currency pairs · Precious metals · Energy · Agricultural · Soft commodities")

    tab_fx,tab_metals,tab_energy,tab_agri=st.tabs(["🌐 FX Majors","🥇 Metals","⛽ Energy","🌾 Agricultural"])

    with tab_fx:
        FX_PAIRS={
            "EUR/USD":"EURUSD=X","GBP/USD":"GBPUSD=X","USD/JPY":"USDJPY=X","USD/CHF":"USDCHF=X",
            "AUD/USD":"AUDUSD=X","NZD/USD":"NZDUSD=X","USD/CAD":"USDCAD=X","USD/CNY":"USDCNY=X",
            "USD/SEK":"USDSEK=X","USD/NOK":"USDNOK=X","USD/DKK":"USDDKK=X","USD/BRL":"USDBRL=X",
            "USD/MXN":"USDMXN=X","USD/INR":"USDINR=X","USD/KRW":"USDKRW=X","USD/TRY":"USDTRY=X",
            "EUR/GBP":"EURGBP=X","EUR/JPY":"EURJPY=X","GBP/JPY":"GBPJPY=X","DXY":"DX-Y.NYB",
        }
        sec("MAJOR CURRENCY PAIRS")
        fc=st.columns(4)
        for i,(nm,tk) in enumerate(FX_PAIRS.items()):
            p,c=get_price_chg(tk); fc[i%4].metric(nm,f"{p:.4f}" if p else "N/A",f"{c:+.3f}%" if c else "—")
        sec("FX PERFORMANCE CHART")
        fx_sel=st.multiselect("Select pairs",list(FX_PAIRS.keys()),default=["EUR/USD","GBP/USD","USD/JPY","DXY"])
        fx_per=st.selectbox("Period",["1mo","3mo","6mo","1y","3y","5y"],index=3,key="fx_per")
        if fx_sel:
            fr_fx={nm:s for nm in fx_sel for s in [get_close(FX_PAIRS[nm],period=fx_per)] if not s.empty}
            if fr_fx:
                d_fx=pd.DataFrame(fr_fx).dropna(how="all").ffill()
                r_fx=((d_fx/d_fx.iloc[0])-1)*100
                fig_fx=go.Figure()
                for idx,col in enumerate(r_fx.columns):
                    fig_fx.add_trace(go.Scatter(x=r_fx.index,y=r_fx[col],name=col,line=dict(width=1.8,color=COLORS[idx%len(COLORS)])))
                fig_fx.add_hline(y=0,line_dash="dot",line_color="#1E4976")
                fig_fx.update_layout(**pla({"xaxis":xaxis_time(),"yaxis":dict(title="Return %",**yaxis_plain()),"height":380,"title":"FX Performance"}))
                st.plotly_chart(fig_fx,use_container_width=True)

    with tab_metals:
        METALS={"Gold":"GC=F","Silver":"SI=F","Platinum":"PL=F","Palladium":"PA=F","Copper":"HG=F","Aluminum":"ALI=F","Gold ETF (GLD)":"GLD","Silver ETF (SLV)":"SLV","Gold Miners (GDX)":"GDX"}
        sec("PRECIOUS & INDUSTRIAL METALS")
        mc=st.columns(3)
        for i,(nm,tk) in enumerate(METALS.items()):
            p,c=get_price_chg(tk); mc[i%3].metric(nm,f"{p:,.2f}" if p else "N/A",f"{c:+.2f}%" if c else "—")
        sec("METALS PERFORMANCE")
        met_per=st.selectbox("Period",["3mo","6mo","1y","3y","5y","10y","max"],index=2,key="met_per")
        fr_m={nm:s for nm,tk in METALS.items() for s in [get_close(tk,period=met_per)] if not s.empty}
        if fr_m:
            d_m=pd.DataFrame(fr_m).dropna(how="all").ffill()
            r_m=((d_m/d_m.iloc[0])-1)*100
            fig_m=go.Figure()
            for idx,col in enumerate(r_m.columns):
                fig_m.add_trace(go.Scatter(x=r_m.index,y=r_m[col],name=col,line=dict(width=1.8,color=COLORS[idx%len(COLORS)])))
            fig_m.add_hline(y=0,line_dash="dot",line_color="#1E4976")
            fig_m.update_layout(**pla({"xaxis":xaxis_time(),"yaxis":dict(title="Return %",**yaxis_plain()),"height":380,"title":"Metals Performance"}))
            st.plotly_chart(fig_m,use_container_width=True)

    with tab_energy:
        ENERGY={"Crude WTI":"CL=F","Brent Crude":"BZ=F","Natural Gas":"NG=F","Gasoline":"RB=F","Heating Oil":"HO=F","USO ETF":"USO","UNG ETF":"UNG","XLE Energy ETF":"XLE","OIH Oil Services":"OIH"}
        sec("ENERGY COMMODITIES")
        ec=st.columns(3)
        for i,(nm,tk) in enumerate(ENERGY.items()):
            p,c=get_price_chg(tk); ec[i%3].metric(nm,f"{p:,.3f}" if p else "N/A",f"{c:+.2f}%" if c else "—")
        sec("ENERGY PERFORMANCE")
        en_per=st.selectbox("Period",["3mo","6mo","1y","3y","5y"],index=2,key="en_per")
        fr_e={nm:s for nm,tk in ENERGY.items() for s in [get_close(tk,period=en_per)] if not s.empty}
        if fr_e:
            d_e=pd.DataFrame(fr_e).dropna(how="all").ffill()
            r_e=((d_e/d_e.iloc[0])-1)*100
            fig_e=go.Figure()
            for idx,col in enumerate(r_e.columns):
                fig_e.add_trace(go.Scatter(x=r_e.index,y=r_e[col],name=col,line=dict(width=1.8,color=COLORS[idx%len(COLORS)])))
            fig_e.add_hline(y=0,line_dash="dot",line_color="#1E4976")
            fig_e.update_layout(**pla({"xaxis":xaxis_time(),"yaxis":dict(title="Return %",**yaxis_plain()),"height":380,"title":"Energy Commodities Performance"}))
            st.plotly_chart(fig_e,use_container_width=True)

    with tab_agri:
        AGRI={"Corn":"ZC=F","Soybeans":"ZS=F","Wheat":"ZW=F","Coffee":"KC=F","Cotton":"CT=F","Sugar":"SB=F","Orange Juice":"OJ=F","Live Cattle":"LE=F","Lean Hogs":"HE=F","DBA ETF":"DBA"}
        sec("AGRICULTURAL COMMODITIES")
        ag=st.columns(4)
        for i,(nm,tk) in enumerate(AGRI.items()):
            p,c=get_price_chg(tk); ag[i%4].metric(nm,f"{p:,.3f}" if p else "N/A",f"{c:+.2f}%" if c else "—")

# ══════════════════════════════════════════════════════════
#  PAGE: ECONOMIC CALENDAR (Static reference)
# ══════════════════════════════════════════════════════════
elif choice == "Economic Calendar":
    ptitle("ECONOMIC CALENDAR","Key macro events · Earnings calendar · Fed schedule")

    st.info("💡 Economic calendar data requires premium API access (e.g. Quandl, FRED, Refinitiv). Below are live proxy indicators from yFinance and reference links.")

    sec("REAL-TIME MACRO PROXIES")
    macro_tickers={
        "^VIX (Fear)":"^VIX","^MOVE (Bond Vol)":"^MOVE","HYG (Credit Risk)":"HYG",
        "LQD (IG Credit)":"LQD","TLT (Duration)":"TLT","DXY (USD Index)":"DX-Y.NYB",
        "GLD (Gold)":"GLD","CL=F (Oil WTI)":"CL=F","BTC-USD":"BTC-USD",
        "EEM (EM Risk)":"EEM","EURUSD=X":"EURUSD=X","^TNX (10Y Yield)":"^TNX",
    }
    mc_cols=st.columns(4)
    for i,(nm,tk) in enumerate(macro_tickers.items()):
        p,c=get_price_chg(tk); mc_cols[i%4].metric(nm,f"{p:,.3f}" if p else "N/A",f"{c:+.3f}%" if c else "—")

    st.markdown("---")
    sec("EARNINGS CALENDAR — NEXT UPCOMING")
    earn_tickers_watch=["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","JPM","GS","BAC"]
    ec_data=[]
    for tk in earn_tickers_watch:
        try:
            ed=get_earnings_dates(tk)
            if not ed.empty:
                future=ed[ed.index>datetime.now()] if hasattr(ed.index,'tz') else ed
                if not future.empty:
                    next_d=str(future.index[0])[:10] if len(future)>0 else "N/A"
                    ec_data.append({"Ticker":tk,"Next Earnings":next_d})
        except: pass
    if ec_data: st.dataframe(pd.DataFrame(ec_data).set_index("Ticker"),use_container_width=True)

    st.markdown("---")
    sec("KEY DATA SOURCES")
    sources={
        "US Economic Data":"https://fred.stlouisfed.org","Fed Calendar":"https://www.federalreserve.gov/newsevents/calendar.htm",
        "ECB":"https://www.ecb.europa.eu/press/calendars","Earnings Whispers":"https://www.earningswhispers.com",
        "Seeking Alpha Earnings":"https://seekingalpha.com/earnings/earnings-calendar","CME FedWatch":"https://www.cmegroup.com/trading/interest-rates/countdown-to-fomc.html",
    }
    for nm,url in sources.items():
        st.markdown(f"<div class='term-box' style='padding:0.45rem 0.9rem;margin-bottom:5px'><a href='{url}' target='_blank' style='color:#F5A623;font-family:IBM Plex Mono,monospace;font-size:0.78rem;text-decoration:none'>{nm} → {url}</a></div>",unsafe_allow_html=True)

sh

cat > /home/claude/navy_terminal_pro.py << 'ENDOFFILE'
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random, time, warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Navy Terminal Pro", layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────
#  CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
html,body,.stApp,[data-testid="stAppViewContainer"],.main{background-color:#050D1A!important;font-family:'IBM Plex Sans',sans-serif!important}
[data-testid="stSidebar"]{background-color:#030A14!important;border-right:1px solid #0E2440!important;min-height:100vh!important}
[data-testid="stSidebar"] *{color:#FFFFFF!important}
[data-testid="stSidebar"] .stSelectbox>div>div{background-color:#071220!important;border:1px solid #0E2440!important;color:#FFFFFF!important}
[data-testid="stHeader"]{background-color:#030A14!important;border-bottom:1px solid #0E2440!important}
h1,h2,h3,h4,h5,h6{color:#FFFFFF!important;font-family:'IBM Plex Sans',sans-serif!important;font-weight:700!important;letter-spacing:0.02em!important}
p,span,li,div,label,.stMarkdown{color:#D8E4F0!important;font-family:'IBM Plex Sans',sans-serif!important}
.page-title{font-family:'IBM Plex Mono',monospace!important;font-size:1.35rem;font-weight:600;color:#FFFFFF!important;letter-spacing:0.08em;border-left:3px solid #3B8EF0;padding-left:1rem;margin-bottom:0.3rem}
.page-subtitle{color:#7A9DBE!important;font-size:0.8rem;margin-bottom:1.2rem;padding-left:1.3rem;letter-spacing:0.04em}
[data-testid="stMetricValue"]{color:#FFFFFF!important;font-family:'IBM Plex Mono',monospace!important;font-weight:600!important;font-size:1.15rem!important}
[data-testid="stMetricLabel"]{color:#7A9DBE!important;font-size:0.7rem!important;text-transform:uppercase;letter-spacing:0.08em}
[data-testid="metric-container"]{background:linear-gradient(135deg,#071A30 0%,#0A1E38 100%)!important;border:1px solid #0E2440!important;border-top:1px solid #163860!important;border-radius:4px!important;padding:0.8rem 1rem!important}
.stTextInput label,.stSelectbox label,.stMultiSelect label,.stSlider label,.stNumberInput label,.stRadio label,label[data-testid]{color:#7A9DBE!important;font-size:0.72rem!important;font-weight:600!important;letter-spacing:0.08em!important;text-transform:uppercase!important}
.stSlider [data-baseweb="slider"] [role="slider"]{background-color:#3B8EF0!important;border-color:#3B8EF0!important}
.stSlider [data-baseweb="slider"] div[class*="Track"] div:first-child{background-color:#3B8EF0!important}
.stSlider span{color:#7A9DBE!important}
.stNumberInput input{background-color:#071220!important;color:#FFFFFF!important;border:1px solid #0E2440!important;border-radius:3px!important}
.stNumberInput button{background-color:#0E2440!important;color:#FFFFFF!important;border:none!important}
input[type="text"],textarea,.stTextInput input{background-color:#071220!important;color:#FFFFFF!important;border:1px solid #0E2440!important;border-radius:3px!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.86rem!important}
input[type="text"]:focus,textarea:focus{border-color:#3B8EF0!important;box-shadow:0 0 0 1px rgba(59,142,240,0.3)!important}
.stSelectbox [data-baseweb="select"]>div{background-color:#071220!important;border:1px solid #0E2440!important;color:#FFFFFF!important}
[data-baseweb="popover"]{background-color:#071220!important;border:1px solid #0E2440!important}
[data-baseweb="menu"]{background-color:#071220!important;border:1px solid #0E2440!important}
[data-baseweb="option"]{background-color:#071220!important;color:#D8E4F0!important;font-family:'IBM Plex Sans',sans-serif!important;font-size:0.83rem!important}
[data-baseweb="option"]:hover{background-color:#0E2440!important;color:#FFFFFF!important}
[data-baseweb="option"][aria-selected="true"]{background-color:#163860!important;color:#3B8EF0!important;font-weight:600!important}
li[role="option"]{background-color:#071220!important;color:#D8E4F0!important}
li[role="option"]:hover{background-color:#0E2440!important;color:#FFFFFF!important}
.stRadio>div>label{color:#D8E4F0!important;text-transform:none!important;font-size:0.86rem!important}
.dataframe,table{background-color:#071220!important;color:#FFFFFF!important;border-collapse:collapse!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.79rem!important}
thead tr th{color:#7A9DBE!important;background-color:#040F1E!important;border-bottom:1px solid #0E2440!important;text-transform:uppercase;letter-spacing:0.06em;padding:0.5rem 0.85rem!important;font-size:0.68rem!important}
tbody tr td{color:#D8E4F0!important;border-bottom:1px solid #0A1A2E!important;padding:0.42rem 0.85rem!important}
tbody tr:hover td{background-color:#0E2440!important}
hr{border-color:#0E2440!important;border-style:solid!important;opacity:0.5}
.stAlert,[data-testid="stNotification"]{background-color:#071220!important;border:1px solid #0E2440!important;color:#D8E4F0!important}
.stButton>button{background-color:#071A30!important;color:#D8E4F0!important;border:1px solid #163860!important;border-radius:3px!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.76rem!important;letter-spacing:0.06em!important;transition:all 0.15s ease;padding:0.38rem 1rem!important}
.stButton>button:hover{background-color:#3B8EF0!important;color:#FFFFFF!important;border-color:#3B8EF0!important}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:#030A14}
::-webkit-scrollbar-thumb{background:#0E2440;border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:#3B8EF0}
.sec-hdr{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#3B8EF0;letter-spacing:0.22em;text-transform:uppercase;margin-bottom:0.7rem;margin-top:0.2rem;border-bottom:1px solid #0E2440;padding-bottom:0.35rem}
.terminal-box{background:#030A14;border:1px solid #0E2440;border-radius:3px;padding:0.85rem 1.1rem;font-family:'IBM Plex Mono',monospace;font-size:0.8rem;color:#D8E4F0;margin-bottom:0.8rem}
.ticker-header{background:linear-gradient(135deg,#071A30,#0A1E38);border:1px solid #0E2440;border-top:2px solid #3B8EF0;border-radius:4px;padding:1.1rem 1.5rem;margin-bottom:1rem}
.mover-card{background:linear-gradient(135deg,#071A30,#0A1E38);border:1px solid #0E2440;border-radius:3px;padding:0.6rem 0.9rem;margin-bottom:0.35rem;display:flex;justify-content:space-between;align-items:center}
.stProgress>div>div{background-color:#3B8EF0!important}
div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"]{gap:0.4rem}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
DEFAULTS = dict(page="Global Overview", screener_selected=None,
                screener_results=None, bi_ticker="NVDA", bi_peers="AMD, INTC, AVGO",
                watchlist=["AAPL","NVDA","TSLA","ENI.MI","ASML.AS"])
for k,v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.1rem 0 0.9rem 0'>
      <div style='font-family:IBM Plex Mono,monospace;font-size:1.45rem;font-weight:700;color:#FFFFFF;letter-spacing:0.22em'>⚓ NAVY</div>
      <div style='font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#3B8EF0;letter-spacing:0.42em;margin-top:3px'>TERMINAL PRO</div>
      <div style='height:1px;background:linear-gradient(90deg,transparent,#3B8EF0,transparent);margin-top:0.85rem'></div>
    </div>""", unsafe_allow_html=True)

    MENU = [
        ("🌍","Global Overview"),("⭐","Watchlist"),("🧮","Analisi DCF"),
        ("📊","Multi-Compare"),("🧪","Portfolio Backtest"),
        ("🔍","Stock Screener"),("⌨️","Bloomberg Insights"),("📰","Market News"),
    ]
    for icon, label in MENU:
        active = st.session_state.page == label
        border = "border-left:2px solid #3B8EF0;" if active else ""
        bg     = "background:#163860!important;" if active else ""
        st.markdown(f"<style>#btn_{label.replace(' ','_')} button{{{bg}{border}}}</style>", unsafe_allow_html=True)
        with st.container():
            st.markdown(f"<span id='btn_{label.replace(' ','_')}'></span>", unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                st.session_state.page = label
                st.rerun()

    st.markdown("""
    <div style='margin-top:2rem;padding:0 0.5rem'>
      <div style='height:1px;background:linear-gradient(90deg,transparent,#0E2440,transparent);margin-bottom:0.7rem'></div>
      <div style='font-family:IBM Plex Mono,monospace;font-size:0.52rem;color:#1E3A5F;text-align:center;letter-spacing:0.14em;line-height:1.9'>
        LIVE DATA · YFINANCE<br>v3.0 · NAVY TERMINAL PRO
      </div>
    </div>""", unsafe_allow_html=True)

choice = st.session_state.page

# ─────────────────────────────────────────────
#  LAYOUT HELPERS
# ─────────────────────────────────────────────
def page_title(text, subtitle=""):
    st.markdown(f"<div class='page-title'>{text}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='page-subtitle'>{subtitle}</div>", unsafe_allow_html=True)

def sec(text):
    st.markdown(f"<div class='sec-hdr'>{text}</div>", unsafe_allow_html=True)

COLORS = ["#3B8EF0","#2ECC71","#F39C12","#E74C3C","#9B59B6","#1ABC9C",
          "#E67E22","#3498DB","#EC407A","#AB47BC","#00BCD4","#8BC34A"]

PLOTLY_BASE = dict(
    template="plotly_dark",
    paper_bgcolor='rgba(3,10,20,0)',
    plot_bgcolor='rgba(7,18,32,0.7)',
    font=dict(color="#D8E4F0", family="IBM Plex Mono, monospace", size=10),
    legend=dict(bgcolor='rgba(3,10,20,0.9)', bordercolor='#0E2440', borderwidth=1, font=dict(size=10)),
    xaxis=dict(gridcolor='#0A1A2E', showgrid=True, zeroline=False),
    yaxis=dict(gridcolor='#0A1A2E', showgrid=True, zeroline=False),
    margin=dict(l=48, r=20, t=42, b=38),
    hovermode="x unified", dragmode="zoom",
)

def iaxis():
    return dict(
        gridcolor='#0A1A2E', showgrid=True, zeroline=False,
        rangeslider=dict(visible=True, bgcolor="#030A14", thickness=0.04),
        rangeselector=dict(
            bgcolor="#071220", activecolor="#3B8EF0", bordercolor="#0E2440",
            font=dict(color="#FFFFFF", size=10),
            buttons=[
                dict(count=1,  label="1M", step="month",stepmode="backward"),
                dict(count=6,  label="6M", step="month",stepmode="backward"),
                dict(count=1,  label="1A", step="year", stepmode="backward"),
                dict(count=3,  label="3A", step="year", stepmode="backward"),
                dict(count=5,  label="5A", step="year", stepmode="backward"),
                dict(step="all",label="MAX"),
            ]
        )
    )

def pl(overrides=None):
    d = dict(**PLOTLY_BASE)
    if overrides:
        d.update(overrides)
    return d

# ─────────────────────────────────────────────
#  DATA HELPERS (cached)
# ─────────────────────────────────────────────
@st.cache_data(ttl=240, show_spinner=False)
def fetch_info(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info or len(info) < 4:
            return {}
        if not any(info.get(k) for k in ['regularMarketPrice','currentPrice','previousClose','longName','shortName']):
            return {}
        return info
    except:
        return {}

@st.cache_data(ttl=240, show_spinner=False)
def fetch_hist(ticker, period="2d"):
    try:
        return yf.Ticker(ticker).history(period=period)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=240, show_spinner=False)
def fetch_close(ticker, start=None, period=None):
    try:
        kw = dict(period=period) if period else dict(start=start)
        raw = yf.download(ticker, auto_adjust=True, progress=False, **kw)
        if raw.empty:
            return pd.Series(dtype=float, name=ticker)
        cl = raw["Close"]
        s  = cl.iloc[:,0] if isinstance(cl, pd.DataFrame) else cl.squeeze()
        return s.rename(ticker)
    except:
        return pd.Series(dtype=float, name=ticker)

@st.cache_data(ttl=120, show_spinner=False)
def fetch_price_change(ticker):
    """Returns (price, pct_change_today)"""
    try:
        d = yf.Ticker(ticker).history(period="2d")
        if len(d) >= 2:
            c, p = float(d["Close"].iloc[-1]), float(d["Close"].iloc[-2])
            return c, (c-p)/p*100
        return None, None
    except:
        return None, None

# ─────────────────────────────────────────────
#  FUNDAMENTAL HELPERS  (fixed P/E etc.)
# ─────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def get_pe_history(ticker, years=8):
    """Reliable historical P/E using price / trailing EPS snapshot (avoids dirty quarterly data)."""
    try:
        t = yf.Ticker(ticker)
        ph = t.history(period=f"{years}y")["Close"]
        if ph.empty: return pd.Series(dtype=float, name=ticker)
        ph.index = ph.index.tz_localize(None)

        # Try quarterly EPS first (most accurate)
        eps_series = None
        for attr in ["quarterly_income_stmt","quarterly_financials","income_stmt","financials"]:
            try:
                df = getattr(t, attr)
                if df is None or df.empty: continue
                for row in ["Basic EPS","Diluted EPS","EPS"]:
                    if row in df.index:
                        s = df.loc[row].dropna()
                        s.index = pd.to_datetime(s.index)
                        s = s.sort_index()
                        if len(s) >= 2:
                            eps_series = s
                            break
                if eps_series is not None: break
            except: continue

        if eps_series is not None and not eps_series.empty:
            # Build TTM: if quarterly, roll 4; else use annual directly
            if "quarterly" in attr:
                ttm = eps_series.rolling(4, min_periods=2).sum()
            else:
                ttm = eps_series
            ttm = ttm[ttm != 0]
            if ttm.empty:
                raise ValueError("empty ttm")
            # Align to daily price
            idx_union = ttm.index.union(ph.index)
            eps_daily = ttm.reindex(idx_union).ffill().reindex(ph.index)
            pe = (ph / eps_daily).replace([np.inf,-np.inf], np.nan)
            pe = pe[(pe > 0) & (pe < 500)].dropna()
            if len(pe) > 30:
                return pe.rename(ticker)

        # Fallback: snapshot trailingEps
        eps_snap = t.info.get("trailingEps")
        if eps_snap and eps_snap > 0:
            return (ph / eps_snap).rename(ticker)
        return pd.Series(dtype=float, name=ticker)
    except:
        return pd.Series(dtype=float, name=ticker)

@st.cache_data(ttl=600, show_spinner=False)
def get_ps_history(ticker, years=8):
    try:
        t = yf.Ticker(ticker)
        ph = t.history(period=f"{years}y")["Close"]
        if ph.empty: return pd.Series(dtype=float, name=ticker)
        ph.index = ph.index.tz_localize(None)
        shares = t.info.get("sharesOutstanding") or t.info.get("impliedSharesOutstanding")
        if not shares: return pd.Series(dtype=float, name=ticker)

        rev_series = None
        for attr in ["quarterly_income_stmt","quarterly_financials","income_stmt","financials"]:
            try:
                df = getattr(t, attr)
                if df is None or df.empty: continue
                for row in ["Total Revenue","Revenue","Net Revenue"]:
                    if row in df.index:
                        s = df.loc[row].dropna()
                        s.index = pd.to_datetime(s.index)
                        rev_series = s.sort_index(); break
                if rev_series is not None: break
            except: continue

        if rev_series is not None and not rev_series.empty:
            if "quarterly" in attr:
                ttm = rev_series.rolling(4, min_periods=2).sum()
            else:
                ttm = rev_series
            ttm = ttm[ttm > 0]
            idx_union = ttm.index.union(ph.index)
            rev_daily = ttm.reindex(idx_union).ffill().reindex(ph.index)
            ps = ((ph * shares) / rev_daily).replace([np.inf,-np.inf], np.nan)
            ps = ps[(ps > 0) & (ps < 200)].dropna()
            if len(ps) > 30: return ps.rename(ticker)

        rev_snap = t.info.get("totalRevenue")
        if rev_snap and rev_snap > 0:
            return ((ph * shares) / rev_snap).rename(ticker)
        return pd.Series(dtype=float, name=ticker)
    except:
        return pd.Series(dtype=float, name=ticker)

@st.cache_data(ttl=600, show_spinner=False)
def get_mktcap_history(ticker, years=8):
    try:
        t = yf.Ticker(ticker)
        ph = t.history(period=f"{years}y")["Close"]
        if ph.empty: return pd.Series(dtype=float, name=ticker)
        ph.index = ph.index.tz_localize(None)
        shares = t.info.get("sharesOutstanding") or t.info.get("impliedSharesOutstanding")
        if not shares: return pd.Series(dtype=float, name=ticker)
        return (ph * shares / 1e9).rename(ticker)
    except:
        return pd.Series(dtype=float, name=ticker)

@st.cache_data(ttl=600, show_spinner=False)
def get_quarterly_series(ticker, metric):
    try:
        t = yf.Ticker(ticker)
        if metric == "EPS":
            for attr in ["quarterly_income_stmt","quarterly_financials","income_stmt","financials"]:
                try:
                    df = getattr(t, attr)
                    if df is None or df.empty: continue
                    for row in ["Basic EPS","Diluted EPS","EPS"]:
                        if row in df.index:
                            s = df.loc[row].dropna()
                            s.index = pd.to_datetime(s.index)
                            return s.sort_index().rename(ticker)
                except: continue
        elif metric == "FCF":
            for attr in ["quarterly_cashflow","cashflow","quarterly_cash_flow","cash_flow"]:
                try:
                    df = getattr(t, attr)
                    if df is None or df.empty: continue
                    for row in ["Free Cash Flow","FreeCashFlow","Operating Cash Flow"]:
                        if row in df.index:
                            s = df.loc[row].dropna()
                            s.index = pd.to_datetime(s.index)
                            return (s.sort_index()/1e9).rename(ticker)
                except: continue
        else:
            row_map = {
                "Revenue":     ["Total Revenue","Revenue","Net Revenue"],
                "GrossProfit": ["Gross Profit","GrossProfit"],
                "NetIncome":   ["Net Income","NetIncome","Net Income Common Stockholders"],
                "EBITDA":      ["EBITDA","Normalized EBITDA","Operating Income","EBIT"],
            }
            candidates = row_map.get(metric, [metric])
            for attr in ["quarterly_income_stmt","quarterly_financials","income_stmt","financials"]:
                try:
                    df = getattr(t, attr)
                    if df is None or df.empty: continue
                    for row in candidates:
                        if row in df.index:
                            s = df.loc[row].dropna()
                            s.index = pd.to_datetime(s.index)
                            return (s.sort_index()/1e9).rename(ticker)
                except: continue
        return pd.Series(dtype=float, name=ticker)
    except:
        return pd.Series(dtype=float, name=ticker)

# ─────────────────────────────────────────────
#  UNIVERSE  (large curated list + sources)
# ─────────────────────────────────────────────
CURATED_TICKERS = [
    # ── US MEGA CAP ──────────────────────────────────────────────
    "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","JPM","V",
    "UNH","XOM","JNJ","PG","MA","HD","ABBV","MRK","CVX","PEP","KO","LIN",
    "TMO","DHR","NEE","AMD","INTC","QCOM","TXN","AMAT","LRCX","MU",
    "PANW","ADBE","CRM","NOW","ORCL","IBM","CSCO","DELL","HPQ","WDC",
    # ── US LARGE CAP TECH ────────────────────────────────────────
    "SNOW","PLTR","COIN","RBLX","UBER","LYFT","ABNB","BKNG","EXPE",
    "NFLX","DIS","CMCSA","T","VZ","CHTR","TMUS","SIRI",
    "ARM","SMCI","MRVL","KLAC","MPWR","ENPH","FSLR","SEDG","RUN",
    "FTNT","CRWD","ZS","OKTA","DDOG","MDB","GTLB","ESTC","HUBS",
    "TTD","TRADE","ROKU","SNAP","PINS","SPOT","DUOL",
    # ── US FINANCIALS ────────────────────────────────────────────
    "BAC","WFC","GS","MS","BLK","SCHW","C","USB","PNC","TFC",
    "AXP","COF","DFS","SYF","ALLY","SOFI","AFRM","UPST",
    "BX","KKR","APO","CG","ARES","TPG",
    "CB","PGR","TRV","AIG","MET","PRU","AFL","ALL","CINF","HIG",
    # ── US HEALTHCARE ────────────────────────────────────────────
    "MRNA","PFE","BMY","GILD","REGN","VRTX","BIIB","ILMN","IQV",
    "MCK","ABC","CAH","CVS","CI","HUM","ELV","MOH","CNC",
    "BSX","MDT","SYK","EW","ZBH","BAX","BDX","IDXX","HOLX",
    "LLY","NVO","AZN","GSK","NVS",
    # ── US CONSUMER ──────────────────────────────────────────────
    "COST","WMT","TGT","DG","DLTR","KR","SFM",
    "NKE","LULU","UAA","HBI","PVH","RL","TPR","CPRI","VFC",
    "MCD","SBUX","YUM","CMG","DPZ","QSR","WEN","JACK",
    "F","GM","RIVN","LCID","TM","VWAGY","BAMXF",
    "AMGN","DXCM","ISRG","ABT","A","ZBH",
    # ── US INDUSTRIALS ───────────────────────────────────────────
    "BA","CAT","DE","GE","HON","RTX","LMT","NOC","GD","L3TK",
    "MMM","EMR","ETN","PH","ROK","AME","FTV","XYL","NDSN",
    "UPS","FDX","CHRW","EXPD","XPO","SAIA","ODFL","JBHT",
    # ── US ENERGY ────────────────────────────────────────────────
    "EOG","PXD","COP","OXY","DVN","MRO","APA","FANG",
    "SLB","HAL","BKR","NOV","HP","OIS",
    "CEG","TLN","CCJ","NNE","OKLO","SMR","VST","NRG",
    # ── US REITS & UTILITIES ─────────────────────────────────────
    "AMT","PLD","EQIX","CCI","PSA","SPG","O","WELL","DLR",
    "AVB","EQR","INVH","AMH","IRT","NNN","WPC","STAG",
    "NEE","DUK","SO","AEP","EXC","XEL","ED","WEC","DTE","PPL",
    # ── US MATERIALS ─────────────────────────────────────────────
    "NEM","GOLD","AEM","KGC","FNV","WPM","PAAS",
    "FCX","SCCO","AA","CENX","MP","MTRN",
    "DD","DOW","LYB","CE","OLN","WLK","EMN",
    "NUE","STLD","CLF","X","CMC",
    # ── POPULAR / MEME / GROWTH ──────────────────────────────────
    "DKNG","PENN","MGM","WYNN","LVS","CZR",
    "GME","AMC","BBBY","BBWI","EXPR",
    "CVNA","VRM","KMX","AN","LAD",
    "SQ","PYPL","WU","MQ","FOUR","GPN","FIS","FISV",
    "PATH","AI","BBAI","SOUN","IREN","CORZ","RIOT","MARA","CLSK",
    "IONQ","RGTI","QBTS","IQM","ARQQ",
    # ── ETFs ─────────────────────────────────────────────────────
    "SPY","QQQ","IWM","VOO","VTI","VEA","VWO","VXUS",
    "GLD","SLV","IAU","GDX","GDXJ","USO","UNG",
    "TLT","IEF","SHY","AGG","BND","HYG","LQD","TIP","TIPS",
    "XLK","XLF","XLV","XLE","XLI","XLP","XLU","XLB","XLRE","XLC",
    "ARKK","ARKG","ARKW","ARKF","ARKQ",
    "SOXL","SOXS","TQQQ","UPRO","SPXU","UVXY","VXX",
    "IBIT","ETHA","GBTC","FBTC",
    # ── EUROPA ───────────────────────────────────────────────────
    "ASML.AS","PHIA.AS","HEIA.AS","INGA.AS","UNA.AS","WKL.AS","ADYEN.AS",
    "SAP.DE","BMW.DE","SIE.DE","BAYN.DE","MBG.DE","ALV.DE","BAS.DE",
    "VOW3.DE","DTE.DE","RWE.DE","HEN3.DE","DBK.DE","ADS.DE","AIR.DE",
    "MC.PA","TTE.PA","SAN.PA","BNP.PA","AXA.PA","OR.PA","AIR.PA",
    "SU.PA","DG.PA","EL.PA","KER.PA","RMS.PA","STMPA.PA",
    "NESN.SW","ROG.SW","NOVN.SW","ABB.SW","UBS.SW","ZURN.SW","CFR.SW",
    "HSBA.L","BP.L","SHEL.L","AZN.L","GSK.L","ULVR.L","RIO.L",
    "BARC.L","LLOY.L","NWG.L","BT-A.L","VOD.L","REL.L","EXPN.L",
    "INDITEX.MC","SAN.MC","BBVA.MC","REP.MC","TEF.MC","IBE.MC",
    "NOVO-B.CO","ORSTED.CO","DSV.CO","MAERSK-B.CO",
    # ── ITALIA ───────────────────────────────────────────────────
    "ENI.MI","ENEL.MI","UCG.MI","ISP.MI","STLAM.MI","RACE.MI","ATL.MI",
    "TIT.MI","MB.MI","BMED.MI","PRY.MI","REC.MI","PIRC.MI","BPER.MI",
    "G.MI","SPM.MI","TEN.MI","ENIA.MI","ERG.MI","IREN.MI","A2A.MI",
    "CNHI.MI","LDO.MI","FCA.MI","MONC.MI","SFER.MI","DIA.MI",
    # ── ASIA / LATAM / GLOBAL ────────────────────────────────────
    "TSM","BABA","JD","PDD","BIDU","NIO","LI","XPEV","BYD",
    "SONY","TM","HMC","MUFG","SMFG","MFG",
    "INFY","WIT","HDB","IBN","RELIANCE.NS",
    "VALE","PBR","ITUB","BBAS3.SA","PETR4.SA",
    "MELI","NU","GLOB","PAGS","STNE",
    "SHOP","RY","TD","BNS","BMO","CM","ENB","CNQ","SU",
    "BHP","RIO","GLNCY","SCCO","TECK","FM","AAL",
    "SAMSUNG.KS","LG.KS","KB","SHG",
    # ── CRYPTO / ALTERNATIVE ─────────────────────────────────────
    "BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD","ADA-USD",
    "DOGE-USD","AVAX-USD","DOT-USD","LINK-USD","MATIC-USD","LTC-USD",
]

CURATED_TICKERS = list(dict.fromkeys(CURATED_TICKERS))  # deduplicate preserving order

@st.cache_data(ttl=3600, show_spinner=False)
def get_universe():
    tickers = set(CURATED_TICKERS)
    # Try to augment from Wikipedia S&P500
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", timeout=4)
        syms = tables[0]['Symbol'].str.replace('.', '-', regex=False).tolist()
        tickers.update(syms)
    except: pass
    return sorted(list(tickers))

# ─────────────────────────────────────────────
#  SUPPLY CHAIN MAP
# ─────────────────────────────────────────────
SC_MAP = {
    "Technology":             {"sup":["TSM","ASML.AS","AMAT","LRCX","KLAC"],"cust":["AAPL","MSFT","META","AMZN","GOOGL"],"note":"Foundry asiatici + hyperscaler USA"},
    "Semiconductors":         {"sup":["ASML.AS","AMAT","LRCX","KLAC","MPWR"],"cust":["AAPL","NVDA","AMD","QCOM","AVGO"],"note":"ASML monopolista EUV · domanda AI strutturale"},
    "Communication Services": {"sup":["ERIC","NOK","AKAM","CDN globali"],"cust":["Advertiser B2B","PMI","Consumatori"],"note":"Revenue da pubblicità digitale e abbonamenti"},
    "Financial Services":     {"sup":["Bloomberg LP","LSEG","Broadridge","Fiserv"],"cust":["Banche retail","Investitori istituzionali","PMI"],"note":"Fintech erode margini retail"},
    "Healthcare":             {"sup":["TMO","DHR","Lonza","Wuxi Biologics"],"cust":["Ospedali","Assicurazioni","Governi"],"note":"Pipeline R&D lunga · CDMO critici"},
    "Energy":                 {"sup":["SLB","HAL","BKR","CAT"],"cust":["Utility","Raffinerie","Industria chimica"],"note":"Ciclico · legato al prezzo petrolio"},
    "Industrials":            {"sup":["MMM","HON","PH","ETN"],"cust":["Aerospazio","Auto","Costruzioni","Difesa"],"note":"B2B · sensibile al ciclo economico"},
    "Consumer Defensive":     {"sup":["ADM","BG","PKG","IFF"],"cust":["WMT","COST","Consumatori B2C"],"note":"Anticiclico · pricing power brand premium"},
    "Consumer Cyclical":      {"sup":["Produttori OEM Asia","Materie prime"],"cust":["Consumatori","E-commerce","Retail fisico"],"note":"Correlato al ciclo credito al consumo"},
    "Real Estate":            {"sup":["Costruttori","Property mgmt"],"cust":["Tenant uffici","Retail","Residenziale"],"note":"Sensibile ai tassi · REIT distribuisce 90% utili"},
    "Utilities":              {"sup":["GEV","Siemens Energy","NEE","Fuel"],"cust":["Residenziale","Industria","Data center AI"],"note":"Regolato · crescita AI è catalizzatore strutturale"},
    "Basic Materials":        {"sup":["Minatori RM","Produttori chimici"],"cust":["Manifatturiero","Auto","Farmaceutico"],"note":"Altamente ciclico · domanda cinese"},
}

SECTOR_PEERS = {
    "Technology":             "AAPL, MSFT, GOOGL, META",
    "Semiconductors":         "NVDA, AMD, INTC, AVGO, TSM",
    "Consumer Cyclical":      "AMZN, TSLA, NKE, MCD, BKNG",
    "Consumer Defensive":     "PG, KO, PEP, WMT, COST",
    "Healthcare":             "JNJ, PFE, ABBV, MRK, LLY",
    "Financials":             "JPM, BAC, GS, MS, V",
    "Energy":                 "XOM, CVX, TTE.PA, BP.L, SLB",
    "Industrials":            "GE, CAT, HON, BA, MMM",
    "Communication Services": "META, GOOGL, NFLX, DIS, CMCSA",
    "Utilities":              "NEE, CEG, DUK, SO, AEP",
    "Real Estate":            "PLD, AMT, EQIX, SPG, O",
    "Basic Materials":        "LIN, APD, NEM, FCX, DD",
}

# ─────────────────────────────────────────────
#  BLOOMBERG INSIGHTS COMPONENT
# ─────────────────────────────────────────────
def show_bloomberg(target, peers_default="SPY, QQQ, IWM"):
    inf = fetch_info(target)
    if not inf:
        st.error(f"❌ Ticker **{target}** non trovato. Esempi: `AAPL` `NVDA` `ENI.MI` `MC.PA` `ASML.AS`")
        return

    name    = inf.get('longName') or inf.get('shortName') or target
    price   = inf.get('currentPrice') or inf.get('regularMarketPrice') or inf.get('previousClose')
    prev    = inf.get('previousClose') or price
    chg_pct = (price - prev) / prev * 100 if price and prev and prev != 0 else None
    sector  = inf.get('sector','N/A')

    # ── Header ──
    chg_col = "#2ECC71" if (chg_pct or 0) >= 0 else "#E74C3C"
    chg_str = f"<span style='color:{chg_col}'>{chg_pct:+.2f}% oggi</span>" if chg_pct is not None else ""
    st.markdown(f"""
    <div class='ticker-header'>
      <div style='display:flex;justify-content:space-between;align-items:flex-start'>
        <div>
          <div style='font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#3B8EF0;letter-spacing:0.28em;margin-bottom:5px'>EQUITY · {inf.get('exchange','N/A')} · {inf.get('currency','USD')}</div>
          <div style='font-size:1.55rem;font-weight:700;color:#FFFFFF;line-height:1.2'>{name}</div>
          <div style='font-family:IBM Plex Mono,monospace;font-size:0.8rem;color:#7A9DBE;margin-top:4px'>{target} &nbsp;·&nbsp; {sector} &nbsp;·&nbsp; {inf.get('country','N/A')}</div>
        </div>
        <div style='text-align:right'>
          <div style='font-family:IBM Plex Mono,monospace;font-size:1.9rem;font-weight:700;color:#FFFFFF'>{f"{price:,.2f}" if price else "N/A"}</div>
          <div style='font-size:0.85rem;margin-top:2px'>{chg_str}</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── KPIs ──
    k = st.columns(7)
    vals = [
        ("P/E Fwd",    f"{inf['forwardPE']:.1f}"   if inf.get('forwardPE')        else "N/A"),
        ("P/E Ttm",    f"{inf['trailingPE']:.1f}"  if inf.get('trailingPE')       else "N/A"),
        ("EPS Fwd",    f"{inf['forwardEps']:.2f}"  if inf.get('forwardEps')       else "N/A"),
        ("P/B",        f"{inf['priceToBook']:.2f}" if inf.get('priceToBook')      else "N/A"),
        ("Beta",       f"{inf['beta']:.2f}"        if inf.get('beta')             else "N/A"),
        ("Market Cap", f"${inf['marketCap']/1e9:.1f}B" if inf.get('marketCap')   else "N/A"),
        ("Div Yield",  f"{(inf.get('dividendYield') or 0)*100:.2f}%"),
    ]
    for i,(label,val) in enumerate(vals):
        k[i].metric(label, val)

    st.markdown("---")

    # ── Description + News ──
    c_desc, c_news = st.columns([2,1])
    with c_desc:
        sec("BUSINESS SUMMARY")
        st.write(inf.get('longBusinessSummary') or "Descrizione non disponibile.")
        sec("FINANCIALS")
        f1,f2,f3,f4 = st.columns(4)
        f1.metric("Revenue",   f"${inf.get('totalRevenue',0)/1e9:.1f}B" if inf.get('totalRevenue') else "N/A")
        f2.metric("EBITDA",    f"${inf.get('ebitda',0)/1e9:.1f}B"       if inf.get('ebitda')       else "N/A")
        f3.metric("FCF",       f"${inf.get('freeCashflow',0)/1e9:.1f}B" if inf.get('freeCashflow') else "N/A")
        f4.metric("EV/EBITDA", f"{inf['enterpriseToEbitda']:.1f}"       if inf.get('enterpriseToEbitda') else "N/A")
    with c_news:
        sec("LATEST NEWS")
        yahoo_url = f"https://finance.yahoo.com/quote/{target}/news/"
        st.markdown(f"""
        <div class='terminal-box'>
          <div style='font-size:0.62rem;color:#3B8EF0;letter-spacing:0.18em;margin-bottom:8px'>FONTE LIVE</div>
          <a href='{yahoo_url}' target='_blank'
             style='background:#071220;color:#3B8EF0;border:1px solid #163860;border-radius:3px;
                    padding:5px 11px;font-family:IBM Plex Mono,monospace;font-size:0.73rem;
                    text-decoration:none;display:inline-block'>📰 Yahoo Finance →</a>
        </div>""", unsafe_allow_html=True)
        try:
            news = yf.Ticker(target).news or []
            for n in news[:5]:
                title = n.get('title','')
                link  = n.get('link', yahoo_url)
                if title:
                    st.markdown(f"<div style='border-left:2px solid #0E2440;padding-left:7px;margin-bottom:7px;"
                                f"font-size:0.78rem;'><a href='{link}' target='_blank' "
                                f"style='color:#7A9DBE;text-decoration:none'>{title[:80]}…</a></div>",
                                unsafe_allow_html=True)
        except: pass

    st.markdown("---")
    sec("PEER ANALYSIS")

    # KEY FIX: unique key based on ticker to reset peers when ticker changes
    peers_key = f"peers_{target}"
    if peers_key not in st.session_state:
        st.session_state[peers_key] = peers_default

    peers_in = st.text_input("Competitors (virgola)", value=st.session_state[peers_key], key=f"pi_{target}")
    st.session_state[peers_key] = peers_in

    p_list = [target] + [x.strip().upper() for x in peers_in.split(",") if x.strip()]
    rows = []
    for p in p_list:
        try:
            pi = fetch_info(p)
            pr = pi.get('currentPrice') or pi.get('regularMarketPrice') or pi.get('previousClose') or 0
            rows.append({
                "Ticker":    p,
                "Price":     f"{pr:,.2f}"                                  if pr else "N/A",
                "P/E Fwd":   f"{pi.get('forwardPE'):.1f}"                  if pi.get('forwardPE') else "N/A",
                "P/E Ttm":   f"{pi.get('trailingPE'):.1f}"                 if pi.get('trailingPE') else "N/A",
                "EPS Fwd":   f"{pi.get('forwardEps'):.2f}"                 if pi.get('forwardEps') else "N/A",
                "P/B":       f"{pi.get('priceToBook'):.2f}"                if pi.get('priceToBook') else "N/A",
                "P/S":       f"{pi.get('priceToSalesTrailing12Months'):.1f}" if pi.get('priceToSalesTrailing12Months') else "N/A",
                "EV/EBITDA": f"{pi.get('enterpriseToEbitda'):.1f}"         if pi.get('enterpriseToEbitda') else "N/A",
                "Beta":      f"{pi.get('beta'):.2f}"                       if pi.get('beta') else "N/A",
                "Cap $B":    f"{pi.get('marketCap',0)/1e9:.1f}"            if pi.get('marketCap') else "N/A",
                "Div %":     f"{(pi.get('dividendYield') or 0)*100:.2f}%",
                "ROE %":     f"{pi.get('returnOnEquity',0)*100:.1f}"       if pi.get('returnOnEquity') else "N/A",
                "Op.Mgn %":  f"{pi.get('operatingMargins',0)*100:.1f}"     if pi.get('operatingMargins') else "N/A",
            })
        except:
            rows.append({"Ticker":p,"Price":"ERR","P/E Fwd":"—","P/E Ttm":"—","EPS Fwd":"—",
                         "P/B":"—","P/S":"—","EV/EBITDA":"—","Beta":"—","Cap $B":"—",
                         "Div %":"—","ROE %":"—","Op.Mgn %":"—"})
    if rows:
        st.dataframe(pd.DataFrame(rows).set_index("Ticker"), use_container_width=True)

    st.markdown("---")
    sec("PERFORMANCE RELATIVA 12M")
    try:
        frames = {}
        for tkr in p_list:
            s = fetch_close(tkr, period="1y")
            if not s.empty: frames[tkr] = s
        if frames:
            peer_data = pd.DataFrame(frames).dropna(how='all').ffill()
            peer_norm = ((peer_data / peer_data.iloc[0]) - 1) * 100
            fig = go.Figure()
            for idx, col in enumerate(peer_norm.columns):
                fig.add_trace(go.Scatter(
                    x=peer_norm.index, y=peer_norm[col], name=col,
                    line=dict(width=2.8 if col==target else 1.5, color=COLORS[idx%len(COLORS)]),
                    hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>"+col+"</extra>"))
            fig.add_hline(y=0, line_dash="dot", line_color="#163860", line_width=1)
            fig.update_layout(**pl({"xaxis":iaxis(),"yaxis_title":"Rendimento % (normalizzato)","height":380,
                                    "title":f"Performance relativa 12M — {target} vs peers"}))
            st.plotly_chart(fig, use_container_width=True)
    except: st.info("Grafico peers non disponibile.")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        sec("SECTOR & GEOGRAPHY")
        s1,s2 = st.columns(2)
        s1.metric("Settore",   sector)
        s2.metric("Industria", inf.get('industry','N/A'))
        s3,s4 = st.columns(2)
        s3.metric("Paese",    inf.get('country','N/A'))
        s4.metric("Exchange", inf.get('exchange','N/A'))
    with c2:
        sec("SUPPLY CHAIN ECOSYSTEM")
        sc = SC_MAP.get(sector)
        if sc:
            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown("**🔼 Fornitori**")
                for s in sc["sup"]: st.markdown(f"<div style='font-size:0.8rem;color:#7A9DBE'>· {s}</div>", unsafe_allow_html=True)
            with cc2:
                st.markdown("**🔽 Clienti**")
                for c in sc["cust"]: st.markdown(f"<div style='font-size:0.8rem;color:#7A9DBE'>· {c}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.78rem;color:#3B8EF0;margin-top:6px'>💡 {sc['note']}</div>", unsafe_allow_html=True)
        else:
            st.info("Supply chain map non disponibile per questo settore.")

# ═══════════════════════════════════════════════════════════
#  PAGE 1 — GLOBAL OVERVIEW
# ═══════════════════════════════════════════════════════════
if choice == "Global Overview":
    page_title("🌍  GLOBAL MARKET OVERVIEW", "Snapshot real-time · Indici · Titoli · Top Movers")

    sec("INDICI GLOBALI")
    INDICES = {
        "S&P 500":"^GSPC","Nasdaq 100":"^IXIC","Dow Jones":"^DJI","Nikkei 225":"^N225",
        "FTSE MIB":"FTSEMIB.MI","DAX 40":"^GDAXI","CAC 40":"^FCHI","Hang Seng":"^HSI",
        "Euro Stoxx 50":"^STOXX50E","Russell 2000":"^RUT","VIX":"^VIX","MSCI EM":"EEM",
    }
    cols = st.columns(4)
    for i,(name,tkr) in enumerate(INDICES.items()):
        p,c = fetch_price_change(tkr)
        cols[i%4].metric(name, f"{p:,.2f}" if p else "N/A", f"{c:+.2f}%" if c else "—")

    st.markdown("---")
    sec("TITOLI DI RIFERIMENTO")
    STOCKS = {
        "Apple":"AAPL","Microsoft":"MSFT","Nvidia":"NVDA","Alphabet":"GOOGL",
        "Tesla":"TSLA","Amazon":"AMZN","Meta":"META","ASML":"ASML.AS",
        "SAP":"SAP.DE","ENI":"ENI.MI","LVMH":"MC.PA","Ferrari":"RACE.MI",
    }
    cols2 = st.columns(4)
    for i,(name,tkr) in enumerate(STOCKS.items()):
        p,c = fetch_price_change(tkr)
        cols2[i%4].metric(f"{name} ({tkr})", f"{p:,.2f}" if p else "N/A", f"{c:+.2f}%" if c else "—")

    st.markdown("---")
    sec("TOP MOVERS DEL GIORNO")
    WATCH = [
        "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","JPM","V",
        "AMD","INTC","PANW","ADBE","CRM","SNOW","PLTR","COIN","NFLX","DIS",
        "BAC","WFC","GS","COST","WMT","NKE","MCD","BA","CAT","GE",
        "F","GM","SQ","PYPL","SMCI","ARM","ENPH","MRNA","PFE","GILD",
        "ENI.MI","ENEL.MI","RACE.MI","MC.PA","TTE.PA","SAP.DE","ASML.AS",
    ]
    results_mv = []
    prog_mv = st.progress(0)
    for i,tkr in enumerate(WATCH):
        prog_mv.progress((i+1)/len(WATCH))
        p,c = fetch_price_change(tkr)
        if p and c is not None:
            results_mv.append({"ticker":tkr,"price":p,"pct":c})
    prog_mv.empty()
    results_mv.sort(key=lambda x: x["pct"], reverse=True)
    gainers = results_mv[:5]
    losers  = sorted(results_mv, key=lambda x: x["pct"])[:5]

    cg, cl = st.columns(2)
    for col_data, color, label in [(gainers,"#2ECC71","🟢 TOP GAINERS"),(losers,"#E74C3C","🔴 TOP LOSERS")]:
        with (cg if color=="#2ECC71" else cl):
            st.markdown(f"<div class='sec-hdr' style='color:{color}'>{label}</div>", unsafe_allow_html=True)
            for m in col_data:
                st.markdown(f"""
                <div class='mover-card' style='border-left:3px solid {color}'>
                  <div>
                    <div style='font-family:IBM Plex Mono,monospace;font-size:0.9rem;color:#FFFFFF;font-weight:600'>{m['ticker']}</div>
                    <div style='font-size:0.7rem;color:#7A9DBE;margin-top:2px'>${m['price']:,.2f}</div>
                  </div>
                  <div style='font-family:IBM Plex Mono,monospace;font-size:1.05rem;color:{color};font-weight:700'>{m['pct']:+.2f}%</div>
                </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  PAGE 2 — WATCHLIST
# ═══════════════════════════════════════════════════════════
elif choice == "Watchlist":
    page_title("⭐  WATCHLIST PERSONALE", "Monitora i tuoi ticker preferiti in tempo reale")

    wl_input = st.text_input("Aggiungi ticker (virgola)", "",
                              placeholder="Es: NVDA, ASML.AS, ENI.MI ...")
    if wl_input.strip():
        new_tickers = [x.strip().upper() for x in wl_input.split(",") if x.strip()]
        st.session_state.watchlist = list(dict.fromkeys(st.session_state.watchlist + new_tickers))

    if st.session_state.watchlist:
        remove_sel = st.multiselect("Rimuovi dalla watchlist", st.session_state.watchlist)
        if remove_sel:
            st.session_state.watchlist = [t for t in st.session_state.watchlist if t not in remove_sel]

    st.markdown("---")
    wl = st.session_state.watchlist
    if not wl:
        st.info("Watchlist vuota. Aggiungi dei ticker sopra.")
    else:
        sec("PREZZI IN TEMPO REALE")
        rows_wl = []
        prog_wl = st.progress(0)
        for i,tkr in enumerate(wl):
            prog_wl.progress((i+1)/len(wl))
            inf = fetch_info(tkr)
            p,c = fetch_price_change(tkr)
            if inf:
                rows_wl.append({
                    "Ticker": tkr,
                    "Nome":   (inf.get('shortName') or tkr)[:28],
                    "Prezzo": f"{p:,.2f}" if p else "N/A",
                    "Var %":  f"{c:+.2f}%" if c else "—",
                    "52W Lo": f"{inf.get('fiftyTwoWeekLow','—')}",
                    "52W Hi": f"{inf.get('fiftyTwoWeekHigh','—')}",
                    "P/E":    f"{inf['forwardPE']:.1f}" if inf.get('forwardPE') else "N/A",
                    "Cap $B": f"{inf.get('marketCap',0)/1e9:.1f}" if inf.get('marketCap') else "N/A",
                    "Beta":   f"{inf['beta']:.2f}" if inf.get('beta') else "N/A",
                })
        prog_wl.empty()
        if rows_wl:
            st.dataframe(pd.DataFrame(rows_wl).set_index("Ticker"), use_container_width=True)

        st.markdown("---")
        sec("PERFORMANCE STORICA COMPARATA")
        horiz = st.selectbox("Orizzonte", ["1mo","3mo","6mo","1y","3y","5y"], index=3)
        frames_wl = {}
        for tkr in wl:
            s = fetch_close(tkr, period=horiz)
            if not s.empty: frames_wl[tkr] = s
        if frames_wl:
            data_wl = pd.DataFrame(frames_wl).dropna(how='all').ffill()
            norm_wl = ((data_wl / data_wl.iloc[0]) - 1) * 100
            fig_wl  = go.Figure()
            for idx,col in enumerate(norm_wl.columns):
                fig_wl.add_trace(go.Scatter(x=norm_wl.index, y=norm_wl[col], name=col,
                    line=dict(width=2, color=COLORS[idx%len(COLORS)]),
                    hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>"+col+"</extra>"))
            fig_wl.add_hline(y=0, line_dash="dot", line_color="#163860")
            fig_wl.update_layout(**pl({"xaxis":iaxis(),"yaxis_title":"Rendimento %",
                                       "height":420,"title":"Performance comparata watchlist"}))
            st.plotly_chart(fig_wl, use_container_width=True)

# ═══════════════════════════════════════════════════════════
#  PAGE 3 — DCF
# ═══════════════════════════════════════════════════════════
elif choice == "Analisi DCF":
    page_title("🧮  DISCOUNTED CASH FLOW", "Fair value da WACC · Terminal Value · Sensitivity Analysis")

    c1, c2 = st.columns(2)
    with c1:
        sec("INPUT")
        fcf  = st.number_input("Free Cash Flow ($)",value=1_000_000_000,step=50_000_000,format="%d")
        g_r  = st.slider("Crescita FCF (%)",1,50,10)
        wacc = st.slider("WACC (%)",5,20,9)
        tg   = st.slider("Terminal Growth (%)",0,5,2)
        yrs  = st.slider("Anni proiezione",3,15,10)
        shr  = st.number_input("Azioni in circolazione",value=1_000_000_000,step=10_000_000,format="%d")
        nd   = st.number_input("Net Debt ($, positivo=debito)",value=0,step=100_000_000,format="%d")

    g,w,t = g_r/100, wacc/100, tg/100
    cfs,pvs = [],[]
    for yr in range(1,yrs+1):
        cf = fcf*((1+g)**yr); pv = cf/((1+w)**yr)
        cfs.append(cf); pvs.append(pv)
    tv   = (cfs[-1]*(1+t))/(w-t) if w>t else 0
    pvtv = tv/((1+w)**yrs)
    ev   = sum(pvs)+pvtv
    eq   = ev - nd
    fvs  = eq/shr if shr > 0 else 0

    with c2:
        sec("RISULTATI")
        r1,r2 = st.columns(2)
        r1.metric("Enterprise Value",   f"${ev/1e9:,.2f}B")
        r2.metric("Equity Value",       f"${eq/1e9:,.2f}B")
        r3,r4 = st.columns(2)
        r3.metric("Fair Value/Azione",  f"${fvs:,.2f}")
        r4.metric("% Terminal Value",   f"{pvtv/ev*100:.1f}%" if ev else "N/A")
        r5,r6 = st.columns(2)
        r5.metric("PV FCF Operativi",   f"${sum(pvs)/1e9:,.2f}B")
        r6.metric("Terminal Value PV",  f"${pvtv/1e9:,.2f}B")

    st.markdown("---")
    fig_dcf = go.Figure()
    fig_dcf.add_trace(go.Bar(x=[f"Y{i+1}" for i in range(yrs)], y=[v/1e6 for v in cfs],
                             name="FCF Proiettato", marker_color="#3B8EF0", opacity=0.85))
    fig_dcf.add_trace(go.Bar(x=[f"Y{i+1}" for i in range(yrs)], y=[v/1e6 for v in pvs],
                             name="PV FCF", marker_color="#2ECC71", opacity=0.85))
    fig_dcf.update_layout(**pl({"yaxis_title":"$ Milioni","barmode":"group","height":340,
                                "title":"Cash Flow Proiettato vs Present Value"}))
    st.plotly_chart(fig_dcf, use_container_width=True)

    st.markdown("---")
    sec("SENSITIVITY — FAIR VALUE vs WACC × GROWTH")
    wacc_r  = [w-0.02,w-0.01,w,w+0.01,w+0.02]
    grow_r  = [g-0.02,g-0.01,g,g+0.01,g+0.02]
    tbl = {}
    for gr in grow_r:
        row = {}
        for wc in wacc_r:
            if wc <= t: row[f"W{wc*100:.0f}%"] = "N/A"; continue
            c_s = [fcf*((1+gr)**yr)/((1+wc)**yr) for yr in range(1,yrs+1)]
            tv_s = (fcf*((1+gr)**yrs)*(1+t))/(wc-t)/((1+wc)**yrs)
            ev_s = sum(c_s)+tv_s
            row[f"W{wc*100:.0f}%"] = f"${(ev_s-nd)/shr:,.0f}" if shr else "N/A"
        tbl[f"G{gr*100:.0f}%"] = row
    st.dataframe(pd.DataFrame(tbl).T, use_container_width=True)

# ═══════════════════════════════════════════════════════════
#  PAGE 4 — MULTI-COMPARE
# ═══════════════════════════════════════════════════════════
elif choice == "Multi-Compare":
    page_title("📊  MULTI-ASSET COMPARISON", "Rendimenti · Fondamentali · Correlazioni · Inflazione")

    mode = st.radio("Modalità:", ["📈 Rendimento %","📉 Inflazione","🏢 Fondamentali"], horizontal=True)
    st.markdown("---")

    # ── MODE 1: Returns ──────────────────────────────────────
    if mode == "📈 Rendimento %":
        c1,c2,c3 = st.columns([3,1,1])
        with c1: tk_in   = st.text_input("Ticker (virgola)","AAPL, MSFT, TSLA, NVDA, SPY")
        with c2: horizon = st.selectbox("Orizzonte",["Mesi","Anni"])
        with c3: val     = st.slider("Durata",1,24 if horizon=="Mesi" else 20,12)
        tk_list   = [x.strip().upper() for x in tk_in.split(",") if x.strip()]
        start_str = (datetime.now()-timedelta(days=val*30 if horizon=="Mesi" else val*365)).strftime("%Y-%m-%d")

        if tk_list:
            frames = {t: s for t in tk_list for s in [fetch_close(t, start=start_str)] if not s.empty}
            if frames:
                data  = pd.DataFrame(frames).dropna(how="all").ffill()
                rets  = ((data/data.iloc[0])-1)*100
                fig_r = go.Figure()
                for idx,col in enumerate(rets.columns):
                    fig_r.add_trace(go.Scatter(x=rets.index, y=rets[col],
                        name=f"{col} ({rets[col].iloc[-1]:+.1f}%)",
                        line=dict(width=2,color=COLORS[idx%len(COLORS)]),
                        hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>"+col+"</extra>"))
                fig_r.add_hline(y=0,line_dash="dot",line_color="#163860")
                fig_r.update_layout(**pl({"xaxis":iaxis(),"yaxis_title":"Rendimento %",
                                          "height":460,"title":"Rendimento Normalizzato"}))
                st.plotly_chart(fig_r, use_container_width=True)

                sec("STATISTICHE")
                dr = data.pct_change().dropna()
                stats = []
                for col in rets.columns:
                    ann_v = dr[col].std()*np.sqrt(252)*100
                    ann_r = rets[col].iloc[-1]
                    dd    = ((data[col]/data[col].cummax())-1).min()*100
                    stats.append({"Ticker":col,"Rend. %":f"{ann_r:+.2f}%",
                                  "Vol. Annua":f"{ann_v:.1f}%",
                                  "Sharpe":f"{(ann_r/ann_v):.2f}" if ann_v else "N/A",
                                  "Max DD":f"{dd:.1f}%",
                                  "Max %":f"{rets[col].max():+.1f}%",
                                  "Min %":f"{rets[col].min():+.1f}%"})
                st.dataframe(pd.DataFrame(stats).set_index("Ticker"), use_container_width=True)

                if len(frames) >= 2:
                    sec("CORRELAZIONE")
                    corr = dr.corr()
                    fig_c = go.Figure(go.Heatmap(z=corr.values,x=corr.columns.tolist(),y=corr.index.tolist(),
                        colorscale=[[0,"#E74C3C"],[0.5,"#071220"],[1,"#2ECC71"]],zmid=0,zmin=-1,zmax=1,
                        text=corr.round(2).values,texttemplate="%{text}"))
                    fig_c.update_layout(**pl({"height":340,"title":"Matrice di Correlazione"}))
                    st.plotly_chart(fig_c, use_container_width=True)

    # ── MODE 2: Inflation ────────────────────────────────────
    elif mode == "📉 Inflazione":
        st.info("Proxy inflazione via ETF TIPS: **TIP** · **RINF** · **ITIP** · **STIP**")
        c1,c2,c3 = st.columns([3,1,1])
        with c1: infl_in = st.text_input("TIPS Ticker","TIP, RINF, STIP")
        with c2: ih = st.selectbox("Orizzonte",["Mesi","Anni"],key="ih")
        with c3: iv = st.slider("Durata",1,20,5,key="iv")
        comp_in = st.text_input("Confronta con","SPY, GLD, BND")
        all_t   = list(dict.fromkeys(
            [x.strip().upper() for x in infl_in.split(",") if x.strip()] +
            [x.strip().upper() for x in comp_in.split(",") if x.strip()]
        ))
        infl_lst = [x.strip().upper() for x in infl_in.split(",") if x.strip()]
        start_i  = (datetime.now()-timedelta(days=iv*30 if ih=="Mesi" else iv*365)).strftime("%Y-%m-%d")
        frames_i = {t: s for t in all_t for s in [fetch_close(t, start=start_i)] if not s.empty}
        if frames_i:
            d = pd.DataFrame(frames_i).dropna(how="all").ffill()
            r = ((d/d.iloc[0])-1)*100
            preset = {"TIP":"#F39C12","RINF":"#E74C3C","STIP":"#F1C40F","ITIP":"#E67E22",
                      "SPY":"#3B8EF0","GLD":"#2ECC71","BND":"#9B59B6"}
            fig_i = go.Figure()
            for idx,col in enumerate(r.columns):
                fig_i.add_trace(go.Scatter(x=r.index,y=r[col],name=col,
                    line=dict(width=2.5 if col in infl_lst else 1.5,
                              dash="solid" if col in infl_lst else "dot",
                              color=preset.get(col,COLORS[idx%len(COLORS)])),
                    hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>"+col+"</extra>"))
            fig_i.add_hline(y=0,line_dash="dot",line_color="#163860")
            fig_i.update_layout(**pl({"xaxis":iaxis(),"yaxis_title":"Rendimento % base 100","height":460,
                                      "title":"Proxy Inflazione vs Asset"}))
            st.plotly_chart(fig_i, use_container_width=True)

    # ── MODE 3: Fundamentals ─────────────────────────────────
    else:
        c1,c2 = st.columns([3,2])
        with c1: fund_in  = st.text_input("Ticker","AAPL, MSFT, GOOGL")
        with c2: fund_m   = st.selectbox("Metrica",[
            "P/E Storico","P/S Storico","Market Cap (B$)",
            "EPS","Revenue (B$)","Gross Profit (B$)","Net Income (B$)",
            "EBITDA (B$)","FCF (B$)",
            "D/E snapshot","Op.Margin % snapshot","ROE % snapshot",
        ])
        fund_list   = [x.strip().upper() for x in fund_in.split(",") if x.strip()]
        yrs_back    = st.slider("Anni di storia",1,12,6,key="fy")

        if not fund_list:
            st.info("Inserisci almeno un ticker.")
        else:
            fig_f = go.Figure()
            has   = False
            cutoff = datetime.now()-timedelta(days=365*yrs_back)

            for idx,tkr in enumerate(fund_list):
                col = COLORS[idx%len(COLORS)]

                if fund_m == "P/E Storico":
                    s = get_pe_history(tkr, years=yrs_back)
                    if not s.empty:
                        sm = s.rolling(20,min_periods=1).mean()
                        fig_f.add_trace(go.Scatter(x=sm.index,y=sm,name=tkr,
                            line=dict(width=2,color=col),
                            hovertemplate="%{x|%d %b %Y}<br>P/E: %{y:.1f}<extra>"+tkr+"</extra>"))
                        has = True
                    else:
                        st.warning(f"P/E storico non disponibile per {tkr}")

                elif fund_m == "P/S Storico":
                    s = get_ps_history(tkr, years=yrs_back)
                    if not s.empty:
                        sm = s.rolling(20,min_periods=1).mean()
                        fig_f.add_trace(go.Scatter(x=sm.index,y=sm,name=tkr,
                            line=dict(width=2,color=col),
                            hovertemplate="%{x|%d %b %Y}<br>P/S: %{y:.2f}<extra>"+tkr+"</extra>"))
                        has = True
                    else:
                        st.warning(f"P/S storico non disponibile per {tkr}")

                elif fund_m == "Market Cap (B$)":
                    s = get_mktcap_history(tkr, years=yrs_back)
                    if not s.empty:
                        fig_f.add_trace(go.Scatter(x=s.index,y=s,name=tkr,
                            line=dict(width=2,color=col),
                            hovertemplate="%{x|%d %b %Y}<br>$%{y:.0f}B<extra>"+tkr+"</extra>"))
                        has = True

                elif fund_m in ("D/E snapshot","Op.Margin % snapshot","ROE % snapshot"):
                    # snapshot bar — handled below
                    pass

                else:
                    metric_key_map = {
                        "EPS":              "EPS",
                        "Revenue (B$)":     "Revenue",
                        "Gross Profit (B$)":"GrossProfit",
                        "Net Income (B$)":  "NetIncome",
                        "EBITDA (B$)":      "EBITDA",
                        "FCF (B$)":         "FCF",
                    }
                    mk = metric_key_map.get(fund_m, fund_m)
                    s  = get_quarterly_series(tkr, mk)
                    if not s.empty:
                        s2 = s[s.index >= cutoff]
                        if not s2.empty:
                            fig_f.add_trace(go.Bar(x=s2.index.astype(str),y=s2.values,name=tkr,
                                marker_color=col,
                                hovertemplate="%{x}<br>"+fund_m+": %{y:.2f}<extra>"+tkr+"</extra>"))
                            has = True

            # Snapshot metrics
            if fund_m in ("D/E snapshot","Op.Margin % snapshot","ROE % snapshot"):
                snap_map = {"D/E snapshot":("debtToEquity",100,"D/E"),
                            "Op.Margin % snapshot":("operatingMargins",0.01,"Op.Margin %"),
                            "ROE % snapshot":("returnOnEquity",0.01,"ROE %")}
                info_k,div_k,label_k = snap_map[fund_m]
                bar_d = {}
                for tkr in fund_list:
                    v = fetch_info(tkr).get(info_k)
                    if v is not None:
                        try: bar_d[tkr] = float(v)/div_k
                        except: pass
                if bar_d:
                    fig_f.add_trace(go.Bar(x=list(bar_d.keys()),y=list(bar_d.values()),
                        marker_color=COLORS[:len(bar_d)],
                        text=[f"{v:.2f}" for v in bar_d.values()],
                        textposition="outside",textfont=dict(color="#FFFFFF")))
                    has = True
                    fig_f.update_layout(**pl({"title":f"{label_k} — Valore snapshot","yaxis_title":label_k,
                                              "height":380,"showlegend":False}))
                    st.plotly_chart(fig_f, use_container_width=True)

            elif has:
                title_map = {
                    "P/E Storico":"P/E Ratio Storico","P/S Storico":"P/S Ratio Storico",
                    "Market Cap (B$)":"Market Cap Storico (B$)",
                }
                bm = "group" if fund_m not in ("P/E Storico","P/S Storico","Market Cap (B$)") else None
                extra = {"barmode":bm} if bm else {}
                fig_f.update_layout(**pl({"xaxis":iaxis(),"yaxis_title":fund_m,"height":460,
                                          "title":title_map.get(fund_m,fund_m),**extra}))
                st.plotly_chart(fig_f, use_container_width=True)
            else:
                st.warning("Nessun dato disponibile. Prova ticker diversi o una metrica snapshot.")

            # Full snapshot table (always shown)
            st.markdown("---")
            sec("TABELLA FONDAMENTALI SNAPSHOT")
            snap_rows = []
            for tkr in fund_list:
                inf = fetch_info(tkr)
                if not inf: continue
                snap_rows.append({
                    "Ticker": tkr,
                    "P/E Ttm":   f"{inf.get('trailingPE'):.1f}"                    if inf.get('trailingPE') else "N/A",
                    "P/E Fwd":   f"{inf.get('forwardPE'):.1f}"                     if inf.get('forwardPE')  else "N/A",
                    "P/B":       f"{inf.get('priceToBook'):.2f}"                   if inf.get('priceToBook') else "N/A",
                    "P/S":       f"{inf.get('priceToSalesTrailing12Months'):.1f}"  if inf.get('priceToSalesTrailing12Months') else "N/A",
                    "EV/EBITDA": f"{inf.get('enterpriseToEbitda'):.1f}"            if inf.get('enterpriseToEbitda') else "N/A",
                    "EPS Fwd":   f"{inf.get('forwardEps'):.2f}"                    if inf.get('forwardEps') else "N/A",
                    "Rev $B":    f"{inf.get('totalRevenue',0)/1e9:.1f}"            if inf.get('totalRevenue') else "N/A",
                    "EBITDA $B": f"{inf.get('ebitda',0)/1e9:.1f}"                 if inf.get('ebitda') else "N/A",
                    "FCF $B":    f"{inf.get('freeCashflow',0)/1e9:.1f}"            if inf.get('freeCashflow') else "N/A",
                    "D/E":       f"{inf.get('debtToEquity',0)/100:.2f}"            if inf.get('debtToEquity') else "N/A",
                    "Op.Mgn %":  f"{inf.get('operatingMargins',0)*100:.1f}"        if inf.get('operatingMargins') else "N/A",
                    "ROE %":     f"{inf.get('returnOnEquity',0)*100:.1f}"          if inf.get('returnOnEquity') else "N/A",
                })
            if snap_rows:
                st.dataframe(pd.DataFrame(snap_rows).set_index("Ticker"), use_container_width=True)

# ═══════════════════════════════════════════════════════════
#  PAGE 5 — PORTFOLIO BACKTEST
# ═══════════════════════════════════════════════════════════
elif choice == "Portfolio Backtest":
    page_title("🧪  PORTFOLIO BACKTEST", "Equity curve · Drawdown · Rolling Sharpe · Monthly heatmap · Risk analytics")

    sec("COMPOSIZIONE PORTAFOGLIO")
    n_assets = st.slider("Numero di asset",2,10,4)
    defaults = ["VOO","GLD","TLT","QQQ","BND","VNQ","EEM","PDBC","IAU","VWCE.DE"]
    col_t = st.columns(n_assets)
    col_w = st.columns(n_assets)
    asset_list, weight_list = [], []
    dw = round(100/n_assets)
    for i in range(n_assets):
        with col_t[i]:
            t_v = st.text_input(f"Asset {i+1}", value=defaults[i] if i<len(defaults) else "", key=f"a_{i}")
            asset_list.append(t_v.strip().upper())
        with col_w[i]:
            w_v = st.slider(asset_list[i] or f"A{i+1}",0,100,dw,key=f"w_{i}")
            weight_list.append(w_v)

    tw = sum(weight_list)
    if tw != 100: st.warning(f"⚠️  Somma pesi: {tw}%")
    else:         st.success("✅  Pesi al 100%")

    st.markdown("---")
    sec("BENCHMARK E PARAMETRI")
    b1,b2,b3 = st.columns(3)
    with b1:
        bench_opts = {"S&P 500 (^GSPC)":"^GSPC","Nasdaq 100 (^IXIC)":"^IXIC",
                      "MSCI World (VWCE.DE)":"VWCE.DE","60/40 Custom":None}
        bench_lbl = st.selectbox("Benchmark",list(bench_opts.keys()))
        bench     = bench_opts[bench_lbl]
    with b2: years  = st.slider("Orizzonte (anni)",1,25,7,key="bty")
    with b3: rf_pct = st.slider("Risk-free rate (%)",0.0,7.0,4.2,step=0.1)

    if bench is None:
        bc1,bc2 = st.columns(2)
        with bc1: bench_eq   = st.text_input("Equity part","SPY")
        with bc2: bench_bond = st.text_input("Bond part","AGG")
    else:
        bench_eq, bench_bond = "SPY","AGG"

    run_bt = st.button("▶  ESEGUI BACKTEST", use_container_width=True)

    if run_bt and tw == 100:
        valid_pairs  = [(a,weight_list[i]) for i,a in enumerate(asset_list) if a]
        valid_assets = [p[0] for p in valid_pairs]
        w_norm       = [p[1]/100 for p in valid_pairs]
        start_str    = (datetime.now()-timedelta(days=365*years)).strftime("%Y-%m-%d")
        rf            = rf_pct/100
        b_tickers    = [bench] if bench else [bench_eq.upper(), bench_bond.upper()]

        with st.spinner("Download dati..."):
            frames = {}
            for tkr in valid_assets + b_tickers:
                s = fetch_close(tkr, start=start_str)
                if not s.empty: frames[tkr] = s
                else: st.warning(f"⚠️ No data: {tkr}")

        if not frames:
            st.error("Nessun dato scaricato.")
        else:
            data = pd.DataFrame(frames).dropna(how='all').ffill()
            norm = (data / data.iloc[0]) - 1

            strat_df = pd.DataFrame(index=norm.index)
            for i,a in enumerate(valid_assets):
                if a in norm.columns: strat_df[a] = norm[a]*w_norm[i]
            strat = strat_df.sum(axis=1)

            if bench is None:
                beq,bbd = bench_eq.upper(),bench_bond.upper()
                bench_ser  = norm[beq]*0.6+norm[bbd]*0.4 if (beq in norm.columns and bbd in norm.columns) else None
                bench_col  = None
                bench_name = f"60%{beq}+40%{bbd}"
            else:
                bench_col  = bench
                bench_ser  = None
                bench_name = bench_lbl

            # ── Risk metrics ──
            tot_ret  = strat.iloc[-1]*100
            ann_ret  = ((1+strat.iloc[-1])**(1/years)-1)*100 if years>0 else 0
            dr       = strat.diff().dropna()
            vol      = dr.std()*np.sqrt(252)*100
            sharpe   = (ann_ret/100-rf)/(vol/100) if vol>0 else 0
            dd_s     = ((strat+1)/(strat+1).cummax())-1
            max_dd   = dd_s.min()*100
            calmar   = ann_ret/abs(max_dd) if max_dd!=0 else 0
            neg      = dr[dr<0]
            down_v   = neg.std()*np.sqrt(252)*100 if len(neg)>0 else 0
            sortino  = (ann_ret/100-rf)/(down_v/100) if down_v>0 else 0
            arr      = dr.dropna().values
            var95    = np.percentile(arr,5)*100 if len(arr)>0 else 0
            cvar95   = arr[arr<=np.percentile(arr,5)].mean()*100 if len(arr)>0 else 0
            win_r    = (dr>0).mean()*100
            thr      = rf/252
            g_o      = dr[dr>thr]-thr; l_o = thr-dr[dr<thr]
            omega    = g_o.sum()/l_o.sum() if l_o.sum()>0 else 999

            bench_ann = delta_bench = beta_val = alpha_val = None
            if bench_col and bench_col in norm.columns:
                bs = norm[bench_col]
                bench_ann   = ((1+bs.iloc[-1])**(1/years)-1)*100
                delta_bench = tot_ret - bs.iloc[-1]*100
                br = bs.diff().dropna()
                try:
                    al = pd.DataFrame({"s":dr,"b":br}).dropna()
                    if len(al)>10:
                        cov = al.cov().iloc[0,1]; vb = al["b"].var()
                        beta_val  = cov/vb if vb!=0 else None
                        alpha_val = ann_ret - (rf_pct + (beta_val or 0)*(bench_ann-rf_pct))
                except: pass
            elif bench_ser is not None:
                bs = bench_ser
                bench_ann   = ((1+bs.iloc[-1])**(1/years)-1)*100
                delta_bench = tot_ret - bs.iloc[-1]*100

            # ── KPI Dashboard ──
            st.markdown("---")
            sec("PERFORMANCE DASHBOARD")
            k1,k2,k3,k4 = st.columns(4)
            k1.metric("Rendimento Totale",f"{tot_ret:+.2f}%")
            k2.metric("CAGR",f"{ann_ret:+.2f}%")
            k3.metric("Volatilità Annua",f"{vol:.2f}%")
            k4.metric("Max Drawdown",f"{max_dd:.2f}%")

            k5,k6,k7,k8 = st.columns(4)
            k5.metric("Sharpe Ratio",f"{sharpe:.3f}")
            k6.metric("Sortino Ratio",f"{sortino:.3f}")
            k7.metric("Calmar Ratio",f"{calmar:.3f}")
            k8.metric("Omega Ratio",f"{omega:.2f}")

            k9,k10,k11,k12 = st.columns(4)
            k9.metric("VaR 95% (giorn.)",f"{var95:.2f}%")
            k10.metric("CVaR 95%",f"{cvar95:.2f}%")
            k11.metric("Win Rate",f"{win_r:.1f}%")
            k12.metric("Beta vs Bench",f"{beta_val:.2f}" if beta_val else "N/A")

            if delta_bench is not None:
                da1,da2 = st.columns(2)
                da1.metric(f"Alpha vs {bench_name}", f"{alpha_val:+.2f}%" if alpha_val else "N/A")
                da2.metric(f"Delta vs {bench_name}", f"{delta_bench:+.2f}%",
                           delta="Sovraperforma" if delta_bench>0 else "Sottoperforma")

            # ── Equity Curve ──
            sec("EQUITY CURVE")
            fig_eq = go.Figure()
            fig_eq.add_trace(go.Scatter(x=strat.index,y=strat*100,name="Strategia",
                line=dict(width=3,color="#3B8EF0"),fill='tozeroy',fillcolor='rgba(59,142,240,0.06)',
                hovertemplate="%{x|%d %b %Y}<br><b>%{y:.2f}%</b><extra>Strategia</extra>"))
            if bench_col and bench_col in norm.columns:
                fig_eq.add_trace(go.Scatter(x=norm.index,y=norm[bench_col]*100,name=bench_name,
                    line=dict(width=2,dash='dash',color='#7A9DBE'),
                    hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>Bench</extra>"))
            elif bench_ser is not None:
                fig_eq.add_trace(go.Scatter(x=bench_ser.index,y=bench_ser*100,name=bench_name,
                    line=dict(width=2,dash='dash',color='#7A9DBE')))
            for idx,a in enumerate(valid_assets):
                if a in norm.columns:
                    fig_eq.add_trace(go.Scatter(x=norm.index,y=norm[a]*100,
                        name=f"{a} ({valid_pairs[idx][1]}%)",
                        line=dict(width=1.2,color=COLORS[(idx+2)%len(COLORS)]),opacity=0.5))
            fig_eq.add_hline(y=0,line_dash="dot",line_color="#163860",line_width=1)
            fig_eq.update_layout(**pl({"xaxis":iaxis(),"yaxis_title":"Rendimento %","height":480,
                                       "title":"Equity Curve — Rendimento Cumulativo"}))
            st.plotly_chart(fig_eq, use_container_width=True)

            # ── Rolling Sharpe ──
            sec("ROLLING SHARPE (252 GG)")
            roll_vol  = dr.rolling(252).std()*np.sqrt(252)
            roll_ret  = dr.rolling(252).mean()*252
            roll_sh   = (roll_ret-rf)/roll_vol
            fig_rs = go.Figure()
            fig_rs.add_trace(go.Scatter(x=roll_sh.index,y=roll_sh,name="Rolling Sharpe",
                line=dict(color="#3B8EF0",width=1.8),
                hovertemplate="%{x|%d %b %Y}<br>Sharpe: %{y:.2f}<extra></extra>"))
            fig_rs.add_hline(y=0,line_dash="dot",line_color="#163860")
            fig_rs.add_hline(y=1,line_dash="dot",line_color="#2ECC71",annotation_text="Sharpe=1",annotation_font_color="#2ECC71")
            fig_rs.update_layout(**pl({"height":260,"title":"Rolling Sharpe Ratio (1 anno)"}))
            st.plotly_chart(fig_rs, use_container_width=True)

            # ── Drawdown ──
            sec("DRAWDOWN")
            dd = dd_s*100
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(x=dd.index,y=dd,name="Drawdown",
                fill='tozeroy',line=dict(color='#E74C3C',width=1.5),
                fillcolor='rgba(231,76,60,0.12)',
                hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra></extra>"))
            fig_dd.update_layout(**pl({"xaxis":iaxis(),"yaxis_title":"Drawdown %","height":260,
                                       "title":"Drawdown dalla Massima Equity"}))
            st.plotly_chart(fig_dd, use_container_width=True)

            # ── Monthly Heatmap ──
            sec("MONTHLY RETURNS HEATMAP")
            try:
                mth = strat.resample('ME').last().pct_change().dropna()*100
                mdf = pd.DataFrame({'Y':mth.index.year,'M':mth.index.month,'R':mth.values})
                pvt = mdf.pivot(index='Y',columns='M',values='R')
                mn  = ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic']
                pvt.columns = [mn[m-1] for m in pvt.columns]
                fig_mth = go.Figure(go.Heatmap(
                    z=pvt.values, x=pvt.columns.tolist(), y=pvt.index.tolist(),
                    colorscale=[[0,"#E74C3C"],[0.5,"#071220"],[1,"#2ECC71"]], zmid=0,
                    text=[[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in pvt.values],
                    texttemplate="%{text}",
                    hovertemplate="Anno %{y} · %{x}<br>%{z:.2f}%<extra></extra>"))
                fig_mth.update_layout(**pl({"height":max(180,len(pvt)*26+80),"title":"Rendimenti Mensili (%)"}))
                st.plotly_chart(fig_mth, use_container_width=True)
            except: st.info("Heatmap mensile non disponibile.")

            # ── Return Distribution ──
            sec("DISTRIBUZIONE RENDIMENTI GIORNALIERI")
            fig_h = go.Figure()
            fig_h.add_trace(go.Histogram(x=arr*100,nbinsx=80,marker_color='#3B8EF0',opacity=0.75))
            fig_h.add_vline(x=var95,line_dash="dash",line_color="#E74C3C",
                            annotation_text=f"VaR 95%: {var95:.2f}%",annotation_font_color="#E74C3C")
            fig_h.add_vline(x=0,line_dash="dot",line_color="#7A9DBE")
            fig_h.update_layout(**pl({"height":260,"xaxis_title":"Rendimento Giornaliero %",
                                      "yaxis_title":"Frequenza","title":"Distribuzione Rendimenti"}))
            st.plotly_chart(fig_h, use_container_width=True)

            # ── Correlation ──
            avail = [a for a in valid_assets if a in norm.columns]
            if len(avail)>=2:
                sec("CORRELAZIONE ASSET")
                corr_df = norm[avail].pct_change().dropna().corr()
                fig_co = go.Figure(go.Heatmap(
                    z=corr_df.values,x=corr_df.columns.tolist(),y=corr_df.index.tolist(),
                    colorscale=[[0,"#E74C3C"],[0.5,"#071220"],[1,"#2ECC71"]],zmid=0,
                    text=corr_df.round(2).values,texttemplate="%{text}"))
                fig_co.update_layout(**pl({"height":320,"title":"Correlazione tra Asset"}))
                st.plotly_chart(fig_co, use_container_width=True)

            # ── Smart Suggestions ──
            st.markdown("---")
            sec("ANALISI E SUGGERIMENTI")
            tips = []
            if sharpe < 0: tips.append(f"🔴 <b>Sharpe negativo ({sharpe:.2f})</b> — Rendimento sotto il risk-free ({rf_pct:.1f}%). Individua l'asset con peggior contributo e sostituiscilo.")
            elif sharpe < 0.5: tips.append(f"🟡 <b>Sharpe basso ({sharpe:.2f})</b> — Ogni punto di vol genera poco rendimento. Aggiungi asset decorrelati: GLD, TLT, REITs.")
            elif sharpe >= 1.5: tips.append(f"🏆 <b>Sharpe elevato ({sharpe:.2f})</b> — Eccellente. Verifica su periodo più lungo per survivorship bias.")
            else: tips.append(f"✅ <b>Sharpe accettabile ({sharpe:.2f})</b> — Obiettivo: superare 1.0 per alfa costante.")
            if vol>25: tips.append(f"⚡ <b>Volatilità alta ({vol:.1f}%)</b> — Considera 15-25% in bond aggregati per protezione.")
            if max_dd < -40: tips.append(f"💥 <b>Drawdown estremo ({max_dd:.1f}%)</b> — Implementa risk parity o position sizing Kelly.")
            if var95 < -3: tips.append(f"📉 <b>VaR 95% elevato ({var95:.2f}%/gg)</b> — 1 giorno su 20 rischi una perdita > {abs(var95):.1f}%.")
            if len(valid_assets)<3: tips.append(f"🔀 <b>Bassa diversificazione ({len(valid_assets)} asset)</b> — 8-15 asset non correlati sono ottimali.")
            if not tips: tips.append("ℹ️ Parametri nella norma. Nessun segnale critico.")
            for tip in tips:
                st.markdown(f"<div style='background:linear-gradient(135deg,#071A30,#0A1E38);border-left:3px solid #3B8EF0;border-radius:3px;padding:0.75rem 1rem;margin-bottom:0.45rem;font-size:0.85rem;line-height:1.7;color:#D8E4F0'>{tip}</div>",
                            unsafe_allow_html=True)

    elif run_bt and tw != 100:
        st.error("I pesi devono sommare a 100%.")

# ═══════════════════════════════════════════════════════════
#  PAGE 6 — STOCK SCREENER
# ═══════════════════════════════════════════════════════════
elif choice == "Stock Screener":

    if st.session_state.screener_selected:
        target = st.session_state.screener_selected
        col_back,_ = st.columns([1,6])
        with col_back:
            if st.button("← Torna allo Screener"):
                st.session_state.screener_selected = None; st.rerun()
        page_title(f"⌨️  ANALISI — {target}")
        inf_s  = fetch_info(target)
        sector_s = inf_s.get('sector','') if inf_s else ''
        peers_d  = SECTOR_PEERS.get(sector_s, "SPY, QQQ, IWM")
        show_bloomberg(target, peers_default=peers_d)

    else:
        page_title("🔍  STOCK SCREENER", f"Filtra su universo di {len(CURATED_TICKERS)}+ ticker globali")

        # ── Filtri ──
        sec("FILTRI FONDAMENTALI")
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            pe_max   = st.slider("P/E max",0,200,50)
            pb_max   = st.slider("P/B max",0,30,10)
            ps_max   = st.slider("P/S max",0,50,15)
        with c2:
            cap_min  = st.slider("MktCap min (B$)",0,500,0)
            cap_max  = st.slider("MktCap max (B$)",0,5000,3000)
            de_max   = st.slider("D/E max",0,20,10)
        with c3:
            mgn_min  = st.slider("Op.Margin min %",-50,60,-50)
            roe_min  = st.slider("ROE min %",-20,80,-20)
            ev_max   = st.slider("EV/EBITDA max",0,100,100)
        with c4:
            div_min  = st.slider("Div Yield min %",0.0,10.0,0.0,step=0.1)
            beta_max = st.slider("Beta max",0.0,5.0,5.0,step=0.1)
            sec_f    = st.selectbox("Settore",["Tutti","Technology","Healthcare","Financials",
                                               "Industrials","Consumer Defensive","Consumer Cyclical",
                                               "Energy","Communication Services","Utilities",
                                               "Real Estate","Basic Materials"])

        sec("FILTRI AVANZATI")
        a1,a2 = st.columns(2)
        with a1: kw_f  = st.text_input("Keyword business","",placeholder="es: cloud, AI, defense, pharma ...")
        with a2: extra = st.text_input("Aggiungi ticker extra","",placeholder="AMZN, TSLA, ...")

        UNIVERSE = list(CURATED_TICKERS)
        if extra.strip():
            UNIVERSE = list(dict.fromkeys(UNIVERSE + [x.strip().upper() for x in extra.split(",") if x.strip()]))

        r1,r2 = st.columns(2)
        with r1:
            n_scan = st.selectbox("Ticker da scansionare",
                ["200 (~1min)","400 (~2min)","700 (~4min)","Tutti (~12min+)"])
        with r2:
            sort_by = st.selectbox("Ordina per",["Market Cap","P/E","EV/EBITDA","ROE %","Op.Margin %","Div Yield"])

        run_sc = st.button("▶  ESEGUI SCREENING", use_container_width=True)

        if run_sc:
            n_map = {"200 (~1min)":200,"400 (~2min)":400,"700 (~4min)":700,"Tutti (~12min+)":len(UNIVERSE)}
            n     = n_map.get(n_scan,200)
            scan  = random.sample(UNIVERSE, min(n, len(UNIVERSE)))

            results = []
            prog = st.progress(0)
            stat = st.empty()

            for i,tkr in enumerate(scan):
                prog.progress((i+1)/len(scan))
                stat.markdown(f"<div class='terminal-box' style='padding:0.5rem 0.9rem;margin:0'>⬛ Scansione: <b>{tkr}</b> ({i+1}/{len(scan)})</div>",
                              unsafe_allow_html=True)
                try:
                    inf = fetch_info(tkr)
                    if not inf: continue
                    pe  = inf.get('forwardPE') or inf.get('trailingPE')
                    pb  = inf.get('priceToBook')
                    ps  = inf.get('priceToSalesTrailing12Months')
                    mc  = inf.get('marketCap')
                    de  = inf.get('debtToEquity')
                    om  = inf.get('operatingMargins')
                    roe = inf.get('returnOnEquity')
                    eve = inf.get('enterpriseToEbitda')
                    dy  = (inf.get('dividendYield') or 0)*100
                    bt  = inf.get('beta')
                    sec_v = inf.get('sector','')
                    pr  = inf.get('currentPrice') or inf.get('regularMarketPrice') or inf.get('previousClose')
                    nm  = inf.get('shortName',tkr)

                    if sec_f != "Tutti" and sec_v != sec_f: continue
                    if kw_f.strip():
                        kw = kw_f.strip().lower()
                        txt = " ".join(filter(None,[inf.get('longBusinessSummary',''),
                                                     inf.get('industry',''),inf.get('longName',''),sec_v])).lower()
                        if kw not in txt: continue
                    if pe  is not None and pe > pe_max:          continue
                    if pb  is not None and pb > pb_max:          continue
                    if ps  is not None and ps > ps_max:          continue
                    if de  is not None and de/100 > de_max:      continue
                    if eve is not None and eve > ev_max:         continue
                    if mc  is not None and mc/1e9 < cap_min:     continue
                    if mc  is not None and mc/1e9 > cap_max:     continue
                    if om  is not None and om*100 < mgn_min:     continue
                    if roe is not None and roe*100 < roe_min:    continue
                    if dy < div_min:                             continue
                    if bt  is not None and bt > beta_max:        continue

                    results.append({
                        "Ticker":  tkr,
                        "Nome":    nm[:28],
                        "Settore": sec_v,
                        "Prezzo":  f"{pr:.2f}"       if pr  else "N/A",
                        "P/E":     f"{pe:.1f}"        if pe  else "N/A",
                        "P/B":     f"{pb:.1f}"        if pb  else "N/A",
                        "P/S":     f"{ps:.1f}"        if ps  else "N/A",
                        "EV/EBITDA":f"{eve:.1f}"      if eve else "N/A",
                        "Op.Mgn%": f"{om*100:.1f}"    if om  else "N/A",
                        "ROE%":    f"{roe*100:.1f}"   if roe else "N/A",
                        "Div%":    f"{dy:.2f}",
                        "Beta":    f"{bt:.2f}"        if bt  else "N/A",
                        "D/E":     f"{de/100:.2f}"    if de  else "N/A",
                        "Cap$B":   f"{mc/1e9:.1f}"    if mc  else "N/A",
                        "_mc": mc/1e9 if mc else 0,
                        "_pe": pe if pe else 999,
                        "_ev": eve if eve else 999,
                        "_roe": roe*100 if roe else 0,
                        "_mgn": om*100 if om else 0,
                        "_div": dy,
                    })
                except: continue

            prog.empty(); stat.empty()
            sk_map = {"Market Cap":("_mc",True),"P/E":("_pe",False),"EV/EBITDA":("_ev",False),
                      "ROE %":("_roe",True),"Op.Margin %":("_mgn",True),"Div Yield":("_div",True)}
            sk,rv = sk_map.get(sort_by,("_mc",True))
            results.sort(key=lambda x:x.get(sk,0), reverse=rv)
            st.session_state.screener_results = results

        if st.session_state.screener_results:
            res = st.session_state.screener_results
            st.success(f"✅  {len(res)} aziende trovate")
            disp_cols = ["Nome","Settore","Prezzo","P/E","P/B","P/S","EV/EBITDA","Op.Mgn%","ROE%","Div%","Beta","Cap$B"]
            st.dataframe(pd.DataFrame(res)[["Ticker"]+disp_cols].set_index("Ticker"), use_container_width=True)
            sec("ANALISI DETTAGLIATA")
            sel = st.selectbox("Seleziona azienda",[f"{r['Ticker']} — {r['Nome']}" for r in res])
            if st.button("🔎  APRI BLOOMBERG TERMINAL", use_container_width=True):
                st.session_state.screener_selected = sel.split(" — ")[0].strip()
                st.rerun()
        elif st.session_state.screener_results is not None and len(st.session_state.screener_results)==0:
            st.warning("Nessuna azienda trovata. Allarga i filtri.")

# ═══════════════════════════════════════════════════════════
#  PAGE 7 — BLOOMBERG INSIGHTS
# ═══════════════════════════════════════════════════════════
elif choice == "Bloomberg Insights":
    page_title("⌨️  COMPANY TERMINAL", "Analisi fondamentale · Peers · Supply chain · Performance")

    c_inp, c_btn = st.columns([5,1])
    with c_inp:
        new_t = st.text_input("Ticker",
                              value=st.session_state.bi_ticker,
                              placeholder="AAPL · NVDA · ENI.MI · ASML.AS · MC.PA ...").strip().upper()
    with c_btn:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        go_btn = st.button("🔍 GO", use_container_width=True)

    if (go_btn or new_t) and new_t:
        if new_t != st.session_state.bi_ticker:
            st.session_state.bi_ticker = new_t
            inf_bi = fetch_info(new_t)
            s_bi   = inf_bi.get('sector','') if inf_bi else ''
            st.session_state.bi_peers = SECTOR_PEERS.get(s_bi, "SPY, QQQ, IWM, GLD")

        show_bloomberg(st.session_state.bi_ticker,
                       peers_default=st.session_state.bi_peers)

# ═══════════════════════════════════════════════════════════
#  PAGE 8 — MARKET NEWS
# ═══════════════════════════════════════════════════════════
elif choice == "Market News":
    page_title("📰  MARKET NEWS", "Notizie in tempo reale per mercati e singoli titoli")

    sec("NEWS PER TICKER")
    news_tk = st.text_input("Ticker","AAPL, NVDA, TSLA",placeholder="Inserisci uno o più ticker (virgola)")
    tk_news = [x.strip().upper() for x in news_tk.split(",") if x.strip()]

    for tkr in tk_news[:5]:
        st.markdown(f"<div class='sec-hdr' style='margin-top:1rem'>📌 {tkr}</div>", unsafe_allow_html=True)
        try:
            news = yf.Ticker(tkr).news or []
            if not news:
                st.caption("Nessuna notizia disponibile.")
                continue
            for n in news[:6]:
                title     = n.get('title','')
                link      = n.get('link','#')
                publisher = n.get('publisher','')
                ptime     = n.get('providerPublishTime',0)
                ts = datetime.fromtimestamp(ptime).strftime("%d %b %Y %H:%M") if ptime else ""
                if title:
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#071A30,#0A1E38);border:1px solid #0E2440;
                                border-left:3px solid #3B8EF0;border-radius:3px;padding:0.65rem 1rem;margin-bottom:0.4rem'>
                      <a href='{link}' target='_blank' style='color:#D8E4F0;text-decoration:none;font-size:0.88rem;font-weight:500'>{title}</a>
                      <div style='font-size:0.7rem;color:#7A9DBE;margin-top:4px'>{publisher} &nbsp;·&nbsp; {ts}</div>
                    </div>""", unsafe_allow_html=True)
        except:
            st.caption(f"Notizie non disponibili per {tkr}.")

    st.markdown("---")
    sec("FONTI ESTERNE RACCOMANDATI")
    links = [
        ("Bloomberg Markets","https://www.bloomberg.com/markets"),
        ("Reuters Finance","https://www.reuters.com/finance/"),
        ("Financial Times","https://www.ft.com/markets"),
        ("Yahoo Finance","https://finance.yahoo.com"),
        ("Seeking Alpha","https://seekingalpha.com"),
        ("Il Sole 24 Ore","https://www.ilsole24ore.com/finanza-e-mercati"),
    ]
    cols_n = st.columns(3)
    for i,(name,url) in enumerate(links):
        cols_n[i%3].markdown(f"""
        <a href='{url}' target='_blank' style='display:block;background:linear-gradient(135deg,#071A30,#0A1E38);
           border:1px solid #0E2440;border-radius:3px;padding:0.6rem 0.9rem;text-decoration:none;
           color:#3B8EF0;font-family:IBM Plex Mono,monospace;font-size:0.78rem;
           margin-bottom:0.5rem;letter-spacing:0.04em'>📎 {name}</a>""", unsafe_allow_html=True)
ENDOFFILE
Output

exit code 0
Done


"""
╔══════════════════════════════════════════════════════════════════╗
║   NAVY TERMINAL PRO  v6.1  ·  Institutional Intelligence Engine  ║
║   SEC Edgar · OpenBB · FRED · CAPM/DCF · Monte Carlo             ║
║   PERF BUILD: session_state cache · lazy tabs · client-side grid ║
║   FIX v6.1r2: fluid UX · earnings bypass · labels fix ·          ║
║               comparison tickers · total black · DCE module      ║
╚══════════════════════════════════════════════════════════════════╝
"""

import math
import warnings
import hashlib
import json
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf

warnings.filterwarnings("ignore")

# ── Local modules ─────────────────────────────────────────────────
from data_engine import (
    UnifiedMarketDataEngine,
    yf_info, yf_close, yf_ohlcv, yf_price_chg,
    yf_financials, yf_options, yf_holders,
    yf_recommendations, yf_earnings_dates,
    fetch_fred, FRED_SERIES,
    load_screener_master_data,
    apply_screener_filters,
    SCREENER_UNIVERSE_FULL,
)
from quant_engine import (
    DCFInputs, DCFResult, WACCInputs,
    run_dcf, dcf_sensitivity, monte_carlo_dcf, reverse_dcf,
    compute_wacc, run_backtest,
    rsi, macd, atr, fibonacci,
    fmt_bn,
    # Multi-Factor Regression
    run_factor_regression, run_rolling_factor_regression,
    compare_factor_models,
    FactorRegressionResult, FACTOR_MODEL_COLS,
    MODEL_DISPLAY_NAMES, FACTOR_DESCRIPTIONS,
)
from data_engine import (
    fetch_ff_factors, fetch_asset_returns_for_regression,
    build_regression_dataset,
)
from ui_components import (
    GLOBAL_CSS, COLORS,
    navy_grid, screener_aggrid, render_screener_filter_panel,
    pla, xaxis_time, yaxis_plain,
    build_candle_chart,
    ptitle, sec, alert, badge, interrupted, colored, status_badge,
)

# ══════════════════════════════════════════════════════════
#  APP CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NAVY TERMINAL PRO",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════
#  FIX #5 — TOTAL BLACK BLOOMBERG THEME
#  Full-page injection: deep black base, amber/green accents,
#  IBM Plex Mono throughout, high-density AgGrid dark theme.
# ══════════════════════════════════════════════════════════
BLOOMBERG_BLACK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* ── CSS Variables ─────────────────────────────────────── */
:root {
  --bg-base:         #000000;
  --bg-card:         #080808;
  --bg-panel:        #0d0d0d;
  --bg-hover:        #141414;
  --bg-input:        #060606;
  --border-dim:      #1a1a1a;
  --border-mid:      #222222;
  --border-active:   #F5A623;
  --text-primary:    #E2E8F0;
  --text-secondary:  #7A9BB8;
  --text-muted:      #2A3A4C;
  --text-dim:        #1A2A3C;
  --accent-amber:    #F5A623;
  --accent-blue:     #3B8EF0;
  --accent-green:    #00FF88;
  --accent-red:      #FF3B3B;
  --accent-cyan:     #00D4FF;
  --font-mono:       'IBM Plex Mono', 'Courier New', monospace;
  --font-sans:       'IBM Plex Sans', 'Segoe UI', sans-serif;
}

/* ── Global Reset ──────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

/* ── Root Backgrounds ──────────────────────────────────── */
html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
.main .block-container,
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"] {
  background-color: #000000 !important;
  color: var(--text-primary) !important;
  font-family: var(--font-mono) !important;
}

/* ── Sidebar ───────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
section[data-testid="stSidebar"] > div {
  background-color: #030303 !important;
  border-right: 1px solid #111111 !important;
}

/* ── Block Container Padding ───────────────────────────── */
.main .block-container {
  padding: 0.6rem 1.4rem 1rem 1.4rem !important;
  max-width: 100% !important;
}

/* ── Typography ────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  font-family: var(--font-mono) !important;
  color: var(--text-primary) !important;
  letter-spacing: 0.04em;
}
p, span, div, label, small {
  font-family: var(--font-mono) !important;
}

/* ── Section headers ───────────────────────────────────── */
.sec-hdr {
  font-family: var(--font-mono) !important;
  font-size: 0.58rem !important;
  letter-spacing: 0.18em !important;
  color: var(--text-secondary) !important;
  text-transform: uppercase;
  border-bottom: 1px solid #111111;
  padding-bottom: 3px;
  margin: 0.9rem 0 0.45rem 0;
}

/* ── Nav Title ─────────────────────────────────────────── */
.nav-title {
  font-family: var(--font-mono) !important;
  font-size: 1.4rem !important;
  font-weight: 700 !important;
  color: var(--accent-amber) !important;
  letter-spacing: 0.12em;
}
.nav-sub {
  font-size: 0.50rem !important;
  color: var(--text-dim) !important;
  letter-spacing: 0.16em;
  font-family: var(--font-mono) !important;
}
.nav-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #1a1a1a, transparent);
  margin: 0.6rem 0;
}

/* ── Buttons ───────────────────────────────────────────── */
[data-testid="stButton"] button {
  background: #060606 !important;
  border: 1px solid #181818 !important;
  color: #5A7A9A !important;
  font-family: var(--font-mono) !important;
  font-size: 0.70rem !important;
  letter-spacing: 0.08em;
  border-radius: 2px !important;
  padding: 5px 10px !important;
  transition: border-color 0.12s, color 0.12s, background 0.12s;
  text-transform: uppercase;
}
[data-testid="stButton"] button:hover {
  border-color: var(--accent-amber) !important;
  color: var(--accent-amber) !important;
  background: #0a0600 !important;
}
[data-testid="stButton"] button[kind="primary"],
[data-testid="stButton"] button[aria-pressed="true"] {
  background: #0A0600 !important;
  border-left: 2px solid var(--accent-amber) !important;
  color: var(--accent-amber) !important;
}

/* ── Inputs ────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
  background: #050505 !important;
  border: 1px solid #1a1a1a !important;
  color: var(--text-primary) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.78rem !important;
  border-radius: 2px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
  border-color: var(--accent-amber) !important;
  box-shadow: 0 0 0 1px #F5A62322 !important;
}
[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
  background: #050505 !important;
  border-color: #1a1a1a !important;
  font-family: var(--font-mono) !important;
  border-radius: 2px !important;
}
[data-baseweb="popover"] > div,
[data-baseweb="menu"] {
  background: #090909 !important;
  border: 1px solid #222 !important;
}
[data-baseweb="option"]:hover {
  background: #111 !important;
}
[data-testid="stMultiSelect"] > div { background: #050505 !important; border-color: #1a1a1a !important; }
[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stMultiSelect"] label {
  color: var(--text-secondary) !important;
  font-size: 0.64rem !important;
  letter-spacing: 0.10em;
  text-transform: uppercase;
  font-family: var(--font-mono) !important;
}

/* ── Sliders ───────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
  background: var(--accent-amber) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="progressbar"] {
  background: var(--accent-amber) !important;
}
[data-testid="stSlider"] label { color: var(--text-secondary) !important; font-size: 0.64rem !important; }

/* ── Metrics ───────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: #060606 !important;
  border: 1px solid #111111 !important;
  border-radius: 2px !important;
  padding: 7px 11px !important;
}
[data-testid="stMetricLabel"] {
  color: #3A5A7A !important;
  font-size: 0.56rem !important;
  font-family: var(--font-mono) !important;
  letter-spacing: 0.10em;
  text-transform: uppercase;
}
[data-testid="stMetricValue"] {
  color: var(--text-primary) !important;
  font-family: var(--font-mono) !important;
  font-size: 1.05rem !important;
  font-weight: 600;
}
[data-testid="stMetricDelta"] { font-size: 0.65rem !important; font-family: var(--font-mono) !important; }

/* ── Tabs ──────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
  background: #040404 !important;
  border-bottom: 1px solid #111 !important;
  gap: 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
  color: #2A4A6A !important;
  font-family: var(--font-mono) !important;
  font-size: 0.65rem !important;
  letter-spacing: 0.10em;
  padding: 6px 14px !important;
  border-radius: 0 !important;
  border-bottom: 2px solid transparent !important;
  text-transform: uppercase;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--accent-amber) !important;
  border-bottom: 2px solid var(--accent-amber) !important;
  background: transparent !important;
}
[data-testid="stTabs"] [role="tab"]:hover {
  color: var(--text-secondary) !important;
  background: #0a0a0a !important;
}
[data-testid="stTabsContent"] { background: transparent !important; }

/* ── AgGrid Total Black ────────────────────────────────── */
.ag-root-wrapper, .ag-root, .ag-body,
.ag-header, .ag-header-viewport, .ag-header-container,
.ag-body-viewport, .ag-center-cols-container,
.ag-paging-panel {
  background-color: #040404 !important;
  color: #B0C4D8 !important;
  font-family: var(--font-mono) !important;
  font-size: 0.73rem !important;
}
.ag-header-cell {
  background: #060606 !important;
  color: #3A6A9A !important;
  font-size: 0.60rem !important;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  border-right: 1px solid #0e0e0e !important;
  border-bottom: 1px solid #111 !important;
}
.ag-header-cell:hover { background: #0a0a0a !important; color: var(--accent-amber) !important; }
.ag-row { background: #040404 !important; border-bottom: 1px solid #0c0c0c !important; }
.ag-row:hover { background: #0a0600 !important; }
.ag-row-odd { background: #020202 !important; }
.ag-row-odd:hover { background: #0a0600 !important; }
.ag-cell { color: #9AB0C8 !important; border-right: 1px solid #0c0c0c !important; }
.ag-paging-panel { background: #060606 !important; color: #3A6A9A !important; border-top: 1px solid #111 !important; }
.ag-paging-button { background: transparent !important; border: 1px solid #1a1a1a !important; color: #3A6A9A !important; }
.ag-paging-button:hover { border-color: var(--accent-amber) !important; color: var(--accent-amber) !important; }

/* ── Expanders ─────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: #050505 !important;
  border: 1px solid #111 !important;
  border-radius: 2px !important;
}
[data-testid="stExpander"] summary {
  color: var(--text-secondary) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.68rem !important;
  letter-spacing: 0.10em;
}

/* ── Info / Warning / Error boxes ─────────────────────── */
[data-testid="stAlert"] {
  background: #060606 !important;
  border: 1px solid #1a1a1a !important;
  border-radius: 2px !important;
  color: var(--text-secondary) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.73rem !important;
}
.stInfo { border-left: 2px solid var(--accent-blue) !important; }
.stWarning { border-left: 2px solid var(--accent-amber) !important; }
.stError { border-left: 2px solid var(--accent-red) !important; }
.stSuccess { border-left: 2px solid var(--accent-green) !important; }

/* ── Progress bars ─────────────────────────────────────── */
[data-testid="stProgress"] > div > div { background: var(--accent-amber) !important; }
[data-testid="stProgress"] > div { background: #111 !important; }

/* ── Checkbox / Radio ──────────────────────────────────── */
[data-testid="stCheckbox"] label,
[data-testid="stRadio"] label { color: var(--text-secondary) !important; font-family: var(--font-mono) !important; font-size: 0.70rem !important; }
[data-testid="stRadio"] [role="radio"][aria-checked="true"] { background: var(--accent-amber) !important; }

/* ── Form ──────────────────────────────────────────────── */
[data-testid="stForm"] {
  background: #050505 !important;
  border: 1px solid #111 !important;
  border-radius: 2px !important;
  padding: 0.6rem !important;
}

/* ── Dividers ──────────────────────────────────────────── */
hr { border-color: #0e0e0e !important; margin: 0.5rem 0 !important; }

/* ── Scrollbars ────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #000; }
::-webkit-scrollbar-thumb { background: #1a1a1a; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-amber); }

/* ── Caption / small text ──────────────────────────────── */
[data-testid="stCaptionContainer"],
.stCaption { color: #2A4A6A !important; font-size: 0.60rem !important; font-family: var(--font-mono) !important; }

/* ── Selectbox dropdown options ────────────────────────── */
[data-testid="stSelectbox"] div[role="option"] { background: #090909 !important; color: var(--text-secondary) !important; }
[data-testid="stSelectbox"] div[role="option"]:hover { background: #111 !important; color: var(--accent-amber) !important; }

/* ── Plotly chart background ───────────────────────────── */
.js-plotly-plot .plotly .bg { fill: #000000 !important; }

/* ── Custom card components ────────────────────────────── */
.ticker-card {
  background: #060606;
  border: 1px solid #141414;
  border-left: 3px solid var(--accent-amber);
  border-radius: 2px;
  padding: 14px 18px;
  margin-bottom: 12px;
}
.ticker-tag {
  font-size: 0.52rem;
  letter-spacing: 0.18em;
  color: #3A6A9A;
  text-transform: uppercase;
  font-family: var(--font-mono);
  margin-bottom: 4px;
}
.ticker-name {
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-mono);
  letter-spacing: 0.02em;
  line-height: 1.2;
}
.ticker-meta {
  font-size: 0.63rem;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  margin-top: 4px;
}
.ticker-price {
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-mono);
  letter-spacing: -0.01em;
}

.term-box {
  background: #060606;
  border: 1px solid #111;
  border-radius: 2px;
  padding: 10px 14px;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.mover-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #060606;
  border: 1px solid #0e0e0e;
  border-radius: 2px;
  padding: 6px 10px;
  margin-bottom: 4px;
}

.src-badge {
  background: #0a0a0a;
  border: 1px solid #1a1a1a;
  color: #3A6A9A;
  font-size: 0.52rem;
  padding: 1px 5px;
  border-radius: 2px;
  font-family: var(--font-mono);
  letter-spacing: 0.10em;
  text-transform: uppercase;
  vertical-align: middle;
}

.screener-stats-bar {
  background: #060606;
  border: 1px solid #111;
  border-radius: 2px;
  padding: 5px 14px;
  display: flex;
  gap: 1.4rem;
  align-items: center;
  font-family: var(--font-mono);
  font-size: 0.60rem;
  color: #3A6A9A;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.dce-header {
  background: linear-gradient(90deg, #0a0600, #000);
  border: 1px solid #1a1a1a;
  border-left: 3px solid var(--accent-amber);
  padding: 10px 16px;
  margin-bottom: 12px;
  border-radius: 2px;
}
.dce-title {
  font-family: var(--font-mono);
  font-size: 0.80rem;
  color: var(--accent-amber);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-weight: 600;
}
.dce-sub {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: var(--text-secondary);
  letter-spacing: 0.10em;
  margin-top: 2px;
}

/* ── Columns gap ───────────────────────────────────────── */
[data-testid="stHorizontalBlock"] { gap: 0.5rem !important; }

/* ── Number input spinners ─────────────────────────────── */
[data-testid="stNumberInput"] button {
  background: #0a0a0a !important;
  border-color: #1a1a1a !important;
  color: #3A6A9A !important;
}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown(BLOOMBERG_BLACK_CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  PLOTLY BLACK LAYOUT HELPER
# ══════════════════════════════════════════════════════════
def _pla(overrides: dict = None) -> dict:
    """Black-themed plotly layout — zero animation, pure black backgrounds."""
    base = pla(overrides or {})
    base.update(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        transition={"duration": 0},
        uirevision=None,
        font=dict(family="IBM Plex Mono, monospace", color="#7A9BB8", size=10),
        legend=dict(
            bgcolor="#060606", bordercolor="#111111", borderwidth=1,
            font=dict(family="IBM Plex Mono", color="#7A9BB8", size=9),
        ),
        margin=dict(l=48, r=16, t=40, b=32),
    )
    for ax_key in ("xaxis", "yaxis", "xaxis2", "yaxis2"):
        base.setdefault(ax_key, {})
        base[ax_key].update({
            "gridcolor": "#0e0e0e",
            "zerolinecolor": "#141414",
            "linecolor": "#111111",
            "tickfont": {"family": "IBM Plex Mono", "color": "#3A6A9A", "size": 9},
        })
    return base


def _subsample(series: pd.Series, max_points: int = 2000) -> pd.Series:
    if len(series) <= max_points:
        return series
    step = math.ceil(len(series) / max_points)
    return series.iloc[::step]


def _subsample_df(df: pd.DataFrame, max_points: int = 2000) -> pd.DataFrame:
    if len(df) <= max_points:
        return df
    step = math.ceil(len(df) / max_points)
    return df.iloc[::step]


# ══════════════════════════════════════════════════════════
#  FIX #2 — EARNINGS CALENDAR BYPASS (yfinance-independent)
#  Direct HTTP scrape from Yahoo Finance calendar endpoint
#  with proper headers to bypass bot detection.
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_earnings_calendar_web(tickers: list) -> pd.DataFrame:
    """
    Fetch upcoming earnings dates for a list of tickers.
    Strategy 1: Yahoo Finance v7 screener / quoteSummary API (JSON, no scraping).
    Strategy 2: Direct yf.Ticker.calendar dict fallback.
    Returns a DataFrame with columns: Ticker, Company, EarningsDate, EPSEstimate.
    """
    import requests
    rows = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://finance.yahoo.com/",
    }
    for tkr in tickers:
        date_str, eps_str, name_str = "—", "—", tkr
        # Strategy 1: Yahoo Finance quoteSummary calendarEvents
        try:
            url = (
                f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{tkr}"
                f"?modules=calendarEvents,quoteType"
            )
            r = requests.get(url, headers=headers, timeout=6)
            if r.status_code == 200:
                data = r.json()
                qs = data.get("quoteSummary", {}).get("result", [])
                if qs:
                    cal = qs[0].get("calendarEvents", {})
                    qt  = qs[0].get("quoteType", {})
                    name_str = qt.get("longName") or qt.get("shortName") or tkr
                    earnings = cal.get("earnings", {})
                    dates = earnings.get("earningsDate", [])
                    if dates:
                        ts = dates[0].get("raw")
                        if ts:
                            date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    eps_data = earnings.get("earningsAverage", {})
                    if eps_data:
                        eps_v = eps_data.get("fmt") or eps_data.get("raw")
                        if eps_v is not None:
                            eps_str = str(eps_v)
        except Exception:
            pass

        # Strategy 2: yfinance Ticker.calendar fallback
        if date_str == "—":
            try:
                obj = yf.Ticker(tkr)
                cal_df = obj.calendar
                if cal_df is not None:
                    if isinstance(cal_df, pd.DataFrame) and not cal_df.empty:
                        for col in cal_df.columns:
                            if "earnings" in str(col).lower():
                                v = cal_df[col].iloc[0]
                                if v:
                                    date_str = str(v)[:10]
                                    break
                    elif isinstance(cal_df, dict):
                        ed = cal_df.get("Earnings Date") or cal_df.get("earnings_date")
                        if ed:
                            date_str = str(ed[0] if isinstance(ed, list) else ed)[:10]
            except Exception:
                pass

        rows.append({
            "Ticker":       tkr,
            "Company":      name_str[:32],
            "Earnings Date": date_str,
            "EPS Est.":     eps_str,
        })

    df_out = pd.DataFrame(rows)
    return df_out


# ══════════════════════════════════════════════════════════
#  SESSION STATE INITIALISATION
# ══════════════════════════════════════════════════════════
_DEFAULTS = dict(
    page                    = "Market Overview",
    # Screener
    screener_df             = None,
    screener_source         = None,
    screener_selected       = None,
    # Terminal
    terminal_ticker         = "NVDA",
    terminal_peers          = "AMD,INTC,AVGO,QCOM,SMCI",
    terminal_data_cache     = {},
    # Watchlist
    watchlist               = ["AAPL","NVDA","ASML.AS","ENI.MI","MC.PA","RACE.MI","MSFT","AMZN"],
    watchlist_data          = {},
    watchlist_last_refresh  = None,
    # Market overview
    market_data             = None,
    market_last_refresh     = None,
    # Charts
    chart_ohlcv_cache       = {},
    # DCF
    dcf_result_cache        = {},
    # Backtest
    backtest_result         = None,
    backtest_key            = None,
    # Macro/FRED
    fred_cache              = {},
    # Alerts
    alerts                  = [],
    # DCE
    dce_dataset_source      = "Screener",
    dce_df_cache            = None,
)
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════
#  REFERENCE DATA
# ══════════════════════════════════════════════════════════
SECTOR_PEERS = {
    "Technology":              "AAPL,MSFT,GOOGL,META,ORCL",
    "Semiconductors":          "NVDA,AMD,INTC,AVGO,TSM,KLAC,LRCX",
    "Consumer Cyclical":       "AMZN,TSLA,NKE,MCD,BKNG,ABNB",
    "Consumer Defensive":      "PG,KO,PEP,WMT,COST,CL",
    "Healthcare":              "JNJ,PFE,ABBV,MRK,LLY,AMGN,GILD",
    "Financials":              "JPM,BAC,GS,MS,V,MA,BLK",
    "Energy":                  "XOM,CVX,TTE.PA,BP.L,SLB,COP",
    "Industrials":             "GE,CAT,HON,BA,MMM,RTX,ETN",
    "Communication Services":  "META,GOOGL,NFLX,DIS,CMCSA,SPOT",
    "Utilities":               "NEE,CEG,DUK,SO,AEP,XEL",
    "Real Estate":             "PLD,AMT,EQIX,SPG,O,WELL",
    "Basic Materials":         "LIN,APD,NEM,FCX,DD,DOW",
}

SC_MAP = {
    "Technology":    {"sup":["TSM","ASML.AS","AMAT","LRCX","KLAC"],    "cust":["AAPL","MSFT","META","AMZN","GOOGL"],        "note":"Foundry Asian monopolies + US hyperscaler demand. AI capex is structural."},
    "Semiconductors":{"sup":["ASML.AS","AMAT","LRCX","KLAC","MPWR"],   "cust":["AAPL","NVDA","AMD","QCOM","AVGO"],          "note":"ASML EUV monopoly is non-replicable. AI accelerator demand through 2030."},
    "Healthcare":    {"sup":["TMO","DHR","Lonza","WuXi AppTec"],        "cust":["Hospitals","Insurers","Governments"],        "note":"Long R&D pipelines. CDMO critical. GLP-1 wave driving pharma capex."},
    "Energy":        {"sup":["SLB","HAL","BKR","CAT"],                  "cust":["Utilities","Refineries","Industry"],         "note":"Cyclical — oil price driven. Energy transition creating dual capex cycle."},
    "Industrials":   {"sup":["MMM","HON","PH","ETN"],                   "cust":["Aerospace","Auto","Construction","Defense"], "note":"B2B. Reshoring and defence spending are secular tailwinds."},
    "Consumer Defensive":{"sup":["ADM","BG","PKG","IFF"],              "cust":["WMT","COST","B2C"],                         "note":"Anticyclical. Premium pricing power; private-label pressure rising."},
    "Financials":    {"sup":["Bloomberg LP","LSEG","Fiserv"],           "cust":["Retail banks","Institutional","SME"],        "note":"Fintech eroding retail margins. Higher-for-longer rates = positive NIM."},
    "Utilities":     {"sup":["GEV","Siemens Energy","NEE"],             "cust":["Residential","Industry","Data centres"],     "note":"Regulated monopoly. AI data-centre power demand is generational catalyst."},
    "Basic Materials":{"sup":["Miners RM","Chemical producers"],        "cust":["Manufacturing","Auto","Pharma"],             "note":"Highly cyclical. China property deflation headwind. EV copper supercycle."},
    "Communication Services":{"sup":["ERIC","NOK","AKAM"],             "cust":["Advertisers","SME","Consumers"],             "note":"Digital ads + subscriptions. AI integration is next monetisation lever."},
    "Real Estate":   {"sup":["Builders","Property mgmt"],               "cust":["Tenants","Retail","Residential"],           "note":"Rate sensitive. Data-centre REITs outperform. 90% REIT payout requirement."},
    "Consumer Cyclical":{"sup":["OEM Asia","Raw materials"],            "cust":["Consumers","E-commerce","Retail"],          "note":"Correlated to consumer credit cycle. EV transition reshaping auto chains."},
}


# ══════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:1.0rem 0 0.6rem 0'>
      <div class='nav-title'>⚓ NAVY</div>
      <div class='nav-sub'>TERMINAL PRO · v6.1</div>
      <div class='nav-divider'></div>
    </div>""", unsafe_allow_html=True)

    MENU = [
        "Market Overview",
        "Watchlist",
        "Company Terminal",
        "Charts & Technical",
        "DCF Valuation",
        "Multi-Compare",
        "Portfolio Backtest",
        "Stock Screener",
        "Macro & FRED",
        "Options & Derivatives",
        "FX & Commodities",
        "Economic Calendar",
        "Dynamic Chart Engine",
    ]
    for label in MENU:
    active = st.session_state.page == label
    if st.button(
        f"{'▶' if active else '·'}  {label}",
        key=f"nav_{label}",
        use_container_width=True,
        type="primary" if active else "secondary",
    ):
        st.session_state.page = label
        st.rerun()

    st.markdown("""
    <div style='margin-top:1.5rem;padding:0 0.5rem'>
      <div style='height:1px;background:linear-gradient(90deg,transparent,#111,transparent);margin-bottom:0.6rem'></div>
      <div style='font-family:IBM Plex Mono,monospace;font-size:0.44rem;color:#0e1e2e;text-align:center;letter-spacing:0.14em;line-height:2'>
        FINVIZ · FRED · YFINANCE · AGGRID<br>
        NAVY TERMINAL PRO 
      </div>
    </div>""", unsafe_allow_html=True)

choice = st.session_state.page


# ══════════════════════════════════════════════════════════
#  SHARED HELPERS
# ══════════════════════════════════════════════════════════
def _source_badge(s: str) -> str:
    return f"<span class='src-badge'>{s}</span>"


def _get_terminal_data(ticker: str, force: bool = False) -> dict:
    """
    FIX #1 — Fluid UX: cache engine + info in session_state.
    Only re-fetches if ticker is new or force=True.
    """
    cache = st.session_state.terminal_data_cache
    if not force and ticker in cache:
        return cache[ticker]
    engine = UnifiedMarketDataEngine(ticker)
    inf    = engine.info()
    cache[ticker] = {"info": inf, "engine": engine}
    st.session_state.terminal_data_cache = cache
    return cache[ticker]


def _get_ohlcv(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """FIX #1 — Cache OHLCV per (ticker, period, interval) in session_state."""
    key = (ticker, period, interval)
    cache = st.session_state.chart_ohlcv_cache
    if key not in cache:
        cache[key] = yf_ohlcv(ticker, period=period, interval=interval)
        st.session_state.chart_ohlcv_cache = cache
    return cache[key]


def _get_close(ticker: str, period: str = "1y", start: str = None) -> pd.Series:
    return yf_close(ticker, period=period, start=start)


# ══════════════════════════════════════════════════════════
#  FIX #3 — DEEP FINANCIALS LABELS
#  Wrapper that ensures the Metric/index column is always
#  the first visible column before passing to navy_grid.
# ══════════════════════════════════════════════════════════
def _render_deep_fin_table(df_raw: pd.DataFrame, height: int = 400, key: str = "df_fin") -> None:
    """
    Safely renders a deep financials DataFrame via navy_grid,
    guaranteeing the 'Metric' label column is always visible.
    """
    if df_raw is None or df_raw.empty:
        interrupted("No financial data to display.")
        return
    df = df_raw.copy()
    # If index contains metric names, convert to explicit column
    if df.index.name or (not df.index.equals(pd.RangeIndex(len(df)))):
        df = df.reset_index()
        # Rename first column to 'Metric' if it's unnamed or has a boring name
        first_col = df.columns[0]
        if str(first_col).lower() in ("index", "0", "level_0", "") or first_col is None:
            df.rename(columns={first_col: "Metric"}, inplace=True)
    # If 'Metric' column is missing entirely, try to inject row labels
    if "Metric" not in df.columns:
        df.insert(0, "Metric", [f"Row {i+1}" for i in range(len(df))])
    navy_grid(df, height=height, key=key)


# ══════════════════════════════════════════════════════════
#  COMPANY TERMINAL
# ══════════════════════════════════════════════════════════
def show_terminal(ticker: str, peers_str: str = "SPY,QQQ,IWM", force_refresh: bool = False) -> None:
    # FIX #1: data comes from session_state cache — no re-download on tab switch
    cached = _get_terminal_data(ticker, force=force_refresh)
    engine = cached["engine"]
    inf    = cached["info"]

    if not inf:
        st.error(f"❌ No data for **{ticker}**. Examples: `AAPL` `NVDA` `ENI.MI` `ASML.AS` `BTC-USD`")
        return

    name   = inf.get("longName") or inf.get("shortName") or ticker
    price  = inf.get("currentPrice") or inf.get("regularMarketPrice") or inf.get("previousClose")
    prev   = inf.get("previousClose") or price
    chg    = (price - prev) / prev * 100 if (price and prev and prev != 0) else None
    sector = inf.get("sector", "N/A")
    cur    = inf.get("currency", "USD")
    hi52   = inf.get("fiftyTwoWeekHigh", "—")
    lo52   = inf.get("fiftyTwoWeekLow",  "—")
    vs_hi  = (price / hi52 - 1) * 100 if (price and hi52 and hi52 != "—") else None
    chg_col = "#00FF88" if (chg or 0) >= 0 else "#FF3B3B"
    chg_str = f"<span style='color:{chg_col};font-weight:700'>{chg:+.2f}%</span>" if chg is not None else ""

    st.markdown(f"""
    <div class='ticker-card'>
      <div style='display:flex;justify-content:space-between;align-items:flex-start'>
        <div>
          <div class='ticker-tag'>EQUITY · {inf.get('exchange','N/A')} · {cur} · {inf.get('quoteType','EQUITY')}
               {_source_badge(engine.data_source)}</div>
          <div class='ticker-name'>{name}</div>
          <div class='ticker-meta'>{ticker} &nbsp;·&nbsp; {sector} &nbsp;·&nbsp; {inf.get('industry','N/A')[:32]} &nbsp;·&nbsp; {inf.get('country','N/A')}</div>
          <div style='margin-top:6px;font-family:IBM Plex Mono,monospace;font-size:0.63rem;color:#3A6A9A'>
            52W Lo: <b style='color:#FF3B3B'>{lo52}</b> &nbsp;&nbsp;
            52W Hi: <b style='color:#00FF88'>{hi52}</b>
            {'&nbsp;&nbsp;vs Hi: <b style=color:#F5A623>' + f'{vs_hi:+.1f}%</b>' if vs_hi is not None else ''}
          </div>
        </div>
        <div style='text-align:right'>
          <div class='ticker-price'>{f"{price:,.2f}" if price else "N/A"} <span style='font-size:0.80rem;color:#3A6A9A'>{cur}</span></div>
          <div style='font-size:0.84rem;margin-top:3px'>{chg_str}</div>
          <div style='font-family:IBM Plex Mono,monospace;font-size:0.60rem;color:#3A6A9A;margin-top:4px'>
            Vol: {f"{inf.get('volume',0):,}" if inf.get('volume') else "—"} &nbsp;·&nbsp;
            Avg: {f"{inf.get('averageVolume',0):,}" if inf.get('averageVolume') else "—"}
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    kpis1 = [
        ("P/E Fwd",   f"{inf['forwardPE']:.1f}"                    if inf.get("forwardPE")            else "N/A"),
        ("P/E TTM",   f"{inf['trailingPE']:.1f}"                   if inf.get("trailingPE")           else "N/A"),
        ("EPS Fwd",   f"{inf['forwardEps']:.2f}"                   if inf.get("forwardEps")           else "N/A"),
        ("EPS TTM",   f"{inf.get('trailingEps'):.2f}"              if inf.get("trailingEps")          else "N/A"),
        ("P/B",       f"{inf['priceToBook']:.2f}"                  if inf.get("priceToBook")          else "N/A"),
        ("P/S",       f"{inf['priceToSalesTrailing12Months']:.2f}" if inf.get("priceToSalesTrailing12Months") else "N/A"),
        ("Beta",      f"{inf['beta']:.2f}"                         if inf.get("beta")                 else "N/A"),
        ("Mkt Cap",   fmt_bn(inf["marketCap"])                     if inf.get("marketCap")            else "N/A"),
    ]
    c8 = st.columns(8)
    for i, (lb, v) in enumerate(kpis1):
        c8[i].metric(lb, v)

    kpis2 = [
        ("EV/EBITDA",  f"{inf['enterpriseToEbitda']:.1f}"        if inf.get("enterpriseToEbitda")  else "N/A"),
        ("EV/Rev",     f"{inf['enterpriseToRevenue']:.2f}"       if inf.get("enterpriseToRevenue") else "N/A"),
        ("Div Yield",  f"{(inf.get('dividendYield') or 0)*100:.2f}%"),
        ("Payout",     f"{(inf.get('payoutRatio') or 0)*100:.1f}%"),
        ("ROE",        f"{inf.get('returnOnEquity',0)*100:.1f}%"  if inf.get("returnOnEquity")    else "N/A"),
        ("ROA",        f"{inf.get('returnOnAssets',0)*100:.1f}%"  if inf.get("returnOnAssets")    else "N/A"),
        ("Op Margin",  f"{inf.get('operatingMargins',0)*100:.1f}%"if inf.get("operatingMargins")  else "N/A"),
        ("Net Margin", f"{inf.get('profitMargins',0)*100:.1f}%"   if inf.get("profitMargins")     else "N/A"),
    ]
    c8b = st.columns(8)
    for i, (lb, v) in enumerate(kpis2):
        c8b[i].metric(lb, v)

    if st.button("🔄 Refresh Data", key=f"term_refresh_{ticker}"):
        st.session_state.terminal_data_cache.pop(ticker, None)
        st.rerun()

    st.markdown("---")

    t1, t2, t3, t4, t5, t6, t7 = st.tabs([
        "📋 Overview", "📊 Financials (Deep)", "📈 Performance",
        "👥 Peers", "🏦 Holders", "📰 News & Rec", "⛓️ Supply Chain",
    ])

    # ── Tab 1: Overview ────────────────────────────────────
    with t1:
        c1, c2 = st.columns([3, 2])
        with c1:
            sec("BUSINESS SUMMARY")
            st.write(inf.get("longBusinessSummary", "Description not available.")[:1600])
        with c2:
            sec("FINANCIAL HIGHLIGHTS")
            fl = [
                ("Revenue",    fmt_bn(inf.get("totalRevenue",  0))),
                ("EBITDA",     fmt_bn(inf.get("ebitda",        0))),
                ("FCF",        fmt_bn(inf.get("freeCashflow",  0))),
                ("Gross Mgn",  f"{inf.get('grossMargins',0)*100:.1f}%"    if inf.get("grossMargins")  else "N/A"),
                ("D/E",        f"{inf.get('debtToEquity',0)/100:.2f}"     if inf.get("debtToEquity")  else "N/A"),
                ("Cash",       fmt_bn(inf.get("totalCash",    0))),
                ("Total Debt", fmt_bn(inf.get("totalDebt",   0))),
                ("Employees",  f"{inf.get('fullTimeEmployees',0):,}"      if inf.get("fullTimeEmployees") else "N/A"),
            ]
            r1, r2 = st.columns(2)
            for i, (lb, v) in enumerate(fl):
                (r1 if i % 2 == 0 else r2).metric(lb, v)
            sec("GROWTH")
            g1, g2 = st.columns(2)
            g1.metric("Rev Growth",  f"{inf.get('revenueGrowth',0)*100:.1f}%"   if inf.get("revenueGrowth")  else "N/A")
            g2.metric("Earn Growth", f"{inf.get('earningsGrowth',0)*100:.1f}%"  if inf.get("earningsGrowth") else "N/A")
            g1.metric("Rev/Share",   str(inf.get("revenuePerShare", "N/A")))
            g2.metric("Book/Share",  f"{inf.get('bookValue','N/A')}")

    # ── Tab 2: Deep Financials — FIX #3 ───────────────────
    with t2:
        src_label = engine.data_source
        sec(f"DEEP FINANCIALS  {_source_badge(src_label)}")
        deep_key = f"deep_{ticker}"
        if deep_key not in st.session_state:
            if st.button("⬇ Load Deep Financials", key=f"load_deep_{ticker}"):
                with st.spinner(f"Fetching multi-decade data via {src_label}…"):
                    st.session_state[deep_key] = engine.deep_financials()
                st.rerun()
            else:
                st.info("Click **Load Deep Financials** to fetch income, balance, and cash flow data.")
                deep = None
        else:
            deep = st.session_state[deep_key]

        if deep:
            fin_labels = list(deep.keys())
            sel_metrics = st.multiselect(
                "Plot metrics", fin_labels,
                default=[l for l in ["Revenue","Net Income","Free Cash Flow","EBITDA"] if l in fin_labels][:4],
                key=f"fin_sel_{ticker}",
            )
            if sel_metrics:
                fig_fin = go.Figure()
                for idx, label_f in enumerate(sel_metrics):
                    s = deep[label_f]
                    if not s.empty:
                        fig_fin.add_trace(go.Scatter(
                            x=s.index, y=s.values, name=label_f, mode="lines+markers",
                            line=dict(width=2, color=COLORS[idx % len(COLORS)]),
                            marker=dict(size=5),
                        ))
                fig_fin.update_layout(**_pla({
                    "height": 360,
                    "title": f"{ticker} — {src_label} Multi-Decade Financials",
                    "xaxis": xaxis_time(), "yaxis": yaxis_plain("$ Value"),
                }))
                st.plotly_chart(fig_fin, use_container_width=True)

            # FIX #3: Use _render_deep_fin_table to guarantee Metric column
            sec("ANNUAL TABLE")
            rows_t: list[dict] = []
            for label_f, s in deep.items():
                if s.empty:
                    continue
                row = {"Metric": label_f}
                for d, v in s.tail(12).items():
                    row[str(d)[:4]] = fmt_bn(v)
                rows_t.append(row)
            if rows_t:
                df_tbl = pd.DataFrame(rows_t)
                # Metric is already a column here — pass directly, no set_index
                navy_grid(df_tbl, height=400, key=f"df_{ticker}")
        elif deep is not None:
            yf_fin = yf_financials(ticker)
            if yf_fin:
                mode_f = st.radio("Period:", ["Annual","Quarterly"], horizontal=True, key=f"fm_{ticker}")
                sfx    = "_a" if mode_f == "Annual" else "_q"
                tab_labels = ["Income","Balance","Cash Flow"]
                tab_keys   = ["income","balance","cashflow"]
                fin_tabs   = st.tabs(tab_labels)
                for tab_w, key_f in zip(fin_tabs, tab_keys):
                    with tab_w:
                        df_f = yf_fin.get(key_f + sfx, pd.DataFrame())
                        if not df_f.empty:
                            # FIX #3: ensure index (metric names) become a column
                            df_d = df_f.copy()
                            df_d.columns = [str(c)[:10] for c in df_d.columns]
                            for col in df_d.columns:
                                df_d[col] = df_d[col].apply(fmt_bn)
                            _render_deep_fin_table(df_d, height=400, key=f"{key_f}{sfx}{ticker}")
                        else:
                            interrupted("Financial data unavailable for this sheet.")
            else:
                interrupted("No financial data returned from any source.")

    # ── Tab 3: Performance ─────────────────────────────────
    with t3:
        p_map = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","2Y":"2y","5Y":"5y","10Y":"10y","MAX":"max"}
        p_lbl = st.select_slider("Period:", list(p_map.keys()), value="1Y", key=f"pp_{ticker}")
        s_d   = _get_close(ticker, period=p_map[p_lbl])
        if not s_d.empty:
            s_d_plot = _subsample(s_d)
            ret = ((s_d_plot / s_d_plot.iloc[0]) - 1) * 100
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(
                x=ret.index, y=ret, name=ticker,
                line=dict(width=2.5, color="#F5A623"),
                fill="tozeroy", fillcolor="rgba(245,166,35,0.05)",
            ))
            fig_p.add_hline(y=0, line_dash="dot", line_color="#141414")
            fig_p.update_layout(**_pla({"xaxis":xaxis_time(),"yaxis":yaxis_plain("Return %"),"height":340}))
            st.plotly_chart(fig_p, use_container_width=True)
            dr  = s_d.pct_change().dropna()
            ay  = max((s_d.index[-1] - s_d.index[0]).days / 365.25, 0.1)
            tr  = float(((s_d.iloc[-1] / s_d.iloc[0]) - 1) * 100)
            car = ((1 + tr / 100) ** (1 / ay) - 1) * 100
            vol = dr.std() * np.sqrt(252) * 100
            dd  = ((s_d / s_d.cummax()) - 1).min() * 100
            mc5 = st.columns(5)
            mc5[0].metric("Total Return", f"{tr:+.2f}%")
            mc5[1].metric("CAGR",         f"{car:+.2f}%")
            mc5[2].metric("Ann. Vol",     f"{vol:.2f}%")
            mc5[3].metric("Max DD",       f"{dd:.2f}%")
            mc5[4].metric("Sharpe",       f"{car/vol:.2f}" if vol > 0 else "N/A")
        else:
            interrupted(f"No price history for {ticker}")

    # ── Tab 4: Peers — FIX #4 ─────────────────────────────
    with t4:
        pk = f"peers_{ticker}"
        if pk not in st.session_state:
            st.session_state[pk] = peers_str
        p_in = st.text_input("Peers (comma separated)", value=st.session_state[pk], key=f"pi_{ticker}")
        st.session_state[pk] = p_in

        peer_cache_key = f"peer_table_{ticker}_{p_in}"
        if peer_cache_key not in st.session_state:
            p_list = [ticker] + [x.strip().upper() for x in p_in.split(",") if x.strip()]
            rows_p: list[dict] = []
            prg = st.progress(0)
            for ix, p in enumerate(p_list):
                prg.progress((ix + 1) / len(p_list))
                pi = yf_info(p)
                if not pi:
                    rows_p.append({"Ticker":p,"Name":"ERR",**{k:"ERR" for k in ["Price","P/E","P/B","P/S","EV/EBITDA","Beta","Cap$B","Div%","ROE%","OpMgn%","Rev$B","FCF$B"]}})
                    continue
                pr = pi.get("currentPrice") or pi.get("regularMarketPrice") or pi.get("previousClose") or 0
                # FIX #4: always include Ticker and Name as first columns
                rows_p.append({
                    "Ticker":    p,
                    "Name":      (pi.get("shortName") or p)[:22],
                    "Price":     f"{pr:,.2f}" if pr else "N/A",
                    "P/E":       f"{pi.get('forwardPE'):.1f}"                            if pi.get("forwardPE")                        else "N/A",
                    "P/B":       f"{pi.get('priceToBook'):.2f}"                          if pi.get("priceToBook")                      else "N/A",
                    "P/S":       f"{pi.get('priceToSalesTrailing12Months'):.2f}"         if pi.get("priceToSalesTrailing12Months")      else "N/A",
                    "EV/EBITDA": f"{pi.get('enterpriseToEbitda'):.1f}"                   if pi.get("enterpriseToEbitda")               else "N/A",
                    "Beta":      f"{pi.get('beta'):.2f}"                                 if pi.get("beta")                             else "N/A",
                    "Cap$B":     f"{pi.get('marketCap',0)/1e9:.1f}"                      if pi.get("marketCap")                        else "N/A",
                    "Div%":      f"{(pi.get('dividendYield') or 0)*100:.2f}%",
                    "ROE%":      f"{pi.get('returnOnEquity',0)*100:.1f}"                 if pi.get("returnOnEquity")                   else "N/A",
                    "OpMgn%":    f"{pi.get('operatingMargins',0)*100:.1f}"               if pi.get("operatingMargins")                 else "N/A",
                    "Rev$B":     f"{pi.get('totalRevenue',0)/1e9:.1f}"                   if pi.get("totalRevenue")                     else "N/A",
                    "FCF$B":     f"{pi.get('freeCashflow',0)/1e9:.1f}"                   if pi.get("freeCashflow")                     else "N/A",
                })
            prg.empty()
            st.session_state[peer_cache_key] = (p_list, rows_p)

        p_list, rows_p = st.session_state[peer_cache_key]
        if rows_p:
            # FIX #4: do NOT set_index to preserve Ticker column as visible
            navy_grid(pd.DataFrame(rows_p), height=300, key=f"ptbl_{ticker}")

        sec("RELATIVE PERFORMANCE 1Y")
        perf_cache_key = f"peer_perf_{ticker}_{p_in}"
        if perf_cache_key not in st.session_state:
            fr = {p: s for p in p_list for s in [_get_close(p, period="1y")] if not s.empty}
            if fr:
                pn = pd.DataFrame(fr).dropna(how="all").ffill()
                pn = ((pn / pn.iloc[0]) - 1) * 100
                st.session_state[perf_cache_key] = pn
            else:
                st.session_state[perf_cache_key] = pd.DataFrame()

        pn = st.session_state[perf_cache_key]
        if not pn.empty:
            fig_pr = go.Figure()
            for ix, col in enumerate(pn.columns):
                pn_sub = _subsample(pn[col])
                fig_pr.add_trace(go.Scatter(
                    x=pn_sub.index, y=pn_sub, name=col,
                    line=dict(width=2.8 if col == ticker else 1.5, color=COLORS[ix % len(COLORS)]),
                ))
            fig_pr.add_hline(y=0, line_dash="dot", line_color="#141414")
            fig_pr.update_layout(**_pla({"xaxis":xaxis_time(),"yaxis":yaxis_plain("Return %"),"height":320}))
            st.plotly_chart(fig_pr, use_container_width=True)

    # ── Tab 5: Holders ─────────────────────────────────────
    with t5:
        holders_key = f"holders_{ticker}"
        if holders_key not in st.session_state:
            st.session_state[holders_key] = yf_holders(ticker)
        ih = st.session_state[holders_key]
        if not ih.empty:
            sec("TOP INSTITUTIONAL HOLDERS")
            navy_grid(ih.head(15), height=320, key=f"ih_{ticker}")
        sec("OWNERSHIP SNAPSHOT")
        oi1, oi2, oi3, oi4 = st.columns(4)
        oi1.metric("Float %",      f"{inf.get('floatShares',0)/inf.get('sharesOutstanding',1)*100:.1f}%"  if inf.get("sharesOutstanding") else "N/A")
        oi2.metric("Inst. Held",   f"{inf.get('heldPercentInstitutions',0)*100:.1f}%"                     if inf.get("heldPercentInstitutions") else "N/A")
        oi3.metric("Insider Held", f"{inf.get('heldPercentInsiders',0)*100:.1f}%"                         if inf.get("heldPercentInsiders")     else "N/A")
        oi4.metric("Short Float",  f"{inf.get('shortPercentOfFloat',0)*100:.1f}%"                         if inf.get("shortPercentOfFloat")     else "N/A")

    # ── Tab 6: News & Rec ──────────────────────────────────
    with t6:
        cn, cr = st.columns([3, 2])
        with cn:
            sec("LATEST NEWS")
            try:
                news = yf.Ticker(ticker).news or []
                if not news:
                    interrupted("News feed not available.")
                for n in news[:8]:
                    title = n.get("title", ""); link = n.get("link", f"https://finance.yahoo.com/quote/{ticker}")
                    pub   = n.get("providerPublishTime", "")
                    if title:
                        try:    dt_str = datetime.fromtimestamp(pub).strftime("%d %b %H:%M") if pub else ""
                        except: dt_str = ""
                        st.markdown(
                            f"<div style='border-left:2px solid #111;padding-left:8px;margin-bottom:6px;font-size:0.74rem'>"
                            f"<a href='{link}' target='_blank' style='color:#B0C4D8;text-decoration:none'>{title[:95]}</a>"
                            f"<div style='font-size:0.57rem;color:#3A6A9A;margin-top:2px'>{dt_str}</div></div>",
                            unsafe_allow_html=True)
            except Exception:
                interrupted("News feed unavailable.")
        with cr:
            sec("ANALYST RECOMMENDATIONS")
            recs_key = f"recs_{ticker}"
            if recs_key not in st.session_state:
                st.session_state[recs_key] = yf_recommendations(ticker)
            recs = st.session_state[recs_key]
            if not recs.empty:
                try:
                    avail_cols = [c for c in ["Firm","To Grade","Action"] if c in recs.columns]
                    navy_grid(recs[avail_cols].head(10).reset_index(drop=True) if avail_cols else recs.head(10), height=200, key=f"rec_{ticker}")
                except Exception:
                    navy_grid(recs.head(10), height=200, key=f"rec2_{ticker}")
            rm = inf.get("recommendationMean")
            if rm:
                rl = {1:"Strong Buy",2:"Buy",3:"Hold",4:"Sell",5:"Strong Sell"}.get(round(rm),"N/A")
                st.metric("Consensus", f"{rl} ({rm:.2f})")
                st.metric("# Analysts", str(inf.get("numberOfAnalystOpinions","N/A")))
                if inf.get("targetMeanPrice") and price:
                    st.metric("Target",  f"${inf['targetMeanPrice']:.2f}")
                    st.metric("Upside", f"{(inf['targetMeanPrice']/price-1)*100:.1f}%")

    # ── Tab 7: Supply Chain ────────────────────────────────
    with t7:
        sc = SC_MAP.get(sector)
        if sc:
            s1, s2, s3 = st.columns(3)
            with s1:
                sec("🔼 KEY SUPPLIERS")
                for s_item in sc["sup"]:
                    st.markdown(f"<div style='font-size:0.78rem;color:#B0C4D8;padding:2px 0'>· {s_item}</div>", unsafe_allow_html=True)
            with s2:
                sec("🔽 KEY CUSTOMERS")
                for c_item in sc["cust"]:
                    st.markdown(f"<div style='font-size:0.78rem;color:#B0C4D8;padding:2px 0'>· {c_item}</div>", unsafe_allow_html=True)
            with s3:
                sec("💡 SECTOR NOTE")
                st.markdown(f"<div class='term-box'>{sc['note']}</div>", unsafe_allow_html=True)
        else:
            st.info("Supply chain map not available for this sector.")
        sec("METADATA")
        sm1, sm2, sm3, sm4 = st.columns(4)
        sm1.metric("Sector",   sector)
        sm2.metric("Industry", inf.get("industry","N/A")[:24])
        sm3.metric("Country",  inf.get("country","N/A"))
        sm4.metric("Exchange", inf.get("exchange","N/A"))


# ══════════════════════════════════════════════════════════
#  PAGE: MARKET OVERVIEW
# ══════════════════════════════════════════════════════════
if choice == "Market Overview":
    ptitle("GLOBAL MARKET OVERVIEW","Real-time snapshot · Indices · Rates · FX · Commodities · Movers")

    col_ref, col_ts = st.columns([1, 5])
    with col_ref:
        refresh_mkt = st.button("🔄 Refresh", key="mkt_refresh")
    with col_ts:
        if st.session_state.market_last_refresh:
            st.caption(f"Last refresh: {st.session_state.market_last_refresh.strftime('%H:%M:%S')}")

    if st.session_state.market_data is None or refresh_mkt:
        INDICES = {
            "S&P 500":"^GSPC","Nasdaq 100":"^IXIC","Dow Jones":"^DJI","Russell 2000":"^RUT",
            "VIX":"^VIX","Nikkei 225":"^N225","FTSE MIB":"FTSEMIB.MI","DAX 40":"^GDAXI",
            "CAC 40":"^FCHI","STOXX 50":"^STOXX50E","Hang Seng":"^HSI","MSCI EM":"EEM",
        }
        BONDS  = {"10Y Yield":"^TNX","30Y Yield":"^TYX","5Y Yield":"^FVX","2Y Yield":"^IRX","MOVE":"^MOVE"}
        FX     = {"EUR/USD":"EURUSD=X","GBP/USD":"GBPUSD=X","USD/JPY":"USDJPY=X","USD/CHF":"USDCHF=X","AUD/USD":"AUDUSD=X","DXY":"DX-Y.NYB"}
        COMMS  = {"Gold":"GC=F","Silver":"SI=F","Crude WTI":"CL=F","Brent":"BZ=F","Nat Gas":"NG=F","Copper":"HG=F"}
        STOCKS = {
            "Apple":"AAPL","Microsoft":"MSFT","NVIDIA":"NVDA","Alphabet":"GOOGL",
            "Tesla":"TSLA","Amazon":"AMZN","Meta":"META","ASML":"ASML.AS",
            "SAP":"SAP.DE","ENI":"ENI.MI","LVMH":"MC.PA","Ferrari":"RACE.MI",
            "Berkshire":"BRK-B","JPMorgan":"JPM","TSMC":"TSM","ARM":"ARM",
        }
        WATCH = ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","JPM","V",
                 "AMD","INTC","PANW","ADBE","CRM","SNOW","PLTR","COIN","NFLX","DIS",
                 "BAC","WFC","GS","COST","WMT","NKE","MCD","BA","CAT","GE",
                 "SMCI","ARM","ENPH","MRNA","PFE","GILD",
                 "ENI.MI","ENEL.MI","RACE.MI","MC.PA","TTE.PA","SAP.DE","ASML.AS",
                 "BTC-USD","ETH-USD","SOL-USD","GC=F","CL=F"]
        with st.spinner("Fetching market snapshot…"):
            idx_data  = {n: yf_price_chg(t) for n, t in INDICES.items()}
            bond_data = {n: yf_price_chg(t) for n, t in BONDS.items()}
            fx_data   = {n: yf_price_chg(t) for n, t in FX.items()}
            comm_data = {n: yf_price_chg(t) for n, t in COMMS.items()}
            stock_data = {}
            for nm, tk in STOCKS.items():
                stock_data[nm] = (tk, *yf_price_chg(tk))
            mv: list[dict] = []
            prg_mv = st.progress(0)
            for i, tk in enumerate(WATCH):
                prg_mv.progress((i + 1) / len(WATCH))
                p, c = yf_price_chg(tk)
                if p is not None and c is not None:
                    mv.append({"Ticker": tk, "Price": p, "Change%": c})
            prg_mv.empty()
        st.session_state.market_data = {
            "indices": idx_data, "bonds": bond_data,
            "fx": fx_data, "comms": comm_data,
            "stocks": stock_data, "movers": mv,
            "INDICES": INDICES, "BONDS": BONDS,
            "FX": FX, "COMMS": COMMS, "STOCKS": STOCKS,
        }
        st.session_state.market_last_refresh = datetime.now()

    md = st.session_state.market_data

    sec("GLOBAL INDICES")
    ic = st.columns(4)
    for i, (name, tkr) in enumerate(md["INDICES"].items()):
        p, c = md["indices"].get(name, (None, None))
        ic[i % 4].metric(name, f"{p:,.2f}" if p else "N/A", f"{c:+.2f}%" if c else "—")

    st.markdown("---")
    sec("RATES & FIXED INCOME")
    bc = st.columns(5)
    for i, (nm, _) in enumerate(md["BONDS"].items()):
        p, c = md["bonds"].get(nm, (None, None))
        bc[i].metric(nm, f"{p:.3f}" if p else "N/A", f"{c:+.3f}%" if c else "—")

    st.markdown("---")
    cfx, ccm = st.columns(2)
    with cfx:
        sec("FOREIGN EXCHANGE")
        fc = st.columns(3)
        for i, nm in enumerate(md["FX"]):
            p, c = md["fx"].get(nm, (None, None))
            fc[i % 3].metric(nm, f"{p:.4f}" if p else "N/A", f"{c:+.2f}%" if c else "—")
    with ccm:
        sec("COMMODITIES")
        cc = st.columns(3)
        for i, nm in enumerate(md["COMMS"]):
            p, c = md["comms"].get(nm, (None, None))
            cc[i % 3].metric(nm, f"{p:,.2f}" if p else "N/A", f"{c:+.2f}%" if c else "—")

    st.markdown("---")
    sec("KEY EQUITIES")
    sk = st.columns(4)
    for i, (nm, vals) in enumerate(md["stocks"].items()):
        tk, p, c = vals
        sk[i % 4].metric(f"{nm} ({tk})", f"{p:,.2f}" if p else "N/A", f"{c:+.2f}%" if c else "—")

    st.markdown("---")
    sec("TOP MOVERS — LAST SNAPSHOT")
    mv = md["movers"]
    mv.sort(key=lambda x: x["Change%"], reverse=True)
    cg, cl = st.columns(2)
    for col_w, data, color, label in [
        (cg, mv[:7],                                         "#00FF88", "🟢 TOP GAINERS"),
        (cl, sorted(mv, key=lambda x: x["Change%"])[:7],    "#FF3B3B", "🔴 TOP LOSERS"),
    ]:
        with col_w:
            st.markdown(f"<div class='sec-hdr' style='color:{color}'>{label}</div>", unsafe_allow_html=True)
            for m in data:
                st.markdown(f"""
                <div class='mover-card' style='border-left:3px solid {color}'>
                  <div>
                    <div style='font-family:IBM Plex Mono,monospace;font-size:0.84rem;color:#E2E8F0;font-weight:700'>{m['Ticker']}</div>
                    <div style='font-size:0.62rem;color:#3A6A9A'>${m['Price']:,.3f}</div>
                  </div>
                  <div style='font-family:IBM Plex Mono,monospace;font-size:0.95rem;color:{color};font-weight:700'>{m['Change%']:+.2f}%</div>
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  PAGE: WATCHLIST
# ══════════════════════════════════════════════════════════
elif choice == "Watchlist":
    ptitle("WATCHLIST","Personal tracker · Real-time prices · Comparative performance · Correlation")

    wl_input = st.text_input("Add tickers (comma separated)", "", placeholder="NVDA, ASML.AS, ENI.MI, BTC-USD …")
    if wl_input.strip():
        new = [x.strip().upper() for x in wl_input.split(",") if x.strip()]
        before = len(st.session_state.watchlist)
        st.session_state.watchlist = list(dict.fromkeys(st.session_state.watchlist + new))
        if len(st.session_state.watchlist) > before:
            st.rerun()

    wl = st.session_state.watchlist
    if not wl:
        st.info("Watchlist is empty. Add tickers above.")
    else:
        with st.form("wl_rm"):
            rem = st.multiselect("Remove from watchlist", wl)
            if st.form_submit_button("Remove selected") and rem:
                st.session_state.watchlist = [t for t in wl if t not in rem]
                st.session_state.watchlist_data = {}
                st.rerun()

        refresh_wl = st.button("🔄 Refresh Prices", key="wl_refresh")
        wl_key = ",".join(sorted(wl))
        if not st.session_state.watchlist_data or \
           st.session_state.watchlist_data.get("__key__") != wl_key or \
           refresh_wl:
            rows_wl: list[dict] = []
            prg_wl = st.progress(0)
            for i, tkr in enumerate(wl):
                prg_wl.progress((i + 1) / len(wl))
                inf_wl = yf_info(tkr)
                p, c   = yf_price_chg(tkr)
                if inf_wl:
                    rows_wl.append({
                        "Ticker":  tkr,
                        "Name":    (inf_wl.get("shortName") or tkr)[:28],
                        "Price":   f"{p:,.4f}" if p else "N/A",
                        "Chg %":   f"{c:+.2f}%" if c else "—",
                        "52W Lo":  str(inf_wl.get("fiftyTwoWeekLow",  "—")),
                        "52W Hi":  str(inf_wl.get("fiftyTwoWeekHigh", "—")),
                        "P/E":     f"{inf_wl['forwardPE']:.1f}"   if inf_wl.get("forwardPE")   else "N/A",
                        "Cap$B":   f"{inf_wl.get('marketCap',0)/1e9:.1f}" if inf_wl.get("marketCap") else "N/A",
                        "Beta":    f"{inf_wl['beta']:.2f}"        if inf_wl.get("beta")        else "N/A",
                        "Div%":    f"{(inf_wl.get('dividendYield') or 0)*100:.2f}%",
                        "Sector":  (inf_wl.get("sector") or "")[:18],
                    })
            prg_wl.empty()
            st.session_state.watchlist_data = {"__key__": wl_key, "rows": rows_wl}
            st.session_state.watchlist_last_refresh = datetime.now()

        rows_wl = st.session_state.watchlist_data.get("rows", [])
        if st.session_state.watchlist_last_refresh:
            st.caption(f"Last refresh: {st.session_state.watchlist_last_refresh.strftime('%H:%M:%S')}")

        sec("REAL-TIME PRICES")
        if rows_wl:
            navy_grid(pd.DataFrame(rows_wl), height=min(40 + len(rows_wl)*28, 480), key="wl_grid")

        sec("COMPARATIVE PERFORMANCE")
        h_opts = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","3Y":"3y","5Y":"5y","10Y":"10y","MAX":"max"}
        h_lbl  = st.selectbox("Horizon", list(h_opts.keys()), index=3)
        fr = {tk: s for tk in wl for s in [_get_close(tk, period=h_opts[h_lbl])] if not s.empty}
        if fr:
            d = pd.DataFrame(fr).dropna(how="all").ffill()
            r = ((d / d.iloc[0]) - 1) * 100
            fig_wl = go.Figure()
            for ix, col in enumerate(r.columns):
                r_sub = _subsample(r[col])
                fig_wl.add_trace(go.Scatter(x=r_sub.index, y=r_sub, name=f"{col} ({r[col].iloc[-1]:+.1f}%)", line=dict(width=2, color=COLORS[ix % len(COLORS)])))
            fig_wl.add_hline(y=0, line_dash="dot", line_color="#141414")
            fig_wl.update_layout(**_pla({"xaxis":xaxis_time(),"yaxis":yaxis_plain("Return %"),"height":420,"title":f"Watchlist Performance — {h_lbl}"}))
            st.plotly_chart(fig_wl, use_container_width=True)
            if len(fr) >= 2:
                sec("CORRELATION MATRIX")
                corr = d.pct_change().dropna().corr()
                fig_co = go.Figure(go.Heatmap(
                    z=corr.values, x=corr.columns.tolist(), y=corr.index.tolist(),
                    colorscale=[[0,"#FF3B3B"],[0.5,"#050505"],[1,"#00FF88"]],
                    zmid=0, zmin=-1, zmax=1,
                    text=corr.round(2).values, texttemplate="%{text}",
                ))
                fig_co.update_layout(**_pla({"height":320,"title":"Return Correlation"}))
                st.plotly_chart(fig_co, use_container_width=True)

        sec("OPEN IN TERMINAL")
        sel_wl = st.selectbox("Select ticker", wl)
        if st.button("⌨  OPEN COMPANY TERMINAL", use_container_width=True):
            st.session_state.page = "Company Terminal"
            st.session_state.terminal_ticker = sel_wl
            st.rerun()


# ══════════════════════════════════════════════════════════
#  PAGE: COMPANY TERMINAL
# ══════════════════════════════════════════════════════════
elif choice == "Company Terminal":
    ptitle("COMPANY TERMINAL","Fundamental · Deep Financials · Technical · Peers · Supply Chain · News")
    ci, cb = st.columns([5, 1])
    with ci:
        new_t = st.text_input("Ticker", value=st.session_state.terminal_ticker,
                              placeholder="AAPL · NVDA · ENI.MI · ASML.AS · BTC-USD …").strip().upper()
    with cb:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        go_btn = st.button("▶ GO", use_container_width=True)
    if new_t:
        if new_t != st.session_state.terminal_ticker or go_btn:
            st.session_state.terminal_ticker = new_t
            inf_tmp = yf_info(new_t)
            sec_tmp = inf_tmp.get("sector","") if inf_tmp else ""
            st.session_state.terminal_peers = SECTOR_PEERS.get(sec_tmp, "SPY,QQQ,IWM,GLD")
        show_terminal(st.session_state.terminal_ticker, st.session_state.terminal_peers)


# ══════════════════════════════════════════════════════════
#  PAGE: CHARTS & TECHNICAL
# ══════════════════════════════════════════════════════════
elif choice == "Charts & Technical":
    ptitle("CHARTS & TECHNICAL ANALYSIS","Candlestick · Ichimoku Cloud · Bollinger · MACD · RSI · Fibonacci · Stochastic")

    ct1, ct2, ct3 = st.columns([3, 2, 2])
    with ct1: chart_tkr = st.text_input("Ticker","NVDA", key="chart_tkr")
    with ct2: chart_per = st.selectbox("Period",["1mo","3mo","6mo","1y","2y","5y","10y","max"],index=3,key="chart_per")
    with ct3: chart_int = st.selectbox("Interval",["1d","1wk","1mo"],index=0,key="chart_int")

    ALL_INDS = ["SMA 20","SMA 50","SMA 200","EMA 20","EMA 50","Bollinger Bands","VWAP",
                "Ichimoku","Fibonacci","MACD","RSI","Stochastic","Williams %R","CCI","OBV"]
    sel_ind = st.multiselect("Indicators", ALL_INDS, default=["SMA 20","SMA 50","Bollinger Bands","MACD","RSI"])

    if chart_tkr.strip():
        tkr_c = chart_tkr.strip().upper()
        df_c  = _get_ohlcv(tkr_c, period=chart_per, interval=chart_int)
        if not df_c.empty:
            df_c_plot = _subsample_df(df_c)
            fig_c = build_candle_chart(tkr_c, df_c_plot, sel_ind, f"{chart_per} · {chart_int}")
            st.plotly_chart(fig_c, use_container_width=True)
            sec("PRICE STATISTICS")
            dr_c     = df_c["Close"].pct_change().dropna()
            rsi_val  = rsi(df_c["Close"]).iloc[-1] if len(df_c) > 14 else None
            atr_val  = atr(df_c).iloc[-1]          if len(df_c) > 14 else None
            ps = st.columns(8)
            ps[0].metric("Close",    f"{df_c['Close'].iloc[-1]:,.2f}")
            ps[1].metric("Open",     f"{df_c['Open'].iloc[-1]:,.2f}")
            ps[2].metric("High",     f"{df_c['High'].iloc[-1]:,.2f}")
            ps[3].metric("Low",      f"{df_c['Low'].iloc[-1]:,.2f}")
            ps[4].metric("Volume",   f"{df_c['Volume'].iloc[-1]:,.0f}" if "Volume" in df_c.columns else "—")
            ps[5].metric("Ann. Vol", f"{dr_c.std()*np.sqrt(252)*100:.1f}%")
            ps[6].metric("ATR(14)",  f"{atr_val:,.2f}" if atr_val else "—")
            ps[7].metric("RSI(14)",  f"{rsi_val:.1f}"  if rsi_val else "—")
            sec("FIBONACCI RETRACEMENT LEVELS")
            fib_levels = fibonacci(df_c)
            fc7 = st.columns(7)
            for i, (lbl, val) in enumerate(fib_levels.items()):
                fc7[i % 7].metric(f"Fib {lbl}", f"{val:,.2f}")
        else:
            st.warning(f"No data for **{tkr_c}**.")


# ══════════════════════════════════════════════════════════
#  PAGE: DCF VALUATION ENGINE
# ══════════════════════════════════════════════════════════
elif choice == "DCF Valuation":
    ptitle("DCF VALUATION ENGINE","WACC/CAPM · Multi-Stage · Sensitivity · Reverse DCF · Monte Carlo 1000×")

    mode_dcf = st.radio("Mode:", ["Manual DCF","Auto-fill from Ticker","WACC Builder","Reverse DCF","Monte Carlo"], horizontal=True)
    st.markdown("---")

    if mode_dcf in ("Manual DCF","Auto-fill from Ticker"):
        af_fcf, af_shr, af_nd, af_eg = 1_000_000_000, 1_000_000_000, 0, 0.10
        af_price = None

        if mode_dcf == "Auto-fill from Ticker":
            af_tkr = st.text_input("Ticker", "AAPL", key="af_tkr")
            if af_tkr.strip():
                cached_af = _get_terminal_data(af_tkr.strip().upper())
                af_inf = cached_af["info"]
                if af_inf:
                    af_fcf   = af_inf.get("freeCashflow",     1_000_000_000) or 1_000_000_000
                    af_shr   = af_inf.get("sharesOutstanding",1_000_000_000) or 1_000_000_000
                    af_nd    = (af_inf.get("totalDebt",0) or 0) - (af_inf.get("totalCash",0) or 0)
                    af_eg    = min(max((af_inf.get("earningsGrowth",0.10) or 0.10), 0.01), 0.60)
                    af_price = af_inf.get("currentPrice") or af_inf.get("regularMarketPrice")
                    af_beta  = af_inf.get("beta",1.2) or 1.2
                    af_mc    = af_inf.get("marketCap",10_000_000_000) or 10_000_000_000
                    af_debt  = af_inf.get("totalDebt",0) or 0
                    wacc_preview = compute_wacc(WACCInputs(
                        equity_value=af_mc, debt_value=af_debt, beta=af_beta,
                        risk_free_rate=0.042, market_risk_premium=0.055, tax_rate=0.21, cost_of_debt=0.045,
                    ))
                    st.info(
                        f"📊 Auto-WACC (CAPM): **{wacc_preview['wacc']*100:.2f}%** · "
                        f"Ke: **{wacc_preview['cost_of_equity']*100:.2f}%** · "
                        f"β: **{af_beta:.2f}** · We: **{wacc_preview['weight_equity']*100:.1f}%**"
                    )

        c1, c2 = st.columns(2)
        with c1:
            sec("DCF INPUTS")
            fcf  = st.number_input("Base FCF ($)",        value=int(af_fcf), step=50_000_000,  format="%d")
            g1   = st.slider("Stage 1 Growth (%)",        1, 60, int(af_eg*100))
            g2   = st.slider("Stage 2 Growth (%)",        1, 40, max(int(af_eg*60),1))
            wacc = st.slider("WACC (%)",                  4, 22, 9)
            tg   = st.slider("Terminal Growth (%)",       0,  5, 2)
            n1   = st.slider("Stage 1 Years",             1, 10, 5)
            n2   = st.slider("Stage 2 Years",             1, 10, 5)
            shr  = st.number_input("Shares Outstanding",  value=int(af_shr), step=10_000_000,  format="%d")
            nd   = st.number_input("Net Debt ($)",        value=int(af_nd),  step=100_000_000, format="%d")
            tv_m = st.selectbox("Terminal Value Method",  ["gordon","exit_multiple"])
            ex_m, last_eb = 12.0, 0
            if tv_m == "exit_multiple":
                ex_m    = st.slider("Exit EV/EBITDA Multiple", 5.0, 30.0, 12.0)
                last_eb = st.number_input("Last EBITDA ($)", value=0, step=100_000_000, format="%d")

        dcf_inp = DCFInputs(
            base_fcf=float(fcf), wacc=wacc/100, g1=g1/100, g2=g2/100, tg=tg/100,
            n1=n1, n2=n2, shares=float(shr), net_debt=float(nd),
            tv_method=tv_m, exit_multiple=ex_m, last_ebitda=float(last_eb),
        )

        dcf_hash = hashlib.md5(json.dumps({
            "fcf":fcf,"g1":g1,"g2":g2,"wacc":wacc,"tg":tg,
            "n1":n1,"n2":n2,"shr":str(shr),"nd":str(nd),"tv_m":tv_m,"ex_m":ex_m,"last_eb":str(last_eb)
        }, sort_keys=True).encode()).hexdigest()

        with c2:
            sec("VALUATION RESULTS")
            if wacc/100 > tg/100:
                if dcf_hash not in st.session_state.dcf_result_cache:
                    st.session_state.dcf_result_cache[dcf_hash] = run_dcf(dcf_inp)
                res = st.session_state.dcf_result_cache[dcf_hash]

                r1,r2 = st.columns(2)
                r1.metric("Enterprise Value",   fmt_bn(res.ev))
                r2.metric("Equity Value",       fmt_bn(res.equity_value))
                r3,r4 = st.columns(2)
                r3.metric("Fair Value/Share",   f"${res.fair_value:,.2f}")
                r4.metric("TV % of EV",         f"{res.tv_pct:.1f}%")
                r5,r6 = st.columns(2)
                r5.metric("PV FCF (all stages)",fmt_bn(res.pv_s1 + res.pv_s2))
                r6.metric("PV Terminal Value",  fmt_bn(res.pv_tv))
                if af_price and mode_dcf == "Auto-fill from Ticker":
                    margin = (res.fair_value / af_price - 1) * 100
                    mc1, mc2 = st.columns(2)
                    mc1.metric("Current Price",    f"${af_price:,.2f}")
                    mc2.metric("Margin of Safety", f"{margin:+.1f}%")
                all_cfs   = res.fcfs_s1 + res.fcfs_s2
                yr_labels = [f"Y{i+1}" for i in range(len(all_cfs))]
                bar_cols  = (["#F5A623"] * n1) + (["#3B8EF0"] * n2)
                fig_dcf   = go.Figure()
                fig_dcf.add_trace(go.Bar(x=yr_labels, y=[v/1e6 for v in all_cfs],
                                         name="Projected FCF", marker_color=bar_cols, opacity=0.85))
                fig_dcf.update_layout(**_pla({"yaxis":yaxis_plain("$ Millions"),"height":260,"title":"FCF Projection (Amber=Stage1 · Blue=Stage2)"}))
                st.plotly_chart(fig_dcf, use_container_width=True)
            else:
                st.error("WACC must be > Terminal Growth rate.")

        st.markdown("---")
        sec("SENSITIVITY TABLE — Fair Value vs WACC × Growth")
        w_range = [wacc/100 + d for d in (-0.03,-0.015,0,0.015,0.03)]
        g_range = [g1/100  + d for d in (-0.03,-0.015,0,0.015,0.03)]
        navy_grid(dcf_sensitivity(dcf_inp, w_range, g_range), height=200, key="dcf_sens")

    elif mode_dcf == "WACC Builder":
        sec("CAPM WACC CALCULATOR")
        w1, w2 = st.columns(2)
        with w1:
            tkr_w    = st.text_input("Ticker (auto-fill)", "AAPL", key="wacc_tkr")
            inf_w    = yf_info(tkr_w.strip().upper()) if tkr_w.strip() else {}
            mc_val   = st.number_input("Market Cap ($)", value=int(inf_w.get("marketCap",1e12) or 1e12), step=int(1e9), format="%d")
            dbt_val  = st.number_input("Total Debt ($)",  value=int(inf_w.get("totalDebt",0)   or 0),    step=int(1e8), format="%d")
            beta_w   = st.slider("Beta", 0.1, 3.5, float(inf_w.get("beta",1.2) or 1.2), step=0.05)
        with w2:
            rf_w  = st.slider("Risk-Free Rate (%)",       1.0,  8.0, 4.2, step=0.1)
            erp_w = st.slider("Equity Risk Premium (%)",  2.0,  8.0, 5.5, step=0.1)
            kd_w  = st.slider("Pre-tax Cost of Debt (%)", 1.0, 12.0, 4.5, step=0.1)
            tax_w = st.slider("Effective Tax Rate (%)",   5.0, 35.0, 21.0,step=0.5)
        wres = compute_wacc(WACCInputs(
            equity_value=float(mc_val), debt_value=float(dbt_val),
            beta=beta_w, risk_free_rate=rf_w/100, market_risk_premium=erp_w/100,
            tax_rate=tax_w/100, cost_of_debt=kd_w/100,
        ))
        rw1,rw2,rw3,rw4 = st.columns(4)
        rw1.metric("WACC",           f"{wres['wacc']*100:.3f}%")
        rw2.metric("Cost of Equity", f"{wres['cost_of_equity']*100:.3f}%")
        rw3.metric("After-tax Kd",   f"{wres['after_tax_kd']*100:.3f}%")
        rw4.metric("Equity Weight",  f"{wres['weight_equity']*100:.1f}%")
        st.markdown(f"""<div class='term-box'>
        <b>CAPM:</b> Ke = Rf + β × ERP = {rf_w:.2f}% + {beta_w:.2f} × {erp_w:.2f}% = <b style='color:#F5A623'>{wres['cost_of_equity']*100:.3f}%</b><br>
        <b>WACC:</b> (Ke×We) + (Kd×(1−t)×Wd) = <b style='color:#F5A623'>{wres['wacc']*100:.3f}%</b>
        </div>""", unsafe_allow_html=True)

    elif mode_dcf == "Reverse DCF":
        sec("REVERSE DCF — IMPLIED GROWTH RATE")
        rev_tkr = st.text_input("Ticker", "AAPL", key="rev_tkr")
        if rev_tkr.strip():
            cached_rev = _get_terminal_data(rev_tkr.strip().upper())
            ri = cached_rev["info"]
            if ri:
                mkt_cap = ri.get("marketCap",0) or 0
                nd_r    = (ri.get("totalDebt",0) or 0) - (ri.get("totalCash",0) or 0)
                mkt_ev  = mkt_cap + nd_r
                fcf_r   = ri.get("freeCashflow",0) or 0
                wacc_r  = st.slider("WACC (%)", 4,20,9, key="rev_wacc") / 100
                tg_r    = st.slider("Terminal Growth (%)", 0, 5, 2, key="rev_tg") / 100
                n1_r    = st.slider("Stage 1 Years", 3,10,5, key="rev_n1")
                n2_r    = st.slider("Stage 2 Years", 3,10,5, key="rev_n2")
                rm1,rm2,rm3 = st.columns(3)
                rm1.metric("Market Cap",       fmt_bn(mkt_cap))
                rm2.metric("FCF (TTM)",        fmt_bn(fcf_r))
                rm3.metric("Enterprise Value", fmt_bn(mkt_ev))
                if fcf_r > 0 and mkt_ev > 0:
                    imp_g = reverse_dcf(float(mkt_ev), float(fcf_r), wacc_r, tg_r, n1_r, n2_r)
                    if imp_g is not None:
                        col = "#00FF88" if imp_g < 0.20 else ("#F5A623" if imp_g < 0.40 else "#FF3B3B")
                        alert(
                            f"📊 <b>Implied FCF Growth: <span style='color:{col}'>{imp_g*100:+.2f}% p.a.</span></b><br>"
                            f"The market prices in {imp_g*100:.1f}% annual FCF growth over {n1_r+n2_r} years "
                            f"to justify EV = {fmt_bn(mkt_ev)} at WACC={wacc_r*100:.1f}%, TG={tg_r*100:.1f}%.",
                            color=col,
                        )
                    else:
                        st.warning("Could not solve — adjust WACC / growth bounds.")
                else:
                    st.warning("FCF and Enterprise Value must be positive.")

    else:
        sec("MONTE CARLO SIMULATION — 1000× DCF DISTRIBUTION")
        st.info("⚡ Monte Carlo runs on-demand only. Configure inputs then click **Run**.")

        mc_fcf = st.number_input("Base FCF ($)", value=1_000_000_000, step=50_000_000, format="%d", key="mc_fcf")
        mc1,mc2,mc3 = st.columns(3)
        with mc1:
            g_mu  = st.slider("Growth μ (%)", 1,40,10,key="mc_gmu")
            g_std = st.slider("Growth σ (%)", 1,20, 5,key="mc_gstd")
        with mc2:
            w_mu  = st.slider("WACC μ (%)",  5,18, 9,key="mc_wmu")
            w_std = st.slider("WACC σ (%)",  1, 5, 1,key="mc_wstd")
        with mc3:
            mc_n1  = st.slider("Stage 1 Years",   3,10,5,key="mc_n1")
            mc_n2  = st.slider("Stage 2 Years",   3,10,5,key="mc_n2")
            mc_tg  = st.slider("Terminal Gr (%)", 0, 5,2,key="mc_tg") / 100
            mc_n   = st.select_slider("Simulations",[500,1000,5000,10000],value=1000,key="mc_n")
        mc_shr = st.number_input("Shares",   value=1_000_000_000, step=10_000_000,  format="%d",key="mc_shr")
        mc_nd  = st.number_input("Net Debt", value=0,             step=100_000_000, format="%d",key="mc_nd")

        mc_run_key = f"{mc_fcf}_{g_mu}_{g_std}_{w_mu}_{w_std}_{mc_n1}_{mc_n2}_{mc_tg}_{mc_n}_{mc_shr}_{mc_nd}"

        if st.button("▶ RUN MONTE CARLO", use_container_width=True):
            st.session_state["mc_run_key_last"] = mc_run_key
            with st.spinner(f"Running {mc_n:,} DCF simulations…"):
                fvs = monte_carlo_dcf(
                    base_fcf=float(mc_fcf), shares=float(mc_shr), net_debt=float(mc_nd),
                    n1=mc_n1, n2=mc_n2, tg=mc_tg,
                    wacc_mu=w_mu/100, wacc_sigma=w_std/100,
                    g_mu=g_mu/100,    g_sigma=g_std/100,
                    n_sim=mc_n,
                )
            st.session_state["mc_fvs"] = fvs

        if "mc_fvs" in st.session_state and st.session_state.get("mc_run_key_last") == mc_run_key:
            fvs = st.session_state["mc_fvs"]
            if len(fvs) > 10:
                fig_mc = go.Figure()
                fig_mc.add_trace(go.Histogram(x=fvs, nbinsx=80, marker_color="#F5A623", opacity=0.82, name="Fair Value"))
                for pct, col, lbl in [(5,"#FF3B3B","P5"),(25,"#F39C12","P25"),(50,"#E2E8F0","Median"),(75,"#00FF88","P75"),(95,"#00D4FF","P95")]:
                    v = np.percentile(fvs, pct)
                    fig_mc.add_vline(x=v, line_dash="dash", line_color=col,
                                     annotation_text=f"{lbl}: ${v:,.0f}", annotation_font_color=col, annotation_font_size=9)
                fig_mc.update_layout(**_pla({
                    "height": 360,
                    "title": f"Monte Carlo DCF — {len(fvs):,} valid / {mc_n:,} simulations",
                    "xaxis": yaxis_plain("Fair Value / Share ($)"),
                    "yaxis": yaxis_plain("Frequency"),
                }))
                st.plotly_chart(fig_mc, use_container_width=True)
                mc_c = st.columns(5)
                for cw, pct, lbl in zip(mc_c,[5,25,50,75,95],["P5","P25","Median","P75","P95"]):
                    cw.metric(lbl, f"${np.percentile(fvs,pct):,.0f}")
                st.metric("Mean ± StdDev", f"${np.mean(fvs):,.0f} ± ${np.std(fvs):,.0f}")
            else:
                st.warning("Too few valid simulations — ensure WACC > Terminal Growth.")


# ══════════════════════════════════════════════════════════
#  PAGE: MULTI-COMPARE  — FIX #4 (Ticker names always visible)
# ══════════════════════════════════════════════════════════
elif choice == "Multi-Compare":
    ptitle("MULTI-ASSET COMPARISON","Returns · Fundamentals · Correlation · Risk-adjusted metrics")

    mode_mc = st.radio("Mode:", ["📈 Returns","🏢 Fundamentals","⚡ Risk Metrics"], horizontal=True)
    st.markdown("---")

    if mode_mc == "📈 Returns":
        c1, c2 = st.columns([4, 2])
        with c1: tk_in = st.text_input("Tickers (comma-separated)","AAPL,MSFT,NVDA,TSLA,SPY,QQQ")
        with c2:
            h_map = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","2Y":"2y","3Y":"3y","5Y":"5y","10Y":"10y","MAX":"max"}
            h_lbl = st.selectbox("Horizon", list(h_map.keys()), index=6)
        tk_list = [x.strip().upper() for x in tk_in.split(",") if x.strip()]
        if tk_list:
            fr = {t: s for t in tk_list for s in [_get_close(t, period=h_map[h_lbl])] if not s.empty}
            if fr:
                d = pd.DataFrame(fr).dropna(how="all").ffill()
                r = ((d / d.iloc[0]) - 1) * 100
                fig_r = go.Figure()
                for ix, col in enumerate(r.columns):
                    r_sub = _subsample(r[col])
                    fig_r.add_trace(go.Scatter(x=r_sub.index, y=r_sub, name=f"{col} ({r[col].iloc[-1]:+.1f}%)",
                                               line=dict(width=2, color=COLORS[ix % len(COLORS)])))
                fig_r.add_hline(y=0, line_dash="dot", line_color="#141414")
                fig_r.update_layout(**_pla({"xaxis":xaxis_time(),"yaxis":yaxis_plain("Return %"),"height":460,"title":f"Normalised Returns — {h_lbl}"}))
                st.plotly_chart(fig_r, use_container_width=True)
                dr = d.pct_change().dropna()
                ay = max((d.index[-1]-d.index[0]).days/365.25, 0.1)
                # FIX #4: Ticker always explicit as first column, NOT set as index
                stats = []
                for col in r.columns:
                    tr_v  = float(r[col].iloc[-1])
                    cg_v  = float(((1+tr_v/100)**(1/ay)-1)*100)
                    vl_v  = float(dr[col].std()*np.sqrt(252)*100)
                    dd_v  = float(((d[col]/d[col].cummax())-1).min()*100)
                    stats.append({
                        "Ticker":    col,
                        "Total Ret": f"{tr_v:+.1f}%",
                        "CAGR":      f"{cg_v:+.2f}%",
                        "Ann.Vol":   f"{vl_v:.1f}%",
                        "Sharpe":    f"{cg_v/vl_v:.2f}" if vl_v>0 else "N/A",
                        "Max DD":    f"{dd_v:.1f}%",
                        "Years":     f"{ay:.1f}",
                    })
                navy_grid(pd.DataFrame(stats), height=260, key="cmp_stats")
                if len(fr) >= 2:
                    sec("CORRELATION MATRIX")
                    cr = dr.corr()
                    fig_cr = go.Figure(go.Heatmap(z=cr.values,x=cr.columns.tolist(),y=cr.index.tolist(),
                        colorscale=[[0,"#FF3B3B"],[0.5,"#050505"],[1,"#00FF88"]],zmid=0,
                        text=cr.round(2).values,texttemplate="%{text}"))
                    fig_cr.update_layout(**_pla({"height":320,"title":"Return Correlation Matrix"}))
                    st.plotly_chart(fig_cr, use_container_width=True)

    elif mode_mc == "🏢 Fundamentals":
        fund_in = st.text_input("Tickers","AAPL,MSFT,GOOGL,AMZN,META")
        fund_list = [x.strip().upper() for x in fund_in.split(",") if x.strip()]
        if fund_list:
            snap = []
            for tkr_f in fund_list:
                inf_f = yf_info(tkr_f)
                if not inf_f: continue
                # FIX #4: Ticker + Name always first columns
                snap.append({
                    "Ticker":   tkr_f,
                    "Name":     (inf_f.get("shortName") or tkr_f)[:22],
                    "P/E TTM":  f"{inf_f.get('trailingPE'):.1f}"                        if inf_f.get("trailingPE")                       else "N/A",
                    "P/E Fwd":  f"{inf_f.get('forwardPE'):.1f}"                         if inf_f.get("forwardPE")                        else "N/A",
                    "P/B":      f"{inf_f.get('priceToBook'):.2f}"                       if inf_f.get("priceToBook")                      else "N/A",
                    "P/S":      f"{inf_f.get('priceToSalesTrailing12Months'):.1f}"      if inf_f.get("priceToSalesTrailing12Months")      else "N/A",
                    "EV/EBITDA":f"{inf_f.get('enterpriseToEbitda'):.1f}"                if inf_f.get("enterpriseToEbitda")               else "N/A",
                    "Rev $B":   f"{inf_f.get('totalRevenue',0)/1e9:.1f}"                if inf_f.get("totalRevenue")                     else "N/A",
                    "FCF $B":   f"{inf_f.get('freeCashflow',0)/1e9:.1f}"                if inf_f.get("freeCashflow")                     else "N/A",
                    "ROE %":    f"{inf_f.get('returnOnEquity',0)*100:.1f}"              if inf_f.get("returnOnEquity")                   else "N/A",
                    "Op.Mgn %": f"{inf_f.get('operatingMargins',0)*100:.1f}"            if inf_f.get("operatingMargins")                 else "N/A",
                    "Beta":     f"{inf_f.get('beta'):.2f}"                              if inf_f.get("beta")                             else "N/A",
                })
            if snap:
                navy_grid(pd.DataFrame(snap), height=300, key="fund_grid")

    else:  # Risk Metrics
        c1, c2 = st.columns([4,2])
        with c1: rm_in = st.text_input("Tickers","AAPL,NVDA,TSLA,SPY,GLD,TLT")
        with c2: rm_per = st.selectbox("Period",["1y","3y","5y","10y"],index=2,key="rm_per2")
        rm_list = [x.strip().upper() for x in rm_in.split(",") if x.strip()]
        rf_rm   = st.slider("Risk-free (%)", 0.0, 7.0, 4.0, step=0.1, key="rf_rm2") / 100
        if rm_list:
            fr_r = {t: s for t in rm_list for s in [_get_close(t, period=rm_per)] if not s.empty}
            if fr_r:
                d_r  = pd.DataFrame(fr_r).dropna(how="all").ffill()
                dr_r = d_r.pct_change().dropna()
                ay_r = max((d_r.index[-1]-d_r.index[0]).days/365.25, 0.1)
                rows_rm = []
                for col in dr_r.columns:
                    tr_rv  = float((d_r[col].iloc[-1]/d_r[col].iloc[0]-1)*100)
                    ann_rv = float(((1+tr_rv/100)**(1/ay_r)-1)*100)
                    vl_rv  = float(dr_r[col].std()*np.sqrt(252)*100)
                    dd_rv  = float(((d_r[col]/d_r[col].cummax())-1).min()*100)
                    sh_rv  = (ann_rv/100-rf_rm)/(vl_rv/100) if vl_rv>0 else float("nan")
                    neg_rv = dr_r[col][dr_r[col]<rf_rm/252]
                    dv_rv  = float(neg_rv.std()*np.sqrt(252)) if len(neg_rv)>1 else 0
                    so_rv  = (ann_rv/100-rf_rm)/dv_rv if dv_rv>0 else float("nan")
                    ca_rv  = ann_rv/abs(dd_rv) if dd_rv<0 else float("nan")
                    var_rv = float(np.percentile(dr_r[col].values,5)*100)
                    # FIX #4: Ticker always first column
                    rows_rm.append({
                        "Ticker":  col,
                        "CAGR":    f"{ann_rv:+.2f}%",
                        "Ann.Vol": f"{vl_rv:.1f}%",
                        "MaxDD":   f"{dd_rv:.1f}%",
                        "Sharpe":  f"{sh_rv:.2f}" if not math.isnan(sh_rv) else "N/A",
                        "Sortino": f"{so_rv:.2f}" if not math.isnan(so_rv) else "N/A",
                        "Calmar":  f"{ca_rv:.2f}" if not math.isnan(ca_rv) else "N/A",
                        "VaR95":   f"{var_rv:.2f}%",
                    })
                if rows_rm:
                    navy_grid(pd.DataFrame(rows_rm), height=300, key="risk_grid")


# ══════════════════════════════════════════════════════════
#  PAGE: PORTFOLIO BACKTEST
# ══════════════════════════════════════════════════════════
elif choice == "Portfolio Backtest":
    ptitle("PORTFOLIO BACKTEST ENGINE","Vectorized · Drawdown · Rolling Sharpe · Monthly Heatmap · Factor Exposure")

    sec("PORTFOLIO COMPOSITION")
    n_a  = st.slider("Number of assets", 2, 12, 4)
    defs = ["VOO","GLD","TLT","QQQ","BND","VNQ","EEM","PDBC","IAU","VWCE.DE","AAPL","NVDA"]
    ct   = st.columns(n_a)
    cw   = st.columns(n_a)
    assets: list[str] = []
    weights: list[int] = []
    dw = round(100 / n_a)
    for i in range(n_a):
        with ct[i]:
            a = st.text_input(f"Asset {i+1}", defs[i] if i < len(defs) else "", key=f"at_{i}")
            assets.append(a.strip().upper())
        with cw[i]:
            w = st.slider(assets[i] or f"A{i+1}", 0, 100, dw, key=f"aw_{i}")
            weights.append(w)

    tw = sum(weights)
    if tw != 100:
        st.warning(f"⚠ Weights sum: {tw}% — must equal 100%")
    else:
        st.success("✅ Weights = 100%")

    st.markdown("---")
    sec("PARAMETERS")
    p1,p2,p3,p4 = st.columns(4)
    with p1:
        BENCH_MAP = {"S&P 500 (^GSPC)":"^GSPC","Nasdaq (^IXIC)":"^IXIC","MSCI World (VWCE.DE)":"VWCE.DE","Custom 60/40":None}
        bench_lbl = st.selectbox("Benchmark", list(BENCH_MAP.keys()))
        bench_tkr = BENCH_MAP[bench_lbl]
    with p2: years  = st.slider("Horizon (years)", 1, 30, 10, key="bt_yrs")
    with p3: rf_bt  = st.slider("Risk-free (%)", 0.0, 7.0, 4.2, step=0.1)
    with p4: rebal  = st.selectbox("Rebalancing",["none","M","Q","A"],
                                   format_func=lambda x:{"none":"None","M":"Monthly","Q":"Quarterly","A":"Annually"}[x])

    if bench_tkr is None:
        bc1,bc2 = st.columns(2)
        with bc1: be = st.text_input("Equity leg","SPY",key="be_leg")
        with bc2: bb = st.text_input("Bond leg",  "AGG",key="bb_leg")
    else:
        be, bb = "SPY", "AGG"

    bt_config_key = f"{','.join(a for a in assets if a)}_{','.join(str(w) for w in weights)}_{bench_lbl}_{years}_{rf_bt}_{rebal}"
    run_btn = st.button("▶  RUN BACKTEST", use_container_width=True)

    if run_btn and tw == 100:
        if bt_config_key != st.session_state.backtest_key:
            valid = [(a, weights[i]) for i, a in enumerate(assets) if a]
            wt_dict = {p[0]: p[1]/100 for p in valid}
            start_s = (datetime.now() - timedelta(days=365*years)).strftime("%Y-%m-%d")

            with st.spinner("Downloading price data…"):
                frames: dict[str, pd.Series] = {}
                bench_series = None
                for tk in [p[0] for p in valid]:
                    s = _get_close(tk, start=start_s)
                    if not s.empty: frames[tk] = s
                    else: st.warning(f"⚠ No data: {tk}")
                if bench_tkr:
                    bs = _get_close(bench_tkr, start=start_s)
                    bench_series = bs if not bs.empty else None
                else:
                    b_eq = _get_close(be.upper(), start=start_s)
                    b_bd = _get_close(bb.upper(), start=start_s)
                    if not b_eq.empty and not b_bd.empty:
                        a_b  = pd.concat([b_eq, b_bd], axis=1).dropna().ffill()
                        bench_series = (a_b.iloc[:,0]*0.6 + a_b.iloc[:,1]*0.4).rename("60/40")
                    elif not b_eq.empty:
                        bench_series = b_eq
                if not frames:
                    st.error("No valid asset data.")
                    st.stop()
                px_df = pd.DataFrame(frames).dropna(how="all").ffill().bfill()

            try:
                bt = run_backtest(px_df, wt_dict, bench_series, rf=rf_bt/100, rebalance=rebal)
                st.session_state.backtest_result   = bt
                st.session_state.backtest_key      = bt_config_key
                st.session_state["bt_valid"]       = valid
                st.session_state["bt_px_df"]       = px_df
                st.session_state["bt_bench_series"]= bench_series
            except Exception as e:
                st.error(f"Backtest error: {e}")
                st.stop()

    if st.session_state.backtest_result is not None:
        bt    = st.session_state.backtest_result
        valid = st.session_state.get("bt_valid", [])
        px_df = st.session_state.get("bt_px_df", pd.DataFrame())
        bench_series = st.session_state.get("bt_bench_series", None)

        def _f(v, s="%", d=2):
            if v is None or (isinstance(v,float) and (math.isnan(v) or math.isinf(v))): return "N/A"
            return (f"{{:+.{d}f}}{s}" if s=="%" else f"{{:.{d}f}}{s}").format(v)

        sec("PERFORMANCE DASHBOARD")
        k1,k2,k3,k4 = st.columns(4)
        k1.metric("Total Return",    _f(bt.total_return))
        k2.metric("CAGR",            _f(bt.cagr))
        k3.metric("Ann. Volatility", f"{bt.ann_vol:.2f}%")
        k4.metric("Max Drawdown",    _f(bt.max_dd))
        k5,k6,k7,k8 = st.columns(4)
        k5.metric("Sharpe",  f"{bt.sharpe:.3f}")
        k6.metric("Sortino", f"{bt.sortino:.3f}")
        k7.metric("Calmar",  f"{bt.calmar:.3f}" if not math.isinf(bt.calmar) else "∞")
        k8.metric("Omega",   f"{bt.omega:.2f}"  if bt.omega < 999 else ">999")
        k9,k10,k11,k12 = st.columns(4)
        k9.metric("VaR 95%",   f"{bt.var95:.2f}%")
        k10.metric("CVaR 95%", f"{bt.cvar95:.2f}%")
        k11.metric("Win Rate", f"{bt.win_rate:.1f}%")
        k12.metric("Beta",     f"{bt.beta:.3f}" if bt.beta is not None else "N/A")
        if bt.alpha is not None:
            st.metric(f"Alpha vs {bench_lbl}", f"{bt.alpha:+.2f}%")

        sec("EQUITY CURVE")
        eq_norm = (bt.equity_curve / bt.equity_curve.iloc[0] - 1) * 100
        eq_sub  = _subsample(eq_norm)
        fig_eq  = go.Figure()
        fig_eq.add_trace(go.Scatter(x=eq_sub.index, y=eq_sub, name="Strategy",
                                    line=dict(width=3,color="#F5A623"), fill="tozeroy", fillcolor="rgba(245,166,35,0.04)"))
        if bench_series is not None:
            bn     = (bench_series / bench_series.iloc[0] - 1) * 100
            bn_sub = _subsample(bn)
            fig_eq.add_trace(go.Scatter(x=bn_sub.index, y=bn_sub, name=bench_lbl, line=dict(width=1.8,dash="dash",color="#3B8EF0")))
        wt_dict_render = {p[0]: p[1]/100 for p in valid}
        for ix, a in enumerate([p[0] for p in valid]):
            if a in px_df.columns:
                an     = (px_df[a] / px_df[a].iloc[0] - 1) * 100
                an_sub = _subsample(an)
                fig_eq.add_trace(go.Scatter(x=an_sub.index, y=an_sub, name=f"{a}({wt_dict_render.get(a,0)*100:.0f}%)",
                                            line=dict(width=1,color=COLORS[(ix+2)%len(COLORS)]),opacity=0.40))
        fig_eq.add_hline(y=0, line_dash="dot", line_color="#141414")
        fig_eq.update_layout(**_pla({"xaxis":xaxis_time(),"yaxis":yaxis_plain("Return %"),"height":480,"title":"Portfolio Equity Curve"}))
        st.plotly_chart(fig_eq, use_container_width=True)

        cd, cr = st.columns(2)
        with cd:
            sec("DRAWDOWN FROM PEAK")
            dd_sub = _subsample(bt.drawdown)
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(x=dd_sub.index, y=dd_sub,
                                        fill="tozeroy",line=dict(color="#FF3B3B",width=1.5),
                                        fillcolor="rgba(255,59,59,0.08)"))
            fig_dd.update_layout(**_pla({"xaxis":xaxis_time(),"yaxis":yaxis_plain("Drawdown %"),"height":280}))
            st.plotly_chart(fig_dd, use_container_width=True)
        with cr:
            sec("ROLLING SHARPE (63d)")
            rs_sub = _subsample(bt.rolling_sharpe)
            fig_rs = go.Figure()
            fig_rs.add_trace(go.Scatter(x=rs_sub.index, y=rs_sub, line=dict(color="#F5A623",width=1.5)))
            fig_rs.add_hline(y=0, line_dash="dot", line_color="#141414")
            fig_rs.add_hline(y=1, line_dash="dot", line_color="#00FF88",
                             annotation_text="Sharpe=1", annotation_font_color="#00FF88")
            fig_rs.update_layout(**_pla({"height":280,"title":"Rolling Sharpe"}))
            st.plotly_chart(fig_rs, use_container_width=True)

        if not bt.monthly_heatmap.empty:
            sec("MONTHLY RETURNS HEATMAP (%)")
            fig_mth = go.Figure(go.Heatmap(
                z=bt.monthly_heatmap.values,
                x=bt.monthly_heatmap.columns.tolist(),
                y=bt.monthly_heatmap.index.tolist(),
                colorscale=[[0,"#FF3B3B"],[0.5,"#050505"],[1,"#00FF88"]], zmid=0,
                text=[[f"{v:.1f}%" if not math.isnan(v) else "" for v in row] for row in bt.monthly_heatmap.values],
                texttemplate="%{text}",
            ))
            fig_mth.update_layout(**_pla({"height":max(220,len(bt.monthly_heatmap)*26+80),"title":"Monthly Returns (%)"}))
            st.plotly_chart(fig_mth, use_container_width=True)

        ch, cc = st.columns(2)
        with ch:
            sec("RETURN DISTRIBUTION")
            arr_bt = bt.daily_returns.dropna().values
            fig_h = go.Figure()
            fig_h.add_trace(go.Histogram(x=arr_bt*100, nbinsx=80, marker_color="#F5A623", opacity=0.75))
            if bt.var95: fig_h.add_vline(x=bt.var95, line_dash="dash", line_color="#FF3B3B",
                                          annotation_text=f"VaR95:{bt.var95:.2f}%", annotation_font_color="#FF3B3B")
            fig_h.add_vline(x=0, line_dash="dot", line_color="#3A6A9A")
            fig_h.update_layout(**_pla({"xaxis":yaxis_plain("Daily Return %"),"yaxis":yaxis_plain("Frequency"),"height":280}))
            st.plotly_chart(fig_h, use_container_width=True)
        with cc:
            avail_a = [a for a in [p[0] for p in valid] if a in px_df.columns]
            if len(avail_a) >= 2:
                sec("ASSET CORRELATION")
                cor = px_df[avail_a].pct_change().dropna().corr()
                fig_co = go.Figure(go.Heatmap(z=cor.values,x=cor.columns.tolist(),y=cor.index.tolist(),
                    colorscale=[[0,"#FF3B3B"],[0.5,"#050505"],[1,"#00FF88"]],zmid=0,
                    text=cor.round(2).values,texttemplate="%{text}"))
                fig_co.update_layout(**_pla({"height":280}))
                st.plotly_chart(fig_co, use_container_width=True)

        if not bt.contributions.empty:
            sec("ASSET CONTRIBUTIONS")
            navy_grid(bt.contributions, height=160, key="contrib_grid")

        sec("RISK DIAGNOSTICS")
        tips: list[str] = []
        if not math.isnan(bt.sharpe):
            if bt.sharpe < 0:      tips.append(f"🔴 <b>Negative Sharpe ({bt.sharpe:.2f})</b> — return below risk-free.")
            elif bt.sharpe < 0.5:  tips.append(f"🟡 <b>Low Sharpe ({bt.sharpe:.2f})</b> — add uncorrelated assets: GLD, TLT, REITs.")
            elif bt.sharpe >= 1.5: tips.append(f"🏆 <b>High Sharpe ({bt.sharpe:.2f})</b> — excellent. Verify over longer period.")
            else:                   tips.append(f"✅ <b>Acceptable Sharpe ({bt.sharpe:.2f})</b> — target >1.0 for consistent alpha.")
        if bt.ann_vol > 25:  tips.append(f"⚡ <b>High Volatility ({bt.ann_vol:.1f}%)</b> — reduce equity concentration.")
        if bt.max_dd < -40:  tips.append(f"💥 <b>Extreme Drawdown ({bt.max_dd:.1f}%)</b> — consider volatility targeting.")
        if bt.var95  < -3:   tips.append(f"📉 <b>High VaR95 ({bt.var95:.2f}%/day)</b>.")
        if len(valid) < 4:   tips.append(f"🔀 <b>Low Diversification ({len(valid)} assets)</b> — 8–15 uncorrelated assets optimal.")
        if not tips:          tips.append("ℹ️ Parameters within normal bounds. No critical signals detected.")
        for tip in tips:
            alert(tip)

    elif run_btn and tw != 100:
        st.error("Portfolio weights must sum to exactly 100%.")


# ══════════════════════════════════════════════════════════
#  PAGE: STOCK SCREENER
# ══════════════════════════════════════════════════════════
elif choice == "Stock Screener":
    if st.session_state.screener_selected:
        tgt = st.session_state.screener_selected
        back_col, _ = st.columns([1, 8])
        if back_col.button("← Back to Screener"):
            st.session_state.screener_selected = None
            st.rerun()
        ptitle(f"TERMINAL — {tgt}")
        inf_s = yf_info(tgt)
        sec_s = inf_s.get("sector","") if inf_s else ""
        show_terminal(tgt, SECTOR_PEERS.get(sec_s,"SPY,QQQ,IWM"))
        st.stop()

    ptitle(
        "INSTITUTIONAL STOCK SCREENER  v6.1",
        "Finviz Primary Engine · yFinance Batch Fallback · 1,500+ Global Tickers · AgGrid",
    )

    ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([2, 2, 3])
    with ctrl_c1:
        force_yf = st.checkbox("Force yFinance fallback", value=False, key="scr_force_yf")
    with ctrl_c2:
        reload_btn = st.button("🔄  Reload Data", use_container_width=True, key="scr_reload")
    with ctrl_c3:
        st.markdown(
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.60rem;color:#3A6A9A;"
            "padding-top:8px'>Finviz data cached 10 min · yFinance via ThreadPoolExecutor(40)</div>",
            unsafe_allow_html=True,
        )

    needs_load = (st.session_state.screener_df is None or reload_btn)
    if needs_load:
        with st.spinner("⬛ Loading screener data…  (Finviz → yFinance fallback)"):
            df_master, src_label = load_screener_master_data(force_fallback=force_yf)
        st.session_state.screener_df     = df_master
        st.session_state.screener_source = src_label

    df_master = st.session_state.screener_df
    src_label = st.session_state.screener_source or "—"

    n_total = len(df_master) if df_master is not None else 0
    src_col  = "#00FF88" if "Finviz" in src_label else ("#F5A623" if "yFinance" in src_label else "#FF3B3B")
    st.markdown(
        f"<div class='screener-stats-bar'>"
        f"<span>SOURCE: <b style='color:{src_col}'>{src_label}</b></span>"
        f"<span>UNIVERSE: <b>{n_total:,}</b> tickers loaded</span>"
        f"<span style='color:#111'>│</span>"
        f"<span style='color:#2A4A6A;font-size:0.58rem'>Filters applied in-memory · No extra requests</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if df_master is not None and not df_master.empty:
        sectors   = sorted(df_master["Sector"].dropna().unique().tolist())
        countries = sorted(df_master["Country"].dropna().unique().tolist())
    else:
        sectors, countries = [], []

    with st.expander("⚙  SCREENER FILTERS", expanded=True):
        filter_vals = render_screener_filter_panel(sectors=sectors, countries=countries)

    if df_master is not None and not df_master.empty:
        df_filtered = apply_screener_filters(
            df              = df_master,
            sector          = filter_vals["sector"],
            country         = filter_vals["country"],
            keyword         = filter_vals["keyword"],
            min_marketcap_b = filter_vals["min_marketcap_b"],
            max_marketcap_b = filter_vals["max_marketcap_b"],
            max_pe          = filter_vals["max_pe"],
            min_pe          = filter_vals["min_pe"],
            min_change_pct  = filter_vals["min_change_pct"],
            max_change_pct  = filter_vals["max_change_pct"],
        )

        sort_col = filter_vals["sort_col"]
        sort_asc = filter_vals["sort_asc"]
        if sort_col in df_filtered.columns:
            df_filtered = df_filtered.sort_values(sort_col, ascending=sort_asc, na_position="last").reset_index(drop=True)

        n_filtered = len(df_filtered)
        pct_shown  = n_filtered / n_total * 100 if n_total > 0 else 0
        st.markdown(
            f"<div class='screener-stats-bar' style='margin-top:0.5rem'>"
            f"<span>RESULTS: <b style='color:#F5A623'>{n_filtered:,}</b> / {n_total:,} "
            f"(<b>{pct_shown:.1f}%</b>)</span>"
            f"<span>SORT: <b>{sort_col}</b> {'↑' if sort_asc else '↓'}</span>"
            f"<span>PAGE: <b>{filter_vals['page_size']}</b></span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        grid_result = screener_aggrid(
            df       = df_filtered,
            height   = 580,
            key      = "screener_main_grid",
            page_size= filter_vals["page_size"],
        )

        if n_filtered > 0:
            st.markdown("---")
            ch_left, ch_right = st.columns(2)
            with ch_left:
                sec("SECTOR DISTRIBUTION")
                sect_counts = df_filtered["Sector"].value_counts().head(12).reset_index()
                sect_counts.columns = ["Sector", "Count"]
                fig_sec = go.Figure(go.Bar(
                    x=sect_counts["Sector"], y=sect_counts["Count"],
                    marker_color=[COLORS[i % len(COLORS)] for i in range(len(sect_counts))], opacity=0.85,
                ))
                fig_sec.update_layout(**_pla({
                    "height": 260,
                    "xaxis": dict(tickangle=-30, tickfont=dict(size=8, color="#3A6A9A")),
                    "yaxis": yaxis_plain("Companies"),
                }))
                st.plotly_chart(fig_sec, use_container_width=True)
            with ch_right:
                sec("MARKET CAP DISTRIBUTION")
                mc_vals = pd.to_numeric(df_filtered["MarketCap_B"], errors="coerce").dropna()
                if not mc_vals.empty:
                    fig_mc_hist = go.Figure(go.Histogram(x=mc_vals, nbinsx=40, marker_color="#3B8EF0", opacity=0.80))
                    fig_mc_hist.update_layout(**_pla({"height":260,"xaxis":yaxis_plain("Market Cap ($B)"),"yaxis":yaxis_plain("Count")}))
                    st.plotly_chart(fig_mc_hist, use_container_width=True)

        st.markdown("---")
        sec("OPEN IN COMPANY TERMINAL")
        if n_filtered > 0:
            ticker_options = [f"{row['Ticker']}  —  {row['Name']}" for _, row in df_filtered.head(200).iterrows()]
            sel_scr = st.selectbox("Select company to analyse", ticker_options, key="scr_sel_box")
            if st.button("⌨  OPEN COMPANY TERMINAL", use_container_width=True, key="scr_open_btn"):
                st.session_state.screener_selected = sel_scr.split("  —  ")[0].strip()
                st.rerun()
            if grid_result is not None:
                try:
                    selected_rows = grid_result.get("selected_rows", None)
                    if selected_rows is not None:
                        if hasattr(selected_rows, "empty"):
                            if not selected_rows.empty and "Ticker" in selected_rows.columns:
                                clicked_tkr = str(selected_rows.iloc[0]["Ticker"]).strip()
                                if clicked_tkr:
                                    st.session_state.screener_selected = clicked_tkr
                                    st.rerun()
                        elif isinstance(selected_rows, list) and len(selected_rows) > 0:
                            clicked_tkr = str(selected_rows[0].get("Ticker", "")).strip()
                            if clicked_tkr:
                                st.session_state.screener_selected = clicked_tkr
                                st.rerun()
                except Exception:
                    pass
        else:
            st.info("No companies match the current filters. Try broadening your criteria.")
    else:
        st.error("⚠ Could not load screener data. Both Finviz and yFinance are unreachable.")


# ══════════════════════════════════════════════════════════
#  PAGE: MACRO & FRED
# ══════════════════════════════════════════════════════════
elif choice == "Macro & FRED":
    ptitle("MACRO & FIXED INCOME", f"FRED Live Data · Yield Curve · Inflation · Employment · Credit Spreads {badge('FRED')}")

    tab_yc, tab_infl, tab_emp, tab_cr, tab_rates = st.tabs([
        "📈 Yield Curve","💸 Inflation","👷 Employment & GDP","🏦 Credit Spreads","🌐 Global Rates",
    ])

    with tab_yc:
        sec("US TREASURY YIELD CURVE — LIVE")
        TSERIES = {"3M":"DGS3MO","2Y":"DGS2","5Y":"DGS5","7Y":"DGS7","10Y":"DGS10","20Y":"DGS20","30Y":"DGS30"}
        snap: dict[str,float] = {}
        yc_cols = st.columns(7)
        for i, (lbl, sid) in enumerate(TSERIES.items()):
            s = fetch_fred(sid)
            if not s.empty:
                val  = float(s.iloc[-1])
                prev = float(s.iloc[-2]) if len(s)>1 else val
                snap[lbl] = val
                yc_cols[i].metric(f"{lbl} Yield", f"{val:.3f}%", f"{val-prev:+.3f}bps")
        if len(snap) >= 3:
            fig_yc = go.Figure()
            fig_yc.add_trace(go.Scatter(
                x=list(snap.keys()), y=list(snap.values()),
                mode="lines+markers", line=dict(color="#F5A623",width=2.5), marker=dict(size=9),
                fill="tozeroy", fillcolor="rgba(245,166,35,0.05)",
            ))
            for x,y in snap.items():
                fig_yc.add_annotation(x=x, y=y, text=f"{y:.3f}%", showarrow=False, yshift=13,
                                      font=dict(color="#F5A623",size=9,family="IBM Plex Mono"))
            fig_yc.update_layout(**_pla({"height":300,"title":"US Treasury Yield Curve",
                                         "xaxis":yaxis_plain("Maturity"),"yaxis":yaxis_plain("Yield (%)")}))
            st.plotly_chart(fig_yc, use_container_width=True)
        sec("YIELD SPREAD HISTORY")
        ysp_per = st.selectbox("Period",["1y","3y","5y","10y","20y"],index=2,key="ysp_per")
        start_y = {"1y":"2023","3y":"2021","5y":"2019","10y":"2014","20y":"2004"}[ysp_per]
        s10 = fetch_fred("DGS10",  start=f"{start_y}-01-01")
        s2  = fetch_fred("DGS2",   start=f"{start_y}-01-01")
        s3m = fetch_fred("DGS3MO", start=f"{start_y}-01-01")
        ssp = fetch_fred("T10Y2Y", start=f"{start_y}-01-01")
        fig_sp = make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=0.06,row_heights=[0.6,0.4])
        if not s10.empty: fig_sp.add_trace(go.Scatter(x=s10.index,y=s10,name="10Y",line=dict(color="#F5A623",width=1.5)),row=1,col=1)
        if not s2.empty:  fig_sp.add_trace(go.Scatter(x=s2.index, y=s2, name="2Y", line=dict(color="#3B8EF0",width=1.5)),row=1,col=1)
        if not s3m.empty: fig_sp.add_trace(go.Scatter(x=s3m.index,y=s3m,name="3M",line=dict(color="#9B59B6",width=1.2)),row=1,col=1)
        if not ssp.empty:
            sc_colors = ["#00FF88" if v>=0 else "#FF3B3B" for v in ssp]
            fig_sp.add_trace(go.Bar(x=ssp.index,y=ssp,name="10Y-2Y Spread",marker_color=sc_colors,opacity=0.80),row=2,col=1)
            fig_sp.add_hline(y=0,line_dash="dash",line_color="#111",row=2,col=1)
        fig_sp.update_layout(**_pla({"height":440,"title":"Treasury Yields & 10Y-2Y Spread"}))
        for r in [1,2]: fig_sp.update_yaxes(gridcolor="#0e0e0e",showgrid=True,row=r,col=1)
        st.plotly_chart(fig_sp, use_container_width=True)

    with tab_infl:
        sec("INFLATION INDICATORS")
        INFL = {"CPI (CPIAUCSL)":"CPIAUCSL","Core CPI (CPILFESL)":"CPILFESL","PCE (PCEPI)":"PCEPI"}
        infl_per = st.selectbox("Period",["1y","3y","5y","10y","20y"],index=3,key="infl_per")
        start_i  = {"1y":"2023","3y":"2021","5y":"2019","10y":"2014","20y":"2004"}[infl_per]
        fig_infl = go.Figure()
        for ix, (lbl_i, sid_i) in enumerate(INFL.items()):
            s_i = fetch_fred(sid_i, start=f"{start_i}-01-01")
            if not s_i.empty:
                yoy = s_i.pct_change(12).dropna() * 100
                if not yoy.empty:
                    fig_infl.add_trace(go.Scatter(x=yoy.index,y=yoy,name=lbl_i,line=dict(width=2,color=COLORS[ix%len(COLORS)])))
                    val_i  = float(yoy.iloc[-1])
                    prev_i = float(yoy.iloc[-2]) if len(yoy)>1 else val_i
                    st.metric(lbl_i, f"{val_i:.2f}%", f"{val_i-prev_i:+.2f}bps")
        fig_infl.add_hline(y=2.0,line_dash="dot",line_color="rgba(245,166,35,0.5)",
                           annotation_text="Fed 2% Target",annotation_font_color="#F5A623")
        fig_infl.update_layout(**_pla({"height":340,"title":"Inflation YoY (%)","xaxis":xaxis_time(),"yaxis":yaxis_plain("YoY %")}))
        st.plotly_chart(fig_infl, use_container_width=True)

    with tab_emp:
        sec("EMPLOYMENT & GROWTH")
        EMPL = {"Unemployment Rate":"UNRATE","Non-Farm Payrolls":"PAYEMS","Initial Claims":"ICSA"}
        GDP  = {"Real GDP QoQ":"A191RL1Q225SBEA","Industrial Production":"INDPRO","Retail Sales":"RSAFS"}
        emp_per = st.selectbox("Period",["1y","3y","5y","10y","20y"],index=3,key="emp_per")
        start_e = {"1y":"2023","3y":"2021","5y":"2019","10y":"2014","20y":"2004"}[emp_per]
        ce, cg = st.columns(2)
        with ce:
            fig_e = go.Figure()
            for ix, (lbl_e, sid_e) in enumerate(EMPL.items()):
                s_e = fetch_fred(sid_e, start=f"{start_e}-01-01")
                if not s_e.empty:
                    fig_e.add_trace(go.Scatter(x=s_e.index,y=s_e,name=lbl_e,line=dict(width=1.8,color=COLORS[ix%len(COLORS)])))
                    val_e  = float(s_e.iloc[-1])
                    prev_e = float(s_e.iloc[-2]) if len(s_e)>1 else val_e
                    st.metric(lbl_e, f"{val_e:,.1f}", f"{val_e-prev_e:+.1f}")
            fig_e.update_layout(**_pla({"height":260,"title":"Employment","xaxis":xaxis_time(),"yaxis":yaxis_plain()}))
            st.plotly_chart(fig_e, use_container_width=True)
        with cg:
            fig_g = go.Figure()
            for ix, (lbl_g, sid_g) in enumerate(GDP.items()):
                s_g = fetch_fred(sid_g, start=f"{start_e}-01-01")
                if not s_g.empty:
                    if sid_g == "A191RL1Q225SBEA":
                        fig_g.add_trace(go.Bar(x=s_g.index,y=s_g,name=lbl_g,
                                               marker_color=["#00FF88" if v>=0 else "#FF3B3B" for v in s_g],opacity=0.8))
                    else:
                        fig_g.add_trace(go.Scatter(x=s_g.index,y=s_g,name=lbl_g,line=dict(width=1.8,color=COLORS[(ix+3)%len(COLORS)])))
                    val_g  = float(s_g.iloc[-1])
                    prev_g = float(s_g.iloc[-2]) if len(s_g)>1 else val_g
                    st.metric(lbl_g, f"{val_g:,.2f}", f"{val_g-prev_g:+.2f}")
            fig_g.update_layout(**_pla({"height":260,"title":"GDP & Activity","xaxis":xaxis_time(),"yaxis":yaxis_plain()}))
            st.plotly_chart(fig_g, use_container_width=True)

    with tab_cr:
        sec("CREDIT SPREADS & RISK")
        CR_SER = {"HY Spread (BAMLH0A0HYM2)":"BAMLH0A0HYM2","IG Spread (BAMLC0A0CM)":"BAMLC0A0CM","TED Spread":"TEDRATE"}
        cr_per  = st.selectbox("Period",["1y","3y","5y","10y","20y"],index=3,key="cr_per")
        start_c = {"1y":"2023","3y":"2021","5y":"2019","10y":"2014","20y":"2004"}[cr_per]
        fig_cr  = go.Figure()
        for ix, (lbl_c, sid_c) in enumerate(CR_SER.items()):
            s_c = fetch_fred(sid_c, start=f"{start_c}-01-01")
            if not s_c.empty:
                fig_cr.add_trace(go.Scatter(x=s_c.index,y=s_c,name=lbl_c,line=dict(width=1.8,color=COLORS[ix%len(COLORS)])))
                val_c  = float(s_c.iloc[-1])
                prev_c = float(s_c.iloc[-2]) if len(s_c)>1 else val_c
                st.metric(lbl_c, f"{val_c:.3f}%", f"{val_c-prev_c:+.3f}bps")
        fig_cr.update_layout(**_pla({"height":320,"title":"Credit Spreads","xaxis":xaxis_time(),"yaxis":yaxis_plain("Spread %")}))
        st.plotly_chart(fig_cr, use_container_width=True)
        sec("MARKET RISK PROXIES")
        RISK_T = {"^VIX":"^VIX","^MOVE":"^MOVE","HYG":"HYG","LQD":"LQD","EEM":"EEM","DXY":"DX-Y.NYB"}
        rp = st.columns(3)
        for i, (nm, tk) in enumerate(RISK_T.items()):
            p, c = yf_price_chg(tk)
            rp[i%3].metric(nm, f"{p:,.3f}" if p else "N/A", f"{c:+.3f}%" if c else "—")

    with tab_rates:
        sec("GLOBAL POLICY RATES")
        POL = {"Fed Funds (FEDFUNDS)":"FEDFUNDS"}
        gr_per   = st.selectbox("Period",["1y","3y","5y","10y","20y"],index=3,key="gr_per")
        start_gr = {"1y":"2023","3y":"2021","5y":"2019","10y":"2014","20y":"2004"}[gr_per]
        fig_gr   = go.Figure()
        for ix, (lbl_r, sid_r) in enumerate(POL.items()):
            s_r = fetch_fred(sid_r, start=f"{start_gr}-01-01")
            if not s_r.empty:
                fig_gr.add_trace(go.Scatter(x=s_r.index,y=s_r,name=lbl_r,line=dict(width=2,color=COLORS[ix%len(COLORS)])))
                st.metric(lbl_r, f"{float(s_r.iloc[-1]):.3f}%")
        fig_gr.update_layout(**_pla({"height":300,"title":"Policy Rates","xaxis":xaxis_time(),"yaxis":yaxis_plain("Rate %")}))
        st.plotly_chart(fig_gr, use_container_width=True)
        sec("FX CROSS RATES")
        FX_G = {"EUR/USD":"EURUSD=X","GBP/USD":"GBPUSD=X","USD/JPY":"USDJPY=X","USD/CHF":"USDCHF=X","AUD/USD":"AUDUSD=X","DXY":"DX-Y.NYB"}
        fx_c = st.columns(3)
        for i, (nm, tk) in enumerate(FX_G.items()):
            p, c = yf_price_chg(tk)
            fx_c[i%3].metric(nm, f"{p:.4f}" if p else "N/A", f"{c:+.3f}%" if c else "—")


# ══════════════════════════════════════════════════════════
#  PAGE: OPTIONS & DERIVATIVES
# ══════════════════════════════════════════════════════════
elif choice == "Options & Derivatives":
    ptitle("OPTIONS & DERIVATIVES","Option chains · IV Smile · Greeks · OI Distribution · Put/Call Ratio")

    opt_tkr = st.text_input("Ticker","AAPL",key="opt_tkr")
    if opt_tkr.strip():
        tkr_o = opt_tkr.strip().upper()
        opt_cache_key = f"options_{tkr_o}"
        if opt_cache_key not in st.session_state:
            calls, puts, exps = yf_options(tkr_o)
            st.session_state[opt_cache_key] = (calls, puts, exps)
        calls, puts, exps = st.session_state[opt_cache_key]

        if calls is None or (isinstance(calls, pd.DataFrame) and calls.empty and not exps):
            interrupted(f"No options data for {tkr_o}.")
        else:
            inf_o = yf_info(tkr_o)
            cur_p = inf_o.get("currentPrice") or inf_o.get("regularMarketPrice") if inf_o else None
            sec("SELECT EXPIRATION")
            if exps:
                exp_sel = st.selectbox("Expiration", exps)
                exp_cache_key = f"opt_chain_{tkr_o}_{exp_sel}"
                if exp_cache_key not in st.session_state:
                    try:
                        ch = yf.Ticker(tkr_o).option_chain(exp_sel)
                        st.session_state[exp_cache_key] = (ch.calls, ch.puts)
                    except Exception:
                        st.session_state[exp_cache_key] = (calls, puts)
                calls, puts = st.session_state[exp_cache_key]

            m1,m2,m3 = st.columns(3)
            if cur_p: m1.metric("Spot Price", f"${cur_p:,.2f}")
            if not calls.empty and "openInterest" in calls.columns: m2.metric("Call OI",f"{calls['openInterest'].sum():,.0f}")
            if not puts.empty  and "openInterest" in puts.columns:  m3.metric("Put OI", f"{puts['openInterest'].sum():,.0f}")
            if not calls.empty and not puts.empty and "openInterest" in calls.columns and "openInterest" in puts.columns:
                pc = puts["openInterest"].sum() / max(calls["openInterest"].sum(),1)
                m1.metric("Put/Call Ratio", f"{pc:.2f}")
            t_ca, t_pu, t_iv, t_oi = st.tabs(["📈 Calls","📉 Puts","📊 IV Smile","📦 OI Distribution"])
            _DISP = ["strike","lastPrice","bid","ask","volume","openInterest","impliedVolatility","inTheMoney"]
            with t_ca:
                if not calls.empty:
                    dc = [c for c in _DISP if c in calls.columns]
                    df_c = calls[dc].copy()
                    if cur_p and "strike" in df_c.columns:
                        df_c = df_c.iloc[(df_c["strike"]-cur_p).abs().argsort()[:35]]
                    if "impliedVolatility" in df_c.columns:
                        df_c["IV%"] = df_c["impliedVolatility"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A")
                        df_c.drop(columns=["impliedVolatility"],inplace=True)
                    navy_grid(df_c.reset_index(drop=True), height=360, key="calls_g")
                else: interrupted("Call chain unavailable.")
            with t_pu:
                if not puts.empty:
                    dp = [c for c in _DISP if c in puts.columns]
                    df_p = puts[dp].copy()
                    if cur_p and "strike" in df_p.columns:
                        df_p = df_p.iloc[(df_p["strike"]-cur_p).abs().argsort()[:35]]
                    if "impliedVolatility" in df_p.columns:
                        df_p["IV%"] = df_p["impliedVolatility"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A")
                        df_p.drop(columns=["impliedVolatility"],inplace=True)
                    navy_grid(df_p.reset_index(drop=True), height=360, key="puts_g")
                else: interrupted("Put chain unavailable.")
            with t_iv:
                if not calls.empty and "impliedVolatility" in calls.columns and "strike" in calls.columns:
                    iv_c = calls[["strike","impliedVolatility"]].dropna()
                    if cur_p: iv_c = iv_c[(iv_c["strike"]>cur_p*0.70)&(iv_c["strike"]<cur_p*1.30)]
                    iv_c = iv_c.sort_values("strike")
                    fig_iv = go.Figure()
                    fig_iv.add_trace(go.Scatter(x=iv_c["strike"],y=iv_c["impliedVolatility"]*100,mode="lines+markers",
                                                name="Call IV",line=dict(color="#F5A623",width=2),marker=dict(size=6)))
                    if not puts.empty and "impliedVolatility" in puts.columns:
                        iv_p = puts[["strike","impliedVolatility"]].dropna()
                        if cur_p: iv_p = iv_p[(iv_p["strike"]>cur_p*0.70)&(iv_p["strike"]<cur_p*1.30)]
                        iv_p = iv_p.sort_values("strike")
                        fig_iv.add_trace(go.Scatter(x=iv_p["strike"],y=iv_p["impliedVolatility"]*100,mode="lines+markers",
                                                    name="Put IV",line=dict(color="#3B8EF0",width=2),marker=dict(size=6)))
                    if cur_p: fig_iv.add_vline(x=cur_p,line_dash="dash",line_color="#00FF88",
                                               annotation_text=f"Spot ${cur_p:.2f}",annotation_font_color="#00FF88")
                    fig_iv.update_layout(**_pla({"height":360,"title":f"IV Smile — {tkr_o}",
                                                "xaxis":yaxis_plain("Strike ($)"),"yaxis":yaxis_plain("IV (%)")}))
                    st.plotly_chart(fig_iv, use_container_width=True)
                else: interrupted("IV data unavailable.")
            with t_oi:
                if not calls.empty and not puts.empty and "openInterest" in calls.columns and "openInterest" in puts.columns:
                    oi_c = calls[["strike","openInterest"]].dropna().rename(columns={"openInterest":"Call OI"})
                    oi_p = puts[["strike","openInterest"]].dropna().rename(columns={"openInterest":"Put OI"})
                    oi_m = oi_c.merge(oi_p,on="strike",how="outer").fillna(0).sort_values("strike")
                    if cur_p: oi_m = oi_m[(oi_m["strike"]>cur_p*0.75)&(oi_m["strike"]<cur_p*1.25)]
                    fig_oi = go.Figure()
                    fig_oi.add_trace(go.Bar(x=oi_m["strike"],y=oi_m["Call OI"],name="Call OI",marker_color="#00FF88",opacity=0.75))
                    fig_oi.add_trace(go.Bar(x=oi_m["strike"],y=-oi_m["Put OI"],name="Put OI",marker_color="#FF3B3B",opacity=0.75))
                    if cur_p: fig_oi.add_vline(x=cur_p,line_dash="dash",line_color="#F5A623",annotation_text=f"Spot ${cur_p:.2f}")
                    fig_oi.update_layout(**_pla({"barmode":"overlay","height":340,"title":f"OI Distribution — {tkr_o}",
                                                "xaxis":yaxis_plain("Strike ($)"),"yaxis":yaxis_plain("Open Interest")}))
                    st.plotly_chart(fig_oi, use_container_width=True)
                else: interrupted("OI data unavailable.")


# ══════════════════════════════════════════════════════════
#  PAGE: FX & COMMODITIES
# ══════════════════════════════════════════════════════════
elif choice == "FX & Commodities":
    ptitle("FX & COMMODITIES","Currency pairs · Precious metals · Energy · Agricultural · Soft commodities")

    t_fx, t_met, t_en, t_ag = st.tabs(["🌐 FX Majors","🥇 Metals","⛽ Energy","🌾 Agricultural"])

    with t_fx:
        FX_PAIRS = {
            "EUR/USD":"EURUSD=X","GBP/USD":"GBPUSD=X","USD/JPY":"USDJPY=X","USD/CHF":"USDCHF=X",
            "AUD/USD":"AUDUSD=X","NZD/USD":"NZDUSD=X","USD/CAD":"USDCAD=X","USD/CNY":"USDCNY=X",
            "USD/SEK":"USDSEK=X","USD/NOK":"USDNOK=X","USD/BRL":"USDBRL=X","USD/MXN":"USDMXN=X",
            "USD/INR":"USDINR=X","EUR/GBP":"EURGBP=X","EUR/JPY":"EURJPY=X","DXY":"DX-Y.NYB",
        }
        sec("MAJOR CURRENCY PAIRS")
        fc = st.columns(4)
        for i,(nm,tk) in enumerate(FX_PAIRS.items()):
            p,c = yf_price_chg(tk); fc[i%4].metric(nm, f"{p:.4f}" if p else "N/A", f"{c:+.3f}%" if c else "—")
        fx_sel = st.multiselect("Chart pairs", list(FX_PAIRS.keys()), default=["EUR/USD","GBP/USD","USD/JPY","DXY"])
        fx_per = st.selectbox("Period",["1mo","3mo","6mo","1y","3y","5y"],index=3,key="fx_per")
        if fx_sel:
            fr_fx = {nm:s for nm in fx_sel for s in [_get_close(FX_PAIRS[nm],period=fx_per)] if not s.empty}
            if fr_fx:
                d_fx = pd.DataFrame(fr_fx).dropna(how="all").ffill()
                r_fx = ((d_fx/d_fx.iloc[0])-1)*100
                fig_fx = go.Figure()
                for ix,col in enumerate(r_fx.columns):
                    r_sub = _subsample(r_fx[col])
                    fig_fx.add_trace(go.Scatter(x=r_sub.index,y=r_sub,name=col,line=dict(width=1.8,color=COLORS[ix%len(COLORS)])))
                fig_fx.add_hline(y=0,line_dash="dot",line_color="#141414")
                fig_fx.update_layout(**_pla({"xaxis":xaxis_time(),"yaxis":yaxis_plain("Return %"),"height":360,"title":"FX Performance"}))
                st.plotly_chart(fig_fx, use_container_width=True)

    with t_met:
        METALS = {"Gold":"GC=F","Silver":"SI=F","Platinum":"PL=F","Palladium":"PA=F","Copper":"HG=F","Aluminum":"ALI=F","GLD ETF":"GLD","SLV ETF":"SLV","GDX Miners":"GDX"}
        sec("PRECIOUS & INDUSTRIAL METALS")
        mc = st.columns(3)
        for i,(nm,tk) in enumerate(METALS.items()):
            p,c = yf_price_chg(tk); mc[i%3].metric(nm, f"{p:,.2f}" if p else "N/A", f"{c:+.2f}%" if c else "—")
        met_per = st.selectbox("Period",["3mo","6mo","1y","3y","5y","10y","max"],index=2,key="met_per")
        fr_m = {nm:s for nm,tk in METALS.items() for s in [_get_close(tk,period=met_per)] if not s.empty}
        if fr_m:
            d_m = pd.DataFrame(fr_m).dropna(how="all").ffill()
            r_m = ((d_m/d_m.iloc[0])-1)*100
            fig_m = go.Figure()
            for ix,col in enumerate(r_m.columns):
                r_sub = _subsample(r_m[col])
                fig_m.add_trace(go.Scatter(x=r_sub.index,y=r_sub,name=col,line=dict(width=1.8,color=COLORS[ix%len(COLORS)])))
            fig_m.add_hline(y=0,line_dash="dot",line_color="#141414")
            fig_m.update_layout(**_pla({"xaxis":xaxis_time(),"yaxis":yaxis_plain("Return %"),"height":360,"title":"Metals Performance"}))
            st.plotly_chart(fig_m, use_container_width=True)

    with t_en:
        ENERGY = {"Crude WTI":"CL=F","Brent Crude":"BZ=F","Natural Gas":"NG=F","Gasoline":"RB=F","Heating Oil":"HO=F","USO ETF":"USO","UNG ETF":"UNG","XLE ETF":"XLE","OIH Services":"OIH"}
        sec("ENERGY COMMODITIES")
        ec = st.columns(3)
        for i,(nm,tk) in enumerate(ENERGY.items()):
            p,c = yf_price_chg(tk); ec[i%3].metric(nm, f"{p:,.3f}" if p else "N/A", f"{c:+.2f}%" if c else "—")
        en_per = st.selectbox("Period",["3mo","6mo","1y","3y","5y"],index=2,key="en_per")
        fr_e = {nm:s for nm,tk in ENERGY.items() for s in [_get_close(tk,period=en_per)] if not s.empty}
        if fr_e:
            d_e = pd.DataFrame(fr_e).dropna(how="all").ffill()
            r_e = ((d_e/d_e.iloc[0])-1)*100
            fig_e = go.Figure()
            for ix,col in enumerate(r_e.columns):
                r_sub = _subsample(r_e[col])
                fig_e.add_trace(go.Scatter(x=r_sub.index,y=r_sub,name=col,line=dict(width=1.8,color=COLORS[ix%len(COLORS)])))
            fig_e.add_hline(y=0,line_dash="dot",line_color="#141414")
            fig_e.update_layout(**_pla({"xaxis":xaxis_time(),"yaxis":yaxis_plain("Return %"),"height":360,"title":"Energy Performance"}))
            st.plotly_chart(fig_e, use_container_width=True)

    with t_ag:
        AGRI = {"Corn":"ZC=F","Soybeans":"ZS=F","Wheat":"ZW=F","Coffee":"KC=F","Cotton":"CT=F","Sugar":"SB=F","Orange Juice":"OJ=F","Live Cattle":"LE=F","Lean Hogs":"HE=F","DBA ETF":"DBA"}
        sec("AGRICULTURAL COMMODITIES")
        ag = st.columns(4)
        for i,(nm,tk) in enumerate(AGRI.items()):
            p,c = yf_price_chg(tk); ag[i%4].metric(nm, f"{p:,.3f}" if p else "N/A", f"{c:+.2f}%" if c else "—")


# ══════════════════════════════════════════════════════════
#  PAGE: ECONOMIC CALENDAR  — FIX #2 (bypass yfinance)
# ══════════════════════════════════════════════════════════
elif choice == "Economic Calendar":
    ptitle("ECONOMIC CALENDAR","Key macro events · Earnings dates · FRED proxies · Reference links")

    sec("REAL-TIME MACRO PROXIES")
    MACRO_T = {
        "^VIX (Fear)":"^VIX","^MOVE (Bond Vol)":"^MOVE","HYG (Credit)":"HYG",
        "LQD (IG Credit)":"LQD","TLT (Duration)":"TLT","DXY (USD)":"DX-Y.NYB",
        "GLD (Gold)":"GLD","CL=F (WTI Oil)":"CL=F","BTC-USD":"BTC-USD",
        "EEM (EM Risk)":"EEM","EUR/USD":"EURUSD=X","^TNX (10Y Yield)":"^TNX",
    }
    mc_c = st.columns(4)
    for i,(nm,tk) in enumerate(MACRO_T.items()):
        p,c = yf_price_chg(tk); mc_c[i%4].metric(nm, f"{p:,.3f}" if p else "N/A", f"{c:+.3f}%" if c else "—")

    st.markdown("---")

    # FIX #2 — EARNINGS CALENDAR bypass via direct HTTP scrape
    sec("EARNINGS CALENDAR — NEXT UPCOMING")
    earn_tickers = ["AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","JPM","GS","BAC",
                    "V","MA","NFLX","ADBE","CRM","INTC","AMD","AVGO","ASML.AS","SAP.DE"]

    earn_refresh = st.button("🔄 Refresh Earnings Calendar", key="earn_refresh")
    earn_cache_key = "earn_cal_v2"

    if earn_cache_key not in st.session_state or earn_refresh:
        with st.spinner("Fetching earnings dates via Yahoo Finance API…"):
            earn_df = fetch_earnings_calendar_web(earn_tickers)
        st.session_state[earn_cache_key] = earn_df

    earn_df = st.session_state[earn_cache_key]
    if not earn_df.empty:
        # Sort: known dates first, then "—"
        earn_df_sorted = earn_df.copy()
        earn_df_sorted["_sort"] = earn_df_sorted["Earnings Date"].apply(
            lambda x: x if x != "—" else "9999-99-99"
        )
        earn_df_sorted = earn_df_sorted.sort_values("_sort").drop(columns=["_sort"])
        navy_grid(earn_df_sorted.reset_index(drop=True), height=320, key="earn_cal_v2_grid")
        # Summary stats
        known = earn_df_sorted[earn_df_sorted["Earnings Date"] != "—"]
        st.caption(f"{len(known)} of {len(earn_df_sorted)} tickers have confirmed upcoming earnings dates.")
    else:
        st.info("Earnings calendar data temporarily unavailable. Try refreshing.")

    st.markdown("---")
    sec("FRED LIVE SNAPSHOT")
    FRED_SNAP = {"Fed Funds Rate":"FEDFUNDS","Unemployment":"UNRATE","CPI YoY":"CPIAUCSL","10Y Yield":"DGS10","10Y-2Y Spread":"T10Y2Y","VIX (FRED)":"VIXCLS"}
    fs_c = st.columns(3)
    for i,(nm,sid) in enumerate(FRED_SNAP.items()):
        s = fetch_fred(sid)
        if not s.empty:
            val  = float(s.iloc[-1])
            prev = float(s.iloc[-2]) if len(s)>1 else val
            fs_c[i%3].metric(nm, f"{val:,.3f}", f"{val-prev:+.3f}")

    st.markdown("---")
    sec("KEY DATA SOURCES")
    SOURCES = {
        "US Economic Data (FRED)": "https://fred.stlouisfed.org",
        "Fed Calendar":            "https://www.federalreserve.gov/newsevents/calendar.htm",
        "ECB Calendars":           "https://www.ecb.europa.eu/press/calendars",
        "Earnings Whispers":       "https://www.earningswhispers.com",
        "CME FedWatch Tool":       "https://www.cmegroup.com/trading/interest-rates/countdown-to-fomc.html",
        "SEC EDGAR":               "https://www.sec.gov/cgi-bin/browse-edgar",
        "OpenBB Platform":         "https://openbb.co",
    }
    for nm, url in SOURCES.items():
        st.markdown(
            f"<div class='term-box' style='padding:0.38rem 0.88rem;margin-bottom:4px'>"
            f"<a href='{url}' target='_blank' style='color:#F5A623;font-family:IBM Plex Mono,monospace;"
            f"font-size:0.73rem;text-decoration:none'>{nm} → {url}</a></div>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════
#  PAGE: DYNAMIC CHART ENGINE (DCE)  — FIX #6
#  New module: interactive, user-configurable charts
#  from any in-session dataset (Screener, OHLCV, custom CSV).
# ══════════════════════════════════════════════════════════
elif choice == "Dynamic Chart Engine":
    st.markdown("""
    <div class='dce-header'>
      <div class='dce-title'>⚡ DYNAMIC CHART ENGINE  ·  DCE v1.0</div>
      <div class='dce-sub'>User-configurable axis · Multi-metric overlay · Live dataset injection · Plotly black renderer</div>
    </div>""", unsafe_allow_html=True)

    # ── Dataset Selector ───────────────────────────────────
    sec("DATA SOURCE")
    dataset_options = ["Stock Screener (loaded)", "OHLCV — fetch ticker", "Custom tickers — multi-metric", "Upload CSV"]
    ds_choice = st.selectbox("Select dataset", dataset_options, key="dce_ds")

    dce_df: pd.DataFrame | None = None

    if ds_choice == "Stock Screener (loaded)":
        if st.session_state.screener_df is not None and not st.session_state.screener_df.empty:
            dce_df = st.session_state.screener_df.copy()
            st.success(f"✅ Screener dataset loaded — {len(dce_df):,} rows, {len(dce_df.columns)} columns")
        else:
            st.warning("Screener data not loaded. Go to **Stock Screener** tab first and load data.")
            st.stop()

    elif ds_choice == "OHLCV — fetch ticker":
        dc1, dc2, dc3 = st.columns(3)
        with dc1: dce_tkr = st.text_input("Ticker", "AAPL", key="dce_tkr")
        with dc2: dce_per = st.selectbox("Period", ["1mo","3mo","6mo","1y","2y","5y","10y","max"], index=3, key="dce_per")
        with dc3: dce_int = st.selectbox("Interval", ["1d","1wk","1mo"], index=0, key="dce_int")
        if dce_tkr.strip():
            raw_df = _get_ohlcv(dce_tkr.strip().upper(), period=dce_per, interval=dce_int)
            if not raw_df.empty:
                dce_df = raw_df.reset_index()
                # Add computed columns
                dce_df["Return%"]    = dce_df["Close"].pct_change() * 100
                dce_df["SMA_20"]     = dce_df["Close"].rolling(20).mean()
                dce_df["SMA_50"]     = dce_df["Close"].rolling(50).mean()
                dce_df["Volatility"] = dce_df["Return%"].rolling(20).std()
                dce_df["Date"]       = dce_df.iloc[:,0].astype(str)
                st.success(f"✅ {dce_tkr.upper()} OHLCV loaded — {len(dce_df)} rows")
            else:
                st.warning(f"No data for {dce_tkr.strip().upper()}")
                st.stop()

    elif ds_choice == "Custom tickers — multi-metric":
        dc_in = st.text_input("Tickers (comma-separated)", "AAPL,MSFT,NVDA,GOOGL,TSLA", key="dce_multi_in")
        dc_per = st.selectbox("Period", ["3mo","6mo","1y","2y","5y"], index=2, key="dce_multi_per")
        tk_list_dce = [x.strip().upper() for x in dc_in.split(",") if x.strip()]
        if tk_list_dce:
            # Build cross-sectional fundamental comparison DataFrame
            rows_dce = []
            for tkr_dce in tk_list_dce:
                inf_dce = yf_info(tkr_dce)
                if not inf_dce:
                    continue
                p_dce, c_dce = yf_price_chg(tkr_dce)
                rows_dce.append({
                    "Ticker":    tkr_dce,
                    "Name":      (inf_dce.get("shortName") or tkr_dce)[:20],
                    "Price":     p_dce or 0,
                    "Change%":   c_dce or 0,
                    "MarketCap_B": (inf_dce.get("marketCap") or 0) / 1e9,
                    "P/E":       inf_dce.get("forwardPE") or 0,
                    "P/B":       inf_dce.get("priceToBook") or 0,
                    "EV/EBITDA": inf_dce.get("enterpriseToEbitda") or 0,
                    "ROE%":      (inf_dce.get("returnOnEquity") or 0) * 100,
                    "OpMgn%":    (inf_dce.get("operatingMargins") or 0) * 100,
                    "Beta":      inf_dce.get("beta") or 0,
                    "Div%":      (inf_dce.get("dividendYield") or 0) * 100,
                    "Rev_B":     (inf_dce.get("totalRevenue") or 0) / 1e9,
                    "FCF_B":     (inf_dce.get("freeCashflow") or 0) / 1e9,
                })
            if rows_dce:
                dce_df = pd.DataFrame(rows_dce)
                st.success(f"✅ {len(dce_df)} tickers loaded with fundamental metrics")
            else:
                st.warning("No data returned. Check tickers.")
                st.stop()

    elif ds_choice == "Upload CSV":
        uploaded = st.file_uploader("Upload CSV file", type=["csv"], key="dce_upload")
        if uploaded is not None:
            try:
                dce_df = pd.read_csv(uploaded)
                st.success(f"✅ CSV loaded — {len(dce_df)} rows, {len(dce_df.columns)} columns")
            except Exception as e:
                st.error(f"CSV parse error: {e}")
                st.stop()
        else:
            st.info("Upload a CSV file to begin. The first row should be column headers.")
            st.stop()

    if dce_df is None or dce_df.empty:
        st.stop()

    # ── Preview ────────────────────────────────────────────
    with st.expander("📋 Dataset Preview (first 10 rows)", expanded=False):
        navy_grid(dce_df.head(10), height=220, key="dce_preview")

    st.markdown("---")

    # ── Chart Configurator ─────────────────────────────────
    sec("CHART CONFIGURATOR")

    all_cols     = dce_df.columns.tolist()
    numeric_cols = dce_df.select_dtypes(include=[np.number]).columns.tolist()
    any_cols     = all_cols

    cc1, cc2, cc3, cc4 = st.columns(4)
    with cc1:
        chart_type = st.selectbox(
            "Chart Type",
            ["Line", "Bar", "Scatter", "Area", "Histogram", "Box", "Heatmap (correlation)"],
            key="dce_chart_type",
        )
    with cc2:
        x_axis = st.selectbox("X Axis", any_cols, key="dce_x_axis",
                              index=0 if any_cols else 0)
    with cc3:
        y_axis_multi = st.multiselect(
            "Y Axis (one or more)",
            numeric_cols,
            default=numeric_cols[:min(2, len(numeric_cols))],
            key="dce_y_axis",
        )
    with cc4:
        color_col = st.selectbox(
            "Color / Group By (optional)",
            ["None"] + any_cols,
            key="dce_color_col",
        )

    dce_opts_row = st.columns(3)
    with dce_opts_row[0]:
        chart_title = st.text_input("Chart Title", f"DCE — {ds_choice}", key="dce_title")
    with dce_opts_row[1]:
        chart_height = st.slider("Chart Height (px)", 280, 800, 460, step=20, key="dce_height")
    with dce_opts_row[2]:
        max_rows = st.slider("Max rows to plot", 50, min(5000, len(dce_df)), min(500, len(dce_df)), step=50, key="dce_max_rows")

    # ── Render ─────────────────────────────────────────────
    if not y_axis_multi and chart_type != "Heatmap (correlation)":
        st.info("Select at least one column for the Y axis.")
        st.stop()

    plot_df = dce_df.head(max_rows).copy()
    # Coerce X to string for categorical charts
    x_is_numeric = x_axis in numeric_cols
    color_by = None if color_col == "None" else color_col

    def _make_dce_chart() -> go.Figure:
        fig = go.Figure()
        base = _pla({"height": chart_height, "title": chart_title})

        if chart_type == "Heatmap (correlation)":
            cor_df = plot_df[numeric_cols].corr()
            fig = go.Figure(go.Heatmap(
                z=cor_df.values,
                x=cor_df.columns.tolist(),
                y=cor_df.index.tolist(),
                colorscale=[[0,"#FF3B3B"],[0.5,"#050505"],[1,"#00FF88"]],
                zmid=0, zmin=-1, zmax=1,
                text=cor_df.round(2).values,
                texttemplate="%{text}",
                colorbar=dict(
                    tickfont=dict(family="IBM Plex Mono", color="#7A9BB8", size=9),
                    title=dict(text="Corr", font=dict(color="#7A9BB8")),
                ),
            ))
            fig.update_layout(**base)
            return fig

        x_vals = plot_df[x_axis].astype(str) if not x_is_numeric else plot_df[x_axis]

        for ix, y_col in enumerate(y_axis_multi):
            col_color = COLORS[ix % len(COLORS)]
            y_vals = plot_df[y_col]

            if chart_type == "Line":
                fig.add_trace(go.Scatter(
                    x=x_vals, y=y_vals, name=y_col, mode="lines",
                    line=dict(width=2, color=col_color),
                ))
            elif chart_type == "Area":
                fig.add_trace(go.Scatter(
                    x=x_vals, y=y_vals, name=y_col, mode="lines",
                    line=dict(width=2, color=col_color),
                    fill="tozeroy", fillcolor=col_color.replace(")", ",0.06)").replace("rgb(", "rgba(") if col_color.startswith("rgb") else col_color + "0a",
                ))
            elif chart_type == "Bar":
                fig.add_trace(go.Bar(
                    x=x_vals, y=y_vals, name=y_col,
                    marker_color=col_color, opacity=0.82,
                ))
            elif chart_type == "Scatter":
                # If multiple Y cols, use second as size optionally
                marker_size = 6
                fig.add_trace(go.Scatter(
                    x=x_vals, y=y_vals, name=y_col, mode="markers",
                    marker=dict(size=marker_size, color=col_color, opacity=0.80,
                                line=dict(width=0.5, color="#111")),
                ))
            elif chart_type == "Histogram":
                fig.add_trace(go.Histogram(
                    x=y_vals, name=y_col,
                    marker_color=col_color, opacity=0.75, nbinsx=40,
                ))
            elif chart_type == "Box":
                fig.add_trace(go.Box(
                    y=y_vals, name=y_col,
                    marker_color=col_color,
                    line_color=col_color,
                    fillcolor=col_color + "22" if len(col_color) == 7 else col_color,
                ))

        # Layout patches
        base["xaxis"].update({"title": {"text": x_axis, "font": {"color": "#3A6A9A", "size": 10}}})
        base["yaxis"].update({"title": {"text": " / ".join(y_axis_multi[:2]), "font": {"color": "#3A6A9A", "size": 10}}})
        if chart_type == "Bar" and len(y_axis_multi) > 1:
            base["barmode"] = "group"
        fig.update_layout(**base)
        return fig

    try:
        dce_fig = _make_dce_chart()
        st.plotly_chart(dce_fig, use_container_width=True)
    except Exception as ex:
        st.error(f"Chart render error: {ex}")

    # ── Stats panel ────────────────────────────────────────
    if y_axis_multi and chart_type not in ("Heatmap (correlation)",):
        st.markdown("---")
        sec("DESCRIPTIVE STATISTICS")
        try:
            stats_df = plot_df[y_axis_multi].describe().T
            stats_df.insert(0, "Metric", stats_df.index)
            navy_grid(stats_df.reset_index(drop=True), height=200, key="dce_stats_grid")
        except Exception:
            pass

    # ── Raw data export ────────────────────────────────────
    with st.expander("📥 Export / View Full Dataset"):
        navy_grid(dce_df, height=360, key="dce_full_data")
        csv_bytes = dce_df.to_csv(index=False).encode()
        st.download_button(
            "⬇ Download as CSV",
            data=csv_bytes,
            file_name="navy_dce_export.csv",
            mime="text/csv",
            key="dce_download",
        )

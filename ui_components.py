"""
╔══════════════════════════════════════════════════════════════════╗
║   NAVY TERMINAL PRO  v6.0  ·  UI Components                      ║
║   Global CSS · AgGrid · Charts · Candle Builder · Helpers        ║
╚══════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import warnings
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

warnings.filterwarnings("ignore")

# ── AgGrid imports (graceful fallback if not installed) ───────────
try:
    from st_aggrid import (
        AgGrid,
        GridOptionsBuilder,
        JsCode,
        GridUpdateMode,
        DataReturnMode,
        ColumnsAutoSizeMode,
        AgGridTheme,
    )
    _AGGRID_AVAILABLE = True
except ImportError:
    _AGGRID_AVAILABLE = False


# ══════════════════════════════════════════════════════════
#  COLOUR PALETTE
# ══════════════════════════════════════════════════════════
COLORS: list[str] = [
    "#F5A623", "#3B8EF0", "#2ECC71", "#E74C3C", "#9B59B6",
    "#1ABC9C", "#F39C12", "#E67E22", "#34495E", "#EC407A",
    "#00BCD4", "#8BC34A", "#FF7043", "#AB47BC", "#26C6DA",
    "#66BB6A", "#FFA726", "#EF5350", "#42A5F5", "#26A69A",
]

# ══════════════════════════════════════════════════════════
#  GLOBAL CSS  — Bloomberg dark + v6 refinements
# ══════════════════════════════════════════════════════════
GLOBAL_CSS = """
<style>
/* ── Google Fonts ──────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root tokens ────────────────────────────────────────── */
:root {
  --navy-bg:        #040D18;
  --navy-panel:     #071220;
  --navy-card:      #091827;
  --navy-border:    #0D2137;
  --navy-border2:   #112844;
  --navy-blue:      #0F2A47;
  --navy-blue2:     #1E4976;
  --navy-accent:    #F5A623;
  --navy-accent2:   #D4891A;
  --navy-cyan:      #3B8EF0;
  --navy-green:     #2ECC71;
  --navy-red:       #E74C3C;
  --navy-purple:    #9B59B6;
  --navy-text:      #C8D8EC;
  --navy-text2:     #8AAEC8;
  --navy-text3:     #5A88B0;
  --navy-muted:     #1A3A5C;
  --font-mono:      'IBM Plex Mono', 'Courier New', monospace;
  --font-sans:      'Inter', system-ui, sans-serif;
  --radius-sm:      4px;
  --radius-md:      6px;
  --radius-lg:      10px;
  --shadow:         0 2px 12px rgba(0,0,0,0.55);
  --shadow-lg:      0 4px 28px rgba(0,0,0,0.70);
  --transition:     all 0.18s ease;
}

/* ── Streamlit overrides ────────────────────────────────── */
html, body, [data-testid="stApp"], .main, .block-container {
  background-color: var(--navy-bg) !important;
  color: var(--navy-text) !important;
  font-family: var(--font-sans) !important;
}

.block-container { padding: 1.2rem 2rem 3rem 2rem !important; max-width: 100% !important; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--navy-panel) !important;
  border-right: 1px solid var(--navy-border) !important;
}
[data-testid="stSidebar"] * { color: var(--navy-text3) !important; }
[data-testid="stSidebar"] button {
  background: transparent !important;
  border: none !important;
  color: var(--navy-text3) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.69rem !important;
  letter-spacing: 0.06em !important;
  padding: 0.42rem 0.7rem !important;
  text-align: left !important;
  border-radius: var(--radius-sm) !important;
  transition: var(--transition) !important;
  width: 100% !important;
}
[data-testid="stSidebar"] button:hover {
  background: var(--navy-blue) !important;
  color: var(--navy-accent) !important;
}

/* Inputs, selects, sliders */
input, select, textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
  background: var(--navy-card) !important;
  border: 1px solid var(--navy-border2) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--navy-text) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.78rem !important;
}
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stRadio"] label { color: var(--navy-text3) !important; font-size: 0.73rem !important; }

/* Metric tiles */
[data-testid="stMetricValue"] {
  font-family: var(--font-mono) !important;
  font-size: 0.95rem !important;
  font-weight: 600 !important;
  color: var(--navy-accent) !important;
}
[data-testid="stMetricLabel"] {
  font-family: var(--font-mono) !important;
  font-size: 0.62rem !important;
  color: var(--navy-text3) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
}
[data-testid="stMetricDelta"] { font-size: 0.70rem !important; }

/* Tabs */
[data-testid="stTabs"] [role="tablist"] {
  border-bottom: 1px solid var(--navy-border2) !important;
  gap: 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
  font-family: var(--font-mono) !important;
  font-size: 0.68rem !important;
  letter-spacing: 0.05em !important;
  color: var(--navy-text3) !important;
  padding: 0.45rem 1rem !important;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
  border: 1px solid transparent !important;
  transition: var(--transition) !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--navy-accent) !important;
  background: var(--navy-blue) !important;
  border-color: var(--navy-border2) !important;
  border-bottom-color: var(--navy-bg) !important;
}
[data-testid="stTabs"] [role="tab"]:hover { color: var(--navy-text) !important; }

/* Expander */
[data-testid="stExpander"] {
  background: var(--navy-card) !important;
  border: 1px solid var(--navy-border2) !important;
  border-radius: var(--radius-md) !important;
}
[data-testid="stExpander"] summary {
  font-family: var(--font-mono) !important;
  font-size: 0.73rem !important;
  color: var(--navy-text2) !important;
  letter-spacing: 0.05em !important;
}

/* Buttons */
[data-testid="stButton"] button {
  background: var(--navy-blue) !important;
  border: 1px solid var(--navy-border2) !important;
  color: var(--navy-text) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.06em !important;
  border-radius: var(--radius-sm) !important;
  transition: var(--transition) !important;
}
[data-testid="stButton"] button:hover {
  background: var(--navy-accent) !important;
  color: #000 !important;
  border-color: var(--navy-accent) !important;
}

/* Progress bar */
[data-testid="stProgressBar"] > div > div {
  background: linear-gradient(90deg, var(--navy-cyan), var(--navy-accent)) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--navy-panel); }
::-webkit-scrollbar-thumb { background: var(--navy-muted); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--navy-blue2); }

/* ── Custom component classes ───────────────────────────── */

/* Page header */
.page-header {
  padding: 1.1rem 1.4rem 0.8rem 1.4rem;
  margin-bottom: 1.4rem;
  background: linear-gradient(135deg, var(--navy-panel) 0%, var(--navy-blue) 100%);
  border: 1px solid var(--navy-border2);
  border-left: 3px solid var(--navy-accent);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}
.page-header-title {
  font-family: var(--font-mono);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--navy-accent);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin: 0;
}
.page-header-sub {
  font-family: var(--font-mono);
  font-size: 0.60rem;
  color: var(--navy-text3);
  letter-spacing: 0.10em;
  margin-top: 3px;
  text-transform: uppercase;
}

/* Section header */
.sec-hdr {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--navy-text3);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  padding: 0.55rem 0 0.3rem 0;
  border-bottom: 1px solid var(--navy-border);
  margin-bottom: 0.7rem;
}

/* Ticker card */
.ticker-card {
  background: linear-gradient(135deg, var(--navy-panel) 0%, var(--navy-blue) 100%);
  border: 1px solid var(--navy-border2);
  border-radius: var(--radius-lg);
  padding: 1.1rem 1.4rem;
  margin-bottom: 1.1rem;
  box-shadow: var(--shadow);
}
.ticker-tag {
  font-family: var(--font-mono);
  font-size: 0.60rem;
  color: var(--navy-text3);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.ticker-name {
  font-family: var(--font-sans);
  font-size: 1.30rem;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 3px;
}
.ticker-meta {
  font-family: var(--font-mono);
  font-size: 0.66rem;
  color: var(--navy-text3);
  letter-spacing: 0.06em;
}
.ticker-price {
  font-family: var(--font-mono);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--navy-accent);
  letter-spacing: -0.01em;
}

/* Mover card */
.mover-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.42rem 0.75rem;
  margin-bottom: 5px;
  background: var(--navy-card);
  border-radius: var(--radius-sm);
  border: 1px solid var(--navy-border);
}

/* Term box */
.term-box {
  background: var(--navy-card);
  border: 1px solid var(--navy-border2);
  border-radius: var(--radius-sm);
  padding: 0.65rem 0.9rem;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--navy-text2);
  line-height: 1.7;
  margin-bottom: 0.5rem;
}

/* Alert / info boxes */
.navy-alert {
  border-left: 3px solid var(--navy-accent);
  background: rgba(15, 42, 71, 0.55);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  padding: 0.55rem 0.9rem;
  margin: 0.35rem 0;
  font-family: var(--font-mono);
  font-size: 0.73rem;
  color: var(--navy-text);
  line-height: 1.65;
}

/* Badge */
.src-badge {
  display: inline-block;
  background: var(--navy-blue2);
  color: var(--navy-accent);
  font-family: var(--font-mono);
  font-size: 0.52rem;
  font-weight: 600;
  letter-spacing: 0.10em;
  padding: 1px 6px;
  border-radius: 2px;
  text-transform: uppercase;
  vertical-align: middle;
}
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 9px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 0.60rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.status-badge.live    { background: rgba(46,204,113,0.15); color: var(--navy-green); border: 1px solid rgba(46,204,113,0.3); }
.status-badge.warning { background: rgba(245,166,35,0.15); color: var(--navy-accent); border: 1px solid rgba(245,166,35,0.3); }
.status-badge.error   { background: rgba(231,76,60,0.15);  color: var(--navy-red);    border: 1px solid rgba(231,76,60,0.3); }

/* Screener filter panel */
.screener-filter-panel {
  background: var(--navy-panel);
  border: 1px solid var(--navy-border2);
  border-radius: var(--radius-lg);
  padding: 1.0rem 1.2rem;
  margin-bottom: 1.1rem;
}
.screener-filter-title {
  font-family: var(--font-mono);
  font-size: 0.63rem;
  font-weight: 600;
  color: var(--navy-accent);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 0.7rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid var(--navy-border);
}
.screener-stats-bar {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  padding: 0.55rem 1rem;
  background: var(--navy-card);
  border: 1px solid var(--navy-border2);
  border-radius: var(--radius-sm);
  margin-bottom: 0.8rem;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--navy-text3);
}
.screener-stats-bar b { color: var(--navy-accent); }

/* Sidebar nav */
.nav-title {
  font-family: var(--font-mono);
  font-size: 1.10rem;
  font-weight: 700;
  color: var(--navy-accent);
  letter-spacing: 0.18em;
}
.nav-sub {
  font-family: var(--font-mono);
  font-size: 0.52rem;
  color: var(--navy-text3);
  letter-spacing: 0.12em;
  margin-top: 2px;
  text-transform: uppercase;
}
.nav-divider {
  height: 1px;
  background: linear-gradient(90deg, var(--navy-border2), transparent);
  margin: 0.6rem 0;
}

/* Interrupted / no-data notice */
.interrupted-notice {
  padding: 0.55rem 0.9rem;
  background: rgba(90,136,176,0.08);
  border: 1px dashed var(--navy-muted);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 0.70rem;
  color: var(--navy-text3);
}

/* Plotly chart background override */
.js-plotly-plot .plotly, .plotly-graph-div {
  background: transparent !important;
}
</style>
"""


# ══════════════════════════════════════════════════════════
#  PLOTLY LAYOUT HELPERS
# ══════════════════════════════════════════════════════════

_PLOTLY_BASE = dict(
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "rgba(0,0,0,0)",
    font          = dict(family="IBM Plex Mono, monospace", size=11, color="#8AAEC8"),
    legend        = dict(bgcolor="rgba(4,13,24,0.7)", bordercolor="#0D2137",
                         borderwidth=1, font=dict(size=10)),
    margin        = dict(l=48, r=24, t=44, b=38),
    hovermode     = "x unified",
    hoverlabel    = dict(bgcolor="#071220", bordercolor="#0D2137",
                         font=dict(family="IBM Plex Mono", size=11, color="#C8D8EC")),
)


def pla(overrides: dict | None = None) -> dict:
    """Merge plotly base layout with caller overrides."""
    out = dict(_PLOTLY_BASE)
    if overrides:
        out.update(overrides)
    return out


def xaxis_time() -> dict:
    return dict(
        gridcolor="#091827", showgrid=True,
        tickfont=dict(family="IBM Plex Mono", size=9, color="#5A88B0"),
        rangeslider=dict(visible=False),
        type="date",
    )


def yaxis_plain(title: str = "") -> dict:
    return dict(
        gridcolor="#091827", showgrid=True, zeroline=False,
        tickfont=dict(family="IBM Plex Mono", size=9, color="#5A88B0"),
        title=dict(text=title, font=dict(size=10, color="#5A88B0")) if title else {},
    )


# ══════════════════════════════════════════════════════════
#  AGGRID — INSTITUTIONAL SCREENER GRID
# ══════════════════════════════════════════════════════════

# ── Cell renderer JS strings ─────────────────────────────
_JS_CHANGE_CELL = """
class ChangeCellRenderer {
  init(params) {
    this.eGui = document.createElement('span');
    const v = parseFloat(params.value);
    if (isNaN(v)) { this.eGui.innerText = 'N/A'; this.eGui.style.color = '#5A88B0'; return; }
    const color  = v >= 0 ? '#2ECC71' : '#E74C3C';
    const bg     = v >= 0 ? 'rgba(46,204,113,0.12)' : 'rgba(231,76,60,0.12)';
    const arrow  = v >= 0 ? '▲' : '▼';
    this.eGui.style.cssText = `color:${color};background:${bg};padding:1px 6px;border-radius:3px;font-family:IBM Plex Mono,monospace;font-size:11px;font-weight:600`;
    this.eGui.innerText = arrow + ' ' + Math.abs(v).toFixed(2) + '%';
  }
  getGui() { return this.eGui; }
}
"""

_JS_MCAP_CELL = """
class McapCellRenderer {
  init(params) {
    this.eGui = document.createElement('span');
    const v = parseFloat(params.value);
    if (isNaN(v)) { this.eGui.innerText = 'N/A'; this.eGui.style.color = '#5A88B0'; return; }
    let txt;
    if (v >= 1000) txt = (v/1000).toFixed(2) + 'T';
    else if (v >= 1) txt = v.toFixed(2) + 'B';
    else txt = (v*1000).toFixed(0) + 'M';
    this.eGui.style.cssText = 'color:#C8D8EC;font-family:IBM Plex Mono,monospace;font-size:11px';
    this.eGui.innerText = txt;
  }
  getGui() { return this.eGui; }
}
"""

_JS_TICKER_CELL = """
class TickerCellRenderer {
  init(params) {
    this.eGui = document.createElement('span');
    this.eGui.style.cssText = 'color:#F5A623;font-family:IBM Plex Mono,monospace;font-size:11px;font-weight:700;letter-spacing:0.04em';
    this.eGui.innerText = params.value || '';
  }
  getGui() { return this.eGui; }
}
"""

_JS_PE_CELL = """
class PeCellRenderer {
  init(params) {
    this.eGui = document.createElement('span');
    const v = parseFloat(params.value);
    if (isNaN(v)) { this.eGui.innerText = 'N/A'; this.eGui.style.color = '#5A88B0'; return; }
    let color = '#C8D8EC';
    if (v < 15) color = '#2ECC71';
    else if (v > 50) color = '#E74C3C';
    else if (v > 30) color = '#F5A623';
    this.eGui.style.cssText = `color:${color};font-family:IBM Plex Mono,monospace;font-size:11px`;
    this.eGui.innerText = v.toFixed(1);
  }
  getGui() { return this.eGui; }
}
"""

# ── Custom AgGrid CSS ─────────────────────────────────────
_AGGRID_CUSTOM_CSS = {
    ".ag-root-wrapper": {
        "background-color": "#071220 !important",
        "border": "1px solid #0D2137 !important",
        "border-radius": "6px !important",
    },
    ".ag-header": {
        "background-color": "#040D18 !important",
        "border-bottom": "1px solid #0D2137 !important",
    },
    ".ag-header-cell": {
        "color": "#5A88B0 !important",
        "font-family": "IBM Plex Mono, monospace !important",
        "font-size": "10px !important",
        "font-weight": "600 !important",
        "letter-spacing": "0.10em !important",
        "text-transform": "uppercase !important",
        "background-color": "#040D18 !important",
    },
    ".ag-header-cell:hover": {
        "background-color": "#091827 !important",
    },
    ".ag-row": {
        "background-color": "#071220 !important",
        "border-bottom": "1px solid #091827 !important",
        "font-family": "IBM Plex Mono, monospace !important",
        "font-size": "11px !important",
        "color": "#C8D8EC !important",
    },
    ".ag-row:hover": {
        "background-color": "#0F2A47 !important",
        "cursor": "pointer !important",
    },
    ".ag-row-selected": {
        "background-color": "#1E4976 !important",
    },
    ".ag-cell": {
        "border-right": "1px solid #091827 !important",
        "padding": "0 8px !important",
    },
    ".ag-pinned-left-cols-container .ag-cell": {
        "background-color": "#040D18 !important",
        "border-right": "1px solid #112844 !important",
    },
    ".ag-body-viewport": {
        "background-color": "#071220 !important",
    },
    ".ag-overlay-loading-center": {
        "background-color": "#071220 !important",
        "color": "#F5A623 !important",
        "font-family": "IBM Plex Mono !important",
        "font-size": "12px !important",
        "border": "1px solid #0D2137 !important",
        "border-radius": "4px !important",
        "padding": "10px 20px !important",
    },
    ".ag-tool-panel-wrapper": {
        "background-color": "#040D18 !important",
        "border-left": "1px solid #0D2137 !important",
        "color": "#8AAEC8 !important",
    },
    ".ag-paging-panel": {
        "background-color": "#040D18 !important",
        "border-top": "1px solid #0D2137 !important",
        "color": "#5A88B0 !important",
        "font-family": "IBM Plex Mono, monospace !important",
        "font-size": "10px !important",
    },
    ".ag-paging-button": {
        "color": "#F5A623 !important",
    },
    ".ag-icon": {
        "color": "#5A88B0 !important",
    },
    ".ag-filter-toolpanel-group-title-bar": {
        "background-color": "#091827 !important",
    },
    ".ag-column-drop-horizontal": {
        "background-color": "#040D18 !important",
    },
    ".ag-status-bar": {
        "background-color": "#040D18 !important",
        "border-top": "1px solid #0D2137 !important",
        "color": "#5A88B0 !important",
        "font-family": "IBM Plex Mono, monospace !important",
        "font-size": "10px !important",
    },
}


def screener_aggrid(
    df: pd.DataFrame,
    height: int = 560,
    key: str = "screener_grid",
    page_size: int = 50,
) -> Any:
    """
    Render the Bloomberg-style institutional screener grid using AgGrid.
    Applies neon-green / crimson conditional formatting on Change_Pct,
    colour-coded P/E, ticker pinning, sidebar filters, and column sorting.
    Falls back to st.dataframe if AgGrid is unavailable.
    """
    if df is None or df.empty:
        st.markdown(
            "<div class='interrupted-notice'>⚠ No data to display.</div>",
            unsafe_allow_html=True,
        )
        return None

    if not _AGGRID_AVAILABLE:
        st.dataframe(df, use_container_width=True, height=height)
        return None

    # Work on a display copy
    display_df = df.copy()

    # Round numeric columns for display
    for col in ["MarketCap_B", "PE", "Price", "Change_Pct", "Volume"]:
        if col in display_df.columns:
            display_df[col] = pd.to_numeric(display_df[col], errors="coerce")

    gb = GridOptionsBuilder.from_dataframe(display_df)

    # ── Default column settings ───────────────────────────
    gb.configure_default_column(
        resizable=True,
        sortable=True,
        filter=True,
        floatingFilter=True,
        suppressMenu=False,
        wrapHeaderText=True,
        autoHeaderHeight=True,
        minWidth=60,
    )

    # ── Per-column configuration ──────────────────────────
    gb.configure_column(
        "Ticker",
        header_name="TICKER",
        pinned="left",
        width=90,
        cellRenderer=JsCode(_JS_TICKER_CELL),
    )
    gb.configure_column(
        "Name",
        header_name="COMPANY",
        pinned="left",
        width=180,
        filter="agTextColumnFilter",
    )
    gb.configure_column(
        "Sector",
        header_name="SECTOR",
        width=130,
        filter="agSetColumnFilter",
    )
    gb.configure_column(
        "Industry",
        header_name="INDUSTRY",
        width=150,
        filter="agSetColumnFilter",
    )
    gb.configure_column(
        "Country",
        header_name="COUNTRY",
        width=100,
        filter="agSetColumnFilter",
    )
    gb.configure_column(
        "Price",
        header_name="PRICE",
        width=88,
        type=["numericColumn"],
        valueFormatter=JsCode("""
            function(params) {
                if (params.value == null || isNaN(params.value)) return 'N/A';
                return params.value.toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:4});
            }
        """),
    )
    gb.configure_column(
        "Change_Pct",
        header_name="CHG%",
        width=95,
        type=["numericColumn"],
        cellRenderer=JsCode(_JS_CHANGE_CELL),
    )
    gb.configure_column(
        "MarketCap_B",
        header_name="MCAP",
        width=95,
        type=["numericColumn"],
        cellRenderer=JsCode(_JS_MCAP_CELL),
    )
    gb.configure_column(
        "PE",
        header_name="P/E",
        width=72,
        type=["numericColumn"],
        cellRenderer=JsCode(_JS_PE_CELL),
    )
    gb.configure_column(
        "Volume",
        header_name="VOLUME",
        width=110,
        type=["numericColumn"],
        valueFormatter=JsCode("""
            function(params) {
                if (params.value == null || isNaN(params.value)) return 'N/A';
                if (params.value >= 1e9) return (params.value/1e9).toFixed(2) + 'B';
                if (params.value >= 1e6) return (params.value/1e6).toFixed(2) + 'M';
                if (params.value >= 1e3) return (params.value/1e3).toFixed(1) + 'K';
                return params.value.toFixed(0);
            }
        """),
    )
    if "Source" in display_df.columns:
        gb.configure_column(
            "Source",
            header_name="SRC",
            width=80,
        )

    # ── Grid-level options ────────────────────────────────
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_side_bar(filters_panel=True, columns_panel=True)
    gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=page_size)
    gb.configure_grid_options(
        rowHeight=26,
        headerHeight=34,
        enableRangeSelection=True,
        suppressCopyRowsToClipboard=False,
        domLayout="normal",
        animateRows=True,
        rowSelection="single",
        suppressFieldDotNotation=True,
        enableStatusBar=True,
        statusBar={
            "statusPanels": [
                {"statusPanel": "agTotalAndFilteredRowCountComponent", "align": "left"},
                {"statusPanel": "agAggregationComponent",              "align": "right"},
            ]
        },
    )

    grid_options = gb.build()

    result = AgGrid(
        data               = display_df,
        gridOptions        = grid_options,
        height             = height,
        theme              = AgGridTheme.BALHAM,
        custom_css         = _AGGRID_CUSTOM_CSS,
        allow_unsafe_jscode= True,
        update_mode        = GridUpdateMode.SELECTION_CHANGED,
        data_return_mode   = DataReturnMode.FILTERED_AND_SORTED,
        columns_auto_size_mode = ColumnsAutoSizeMode.NO_AUTOSIZE,
        key                = key,
    )
    return result


def navy_grid(
    df: pd.DataFrame,
    height: int = 300,
    key: str = "grid",
) -> Any:
    """
    General-purpose institutional-styled AgGrid for non-screener tables
    (financials, peers, holders, etc.).  Falls back to st.dataframe gracefully.
    """
    if df is None or df.empty:
        st.markdown(
            "<div class='interrupted-notice'>No data available.</div>",
            unsafe_allow_html=True,
        )
        return None

    if not _AGGRID_AVAILABLE:
        st.dataframe(df, use_container_width=True, height=height)
        return None

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        resizable=True,
        sortable=True,
        filter=True,
        minWidth=60,
    )
    gb.configure_grid_options(
        rowHeight=24,
        headerHeight=30,
        domLayout="normal",
        animateRows=True,
        suppressFieldDotNotation=True,
    )
    go_opts = gb.build()

    result = AgGrid(
        data               = df,
        gridOptions        = go_opts,
        height             = height,
        theme              = AgGridTheme.BALHAM,
        custom_css         = _AGGRID_CUSTOM_CSS,
        allow_unsafe_jscode= True,
        update_mode        = GridUpdateMode.NO_UPDATE,
        key                = key,
    )
    return result


# ══════════════════════════════════════════════════════════
#  CANDLESTICK CHART BUILDER
# ══════════════════════════════════════════════════════════

def build_candle_chart(
    ticker:    str,
    df:        pd.DataFrame,
    indicators: list[str],
    subtitle:  str = "",
) -> go.Figure:
    """
    Build a full Plotly candlestick chart with the selected technical
    indicators.  MACD and RSI get their own subplot rows.
    """
    # Import from quant_engine inline to avoid circular import
    from quant_engine import (
        rsi as _rsi, macd as _macd, atr as _atr, fibonacci as _fib,
        stochastic as _stoch, williams_r as _williams_r, cci as _cci,
        obv as _obv, vwap as _vwap, ichimoku as _ichimoku,
        bollinger_bands as _boll,
    )

    need_macd = "MACD" in indicators
    need_rsi  = "RSI"  in indicators
    extra_rows = int(need_macd) + int(need_rsi)
    total_rows = 1 + extra_rows

    row_heights = [0.60] if extra_rows == 0 else (
        [0.55, 0.22, 0.23] if extra_rows == 2 else [0.65, 0.35]
    )

    fig = make_subplots(
        rows         = total_rows,
        cols         = 1,
        shared_xaxes = True,
        vertical_spacing = 0.04,
        row_heights  = row_heights[:total_rows],
    )

    close   = df["Close"]
    high    = df["High"]
    low     = df["Low"]
    open_   = df["Open"]
    volume  = df.get("Volume", pd.Series(dtype=float))

    # ── Candlestick ───────────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=df.index, open=open_, high=high, low=low, close=close,
        name=ticker,
        increasing_line_color="#2ECC71", increasing_fillcolor="rgba(46,204,113,0.55)",
        decreasing_line_color="#E74C3C", decreasing_fillcolor="rgba(231,76,60,0.55)",
        line=dict(width=1),
    ), row=1, col=1)

    # ── Volume bars (on main row, secondary y) ─────────────
    if not volume.empty:
        vol_colors = [
            "#2ECC71" if close.iloc[i] >= open_.iloc[i] else "#E74C3C"
            for i in range(len(close))
        ]
        fig.add_trace(go.Bar(
            x=df.index, y=volume,
            name="Volume", marker_color=vol_colors, opacity=0.25,
            yaxis="y2",
        ), row=1, col=1)

    # ── SMA 20 ────────────────────────────────────────────
    if "SMA 20" in indicators:
        sma20 = close.rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=sma20, name="SMA 20",
            line=dict(color="#F5A623", width=1.3, dash="solid"), opacity=0.85,
        ), row=1, col=1)

    # ── SMA 50 ────────────────────────────────────────────
    if "SMA 50" in indicators:
        sma50 = close.rolling(50).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=sma50, name="SMA 50",
            line=dict(color="#3B8EF0", width=1.3, dash="solid"), opacity=0.85,
        ), row=1, col=1)

    # ── SMA 200 ───────────────────────────────────────────
    if "SMA 200" in indicators:
        sma200 = close.rolling(200).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=sma200, name="SMA 200",
            line=dict(color="#9B59B6", width=1.5, dash="solid"), opacity=0.85,
        ), row=1, col=1)

    # ── EMA 20 ────────────────────────────────────────────
    if "EMA 20" in indicators:
        ema20 = close.ewm(span=20, adjust=False).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ema20, name="EMA 20",
            line=dict(color="#1ABC9C", width=1.3, dash="dot"), opacity=0.85,
        ), row=1, col=1)

    # ── EMA 50 ────────────────────────────────────────────
    if "EMA 50" in indicators:
        ema50 = close.ewm(span=50, adjust=False).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ema50, name="EMA 50",
            line=dict(color="#EC407A", width=1.3, dash="dot"), opacity=0.85,
        ), row=1, col=1)

    # ── Bollinger Bands ───────────────────────────────────
    if "Bollinger Bands" in indicators:
        bb_upper, bb_mid, bb_lower = _boll(close)
        fig.add_trace(go.Scatter(
            x=df.index, y=bb_upper, name="BB Upper",
            line=dict(color="#F5A623", width=0.8, dash="dash"), opacity=0.60,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=bb_lower, name="BB Lower",
            line=dict(color="#F5A623", width=0.8, dash="dash"), opacity=0.60,
            fill="tonexty", fillcolor="rgba(245,166,35,0.04)",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=bb_mid, name="BB Mid",
            line=dict(color="#F5A623", width=0.7, dash="dot"), opacity=0.45,
        ), row=1, col=1)

    # ── VWAP ─────────────────────────────────────────────
    if "VWAP" in indicators and not volume.empty:
        vwap_s = _vwap(df)
        fig.add_trace(go.Scatter(
            x=df.index, y=vwap_s, name="VWAP",
            line=dict(color="#26C6DA", width=1.4, dash="solid"), opacity=0.80,
        ), row=1, col=1)

    # ── Ichimoku ──────────────────────────────────────────
    if "Ichimoku" in indicators and len(df) >= 52:
        ich = _ichimoku(df)
        fig.add_trace(go.Scatter(
            x=df.index, y=ich["tenkan"], name="Tenkan",
            line=dict(color="#E74C3C", width=1.0), opacity=0.80,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=ich["kijun"], name="Kijun",
            line=dict(color="#3B8EF0", width=1.0), opacity=0.80,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=ich["senkou_a"], name="Senkou A",
            line=dict(color="#2ECC71", width=0.7), opacity=0.55,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=ich["senkou_b"], name="Senkou B",
            line=dict(color="#E74C3C", width=0.7), opacity=0.55,
            fill="tonexty", fillcolor="rgba(46,204,113,0.06)",
        ), row=1, col=1)

    # ── Fibonacci ─────────────────────────────────────────
    if "Fibonacci" in indicators and len(df) >= 10:
        fib_lvls = _fib(df)
        fib_colors = ["#E74C3C","#F39C12","#F5A623","#2ECC71","#1ABC9C","#3B8EF0","#9B59B6"]
        for (lbl, val), col_f in zip(fib_lvls.items(), fib_colors):
            fig.add_hline(
                y=val, line_dash="dot", line_color=col_f,
                line_width=0.8, opacity=0.55,
                annotation_text=f"Fib {lbl}: {val:,.2f}",
                annotation_font_size=8, annotation_font_color=col_f,
                row=1, col=1,
            )

    # ── Stochastic (on main row) ──────────────────────────
    if "Stochastic" in indicators and len(df) >= 14:
        stoch_k, stoch_d = _stoch(df)
        # Use secondary Y axis overlay
        fig.add_trace(go.Scatter(
            x=df.index, y=stoch_k, name="%K",
            line=dict(color="#AB47BC", width=1.0), opacity=0.75,
            yaxis="y3",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=stoch_d, name="%D",
            line=dict(color="#7E57C2", width=1.0, dash="dot"), opacity=0.75,
            yaxis="y3",
        ), row=1, col=1)

    # ── MACD subplot ──────────────────────────────────────
    current_row = 2
    if need_macd and len(df) >= 26:
        macd_line, macd_signal, macd_hist = _macd(close)
        hist_colors = ["#2ECC71" if v >= 0 else "#E74C3C" for v in macd_hist.fillna(0)]
        fig.add_trace(go.Bar(
            x=df.index, y=macd_hist, name="MACD Hist",
            marker_color=hist_colors, opacity=0.75,
        ), row=current_row, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=macd_line, name="MACD",
            line=dict(color="#F5A623", width=1.4),
        ), row=current_row, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=macd_signal, name="Signal",
            line=dict(color="#3B8EF0", width=1.1, dash="dash"),
        ), row=current_row, col=1)
        fig.update_yaxes(
            title_text="MACD", row=current_row, col=1,
            gridcolor="#091827", tickfont=dict(size=9, color="#5A88B0"),
        )
        current_row += 1

    # ── RSI subplot ───────────────────────────────────────
    if need_rsi and len(df) >= 14:
        rsi_series = _rsi(close)
        fig.add_trace(go.Scatter(
            x=df.index, y=rsi_series, name="RSI(14)",
            line=dict(color="#9B59B6", width=1.4),
        ), row=current_row, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(231,76,60,0.07)",  line_width=0, row=current_row, col=1)
        fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(46,204,113,0.07)", line_width=0, row=current_row, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#E74C3C", line_width=0.8,
                      annotation_text="OB", annotation_font_size=8,
                      annotation_font_color="#E74C3C", row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#2ECC71", line_width=0.8,
                      annotation_text="OS", annotation_font_size=8,
                      annotation_font_color="#2ECC71", row=current_row, col=1)
        fig.update_yaxes(
            title_text="RSI", range=[0, 100], row=current_row, col=1,
            gridcolor="#091827", tickfont=dict(size=9, color="#5A88B0"),
        )

    # ── Global layout ─────────────────────────────────────
    fig.update_layout(**pla({
        "height": 580 + extra_rows * 130,
        "title":  dict(
            text=f"{ticker}  ·  {subtitle}",
            font=dict(family="IBM Plex Mono", size=13, color="#F5A623"),
        ),
        "xaxis":  xaxis_time(),
        "yaxis":  dict(
            **yaxis_plain("Price"),
            domain=[0.30, 1.0] if extra_rows == 2 else (
                [0.22, 1.0] if extra_rows == 1 else [0, 1]
            ),
        ),
        "yaxis2": dict(
            overlaying="y", side="right", showgrid=False,
            tickfont=dict(size=8, color="#1A3A5C"),
            showticklabels=False,
        ),
        "yaxis3": dict(
            overlaying="y", side="right", range=[0, 100],
            showgrid=False, showticklabels=False,
        ),
        "showlegend": True,
    }))

    fig.update_xaxes(gridcolor="#091827", showgrid=True, rangeslider_visible=False)

    return fig


# ══════════════════════════════════════════════════════════
#  SCREENER FILTER PANEL  (renders the Streamlit widgets)
# ══════════════════════════════════════════════════════════

def render_screener_filter_panel(
    sectors:   list[str],
    countries: list[str],
) -> dict:
    """
    Render the dense filter sidebar panel and return a dict of current values.
    Designed to be called inside an st.expander.
    """
    st.markdown(
        "<div class='screener-filter-title'>⚙ FUNDAMENTAL FILTERS</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("**UNIVERSE**")
        sector_opts  = ["All"] + sorted([s for s in sectors  if s and s != "N/A"])
        country_opts = ["All"] + sorted([c for c in countries if c and c != "N/A"])
        sector  = st.selectbox("Sector",  sector_opts,  key="scr_sector")
        country = st.selectbox("Country", country_opts, key="scr_country")
        keyword = st.text_input("Keyword", "", placeholder="AI, defense, cloud…", key="scr_kw")

    with c2:
        st.markdown("**MARKET CAP (B)**")
        min_mc = st.number_input("Min $B", value=0.0,      step=0.5,  min_value=0.0,   key="scr_mc_min")
        max_mc = st.number_input("Max $B", value=10_000.0, step=10.0, min_value=0.01,  key="scr_mc_max")
        st.markdown("**VALUATION**")
        max_pe = st.number_input("P/E max", value=500.0, step=5.0, min_value=0.0, key="scr_pe_max")
        min_pe = st.number_input("P/E min", value=0.0,   step=1.0, min_value=0.0, key="scr_pe_min")

    with c3:
        st.markdown("**PRICE MOVEMENT**")
        min_chg = st.slider("Min Change %", -30.0, 0.0,   -30.0, step=0.5, key="scr_chg_min")
        max_chg = st.slider("Max Change %",  0.0, 30.0,    30.0, step=0.5, key="scr_chg_max")

    with c4:
        st.markdown("**SORT & DISPLAY**")
        sort_col = st.selectbox("Sort by", [
            "MarketCap_B", "Change_Pct", "PE", "Volume", "Price",
        ], key="scr_sort")
        sort_asc = st.radio("Order", ["Descending", "Ascending"],
                            index=0, key="scr_sort_dir", horizontal=True)
        page_sz = st.select_slider("Rows/page", [25, 50, 100, 200], value=50, key="scr_page_sz")

    return dict(
        sector        = sector,
        country       = country,
        keyword       = keyword,
        min_marketcap_b = float(min_mc),
        max_marketcap_b = float(max_mc),
        max_pe        = float(max_pe),
        min_pe        = float(min_pe),
        min_change_pct= float(min_chg),
        max_change_pct= float(max_chg),
        sort_col      = sort_col,
        sort_asc      = sort_asc == "Ascending",
        page_size     = int(page_sz),
    )


# ══════════════════════════════════════════════════════════
#  UI PRIMITIVE HELPERS
# ══════════════════════════════════════════════════════════

def ptitle(title: str, subtitle: str = "") -> None:
    """Render the Bloomberg-style page header block."""
    sub_html = (
        f"<div class='page-header-sub'>{subtitle}</div>"
        if subtitle else ""
    )
    st.markdown(
        f"<div class='page-header'>"
        f"<div class='page-header-title'>{title}</div>"
        f"{sub_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def sec(label: str) -> None:
    """Render a section divider header."""
    st.markdown(
        f"<div class='sec-hdr'>{label}</div>",
        unsafe_allow_html=True,
    )


def alert(msg: str, color: str = "#F5A623") -> None:
    """Render a highlighted alert / info box."""
    st.markdown(
        f"<div class='navy-alert' style='border-left-color:{color}'>{msg}</div>",
        unsafe_allow_html=True,
    )


def badge(label: str, color: str = "#F5A623") -> str:
    """Return an inline HTML badge string (use inside f-strings)."""
    return (
        f"<span class='src-badge' style='color:{color}'>{label}</span>"
    )


def interrupted(msg: str = "Data not available.") -> None:
    """Render a dashed 'no data' notice."""
    st.markdown(
        f"<div class='interrupted-notice'>⚠ {msg}</div>",
        unsafe_allow_html=True,
    )


def colored(text: str, color: str) -> str:
    """Wrap text in an inline-colour span."""
    return f"<span style='color:{color}'>{text}</span>"


def status_badge(label: str, kind: str = "live") -> None:
    """Render a small live / warning / error status pill."""
    icons = {"live": "●", "warning": "▲", "error": "✖"}
    icon = icons.get(kind, "●")
    st.markdown(
        f"<span class='status-badge {kind}'>{icon} {label}</span>",
        unsafe_allow_html=True,
    )

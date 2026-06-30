"""
╔══════════════════════════════════════════════════════════════════╗
║   NAVY TERMINAL PRO  v7.0  ·  UI Components                      ║
║   Total Black Bloomberg Theme · AgGrid v7 · DCE Engine           ║
║   Fixes: metric labels · ticker index · earnings bypass · DCE    ║
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

# ── AgGrid imports (graceful fallback) ────────────────────
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
#  GLOBAL CSS  — Total Black Bloomberg Terminal v7
# ══════════════════════════════════════════════════════════
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root tokens ──────────────────────────────────────── */
:root {
  --bg:           #000000;
  --bg-panel:     #080808;
  --bg-card:      #0a0a0a;
  --bg-card2:     #0d0d0d;
  --bg-blue:      #050e1a;
  --border:       #111111;
  --border2:      #1a1a1a;
  --border3:      #222222;
  --accent:       #F5A623;
  --accent2:      #D4891A;
  --cyan:         #3B8EF0;
  --green:        #2ECC71;
  --red:          #E74C3C;
  --purple:       #9B59B6;
  --text:         #D0D8E4;
  --text2:        #8AAEC8;
  --text3:        #4A6A8A;
  --text-muted:   #1E3050;
  --font-mono:    'IBM Plex Mono', 'Courier New', monospace;
  --font-sans:    'Inter', system-ui, sans-serif;
  --r-sm:         3px;
  --r-md:         5px;
  --r-lg:         8px;
  --shadow:       0 2px 16px rgba(0,0,0,0.80);
  --trans:        all 0.15s ease;
}

/* ── Global reset ─────────────────────────────────────── */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
.block-container,
section[data-testid="stSidebar"] ~ div {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--font-sans) !important;
}

.block-container {
  padding: 1rem 1.8rem 3rem 1.8rem !important;
  max-width: 100% !important;
}

/* ── Sidebar ──────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
  background: #050505 !important;
  border-right: 1px solid var(--border2) !important;
}
[data-testid="stSidebar"] * { color: var(--text3) !important; }
[data-testid="stSidebar"] button {
  background: transparent !important;
  border: none !important;
  color: var(--text3) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.68rem !important;
  letter-spacing: 0.06em !important;
  padding: 0.38rem 0.65rem !important;
  text-align: left !important;
  border-radius: var(--r-sm) !important;
  transition: var(--trans) !important;
  width: 100% !important;
}
[data-testid="stSidebar"] button:hover {
  background: var(--bg-blue) !important;
  color: var(--accent) !important;
}

/* ── Form inputs ──────────────────────────────────────── */
input, select, textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
  background: var(--bg-card) !important;
  border: 1px solid var(--border3) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.77rem !important;
}
[data-baseweb="select"] > div {
  background: var(--bg-card) !important;
  border-color: var(--border3) !important;
}
[data-baseweb="select"] span { color: var(--text) !important; }

[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label {
  color: var(--text3) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.70rem !important;
  letter-spacing: 0.05em !important;
}

/* ── Metric tiles ─────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r-sm) !important;
  padding: 5px 9px !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--font-mono) !important;
  font-size: 0.92rem !important;
  font-weight: 600 !important;
  color: var(--accent) !important;
}
[data-testid="stMetricLabel"] {
  font-family: var(--font-mono) !important;
  font-size: 0.60rem !important;
  color: var(--text3) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
}
[data-testid="stMetricDelta"] { font-size: 0.68rem !important; }

/* ── Tabs ─────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
  border-bottom: 1px solid var(--border2) !important;
  background: var(--bg-panel) !important;
  gap: 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
  font-family: var(--font-mono) !important;
  font-size: 0.66rem !important;
  letter-spacing: 0.05em !important;
  color: var(--text3) !important;
  padding: 0.42rem 0.9rem !important;
  border-radius: var(--r-sm) var(--r-sm) 0 0 !important;
  border: 1px solid transparent !important;
  transition: var(--trans) !important;
  background: transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--accent) !important;
  background: var(--bg-card) !important;
  border-color: var(--border2) !important;
  border-bottom-color: var(--bg-card) !important;
}
[data-testid="stTabs"] [role="tab"]:hover { color: var(--text2) !important; }
[data-testid="stTabs"] [role="tabpanel"] {
  background: var(--bg) !important;
  padding-top: 0.8rem !important;
}

/* ── Expander ─────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r-md) !important;
}
[data-testid="stExpander"] summary {
  font-family: var(--font-mono) !important;
  font-size: 0.70rem !important;
  color: var(--text2) !important;
  letter-spacing: 0.05em !important;
  background: var(--bg-card) !important;
}

/* ── Buttons ──────────────────────────────────────────── */
[data-testid="stButton"] button {
  background: var(--bg-card) !important;
  border: 1px solid var(--border3) !important;
  color: var(--text2) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.71rem !important;
  letter-spacing: 0.06em !important;
  border-radius: var(--r-sm) !important;
  transition: var(--trans) !important;
}
[data-testid="stButton"] button:hover {
  background: var(--accent) !important;
  color: #000 !important;
  border-color: var(--accent) !important;
}

/* ── Progress bar ─────────────────────────────────────── */
[data-testid="stProgressBar"] > div > div {
  background: linear-gradient(90deg, var(--cyan), var(--accent)) !important;
}
[data-testid="stProgress"] > div {
  background: var(--border2) !important;
}

/* ── Alerts / info boxes ──────────────────────────────── */
[data-testid="stAlert"] {
  background: var(--bg-card) !important;
  border-color: var(--border2) !important;
  color: var(--text) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.73rem !important;
}

/* ── Scrollbar ────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border3); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── HR dividers ──────────────────────────────────────── */
hr { border-color: var(--border2) !important; margin: 0.6rem 0 !important; }

/* ══ COMPONENT CLASSES ═══════════════════════════════════ */

/* Page header */
.page-header {
  padding: 0.9rem 1.2rem 0.7rem 1.2rem;
  margin-bottom: 1.2rem;
  background: linear-gradient(135deg, #070707 0%, #0b0e14 100%);
  border: 1px solid var(--border2);
  border-left: 3px solid var(--accent);
  border-radius: var(--r-lg);
  box-shadow: var(--shadow);
}
.page-header-title {
  font-family: var(--font-mono);
  font-size: 1.02rem;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin: 0;
}
.page-header-sub {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: var(--text3);
  letter-spacing: 0.10em;
  margin-top: 3px;
  text-transform: uppercase;
}

/* Section header */
.sec-hdr {
  font-family: var(--font-mono);
  font-size: 0.63rem;
  font-weight: 600;
  color: var(--text3);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  padding: 0.50rem 0 0.28rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.65rem;
}

/* Ticker card */
.ticker-card {
  background: linear-gradient(135deg, #070707 0%, #0b0e14 100%);
  border: 1px solid var(--border2);
  border-radius: var(--r-lg);
  padding: 1.0rem 1.3rem;
  margin-bottom: 1.0rem;
  box-shadow: var(--shadow);
}
.ticker-tag {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: var(--text3);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.ticker-name {
  font-family: var(--font-sans);
  font-size: 1.28rem;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 3px;
}
.ticker-meta {
  font-family: var(--font-mono);
  font-size: 0.63rem;
  color: var(--text3);
  letter-spacing: 0.06em;
}
.ticker-price {
  font-family: var(--font-mono);
  font-size: 1.72rem;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: -0.01em;
}

/* Mover card */
.mover-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.38rem 0.7rem;
  margin-bottom: 4px;
  background: var(--bg-card);
  border-radius: var(--r-sm);
  border: 1px solid var(--border);
}

/* Term box */
.term-box {
  background: var(--bg-card);
  border: 1px solid var(--border2);
  border-radius: var(--r-sm);
  padding: 0.60rem 0.85rem;
  font-family: var(--font-mono);
  font-size: 0.70rem;
  color: var(--text2);
  line-height: 1.7;
  margin-bottom: 0.5rem;
}

/* Alert box */
.navy-alert {
  border-left: 3px solid var(--accent);
  background: rgba(10,10,10,0.90);
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  padding: 0.50rem 0.85rem;
  margin: 0.30rem 0;
  font-family: var(--font-mono);
  font-size: 0.71rem;
  color: var(--text);
  line-height: 1.65;
}

/* Source badge */
.src-badge {
  display: inline-block;
  background: var(--border3);
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: 0.50rem;
  font-weight: 600;
  letter-spacing: 0.10em;
  padding: 1px 5px;
  border-radius: 2px;
  text-transform: uppercase;
  vertical-align: middle;
}

/* Status badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 0.58rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.status-badge.live    { background: rgba(46,204,113,0.12); color: var(--green);  border: 1px solid rgba(46,204,113,0.25); }
.status-badge.warning { background: rgba(245,166,35,0.12); color: var(--accent); border: 1px solid rgba(245,166,35,0.25); }
.status-badge.error   { background: rgba(231,76,60,0.12);  color: var(--red);    border: 1px solid rgba(231,76,60,0.25); }

/* Screener */
.screener-filter-title {
  font-family: var(--font-mono);
  font-size: 0.61rem;
  font-weight: 600;
  color: var(--accent);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 0.65rem;
  padding-bottom: 0.30rem;
  border-bottom: 1px solid var(--border);
}
.screener-stats-bar {
  display: flex;
  gap: 1.4rem;
  align-items: center;
  padding: 0.50rem 0.9rem;
  background: var(--bg-card);
  border: 1px solid var(--border2);
  border-radius: var(--r-sm);
  margin-bottom: 0.75rem;
  font-family: var(--font-mono);
  font-size: 0.66rem;
  color: var(--text3);
}
.screener-stats-bar b { color: var(--accent); }

/* Sidebar nav */
.nav-title {
  font-family: var(--font-mono);
  font-size: 1.08rem;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 0.18em;
}
.nav-sub {
  font-family: var(--font-mono);
  font-size: 0.50rem;
  color: var(--text3);
  letter-spacing: 0.12em;
  margin-top: 2px;
  text-transform: uppercase;
}
.nav-divider {
  height: 1px;
  background: linear-gradient(90deg, var(--border2), transparent);
  margin: 0.55rem 0;
}

/* Interrupted / no-data */
.interrupted-notice {
  padding: 0.50rem 0.85rem;
  background: rgba(20,20,20,0.80);
  border: 1px dashed var(--border3);
  border-radius: var(--r-sm);
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--text3);
}

/* DCE panel */
.dce-header {
  padding: 0.60rem 1rem;
  background: linear-gradient(90deg, #050505, #0b0e14);
  border: 1px solid var(--border2);
  border-left: 3px solid var(--cyan);
  border-radius: var(--r-md);
  margin-bottom: 0.8rem;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--cyan);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

/* Plotly transparent bg */
.js-plotly-plot .plotly, .plotly-graph-div {
  background: transparent !important;
}
</style>
"""

# ══════════════════════════════════════════════════════════
#  PLOTLY LAYOUT HELPERS — Total Black
# ══════════════════════════════════════════════════════════

_PLOTLY_BASE = dict(
    paper_bgcolor = "#000000",
    plot_bgcolor  = "#000000",
    font          = dict(family="IBM Plex Mono, monospace", size=11, color="#8AAEC8"),
    legend        = dict(
        bgcolor="rgba(5,5,5,0.92)", bordercolor="#111111",
        borderwidth=1, font=dict(size=10, color="#8AAEC8"),
    ),
    margin        = dict(l=46, r=22, t=42, b=36),
    hovermode     = "x unified",
    hoverlabel    = dict(
        bgcolor="#050505", bordercolor="#1a1a1a",
        font=dict(family="IBM Plex Mono", size=11, color="#D0D8E4"),
    ),
    transition    = {"duration": 0},
)


def pla(overrides: dict | None = None) -> dict:
    out = dict(_PLOTLY_BASE)
    if overrides:
        out.update(overrides)
    # Force black axes gridlines
    for ax in ("xaxis", "yaxis"):
        if ax not in out:
            out[ax] = {}
        out[ax].setdefault("gridcolor", "#0d0d0d")
        out[ax].setdefault("zerolinecolor", "#111111")
    return out


def xaxis_time() -> dict:
    return dict(
        gridcolor="#0d0d0d", showgrid=True,
        tickfont=dict(family="IBM Plex Mono", size=9, color="#4A6A8A"),
        rangeslider=dict(visible=False),
        type="date",
    )


def yaxis_plain(title: str = "") -> dict:
    return dict(
        gridcolor="#0d0d0d", showgrid=True, zeroline=False,
        tickfont=dict(family="IBM Plex Mono", size=9, color="#4A6A8A"),
        title=dict(text=title, font=dict(size=10, color="#4A6A8A")) if title else {},
    )


# ══════════════════════════════════════════════════════════
#  AGGRID THEME — Total Black Bloomberg
# ══════════════════════════════════════════════════════════

_JS_CHANGE_CELL = """
class ChangeCellRenderer {
  init(p) {
    this.eGui = document.createElement('span');
    const v = parseFloat(p.value);
    if (isNaN(v)) { this.eGui.innerText='N/A'; this.eGui.style.color='#4A6A8A'; return; }
    const c  = v>=0?'#2ECC71':'#E74C3C';
    const bg = v>=0?'rgba(46,204,113,0.12)':'rgba(231,76,60,0.12)';
    const ar = v>=0?'▲':'▼';
    this.eGui.style.cssText=`color:${c};background:${bg};padding:1px 6px;border-radius:3px;font-family:IBM Plex Mono,monospace;font-size:11px;font-weight:600`;
    this.eGui.innerText=ar+' '+Math.abs(v).toFixed(2)+'%';
  }
  getGui(){return this.eGui;}
}
"""

_JS_MCAP_CELL = """
class McapCellRenderer {
  init(p) {
    this.eGui = document.createElement('span');
    const v = parseFloat(p.value);
    if (isNaN(v)){this.eGui.innerText='N/A';this.eGui.style.color='#4A6A8A';return;}
    let t;
    if(v>=1000)t=(v/1000).toFixed(2)+'T';
    else if(v>=1)t=v.toFixed(2)+'B';
    else t=(v*1000).toFixed(0)+'M';
    this.eGui.style.cssText='color:#D0D8E4;font-family:IBM Plex Mono,monospace;font-size:11px';
    this.eGui.innerText=t;
  }
  getGui(){return this.eGui;}
}
"""

_JS_TICKER_CELL = """
class TickerCellRenderer {
  init(p) {
    this.eGui = document.createElement('span');
    this.eGui.style.cssText='color:#F5A623;font-family:IBM Plex Mono,monospace;font-size:11px;font-weight:700;letter-spacing:0.04em';
    this.eGui.innerText=p.value||'';
  }
  getGui(){return this.eGui;}
}
"""

_JS_METRIC_CELL = """
class MetricCellRenderer {
  init(p) {
    this.eGui = document.createElement('span');
    this.eGui.style.cssText='color:#8AAEC8;font-family:IBM Plex Mono,monospace;font-size:11px;font-weight:600;letter-spacing:0.02em';
    this.eGui.innerText=p.value||'';
  }
  getGui(){return this.eGui;}
}
"""

_JS_PE_CELL = """
class PeCellRenderer {
  init(p) {
    this.eGui = document.createElement('span');
    const v = parseFloat(p.value);
    if(isNaN(v)){this.eGui.innerText='N/A';this.eGui.style.color='#4A6A8A';return;}
    let c='#D0D8E4';
    if(v<15)c='#2ECC71';
    else if(v>50)c='#E74C3C';
    else if(v>30)c='#F5A623';
    this.eGui.style.cssText=`color:${c};font-family:IBM Plex Mono,monospace;font-size:11px`;
    this.eGui.innerText=v.toFixed(1);
  }
  getGui(){return this.eGui;}
}
"""

# Total black AgGrid CSS
_AGGRID_CUSTOM_CSS = {
    ".ag-root-wrapper": {
        "background-color": "#000000 !important",
        "border": "1px solid #111111 !important",
        "border-radius": "5px !important",
    },
    ".ag-header": {
        "background-color": "#050505 !important",
        "border-bottom": "1px solid #1a1a1a !important",
    },
    ".ag-header-cell": {
        "color": "#4A6A8A !important",
        "font-family": "IBM Plex Mono, monospace !important",
        "font-size": "10px !important",
        "font-weight": "600 !important",
        "letter-spacing": "0.10em !important",
        "text-transform": "uppercase !important",
        "background-color": "#050505 !important",
    },
    ".ag-header-cell:hover": {"background-color": "#0a0a0a !important"},
    ".ag-row": {
        "background-color": "#000000 !important",
        "border-bottom": "1px solid #0a0a0a !important",
        "font-family": "IBM Plex Mono, monospace !important",
        "font-size": "11px !important",
        "color": "#D0D8E4 !important",
    },
    ".ag-row:hover":     {"background-color": "#0b0e14 !important", "cursor": "pointer !important"},
    ".ag-row-selected":  {"background-color": "#0f1e30 !important"},
    ".ag-row-odd":       {"background-color": "#030303 !important"},
    ".ag-cell": {
        "border-right": "1px solid #0a0a0a !important",
        "padding": "0 8px !important",
    },
    ".ag-pinned-left-cols-container .ag-cell": {
        "background-color": "#050505 !important",
        "border-right": "1px solid #111111 !important",
    },
    ".ag-body-viewport":  {"background-color": "#000000 !important"},
    ".ag-overlay-loading-center": {
        "background-color": "#050505 !important",
        "color": "#F5A623 !important",
        "font-family": "IBM Plex Mono !important",
        "font-size": "12px !important",
        "border": "1px solid #111111 !important",
        "border-radius": "4px !important",
        "padding": "10px 20px !important",
    },
    ".ag-paging-panel": {
        "background-color": "#050505 !important",
        "border-top": "1px solid #111111 !important",
        "color": "#4A6A8A !important",
        "font-family": "IBM Plex Mono, monospace !important",
        "font-size": "10px !important",
    },
    ".ag-paging-button": {"color": "#F5A623 !important"},
    ".ag-icon":          {"color": "#4A6A8A !important"},
    ".ag-tool-panel-wrapper": {
        "background-color": "#050505 !important",
        "border-left": "1px solid #111111 !important",
        "color": "#8AAEC8 !important",
    },
    ".ag-status-bar": {
        "background-color": "#050505 !important",
        "border-top": "1px solid #111111 !important",
        "color": "#4A6A8A !important",
        "font-family": "IBM Plex Mono, monospace !important",
        "font-size": "10px !important",
    },
    ".ag-filter-toolpanel-group-title-bar": {"background-color": "#0a0a0a !important"},
    ".ag-floating-filter-input input": {
        "background": "#050505 !important",
        "color": "#D0D8E4 !important",
        "border-color": "#1a1a1a !important",
    },
    ".ag-select-native-select": {
        "background": "#050505 !important",
        "color": "#D0D8E4 !important",
    },
    ".ag-checkbox-input-wrapper": {"background-color": "#050505 !important"},
}


# ══════════════════════════════════════════════════════════
#  SCREENER AGGRID
# ══════════════════════════════════════════════════════════

def screener_aggrid(
    df: pd.DataFrame,
    height: int = 560,
    key: str = "screener_grid",
    page_size: int = 50,
) -> Any:
    """Bloomberg-style institutional screener grid."""
    if df is None or df.empty:
        st.markdown("<div class='interrupted-notice'>⚠ No data to display.</div>", unsafe_allow_html=True)
        return None
    if not _AGGRID_AVAILABLE:
        st.dataframe(df, use_container_width=True, height=height)
        return None

    display_df = df.copy()
    for col in ["MarketCap_B", "PE", "Price", "Change_Pct", "Volume"]:
        if col in display_df.columns:
            display_df[col] = pd.to_numeric(display_df[col], errors="coerce")

    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_default_column(
        resizable=True, sortable=True, filter=True,
        floatingFilter=True, suppressMenu=False,
        wrapHeaderText=True, autoHeaderHeight=True, minWidth=60,
    )
    gb.configure_column("Ticker",     header_name="TICKER",  pinned="left", width=90,  cellRenderer=JsCode(_JS_TICKER_CELL))
    gb.configure_column("Name",       header_name="COMPANY", pinned="left", width=180, filter="agTextColumnFilter")
    gb.configure_column("Sector",     header_name="SECTOR",  width=130, filter="agSetColumnFilter")
    gb.configure_column("Industry",   header_name="INDUSTRY",width=150, filter="agSetColumnFilter")
    gb.configure_column("Country",    header_name="COUNTRY", width=100, filter="agSetColumnFilter")
    gb.configure_column("Price",      header_name="PRICE",   width=88, type=["numericColumn"],
        valueFormatter=JsCode("function(p){if(!p.value||isNaN(p.value))return'N/A';return p.value.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:4});}"))
    gb.configure_column("Change_Pct", header_name="CHG%",    width=95, type=["numericColumn"], cellRenderer=JsCode(_JS_CHANGE_CELL))
    gb.configure_column("MarketCap_B",header_name="MCAP",    width=95, type=["numericColumn"], cellRenderer=JsCode(_JS_MCAP_CELL))
    gb.configure_column("PE",         header_name="P/E",     width=72, type=["numericColumn"], cellRenderer=JsCode(_JS_PE_CELL))
    gb.configure_column("Volume",     header_name="VOLUME",  width=110, type=["numericColumn"],
        valueFormatter=JsCode("function(p){if(!p.value||isNaN(p.value))return'N/A';if(p.value>=1e9)return(p.value/1e9).toFixed(2)+'B';if(p.value>=1e6)return(p.value/1e6).toFixed(2)+'M';if(p.value>=1e3)return(p.value/1e3).toFixed(1)+'K';return p.value.toFixed(0);}"))

    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_side_bar(filters_panel=True, columns_panel=True)
    gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=page_size)
    gb.configure_grid_options(
        rowHeight=26, headerHeight=34,
        enableRangeSelection=True,
        suppressCopyRowsToClipboard=False,
        domLayout="normal", animateRows=False,
        rowSelection="single",
        suppressFieldDotNotation=True,
        enableStatusBar=True,
        statusBar={"statusPanels":[
            {"statusPanel":"agTotalAndFilteredRowCountComponent","align":"left"},
            {"statusPanel":"agAggregationComponent","align":"right"},
        ]},
    )
    result = AgGrid(
        data=display_df, gridOptions=gb.build(),
        height=height, theme=AgGridTheme.BALHAM,
        custom_css=_AGGRID_CUSTOM_CSS,
        allow_unsafe_jscode=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        columns_auto_size_mode=ColumnsAutoSizeMode.NO_AUTOSIZE,
        key=key,
    )
    return result


# ══════════════════════════════════════════════════════════
#  NAVY_GRID — FIX #3: always expose index as first column
# ══════════════════════════════════════════════════════════

def navy_grid(
    df: pd.DataFrame,
    height: int = 300,
    key: str = "grid",
) -> Any:
    """
    General-purpose institutional AgGrid.
    FIX #3: The DataFrame index (Metric names, Ticker names, etc.)
    is always converted to an explicit column so it renders in AgGrid.
    """
    if df is None or df.empty:
        st.markdown("<div class='interrupted-notice'>No data available.</div>", unsafe_allow_html=True)
        return None
    if not _AGGRID_AVAILABLE:
        st.dataframe(df, use_container_width=True, height=height)
        return None

    # ── KEY FIX: promote index to column ─────────────────
    display_df = df.copy()
    idx_name = display_df.index.name or "Metric"
    # Only reset if the index is meaningful (not default 0,1,2…)
    if not isinstance(display_df.index, pd.RangeIndex):
        display_df.reset_index(inplace=True)
        # Ensure the first column has a clean name
        if display_df.columns[0] in ("index", None, ""):
            display_df.rename(columns={display_df.columns[0]: idx_name}, inplace=True)
    # Convert all-numeric strings to floats where possible (for sorting)
    for col in display_df.columns[1:]:
        converted = pd.to_numeric(display_df[col], errors="coerce")
        if not converted.isna().all():
            display_df[col] = converted.where(converted.notna(), display_df[col])
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_default_column(resizable=True, sortable=True, filter=True, minWidth=60)

    # First column: always pinned left, styled as metric/label
    first_col = display_df.columns[0]
    gb.configure_column(
        first_col,
        header_name=str(first_col).upper(),
        pinned="left",
        width=180,
        cellRenderer=JsCode(_JS_METRIC_CELL),
    )

    gb.configure_grid_options(
        rowHeight=24, headerHeight=30,
        domLayout="normal", animateRows=False,
        suppressFieldDotNotation=True,
    )
    result = AgGrid(
        data=display_df, gridOptions=gb.build(),
        height=height, theme=AgGridTheme.BALHAM,
        custom_css=_AGGRID_CUSTOM_CSS,
        allow_unsafe_jscode=True,
        update_mode=GridUpdateMode.NO_UPDATE,
        key=key,
    )
    return result


# ══════════════════════════════════════════════════════════
#  COMPARISON TABLE — FIX #4: ticker always first column
# ══════════════════════════════════════════════════════════

def comparison_grid(
    df: pd.DataFrame,
    height: int = 300,
    key: str = "cmp_grid",
) -> Any:
    """
    Comparison table that guarantees Ticker is the first visible column.
    FIX #4: index reset + pinned Ticker column.
    """
    if df is None or df.empty:
        st.markdown("<div class='interrupted-notice'>No comparison data.</div>", unsafe_allow_html=True)
        return None
    if not _AGGRID_AVAILABLE:
        st.dataframe(df, use_container_width=True, height=height)
        return None

    display_df = df.copy()

    # Ensure Ticker column exists
    if "Ticker" not in display_df.columns:
        if display_df.index.name in ("Ticker", "ticker", None):
            display_df.reset_index(inplace=True)
            display_df.rename(columns={display_df.columns[0]: "Ticker"}, inplace=True)
        else:
            display_df.insert(0, "Ticker", display_df.index.astype(str))
            display_df.reset_index(drop=True, inplace=True)

    # Move Ticker to front
    cols = ["Ticker"] + [c for c in display_df.columns if c != "Ticker"]
    display_df = display_df[cols]

    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_default_column(resizable=True, sortable=True, filter=True, minWidth=70)
    gb.configure_column(
        "Ticker", header_name="TICKER",
        pinned="left", width=90,
        cellRenderer=JsCode(_JS_TICKER_CELL),
    )
    # Style numeric columns
    num_cols = [c for c in display_df.columns if c != "Ticker"]
    for col in num_cols:
        gb.configure_column(col, header_name=col.upper(), width=95,
                            type=["numericColumn"] if pd.api.types.is_numeric_dtype(display_df[col]) else [])

    gb.configure_grid_options(
        rowHeight=25, headerHeight=30,
        domLayout="normal", animateRows=False,
        suppressFieldDotNotation=True,
    )
    result = AgGrid(
        data=display_df, gridOptions=gb.build(),
        height=height, theme=AgGridTheme.BALHAM,
        custom_css=_AGGRID_CUSTOM_CSS,
        allow_unsafe_jscode=True,
        update_mode=GridUpdateMode.NO_UPDATE,
        key=key,
    )
    return result


# ══════════════════════════════════════════════════════════
#  CANDLESTICK CHART BUILDER
# ══════════════════════════════════════════════════════════

def build_candle_chart(
    ticker: str,
    df: pd.DataFrame,
    indicators: list[str],
    subtitle: str = "",
) -> go.Figure:
    """Full technical-analysis candlestick chart."""
    from quant_engine import (
        rsi as _rsi, macd as _macd, atr as _atr, fibonacci as _fib,
        stochastic as _stoch, williams_r as _williams_r, cci as _cci,
        obv as _obv, vwap as _vwap, ichimoku as _ichimoku,
        bollinger_bands as _boll,
    )

    need_macd  = "MACD" in indicators
    need_rsi   = "RSI"  in indicators
    extra_rows = int(need_macd) + int(need_rsi)
    total_rows = 1 + extra_rows

    row_heights = (
        [0.60]                if extra_rows == 0 else
        [0.55, 0.22, 0.23]   if extra_rows == 2 else
        [0.65, 0.35]
    )

    fig = make_subplots(
        rows=total_rows, cols=1,
        shared_xaxes=True, vertical_spacing=0.04,
        row_heights=row_heights[:total_rows],
    )

    close  = df["Close"]
    high   = df["High"]
    low    = df["Low"]
    open_  = df["Open"]
    volume = df.get("Volume", pd.Series(dtype=float))

    fig.add_trace(go.Candlestick(
        x=df.index, open=open_, high=high, low=low, close=close,
        name=ticker,
        increasing_line_color="#2ECC71", increasing_fillcolor="rgba(46,204,113,0.50)",
        decreasing_line_color="#E74C3C", decreasing_fillcolor="rgba(231,76,60,0.50)",
        line=dict(width=1),
    ), row=1, col=1)

    if not volume.empty:
        vol_colors = ["#2ECC71" if close.iloc[i] >= open_.iloc[i] else "#E74C3C" for i in range(len(close))]
        fig.add_trace(go.Bar(
            x=df.index, y=volume, name="Volume",
            marker_color=vol_colors, opacity=0.22, yaxis="y2",
        ), row=1, col=1)

    if "SMA 20"  in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=close.rolling(20).mean(),  name="SMA 20",  line=dict(color="#F5A623", width=1.3)), row=1, col=1)
    if "SMA 50"  in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=close.rolling(50).mean(),  name="SMA 50",  line=dict(color="#3B8EF0", width=1.3)), row=1, col=1)
    if "SMA 200" in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=close.rolling(200).mean(), name="SMA 200", line=dict(color="#9B59B6", width=1.5)), row=1, col=1)
    if "EMA 20"  in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=close.ewm(span=20).mean(), name="EMA 20",  line=dict(color="#1ABC9C", width=1.3, dash="dot")), row=1, col=1)
    if "EMA 50"  in indicators:
        fig.add_trace(go.Scatter(x=df.index, y=close.ewm(span=50).mean(), name="EMA 50",  line=dict(color="#EC407A", width=1.3, dash="dot")), row=1, col=1)

    if "Bollinger Bands" in indicators:
        bb_u, bb_m, bb_l = _boll(close)
        fig.add_trace(go.Scatter(x=df.index, y=bb_u, name="BB Up",  line=dict(color="#F5A623", width=0.8, dash="dash"), opacity=0.60), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=bb_l, name="BB Low", line=dict(color="#F5A623", width=0.8, dash="dash"), opacity=0.60, fill="tonexty", fillcolor="rgba(245,166,35,0.04)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=bb_m, name="BB Mid", line=dict(color="#F5A623", width=0.7, dash="dot"),  opacity=0.45), row=1, col=1)

    if "VWAP" in indicators and not volume.empty:
        fig.add_trace(go.Scatter(x=df.index, y=_vwap(df), name="VWAP", line=dict(color="#26C6DA", width=1.4)), row=1, col=1)

    if "Ichimoku" in indicators and len(df) >= 52:
        ich = _ichimoku(df)
        fig.add_trace(go.Scatter(x=df.index, y=ich["tenkan"],  name="Tenkan",   line=dict(color="#E74C3C", width=1.0)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=ich["kijun"],   name="Kijun",    line=dict(color="#3B8EF0", width=1.0)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=ich["senkou_a"],name="Senkou A", line=dict(color="#2ECC71", width=0.7), opacity=0.55), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=ich["senkou_b"],name="Senkou B", line=dict(color="#E74C3C", width=0.7), opacity=0.55, fill="tonexty", fillcolor="rgba(46,204,113,0.05)"), row=1, col=1)

    if "Fibonacci" in indicators and len(df) >= 10:
        fib_lvls = _fib(df)
        fib_colors = ["#E74C3C","#F39C12","#F5A623","#2ECC71","#1ABC9C","#3B8EF0","#9B59B6"]
        for (lbl, val), col_f in zip(fib_lvls.items(), fib_colors):
            fig.add_hline(y=val, line_dash="dot", line_color=col_f, line_width=0.8, opacity=0.50,
                          annotation_text=f"Fib {lbl}: {val:,.2f}",
                          annotation_font_size=8, annotation_font_color=col_f, row=1, col=1)

    current_row = 2
    if need_macd and len(df) >= 26:
        ml, ms, mh = _macd(close)
        hc = ["#2ECC71" if v >= 0 else "#E74C3C" for v in mh.fillna(0)]
        fig.add_trace(go.Bar(x=df.index, y=mh, name="MACD Hist", marker_color=hc, opacity=0.75), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=ml, name="MACD",   line=dict(color="#F5A623", width=1.4)), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=ms, name="Signal", line=dict(color="#3B8EF0", width=1.1, dash="dash")), row=current_row, col=1)
        fig.update_yaxes(title_text="MACD", row=current_row, col=1, gridcolor="#0d0d0d", tickfont=dict(size=9, color="#4A6A8A"))
        current_row += 1

    if need_rsi and len(df) >= 14:
        rs = _rsi(close)
        fig.add_trace(go.Scatter(x=df.index, y=rs, name="RSI(14)", line=dict(color="#9B59B6", width=1.4)), row=current_row, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(231,76,60,0.06)",  line_width=0, row=current_row, col=1)
        fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(46,204,113,0.06)", line_width=0, row=current_row, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#E74C3C", line_width=0.8,
                      annotation_text="OB", annotation_font_size=8, annotation_font_color="#E74C3C", row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#2ECC71", line_width=0.8,
                      annotation_text="OS", annotation_font_size=8, annotation_font_color="#2ECC71", row=current_row, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=current_row, col=1, gridcolor="#0d0d0d", tickfont=dict(size=9, color="#4A6A8A"))

    fig.update_layout(**pla({
        "height": 580 + extra_rows * 130,
        "title": dict(text=f"{ticker}  ·  {subtitle}", font=dict(family="IBM Plex Mono", size=13, color="#F5A623")),
        "xaxis": xaxis_time(),
        "yaxis": dict(**yaxis_plain("Price"),
                      domain=[0.30,1.0] if extra_rows==2 else ([0.22,1.0] if extra_rows==1 else [0,1])),
        "yaxis2": dict(overlaying="y", side="right", showgrid=False, showticklabels=False),
        "showlegend": True,
    }))
    fig.update_xaxes(gridcolor="#0d0d0d", showgrid=True, rangeslider_visible=False)
    return fig


# ══════════════════════════════════════════════════════════
#  DCE — DYNAMIC CHART ENGINE  (Feature #6)
# ══════════════════════════════════════════════════════════

def render_dce_panel(
    df_price: pd.DataFrame | None = None,
    df_screener: pd.DataFrame | None = None,
    key_prefix: str = "dce",
) -> None:
    """
    Dynamic Chart Engine: lets the user pick dataset, X axis, Y metrics,
    and chart type — then renders a Plotly chart in total-black style.

    Parameters
    ----------
    df_price     : OHLCV DataFrame for the current terminal ticker
    df_screener  : Screener master DataFrame (fundamental cross-section)
    key_prefix   : Streamlit widget key namespace
    """
    st.markdown(
        "<div class='dce-header'>⚡ DYNAMIC CHART ENGINE  ·  DCE v1.0  ·  "
        "Select dataset → axes → chart type → render</div>",
        unsafe_allow_html=True,
    )

    # ── Dataset selection ─────────────────────────────────
    datasets: dict[str, pd.DataFrame | None] = {
        "Price / OHLCV (current ticker)": df_price,
        "Screener Cross-Section":         df_screener,
    }
    ds_labels = [k for k, v in datasets.items() if v is not None and not v.empty]

    if not ds_labels:
        st.markdown(
            "<div class='interrupted-notice'>⚠ No datasets available. "
            "Load a ticker or screener data first.</div>",
            unsafe_allow_html=True,
        )
        return

    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
    with c1:
        ds_label = st.selectbox("📦 Dataset", ds_labels, key=f"{key_prefix}_ds")
    df_work = datasets[ds_label].copy()

    # Flatten multi-index columns if needed (OHLCV sometimes has them)
    if isinstance(df_work.columns, pd.MultiIndex):
        df_work.columns = ["_".join(str(c) for c in col if c) for col in df_work.columns]

    # For price data, include the index (Date) as a column option
    if isinstance(df_work.index, pd.DatetimeIndex):
        df_work = df_work.reset_index()
        df_work.rename(columns={df_work.columns[0]: "Date"}, inplace=True)

    all_cols    = list(df_work.columns)
    num_cols    = [c for c in all_cols if pd.api.types.is_numeric_dtype(df_work[c])]
    str_cols    = [c for c in all_cols if not pd.api.types.is_numeric_dtype(df_work[c])]
    x_defaults  = ["Date"] if "Date" in all_cols else (str_cols[:1] if str_cols else all_cols[:1])
    y_defaults  = num_cols[:3] if num_cols else all_cols[1:4]

    with c2:
        x_col = st.selectbox("📐 X Axis", all_cols, index=all_cols.index(x_defaults[0]) if x_defaults else 0, key=f"{key_prefix}_x")
    with c3:
        y_cols = st.multiselect("📊 Y Metrics", num_cols or all_cols, default=y_defaults[:2], key=f"{key_prefix}_y")
    with c4:
        chart_type = st.selectbox(
            "📈 Type",
            ["Lines", "Bars", "Scatter", "Area", "Bar + Line", "Candlestick"],
            key=f"{key_prefix}_type",
        )

    # Sub-controls row
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        normalize = st.checkbox("Normalize to 100", value=False, key=f"{key_prefix}_norm")
    with sc2:
        log_y = st.checkbox("Log Y Scale", value=False, key=f"{key_prefix}_log")
    with sc3:
        max_pts = st.select_slider("Max points", [500, 1000, 2000, 5000, "All"], value=2000, key=f"{key_prefix}_pts")
    with sc4:
        chart_height = st.slider("Height", 300, 800, 460, step=20, key=f"{key_prefix}_h")

    if not y_cols:
        st.info("Select at least one Y metric above.")
        return

    # Sub-sample
    df_plot = df_work.copy()
    if max_pts != "All" and len(df_plot) > int(max_pts):
        step = math.ceil(len(df_plot) / int(max_pts))
        df_plot = df_plot.iloc[::step]

    # Normalize
    if normalize:
        for yc in y_cols:
            if yc in df_plot.columns:
                first_val = df_plot[yc].dropna().iloc[0] if not df_plot[yc].dropna().empty else 1
                if first_val and first_val != 0:
                    df_plot[yc] = df_plot[yc] / first_val * 100

    # ── Build figure ──────────────────────────────────────
    fig = go.Figure()
    x_data = df_plot[x_col] if x_col in df_plot.columns else df_plot.index

    for idx, yc in enumerate(y_cols):
        if yc not in df_plot.columns:
            continue
        color = COLORS[idx % len(COLORS)]
        y_data = df_plot[yc]

        if chart_type == "Lines":
            fig.add_trace(go.Scatter(x=x_data, y=y_data, name=yc, mode="lines",
                                     line=dict(color=color, width=1.8)))
        elif chart_type == "Area":
            fig.add_trace(go.Scatter(x=x_data, y=y_data, name=yc, mode="lines",
                                     fill="tozeroy",
                                     line=dict(color=color, width=1.5),
                                     fillcolor=color.replace(")", ",0.08)").replace("rgb", "rgba") if color.startswith("rgb") else f"rgba(245,166,35,0.08)"))
        elif chart_type == "Bars":
            fig.add_trace(go.Bar(x=x_data, y=y_data, name=yc, marker_color=color, opacity=0.82))
        elif chart_type == "Scatter":
            fig.add_trace(go.Scatter(x=x_data, y=y_data, name=yc, mode="markers",
                                     marker=dict(color=color, size=5, opacity=0.75)))
        elif chart_type == "Bar + Line":
            if idx == 0:
                fig.add_trace(go.Bar(x=x_data, y=y_data, name=yc, marker_color=color, opacity=0.80))
            else:
                fig.add_trace(go.Scatter(x=x_data, y=y_data, name=yc, mode="lines",
                                         line=dict(color=color, width=1.8)))
        elif chart_type == "Candlestick":
            # Needs OHLC columns
            ohlc_map = {"Open": None, "High": None, "Low": None, "Close": None}
            for k in ohlc_map:
                for col in df_plot.columns:
                    if k.lower() in col.lower():
                        ohlc_map[k] = col
                        break
            if all(v for v in ohlc_map.values()):
                fig.add_trace(go.Candlestick(
                    x=x_data,
                    open=df_plot[ohlc_map["Open"]],  high=df_plot[ohlc_map["High"]],
                    low=df_plot[ohlc_map["Low"]],    close=df_plot[ohlc_map["Close"]],
                    name="OHLC",
                    increasing_line_color="#2ECC71", decreasing_line_color="#E74C3C",
                ))
                break  # Only one candlestick trace
            else:
                st.warning("Candlestick requires Open/High/Low/Close columns — falling back to Lines.")
                fig.add_trace(go.Scatter(x=x_data, y=y_data, name=yc,
                                         line=dict(color=color, width=1.8)))

    # Y-axis scale
    yaxis_cfg = yaxis_plain("Value")
    if log_y:
        yaxis_cfg["type"] = "log"

    x_type = "date" if x_col in ("Date", "date", "Datetime") else "-"
    fig.update_layout(**pla({
        "height":     chart_height,
        "title":      dict(
            text=f"DCE  ·  {ds_label}  ·  {', '.join(y_cols)} vs {x_col}",
            font=dict(family="IBM Plex Mono", size=12, color="#F5A623"),
        ),
        "xaxis":      dict(**xaxis_time(), type=x_type) if x_type == "date" else dict(
            gridcolor="#0d0d0d", showgrid=True,
            tickfont=dict(family="IBM Plex Mono", size=9, color="#4A6A8A"),
        ),
        "yaxis":      yaxis_cfg,
        "barmode":    "group",
        "showlegend": True,
    }))

    st.plotly_chart(fig, use_container_width=True)

    # ── Optional: raw data preview ─────────────────────────
    with st.expander("🔍 Raw data preview (first 200 rows)"):
        preview_cols = [x_col] + y_cols
        preview_cols = [c for c in preview_cols if c in df_plot.columns]
        navy_grid(df_plot[preview_cols].head(200).reset_index(drop=True), height=260, key=f"{key_prefix}_raw")


# ══════════════════════════════════════════════════════════
#  SCREENER FILTER PANEL
# ══════════════════════════════════════════════════════════

def render_screener_filter_panel(sectors: list[str], countries: list[str]) -> dict:
    st.markdown("<div class='screener-filter-title'>⚙ FUNDAMENTAL FILTERS</div>", unsafe_allow_html=True)
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
        min_mc = st.number_input("Min $B", value=0.0,      step=0.5,  min_value=0.0,  key="scr_mc_min")
        max_mc = st.number_input("Max $B", value=10_000.0, step=10.0, min_value=0.01, key="scr_mc_max")
        st.markdown("**VALUATION**")
        max_pe = st.number_input("P/E max", value=500.0, step=5.0, min_value=0.0, key="scr_pe_max")
        min_pe = st.number_input("P/E min", value=0.0,   step=1.0, min_value=0.0, key="scr_pe_min")
    with c3:
        st.markdown("**PRICE MOVEMENT**")
        min_chg = st.slider("Min Change %", -30.0,  0.0, -30.0, step=0.5, key="scr_chg_min")
        max_chg = st.slider("Max Change %",  0.0,  30.0,  30.0, step=0.5, key="scr_chg_max")
    with c4:
        st.markdown("**SORT & DISPLAY**")
        sort_col = st.selectbox("Sort by", ["MarketCap_B","Change_Pct","PE","Volume","Price"], key="scr_sort")
        sort_asc = st.radio("Order", ["Descending","Ascending"], index=0, key="scr_sort_dir", horizontal=True)
        page_sz  = st.select_slider("Rows/page", [25,50,100,200], value=50, key="scr_page_sz")
    return dict(
        sector=sector, country=country, keyword=keyword,
        min_marketcap_b=float(min_mc), max_marketcap_b=float(max_mc),
        max_pe=float(max_pe), min_pe=float(min_pe),
        min_change_pct=float(min_chg), max_change_pct=float(max_chg),
        sort_col=sort_col, sort_asc=(sort_asc=="Ascending"), page_size=int(page_sz),
    )


# ══════════════════════════════════════════════════════════
#  UI PRIMITIVE HELPERS
# ══════════════════════════════════════════════════════════

def ptitle(title: str, subtitle: str = "") -> None:
    sub = f"<div class='page-header-sub'>{subtitle}</div>" if subtitle else ""
    st.markdown(f"<div class='page-header'><div class='page-header-title'>{title}</div>{sub}</div>",
                unsafe_allow_html=True)


def sec(label: str) -> None:
    st.markdown(f"<div class='sec-hdr'>{label}</div>", unsafe_allow_html=True)


def alert(msg: str, color: str = "#F5A623") -> None:
    st.markdown(f"<div class='navy-alert' style='border-left-color:{color}'>{msg}</div>",
                unsafe_allow_html=True)


def badge(label: str, color: str = "#F5A623") -> str:
    return f"<span class='src-badge' style='color:{color}'>{label}</span>"


def interrupted(msg: str = "Data not available.") -> None:
    st.markdown(f"<div class='interrupted-notice'>⚠ {msg}</div>", unsafe_allow_html=True)


def colored(text: str, color: str) -> str:
    return f"<span style='color:{color}'>{text}</span>"


def status_badge(label: str, kind: str = "live") -> None:
    icons = {"live": "●", "warning": "▲", "error": "✖"}
    st.markdown(f"<span class='status-badge {kind}'>{icons.get(kind,'●')} {label}</span>",
                unsafe_allow_html=True)

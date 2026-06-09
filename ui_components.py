"""
NAVY TERMINAL PRO  v6.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ui_components.py  ·  AgGrid + Plotly theming + Chart builders
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from quant_engine import (
    sma, ema, bollinger, rsi, macd, stochastic, atr,
    obv, vwap, ichimoku, fibonacci, williams_r, cci,
)

# ─────────────────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────────────────
COLORS = [
    "#F5A623","#3B8EF0","#2ECC71","#E74C3C","#9B59B6","#1ABC9C",
    "#E67E22","#EC407A","#00BCD4","#8BC34A","#FF7043","#AB47BC",
    "#26C6DA","#66BB6A","#FFA726","#EF5350","#7E57C2","#26A69A",
]

# ─────────────────────────────────────────────────────────
#  GLOBAL CSS  (Bloomberg dark · IBM Plex Mono)
# ─────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

html,body,.stApp,[data-testid="stAppViewContainer"],.main,.block-container{
  background-color:#050D1A!important;font-family:'IBM Plex Sans',sans-serif!important;}
.block-container{padding-top:1rem!important;padding-bottom:2rem!important;max-width:100%!important}
[data-testid="stSidebar"]{background-color:#030A14!important;border-right:1px solid #0D2137!important;min-height:100vh!important}
[data-testid="stSidebar"] *{color:#C8D8EC!important}
[data-testid="stHeader"]{background-color:#020810!important;border-bottom:1px solid #0D2137!important}

h1,h2,h3,h4,h5,h6{color:#FFFFFF!important;font-family:'IBM Plex Mono',monospace!important;font-weight:600!important;letter-spacing:0.04em!important}
p,span,li,.stMarkdown{color:#C8D8EC!important;font-family:'IBM Plex Sans',sans-serif!important}

[data-testid="stMetricValue"]{color:#FFFFFF!important;font-family:'IBM Plex Mono',monospace!important;font-weight:700!important;font-size:1.05rem!important}
[data-testid="stMetricLabel"]{color:#5A88B0!important;font-size:0.62rem!important;text-transform:uppercase;letter-spacing:0.12em!important;font-family:'IBM Plex Mono',monospace!important}
[data-testid="metric-container"]{background:linear-gradient(160deg,#061528 0%,#091E35 100%)!important;border:1px solid #0D2137!important;border-top:2px solid #1E4976!important;border-radius:2px!important;padding:0.65rem 0.9rem!important}
[data-testid="stMetricDelta"] svg{display:none!important}
[data-testid="stMetricDelta"]{font-family:'IBM Plex Mono',monospace!important;font-size:0.70rem!important;font-weight:600!important}

.stTextInput label,.stSelectbox label,.stMultiSelect label,.stSlider label,.stNumberInput label,.stRadio label,.stCheckbox label,label[data-testid]{
  color:#5A88B0!important;font-size:0.63rem!important;font-weight:600!important;
  letter-spacing:0.1em!important;text-transform:uppercase!important;font-family:'IBM Plex Mono',monospace!important;}
input[type="text"],textarea,.stTextInput input,.stNumberInput input{
  background-color:#06111F!important;color:#E8F0F8!important;border:1px solid #0D2137!important;
  border-radius:2px!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.82rem!important;}
input[type="text"]:focus,.stTextInput input:focus{border-color:#F5A623!important;box-shadow:0 0 0 1px rgba(245,166,35,0.25)!important}
.stSelectbox [data-baseweb="select"]>div{background-color:#06111F!important;border:1px solid #0D2137!important;color:#E8F0F8!important;border-radius:2px!important}
[data-baseweb="popover"]{background-color:#06111F!important;border:1px solid #0D2137!important}
[data-baseweb="menu"]{background-color:#06111F!important}
[data-baseweb="option"]{background-color:#06111F!important;color:#C8D8EC!important;font-size:0.80rem!important}
[data-baseweb="option"]:hover{background-color:#0D2137!important;color:#FFFFFF!important}
[data-baseweb="option"][aria-selected="true"]{background-color:#122A47!important;color:#F5A623!important;font-weight:600!important}
.stButton>button{background-color:#061528!important;color:#C8D8EC!important;border:1px solid #1E4976!important;
  border-radius:2px!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.70rem!important;
  letter-spacing:0.1em!important;transition:all 0.12s ease;padding:0.4rem 1rem!important;text-transform:uppercase!important;}
.stButton>button:hover{background-color:#F5A623!important;color:#050D1A!important;border-color:#F5A623!important;font-weight:700!important}
.stSlider [data-baseweb="slider"] [role="slider"]{background-color:#F5A623!important;border-color:#F5A623!important}
.stSlider [data-baseweb="slider"] div[class*="Track"] div:first-child{background-color:#F5A623!important}

.dataframe,table{background-color:#06111F!important;color:#E8F0F8!important;border-collapse:collapse!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.74rem!important}
thead tr th{color:#5A88B0!important;background-color:#030A14!important;border-bottom:1px solid #0D2137!important;text-transform:uppercase;letter-spacing:0.08em;padding:0.42rem 0.75rem!important;font-size:0.60rem!important}
tbody tr td{color:#C8D8EC!important;border-bottom:1px solid #091827!important;padding:0.35rem 0.75rem!important}
tbody tr:hover td{background-color:#0D2137!important;color:#FFFFFF!important}

::-webkit-scrollbar{width:4px;height:4px}::-webkit-scrollbar-track{background:#020810}
::-webkit-scrollbar-thumb{background:#0D2137;border-radius:2px}::-webkit-scrollbar-thumb:hover{background:#F5A623}

.nav-title{font-family:'IBM Plex Mono',monospace;font-size:1.45rem;font-weight:700;color:#FFFFFF;letter-spacing:0.3em;text-align:center}
.nav-sub{font-family:'IBM Plex Mono',monospace;font-size:0.50rem;color:#F5A623;letter-spacing:0.55em;text-align:center;margin-top:2px}
.nav-divider{height:1px;background:linear-gradient(90deg,transparent,#F5A623,transparent);margin:0.85rem 0}
.page-title{font-family:'IBM Plex Mono',monospace!important;font-size:1.20rem;font-weight:700;color:#FFFFFF!important;letter-spacing:0.06em;border-left:3px solid #F5A623;padding-left:1rem;margin-bottom:0.15rem}
.page-sub{color:#5A88B0!important;font-size:0.70rem;margin-bottom:1.1rem;padding-left:1.25rem;letter-spacing:0.06em;font-family:'IBM Plex Mono',monospace}
.sec-hdr{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#F5A623;letter-spacing:0.3em;text-transform:uppercase;margin:1.1rem 0 0.55rem 0;border-bottom:1px solid #0D2137;padding-bottom:0.28rem}
.ticker-card{background:linear-gradient(160deg,#061528,#091E35);border:1px solid #0D2137;border-top:2px solid #F5A623;border-radius:2px;padding:1.1rem 1.5rem;margin-bottom:0.9rem}
.ticker-tag{font-family:'IBM Plex Mono',monospace;font-size:0.56rem;color:#F5A623;letter-spacing:0.32em;margin-bottom:5px}
.ticker-name{font-size:1.38rem;font-weight:700;color:#FFFFFF;line-height:1.2;font-family:'IBM Plex Sans',sans-serif}
.ticker-meta{font-family:'IBM Plex Mono',monospace;font-size:0.73rem;color:#5A88B0;margin-top:3px}
.ticker-price{font-family:'IBM Plex Mono',monospace;font-size:1.75rem;font-weight:700;color:#FFFFFF;text-align:right}
.mover-card{background:linear-gradient(160deg,#061528,#091E35);border:1px solid #0D2137;border-radius:2px;padding:0.5rem 0.85rem;margin-bottom:0.28rem;display:flex;justify-content:space-between;align-items:center}
.term-box{background:#020810;border:1px solid #0D2137;border-radius:2px;padding:0.82rem 1.05rem;font-family:'IBM Plex Mono',monospace;font-size:0.76rem;color:#C8D8EC;margin-bottom:0.7rem}
.alert-box{background:linear-gradient(160deg,#061528,#091E35);border-left:3px solid #F5A623;border-radius:2px;padding:0.65rem 0.95rem;margin-bottom:0.38rem;font-size:0.81rem;color:#C8D8EC;line-height:1.65}
.src-badge{display:inline-block;background:#0D2137;border:1px solid #1E4976;border-radius:2px;padding:1px 6px;font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#F5A623;letter-spacing:0.08em;margin-left:6px;vertical-align:middle}
.stProgress>div>div{background-color:#F5A623!important}
[data-testid="stTabs"] [role="tab"]{font-family:'IBM Plex Mono',monospace!important;font-size:0.66rem!important;letter-spacing:0.12em!important;text-transform:uppercase!important;color:#5A88B0!important;background:transparent!important;border:none!important;padding:0.48rem 1rem!important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{color:#F5A623!important;border-bottom:2px solid #F5A623!important}
[data-testid="stTabsContent"]{padding-top:0.9rem!important}
</style>
"""


# ─────────────────────────────────────────────────────────
#  AGGRID WRAPPER  (graceful fallback → st.dataframe)
# ─────────────────────────────────────────────────────────
def _aggrid_ok() -> bool:
    try:
        import importlib
        return importlib.util.find_spec("st_aggrid") is not None
    except Exception:
        return False


def navy_grid(df: pd.DataFrame, height: int = 380, key: str = "grid") -> None:
    """
    Render a Bloomberg-style AgGrid table.
    Applies neon-green / crimson conditional colouring on numeric columns.
    Falls back to st.dataframe if st_aggrid is not installed.
    """
    if df is None or df.empty:
        st.markdown(
            "<div class='term-box' style='color:#E74C3C;border-left:3px solid #E74C3C'>"
            "⚠ Data Stream Interrupted — no records available.</div>",
            unsafe_allow_html=True,
        )
        return

    if _aggrid_ok():
        try:
            from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, ColumnsAutoSizeMode  # type: ignore
            from st_aggrid.shared import GridUpdateMode  # type: ignore

            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_default_column(
                resizable=True, sortable=True, filter=True,
                cellStyle={"fontFamily": "IBM Plex Mono, monospace", "fontSize": "11px"},
            )

            # Numeric green/red
            for col in df.select_dtypes(include=[float, int]).columns:
                gb.configure_column(col, cellStyle=JsCode("""
                    function(p){
                        if(p.value>0)  return{color:'#2ECC71',fontWeight:'700'};
                        if(p.value<0)  return{color:'#E74C3C',fontWeight:'700'};
                        return{color:'#F5A623'};
                    }"""))

            # String % columns
            for col in df.columns:
                if df[col].dtype == object and df[col].astype(str).str.contains("%").any():
                    gb.configure_column(col, cellStyle=JsCode("""
                        function(p){
                            var v=parseFloat(p.value);
                            if(!isNaN(v)){
                                if(v>0) return{color:'#2ECC71',fontWeight:'700'};
                                if(v<0) return{color:'#E74C3C',fontWeight:'700'};
                            }
                            return{color:'#F5A623'};
                        }"""))

            gb.configure_grid_options(domLayout="normal", rowHeight=26, headerHeight=30)
            opts = gb.build()

            custom_css = {
                ".ag-root-wrapper":      {"background-color":"#06111F","border":"1px solid #0D2137"},
                ".ag-header":            {"background-color":"#030A14","border-bottom":"1px solid #1E4976"},
                ".ag-header-cell-label": {"color":"#5A88B0","font-size":"10px","text-transform":"uppercase",
                                          "letter-spacing":"0.1em","font-family":"IBM Plex Mono,monospace"},
                ".ag-row":               {"background-color":"#06111F","border-bottom":"1px solid #091827"},
                ".ag-row:hover":         {"background-color":"#0D2137!important"},
                ".ag-cell":              {"color":"#C8D8EC","font-family":"IBM Plex Mono,monospace","font-size":"11px"},
            }

            AgGrid(
                df, gridOptions=opts, height=height, theme="alpine",
                custom_css=custom_css,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                update_mode=GridUpdateMode.NO_UPDATE,
                allow_unsafe_jscode=True, key=key,
            )
            return
        except Exception:
            pass

    # Fallback
    st.dataframe(df, use_container_width=True, height=height)


# ─────────────────────────────────────────────────────────
#  PLOTLY BASE THEME
# ─────────────────────────────────────────────────────────
_PLOTLY_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(2,8,16,0)",
    plot_bgcolor="rgba(6,17,31,0.90)",
    font=dict(color="#C8D8EC", family="IBM Plex Mono, monospace", size=10),
    legend=dict(
        bgcolor="rgba(3,10,20,0.92)", bordercolor="#0D2137", borderwidth=1,
        font=dict(size=9), orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
    ),
    margin=dict(l=20, r=20, t=30, b=20),
    hovermode="x unified", dragmode="zoom",
    hoverlabel=dict(bgcolor="#06111F", bordercolor="#F5A623",
                    font=dict(family="IBM Plex Mono", color="#E8F0F8", size=11)),
)


def _merge(base: dict, over: dict) -> dict:
    r = dict(base)
    for k, v in over.items():
        r[k] = _merge(r[k], v) if isinstance(v, dict) and isinstance(r.get(k), dict) else v
    return r


def pla(overrides: dict | None = None) -> dict:
    return _merge(_PLOTLY_BASE, overrides) if overrides else dict(_PLOTLY_BASE)


def xaxis_time(bar: bool = False) -> dict:
    d = dict(
        gridcolor="#091827", showgrid=True, zeroline=False,
        rangeselector=dict(
            bgcolor="#06111F", activecolor="#F5A623", bordercolor="#0D2137",
            font=dict(color="#FFFFFF", size=9),
            buttons=[
                dict(count=5,   label="5D",  step="day",   stepmode="backward"),
                dict(count=1,   label="1M",  step="month", stepmode="backward"),
                dict(count=3,   label="3M",  step="month", stepmode="backward"),
                dict(count=6,   label="6M",  step="month", stepmode="backward"),
                dict(count=1,   label="1Y",  step="year",  stepmode="backward"),
                dict(count=3,   label="3Y",  step="year",  stepmode="backward"),
                dict(count=5,   label="5Y",  step="year",  stepmode="backward"),
                dict(count=10,  label="10Y", step="year",  stepmode="backward"),
                dict(step="all",label="MAX"),
            ],
        ),
    )
    if not bar:
        d["rangeslider"] = dict(visible=True, bgcolor="#020810", thickness=0.03)
    return d


def yaxis_plain(title: str = "") -> dict:
    return dict(gridcolor="#091827", showgrid=True, zeroline=False, title=title)


# ─────────────────────────────────────────────────────────
#  ADVANCED CANDLESTICK CHART
# ─────────────────────────────────────────────────────────
def build_candle_chart(ticker: str, df: pd.DataFrame, indicators: list[str], label: str = "") -> go.Figure:
    """
    Multi-pane candlestick chart.
    Ichimoku cloud includes full +26-bar forward projection.
    All sub-pane oscillators are stacked below volume automatically.
    """
    sub_panes = [i for i in indicators if i in ("MACD","RSI","Stochastic","Williams %R","CCI")]
    n_rows    = 2 + len(sub_panes)
    heights   = [0.50, 0.12] + [0.10] * len(sub_panes)
    norm_h    = [h / sum(heights) for h in heights]

    fig = make_subplots(rows=n_rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.018, row_heights=norm_h)

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name=ticker,
        increasing_line_color="#2ECC71",  decreasing_line_color="#E74C3C",
        increasing_fillcolor="rgba(46,204,113,0.85)", decreasing_fillcolor="rgba(231,76,60,0.85)",
        line_width=1.1,
    ), row=1, col=1)

    # ── Moving averages
    if "SMA 20"  in indicators: fig.add_trace(go.Scatter(x=df.index,y=sma(df["Close"],20), name="SMA20",  line=dict(color="#F5A623",width=1.2)), row=1,col=1)
    if "SMA 50"  in indicators: fig.add_trace(go.Scatter(x=df.index,y=sma(df["Close"],50), name="SMA50",  line=dict(color="#3B8EF0",width=1.2)), row=1,col=1)
    if "SMA 200" in indicators: fig.add_trace(go.Scatter(x=df.index,y=sma(df["Close"],200),name="SMA200", line=dict(color="#9B59B6",width=1.5)), row=1,col=1)
    if "EMA 20"  in indicators: fig.add_trace(go.Scatter(x=df.index,y=ema(df["Close"],20), name="EMA20",  line=dict(color="#F39C12",width=1.2,dash="dot")), row=1,col=1)
    if "EMA 50"  in indicators: fig.add_trace(go.Scatter(x=df.index,y=ema(df["Close"],50), name="EMA50",  line=dict(color="#00BCD4",width=1.2,dash="dot")), row=1,col=1)

    # Bollinger Bands
    if "Bollinger Bands" in indicators:
        u, m, l = bollinger(df["Close"])
        fig.add_trace(go.Scatter(x=df.index,y=u,name="BB Up",  line=dict(color="rgba(245,166,35,0.55)",width=1.1)), row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=m,name="BB Mid", line=dict(color="rgba(245,166,35,0.30)",width=1.0,dash="dot")), row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=l,name="BB Low", line=dict(color="rgba(245,166,35,0.55)",width=1.1),
                                 fill="tonexty", fillcolor="rgba(245,166,35,0.04)"), row=1,col=1)

    # VWAP
    if "VWAP" in indicators:
        fig.add_trace(go.Scatter(x=df.index,y=vwap(df),name="VWAP",line=dict(color="#00BCD4",width=1.5,dash="dash")), row=1,col=1)

    # Ichimoku (full cloud + chikou)
    if "Ichimoku" in indicators:
        ic = ichimoku(df)
        fig.add_trace(go.Scatter(x=df.index,y=ic["tenkan"],name="Tenkan",line=dict(color="#E74C3C",width=1.1)), row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=ic["kijun"], name="Kijun", line=dict(color="#3B8EF0",width=1.1)), row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=ic["span_a"],name="Span A",line=dict(color="rgba(46,204,113,0.55)",width=1.0)), row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=ic["span_b"],name="Span B",line=dict(color="rgba(231,76,60,0.55)",width=1.0),
                                 fill="tonexty",fillcolor="rgba(120,120,120,0.07)"), row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=ic["chikou"],name="Chikou",line=dict(color="rgba(245,166,35,0.6)",width=1.0,dash="dot")), row=1,col=1)

    # Fibonacci
    if "Fibonacci" in indicators:
        fib_colors = {"0.0%":"rgba(231,76,60,0.55)","23.6%":"rgba(245,166,35,0.45)","38.2%":"rgba(245,166,35,0.55)",
                      "50.0%":"rgba(255,255,255,0.45)","61.8%":"rgba(46,204,113,0.55)","78.6%":"rgba(59,142,240,0.45)","100%":"rgba(46,204,113,0.35)"}
        for lbl, val in fibonacci(df).items():
            fig.add_hline(y=val, line_dash="dot", line_color=fib_colors.get(lbl,"rgba(245,166,35,0.4)"),
                          annotation_text=f"  Fib {lbl}  {val:,.2f}",
                          annotation_font_color="#F5A623", annotation_font_size=9, row=1, col=1)

    # Volume + OBV
    vol_colors = ["#2ECC71" if float(df["Close"].iloc[i]) >= float(df["Open"].iloc[i]) else "#E74C3C" for i in range(len(df))]
    fig.add_trace(go.Bar(x=df.index,y=df["Volume"],name="Volume",marker_color=vol_colors,opacity=0.65,showlegend=False), row=2,col=1)
    if "OBV" in indicators:
        fig.add_trace(go.Scatter(x=df.index,y=obv(df),name="OBV",line=dict(color="#F5A623",width=1.2)), row=2,col=1)
    fig.update_yaxes(title_text="VOL",row=2,col=1,gridcolor="#091827",tickfont=dict(size=8))

    # Sub-pane oscillators
    sub_row = 3
    for ind in sub_panes:
        if ind == "MACD":
            ml, sg, hist = macd(df["Close"])
            hcol = ["#2ECC71" if v >= 0 else "#E74C3C" for v in hist.fillna(0)]
            fig.add_trace(go.Bar(x=df.index,y=hist,name="MACD Hist",marker_color=hcol,opacity=0.8,showlegend=False), row=sub_row,col=1)
            fig.add_trace(go.Scatter(x=df.index,y=ml,name="MACD",   line=dict(color="#3B8EF0",width=1.3)), row=sub_row,col=1)
            fig.add_trace(go.Scatter(x=df.index,y=sg,name="Signal", line=dict(color="#F5A623",width=1.3)), row=sub_row,col=1)
            fig.update_yaxes(title_text="MACD",row=sub_row,col=1,gridcolor="#091827",zeroline=True,zerolinecolor="#1E4976",tickfont=dict(size=8))
        elif ind == "RSI":
            rv = rsi(df["Close"])
            fig.add_trace(go.Scatter(x=df.index,y=rv,name="RSI",line=dict(color="#F5A623",width=1.5)), row=sub_row,col=1)
            fig.add_hline(y=70,line_dash="dot",line_color="rgba(231,76,60,0.6)",    row=sub_row,col=1)
            fig.add_hline(y=30,line_dash="dot",line_color="rgba(46,204,113,0.6)",   row=sub_row,col=1)
            fig.add_hrect(y0=70,y1=100,fillcolor="rgba(231,76,60,0.04)",            row=sub_row,col=1,line_width=0)
            fig.add_hrect(y0=0,y1=30,  fillcolor="rgba(46,204,113,0.04)",           row=sub_row,col=1,line_width=0)
            fig.update_yaxes(title_text="RSI",range=[0,100],row=sub_row,col=1,gridcolor="#091827",tickfont=dict(size=8))
        elif ind == "Stochastic":
            ks, ds = stochastic(df)
            fig.add_trace(go.Scatter(x=df.index,y=ks,name="%K",line=dict(color="#F5A623",width=1.3)), row=sub_row,col=1)
            fig.add_trace(go.Scatter(x=df.index,y=ds,name="%D",line=dict(color="#3B8EF0",width=1.3)), row=sub_row,col=1)
            fig.add_hline(y=80,line_dash="dot",line_color="rgba(231,76,60,0.6)",row=sub_row,col=1)
            fig.add_hline(y=20,line_dash="dot",line_color="rgba(46,204,113,0.6)",row=sub_row,col=1)
            fig.update_yaxes(title_text="STOCH",range=[0,100],row=sub_row,col=1,gridcolor="#091827",tickfont=dict(size=8))
        elif ind == "Williams %R":
            wr = williams_r(df)
            fig.add_trace(go.Scatter(x=df.index,y=wr,name="W%R",line=dict(color="#9B59B6",width=1.3)), row=sub_row,col=1)
            fig.add_hline(y=-20,line_dash="dot",line_color="rgba(231,76,60,0.6)",row=sub_row,col=1)
            fig.add_hline(y=-80,line_dash="dot",line_color="rgba(46,204,113,0.6)",row=sub_row,col=1)
            fig.update_yaxes(title_text="W%R",range=[-100,0],row=sub_row,col=1,gridcolor="#091827",tickfont=dict(size=8))
        elif ind == "CCI":
            cv = cci(df)
            fig.add_trace(go.Scatter(x=df.index,y=cv,name="CCI",line=dict(color="#1ABC9C",width=1.3)), row=sub_row,col=1)
            fig.add_hline(y=100, line_dash="dot",line_color="rgba(231,76,60,0.6)", row=sub_row,col=1)
            fig.add_hline(y=-100,line_dash="dot",line_color="rgba(46,204,113,0.6)",row=sub_row,col=1)
            fig.update_yaxes(title_text="CCI",row=sub_row,col=1,gridcolor="#091827",tickfont=dict(size=8))
        sub_row += 1

    chart_height = 540 + 90 * len(sub_panes)
    fig.update_layout(**pla({
        "height": chart_height,
        "title": f"<b>{ticker}</b>  ·  {label}",
        "xaxis": xaxis_time(),
        "showlegend": True,
        "xaxis_rangeslider_visible": False,
    }))
    for i in range(1, n_rows + 1):
        fig.update_xaxes(gridcolor="#091827", showgrid=True, row=i, col=1)
    return fig


# ─────────────────────────────────────────────────────────
#  LAYOUT HELPERS
# ─────────────────────────────────────────────────────────
def ptitle(text: str, sub: str = "") -> None:
    st.markdown(f"<div class='page-title'>{text}</div>", unsafe_allow_html=True)
    if sub:
        st.markdown(f"<div class='page-sub'>{sub}</div>", unsafe_allow_html=True)


def sec(text: str) -> None:
    st.markdown(f"<div class='sec-hdr'>{text}</div>", unsafe_allow_html=True)


def alert(html: str, color: str = "#F5A623") -> None:
    st.markdown(f"<div class='alert-box' style='border-left-color:{color}'>{html}</div>", unsafe_allow_html=True)


def badge(source: str) -> str:
    return f"<span class='src-badge'>{source}</span>"


def interrupted(msg: str = "Data Stream Interrupted") -> None:
    st.markdown(
        f"<div class='term-box' style='color:#E74C3C;border-left:3px solid #E74C3C'>⚠ {msg}</div>",
        unsafe_allow_html=True,
    )


def colored(val: float | None, above: float = 0, fmt: str = "{:.2f}%") -> str:
    if val is None:
        return "<span style='color:#5A88B0'>N/A</span>"
    col = "#2ECC71" if val > above else ("#E74C3C" if val < above else "#F5A623")
    return f"<span style='color:{col};font-weight:700'>{fmt.format(val)}</span>"

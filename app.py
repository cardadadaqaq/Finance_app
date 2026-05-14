import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =========================================================
# 🔑 CONFIGURAZIONE: INCOLLA LA TUA CHIAVE QUI SOTTO
# =========================================================
API_KEY = "8289268f09684b53abb50e095c0fe696" 
# =========================================================

# FORZATURA STILE NAVY & BIANCO (Global CSS)
st.set_page_config(page_title="Navy Terminal Pro", layout="wide")
st.markdown("""
    <style>
    /* Sfondo principale e Sidebar */
    .stApp, [data-testid="stSidebar"], .main {
        background-color: #000080 !important;
    }
    /* Testi globali */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #FFFFFF !important;
    }
    /* Metriche */
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #E0E0E0 !important; }
    /* Input e Selectbox */
    .stSelectbox div, .stTextInput input, .stNumberInput input {
        background-color: #000066 !important;
        color: white !important;
        border: 1px solid #FFFFFF !important;
    }
    /* Tabelle */
    .styled-table, .dataframe, [data-testid="stTable"] {
        background-color: #000066 !important;
        color: white !important;
    }
    hr { border-top: 1px solid white !important; }
    </style>
    """, unsafe_allow_html=True)

# Menu laterale
st.sidebar.title("⚓ Navy Terminal")
menu = ["🌍 Global Overview", "🧮 Analisi DCF", "📊 Multi-Compare", "🧪 Portfolio Backtest", "⌨️ Bloomberg Insights"]
choice = st.sidebar.selectbox("Navigazione", menu)

# --- 1. GLOBAL OVERVIEW (20 TITOLI) ---
if choice == "🌍 Global Overview":
    st.title("Global Market Overview")
    titles = {
        "S&P 500": "^GSPC", "Nasdaq 100": "^IXIC", "Dow Jones": "^DJI", "Nikkei 225": "^N225",
        "FTSE MIB": "FTSEMIB.MI", "DAX 40": "^GDAXI", "CAC 40": "^FCHI", "Hang Seng": "^HSI",
        "Shanghai": "000001.SS", "Euro Stoxx 50": "^STOXX50E", "Russell 2000": "^RUT", "Nifty 50": "^NSEI",
        "Apple": "AAPL", "Microsoft": "MSFT", "Nvidia": "NVDA", "Google": "GOOGL",
        "Tesla": "TSLA", "Amazon": "AMZN", "LVMH": "MC.PA", "ASML": "ASML.AS"
    }
    cols = st.columns(4)
    for i, (name, ticker) in enumerate(titles.items()):
        try:
            d = yf.Ticker(ticker).history(period="2d")
            c, p = d['Close'].iloc[-1], d['Close'].iloc[-2]
            cols[i%4].metric(name, f"{c:,.2f}", f"{((c-p)/p)*100:+.2f}%")
        except: continue

# --- 2. ANALISI DCF ---
elif choice == "🧮 Analisi DCF":
    st.title("Valutazione Discounted Cash Flow")
    fcf = st.number_input("Free Cash Flow Attuale ($)", value=1000000000)
    wacc = st.slider("WACC %", 5, 20, 9) / 100
    st.metric("Fair Value", f"${(fcf*1.1)/(wacc-0.02):,.2f}")

# --- 3. MULTI-COMPARE ---
elif choice == "📊 Multi-Compare":
    st.title("Percent Return Comparison")
    tk_in = st.text_input("Ticker (separati da virgola)", "AAPL, MSFT, TSLA")
    tk_list = [x.strip().upper() for x in tk_in.split(",")]
    horizon = st.selectbox("Orizzonte", ["Mesi", "Anni"])
    val = st.slider("Durata", 1, 24 if horizon=="Mesi" else 10, 6)
    start = datetime.now() - timedelta(days=val*30 if horizon=="Mesi" else val*365)
    
    if tk_list:
        data = yf.download(tk_list, start=start)['Close']
        rets = ((data / data.iloc[0]) - 1) * 100
        fig = go.Figure()
        for c in (rets.columns if isinstance(rets, pd.DataFrame) else [tk_list[0]]):
            fig.add_trace(go.Scatter(x=rets.index, y=rets[c] if isinstance(rets, pd.DataFrame) else rets, name=c))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# --- 4. PORTFOLIO BACKTEST (STRATEGIA COMPOSTA) ---
elif choice == "🧪 Portfolio Backtest":
    st.title("Backtest: Strategia vs Singoli Asset")
    st.write("Crea una strategia pesata (es: 60% VOO, 40% GLD)")
    
    col_a, col_w = st.columns([3, 2])
    with col_a:
        assets_in = st.text_input("Asset (es: VOO, GLD, BTC-USD)", "VOO, GLD")
    with col_w:
        weights_in = st.text_input("Pesi % (es: 60, 40)", "60, 40")
    
    benchmark = st.selectbox("Benchmark di confronto", ["^GSPC", "VWCE.DE"])
    years = st.slider("Anni", 1, 15, 5)
    start = datetime.now() - timedelta(days=365*years)

    a_list = [x.strip().upper() for x in assets_in.split(",")]
    w_list = [float(x.strip())/100 for x in weights_in.split(",")]

    if len(a_list) == len

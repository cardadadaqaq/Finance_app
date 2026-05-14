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

# Configurazione Layout Dark & Testi visibili
st.set_page_config(page_title="FinLens Terminal Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #00FF00 !important; font-weight: bold; font-size: 2rem; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-size: 1.1rem; }
    [data-testid="stMetricDelta"] { color: #FF4B4B !important; }
    .stMarkdown p { color: #FFFFFF !important; font-size: 1.05rem; }
    h1, h2, h3 { color: #FFD700 !important; } 
    .stButton>button { background-color: #333; color: white; border-radius: 5px; }
    .stDataFrame { background-color: #111; }
    </style>
    """, unsafe_allow_html=True)

# Menu laterale
st.sidebar.title("💎 FinLens Pro")
menu = ["🌍 Market Overview", "🧮 Analisi DCF", "📊 Multi-Compare", "🧪 Backtesting Lab", "⌨️ Terminal Insights"]
choice = st.sidebar.selectbox("Navigazione", menu)

# --- 1. MARKET OVERVIEW (MERCATI GLOBALI) ---
if choice == "🌍 Market Overview":
    st.title("Market Overview - Global Indices")
    
    indices = {
        "S&P 500 (USA)": "^GSPC",
        "Nasdaq (Tech)": "^IXIC",
        "Nikkei 225 (Giappone)": "^N225",
        "Hang Seng (Cina)": "^HSI",
        "DAX (Germania)": "^GDAXI",
        "FTSE MIB (Italia)": "FTSEMIB.MI"
    }
    
    cols = st.columns(3)
    for i, (name, ticker) in enumerate(indices.items()):
        try:
            data = yf.Ticker(ticker).history(period="2d")
            if len(data) >= 2:
                close = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2]
                delta = ((close - prev) / prev) * 100
                cols[i % 3].metric(name, f"{close:,.2f}", f"{delta:+.2f}%")
        except:
            continue

    st.divider()
    st.subheader("🔥 Top Movers (USA)")
    stocks = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "META"]
    s_cols = st.columns(len(stocks))
    for i, s in enumerate(stocks):
        s_data = yf.Ticker(s).history(period="2d")
        if not s_data.empty:
            s_close = s_data['Close'].iloc[-1]
            s_cols[i].metric(s, f"${s_close:,.2f}")

# --- 2. ANALISI DCF ---
elif choice == "🧮 Analisi DCF":
    st.title("Valutazione Discounted Cash Flow")
    col1, col2 = st.columns(2)
    with col1:
        fcf = st.number_input("Free Cash Flow Attuale ($)", value=1000000000)
        growth = st.slider("Tasso di Crescita (Primi 5 anni %)", 1, 50, 10) / 100
    with col2:
        wacc = st.slider("WACC (Tasso di sconto %)", 5, 20, 9) / 100
        terminal_growth = st.slider("Crescita Perpetua (%)", 1, 5, 2) / 100

    proj = [fcf * (1 + growth)**i for i in range(1, 6)]
    pv = [v / (1 + wacc)**i for i, v in enumerate(proj, 1)]
    tv = (proj[-1] * (1 + terminal_growth)) / (wacc - terminal_growth)
    pv_tv = tv / (1 + wacc)**5
    valore_intrinseco = sum(pv) + pv_tv
    
    st.metric("Valore Intrinseco Stimato", f"${valore_intrinseco:,.2f}")

# --- 3. MULTI-COMPARE (AZIENDE A SCELTA) ---
elif choice == "📊 Multi-Compare":
    st.title("Confronto Custom Aziende")
    input_tickers = st.text_input("Inserisci i Ticker separati da virgola", "AAPL, MSFT, NVDA")
    list_tickers = [x.strip().upper() for x in input_tickers.split(",")]
    
    if list_tickers:
        data = yf.download(list_tickers, period="1y")['Close']
        if len(list_tickers) > 1:
            norm_data = (data / data.iloc[0]) * 100
            st.line_chart(norm_data)
        else:
            st.line_chart(data)
        st.dataframe(data.tail(10), use_container_width=True)

# --- 4. BACKTESTING LAB (ETF & ASSETS) ---
elif choice == "🧪 Backtesting Lab":
    st.title("Simulatore Backtesting")
    assets_input = st.text_input("Inserisci Ticker (es: VWCE.DE, QQQ, BTC-USD)", "VWCE.DE, QQQ")
    assets = [x.strip().upper() for x in assets_input.split(",")]
    years = st.slider("Anni di Backtest", 1, 15, 5)
    start = datetime.now() - timedelta(days=365*years)
    
    if assets:
        data = yf.download(assets, start=start)['Close']
        norm = (data / data.iloc[0]) * 100
        st.line_chart(norm)
        for a in assets:
            total_ret = ((data[a].iloc[-1] / data[a].iloc[0]) - 1) * 100
            st.write(f"🟢 **{a}**: {total_ret:.2f}%")

# --- 5. TERMINAL INSIGHTS (PEER COMPARISON) ---
elif choice == "⌨️ Terminal Insights":
    st.title("Bloomberg Style - Peer Analysis")
    target = st.text_input("Ticker principale", "NVDA").upper()
    if target:
        try:
            t_info = yf.Ticker(target).info
            st.header(f"> {t_info.get('longName', target)}")
            st.write(f"Settore: {t_info.get('sector')} | Industria: {t_info.get('industry')}")
            
            peers_in = st.text_input("Competitor da confrontare", "AMD, INTC, AVGO")
            p_list = [target] + [x.strip().upper() for x in peers_in.split(",")]
            
            p_stats = []
            for p in p_list:
                inf = yf.Ticker(p).info
                p_stats.append({
                    "Ticker": p,
                    "Price": inf.get('currentPrice'),
                    "P/E": inf.get('forwardPE'),
                    "Cap (B)": inf.get('marketCap', 0) / 1e9
                })
            st.table(pd.DataFrame(p_stats).set_index("Ticker"))
        except:
            st.error("Ticker non trovato o errore dati.")

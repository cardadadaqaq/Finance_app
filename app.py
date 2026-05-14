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

# Configurazione Layout Navy & Bianco Lucido
st.set_page_config(page_title="FinLens Terminal Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #001f3f; }
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, span {
        color: #FFFFFF !important;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        text-shadow: 0px 0px 12px rgba(255,255,255,0.4);
    }
    [data-testid="stMetricLabel"] { color: #E0E0E0 !important; font-size: 1rem; }
    [data-testid="stSidebar"] { background-color: #001529; border-right: 1px solid #003366; }
    .stDataFrame, table { background-color: #001f3f !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Helper per calcolare data di inizio
def get_start_date(years, months):
    return datetime.now() - timedelta(days=(years*365 + months*30))

# Menu laterale
st.sidebar.title("💎 FINLENS TERMINAL")
menu = ["🌍 Market Overview", "🧮 Analisi DCF", "📊 Multi-Compare", "🧪 Backtesting Lab", "⌨️ Terminal Insights"]
choice = st.sidebar.selectbox("Navigazione", menu)

# --- 1. MARKET OVERVIEW (20+ ASSETS) ---
if choice == "🌍 Market Overview":
    st.title("Market Overview - Global Pulse")
    
    indices = {
        "S&P 500": "^GSPC", "Nasdaq 100": "^IXIC", "Dow Jones": "^DJI",
        "Nikkei 225": "^N225", "Hang Seng": "^HSI", "Shanghai": "000001.SS",
        "DAX 40": "^GDAXI", "FTSE MIB": "FTSEMIB.MI", "CAC 40": "^FCHI",
        "Euro Stoxx 50": "^STOXX50E", "IBEX 35": "^IBEX", "FTSE 100": "^FTSE",
        "KOSPI (S.Korea)": "^KS11", "ASX 200 (AUS)": "^AXJO", "Bitcoin": "BTC-USD",
        "Apple": "AAPL", "Nvidia": "NVDA", "Tesla": "TSLA", 
        "Microsoft": "MSFT", "Amazon": "AMZN", "Meta": "META"
    }
    
    cols = st.columns(3)
    for i, (name, ticker) in enumerate(indices.items()):
        try:
            data = yf.download(ticker, period="2d", progress=False)
            if not data.empty:
                c = float(data['Close'].iloc[-1])
                p = float(data['Close'].iloc[-2])
                d = ((c - p) / p) * 100
                cols[i % 3].metric(name, f"{c:,.2f}", f"{d:+.2f}%", delta_color="off")
        except:
            cols[i % 3].metric(name, "N/D", "0.00%", delta_color="off")

# --- 2. ANALISI DCF ---
elif choice == "🧮 Analisi DCF":
    st.title("🧮 Calcolatore DCF Dinamico")
    ticker_dcf = st.text_input("Inserisci Ticker (es. AAPL)", "").upper()
    if ticker_dcf:
        stock = yf.Ticker(ticker_dcf)
        fcf_val = stock.info.get('freeCashflow', 0)
        fcf = st.number_input("Free Cash Flow ($)", value=float(fcf_val) if fcf_val else 0.0)
        c1, c2 = st.columns(2)
        with c1: growth = st.slider("Crescita (%)", 1, 50, 10) / 100
        with c2: wacc = st.slider("WACC (%)", 5, 20, 10) / 100
        
        if fcf > 0:
            valore = sum([fcf * (1+growth)**i / (1+wacc)**i for i in range(1,6)]) + (fcf*(1+growth)**5 * 1.02 / (wacc-0.02)) / (1+wacc)**5
            st.metric("Fair Value Stimato", f"${valore:,.0f}", delta_color="off")
        else: st.warning("Dati FCF non disponibili. Inseriscili manualmente.")

# --- 3. MULTI-COMPARE (PERCENTUALE) ---
elif choice == "📊 Multi-Compare":
    st.title("Confronto Custom Aziende")
    input_tickers = st.text_input("Tickers (es. AAPL, TSLA)", "AAPL, MSFT").upper()
    c1, c2 = st.columns(2)
    y, m = c1.number_input("Anni", 0, 20, 1), c2.number_input("Mesi", 0, 11, 0)
    
    list_t = [x.strip() for x in input_tickers.split(",") if x.strip()]
    if list_t:
        data = yf.download(list_t, start=get_start_date(y, m))['Close']
        pct_change = ((data / data.iloc[0]) - 1) * 100
        st.subheader("Ritorno Percentuale Cumulativo (%)")
        st.line_chart(pct_change)

# --- 4. BACKTESTING LAB (PERCENTUALE + BENCHMARK) ---
elif choice == "🧪 Backtesting Lab":
    st.title("Simulatore Backtesting vs Index")
    assets_in = st.text_input("Asset (es: QQQ, BTC-USD)", "QQQ").upper()
    benchmark = st.text_input("Indice Benchmark (es: ^GSPC)", "^GSPC").upper()
    c1, c2 = st.columns(2)
    y, m = c1.number_input("Anni", 0, 30, 5), c2.number_input("Mesi", 0, 11, 0)
    
    all_t = [x.strip() for x in assets_in.split(",") if x.strip()] + [benchmark]
    if all_t:
        data = yf.download(all_t, start=get_start_date(y, m))['Close']
        pct_change = ((data / data.iloc[0]) - 1) * 100
        st.subheader("Rendimento Storico Relativo (%)")
        st.line_chart(pct_change)

# --- 5. TERMINAL INSIGHTS ---
elif choice == "⌨️ Terminal Insights":
    st.title("Bloomberg Insights & Global Connections")
    target = st.text_input("Inserisci Ticker principale", "AAPL").upper()
    if target:
        stock = yf.Ticker(target)
        info = stock.info
        st.header(f"COMPANY PROFILE: {info.get('longName', target)}")
        st.write(info.get('longBusinessSummary', "Descrizione non disponibile."))
        
        st.divider()
        peers_in = st.text_input("Competitor Globali", "MSFT, GOOGL, NVDA").upper()
        peer_list = [target] + [x.strip() for x in peers_in.split(",") if x.strip()]
        
        peer_data = []
        for p in peer_list:
            try:
                p_tick = yf.Ticker(p).info
                peer_data.append({
                    "Ticker": p,
                    "Country": p_tick.get('country'),
                    "P/E (Fwd)": round(p_tick.get('forwardPE', 0), 2),
                    "Price/Sales": round(p_tick.get('priceToSalesTrailing12Months', 0), 2),
                    "Market Cap (B)": round(p_tick.get('marketCap', 0)/1e9, 2)
                })
            except: pass
        st.table(pd.DataFrame(peer_data).set_index("Ticker"))

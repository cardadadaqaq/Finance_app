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
    
    /* Tabelle: Tutto in Bianco lucido, allineamento a destra */
    table { width: 100%; color: white !important; border-collapse: collapse; }
    th { text-align: right !important; color: #FFFFFF !important; border-bottom: 2px solid #FFFFFF; padding: 10px; }
    td { text-align: right !important; padding: 10px; border-bottom: 1px solid #112233; color: #FFFFFF !important; }
    td:first-child, th:first-child { text-align: left !important; }
    </style>
    """, unsafe_allow_html=True)

def get_start_date(years, months):
    return datetime.now() - timedelta(days=(years*365 + months*30))

# Menu laterale
st.sidebar.title("💎 FINLENS TERMINAL")
menu = ["🌍 Market Overview", "🧮 Analisi DCF", "📊 Multi-Compare", "🧪 Backtesting Lab", "⌨️ Terminal Insights"]
choice = st.sidebar.selectbox("Navigazione", menu)

# --- 1. MARKET OVERVIEW (ROBUSTO) ---
if choice == "🌍 Market Overview":
    st.title("Market Overview - Global Pulse")
    indices = {
        "S&P 500": "^GSPC", "Nasdaq 100": "^IXIC", "Dow Jones": "^DJI",
        "Nikkei 225": "^N225", "Hang Seng": "^HSI", "Shanghai": "000001.SS",
        "DAX 40": "^GDAXI", "FTSE MIB": "FTSEMIB.MI", "CAC 40": "^FCHI",
        "Euro Stoxx 50": "^STOXX50E", "IBEX 35": "^IBEX", "FTSE 100": "^FTSE",
        "KOSPI": "^KS11", "ASX 200": "^AXJO", "Bitcoin": "BTC-USD",
        "Apple": "AAPL", "Nvidia": "NVDA", "Tesla": "TSLA", 
        "Microsoft": "MSFT", "Amazon": "AMZN", "Meta": "META"
    }
    cols = st.columns(3)
    tickers_list = list(indices.values())
    try:
        raw_data = yf.download(tickers_list, period="2d", group_by='ticker', progress=False)
        for i, (name, ticker) in enumerate(indices.items()):
            try:
                df = raw_data[ticker] if len(tickers_list) > 1 else raw_data
                c = float(df['Close'].iloc[-1])
                p = float(df['Close'].iloc[-2])
                d = ((c - p) / p) * 100
                cols[i % 3].metric(name, f"{c:,.2f}", f"{d:+.2f}%", delta_color="off")
            except: cols[i % 3].metric(name, "N/D", "0.00%", delta_color="off")
    except: st.error("Errore di connessione ai dati. Ricarica la pagina.")

# --- 2. ANALISI DCF ---
elif choice == "🧮 Analisi DCF":
    st.title("🧮 Calcolatore DCF Dinamico")
    ticker_dcf = st.text_input("Inserisci Ticker (es. AAPL)", "").upper()
    if ticker_dcf:
        stock = yf.Ticker(ticker_dcf)
        fcf_val = stock.info.get('freeCashflow', 0)
        fcf = st.number_input("Free Cash Flow ($)", value=

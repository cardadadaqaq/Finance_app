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
        font-size: 2.5rem !important;
        text-shadow: 0px 0px 12px rgba(255,255,255,0.4);
    }
    [data-testid="stMetricLabel"] { color: #E0E0E0 !important; font-size: 1.1rem; }
    [data-testid="stSidebar"] { background-color: #001529; border-right: 1px solid #003366; }
    .stDataFrame, table { background-color: #001f3f !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Menu laterale
st.sidebar.title("💎 FINLENS TERMINAL")
menu = ["🌍 Market Overview", "🧮 Analisi DCF", "📊 Multi-Compare", "🧪 Backtesting Lab", "⌨️ Terminal Insights"]
choice = st.sidebar.selectbox("Navigazione", menu)

# --- 1. MARKET OVERVIEW ---
if choice == "🌍 Market Overview":
    st.title("Market Overview - Global Indices")
    indices = {
        "S&P 500 (USA)": "^GSPC", "Nasdaq (Tech)": "^IXIC",
        "Nikkei 225 (JPN)": "^N225", "Hang Seng (HK)": "^HSI",
        "DAX (GER)": "^GDAXI", "FTSE MIB (ITA)": "FTSEMIB.MI"
    }
    cols = st.columns(3)
    for i, (name, ticker) in enumerate(indices.items()):
        data = yf.Ticker(ticker).history(period="2d")
        if not data.empty:
            close = data['Close'].iloc[-1]
            prev = data['Close'].iloc[-2]
            delta = ((close - prev) / prev) * 100
            cols[i % 3].metric(name, f"{close:,.2f}", f"{delta:+.2f}%", delta_color="off")

# --- 2. ANALISI DCF DINAMICA ---
elif choice == "🧮 Analisi DCF":
    st.title("🧮 Calcolatore DCF Dinamico")
    ticker_dcf = st.text_input("Inserisci Ticker Azienda per DCF (es. AAPL, NVDA, TSLA)", "").upper()
    
    if ticker_dcf:
        stock = yf.Ticker(ticker_dcf)
        info = stock.info
        
        # Prova a recuperare dati reali, altrimenti mette 0
        cash_flow_iniziale = info.get('freeCashflow', 0)
        wacc_stimato = info.get('ebitdaMargins', 0.10) * 100 # Approssimazione se manca WACC
        
        st.subheader(f"Parametri per {info.get('longName', ticker_dcf)}")
        
        col1, col2 = st.columns(2)
        with col1:
            fcf = st.number_input("Free Cash Flow Attuale ($)", value=float(cash_flow_iniziale))
            growth = st.slider("Tasso di Crescita stimato (%)", 1, 50, 10) / 100
        with col2:
            wacc = st.slider("Tasso di Sconto / WACC (%)", 5, 20, 10) / 100
            t_growth = st.slider("Crescita Perpetua (%)", 1, 5, 2) / 100

        if fcf > 0:
            years = list(range(1, 6))
            proiezioni = [fcf * (1 + growth)**i for i in years]
            valori_attuali = [val / (1 + wacc)**i for i, val in enumerate(proiezioni, 1)]
            
            terminal_val = (proiezioni[-1] * (1 + t_growth)) / (wacc - t_growth)
            pv_terminal = terminal_val / (1 + wacc)**5
            valore_intrinseco = sum(valori_attuali) + pv_terminal
            
            st.divider()
            st.metric("Valore Intrinseco Stimato (EV)", f"${valore_intrinseco:,.0f}", delta_color="off")
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=[f"Anno {i}" for i in years], y=proiezioni, marker_color='#FFFFFF'))
            fig.update_layout(title="Proiezione Flussi di Cassa", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dati Free Cash Flow non trovati per questo ticker. Inseriscili manualmente sopra.")
    else:
        st.info("Digita un Ticker (es. MSFT) per avviare il calcolo DCF.")

# --- 3. MULTI-COMPARE ---
elif choice == "📊 Multi-Compare":
    st.title("Confronto Custom Aziende")
    input_tickers = st.text_input("Inserisci i Ticker (separati da virgola)", "AAPL, MSFT").upper()
    list_tickers = [x.strip() for x in input_tickers.split(",") if x.strip()]
    if list_tickers:
        data = yf.download(list_tickers, period="1y")['Close']
        st.line_chart((data / data.iloc[0]) * 100)

# --- 4. BACKTESTING LAB ---
elif choice == "🧪 Backtesting Lab":
    st.title("Simulatore Backtesting")
    assets_input = st.text_input("Asset da testare (es: QQQ, BTC-USD)", "QQQ").upper()
    assets = [x.strip() for x in assets_input.split(",") if x.strip()]
    if assets:
        data = yf.download(assets, period="5y")['Close']
        st.line_chart((data / data.iloc[0]) * 100)

# --- 5. TERMINAL INSIGHTS ---
elif choice == "⌨️ Terminal Insights":
    st.title("Bloomberg Style - Peer Analysis")
    target = st.text_input("Inserisci Ticker principale", "NVDA").upper()
    if target:
        t_info = yf.Ticker(target).info
        st.header(f"REPORT: {t_info.get('longName', target)}")
        peers_in = st.text_input("Ticker Competitor da confrontare", "AMD, INTC, AVGO").upper()
        peer_list = [target] + [x.strip() for x in peers_in.split(",") if x.strip()]
        
        peer_data = []
        for p in peer_list:
            try:
                p_tick = yf.Ticker(p).info
                peer_data.append({
                    "Ticker": p, "Price": p_tick.get('currentPrice'),
                    "P/E (Forward)": p_tick.get('forwardPE'),
                    "Market Cap (B)": p_tick.get('marketCap', 0) / 1e9
                })
            except: pass
        st.table(pd.DataFrame(peer_data).set_index("Ticker"))

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
    /* Rende le metriche e i testi molto più leggibili */
    [data-testid="stMetricValue"] { color: #00FF00 !important; font-weight: bold; font-size: 2rem; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; font-size: 1.1rem; }
    [data-testid="stMetricDelta"] { color: #FF4B4B !important; }
    .stMarkdown p { color: #FFFFFF !important; font-size: 1.05rem; }
    h1, h2, h3 { color: #FFD700 !important; } /* Titoli in Oro stile Bloomberg */
    .stButton>button { background-color: #333; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# Menu laterale
st.sidebar.title("💎 FinLens Pro")
menu = ["🌍 Market Overview", "🧮 Analisi DCF", "📊 Multi-Compare", "🧪 Backtesting Lab", "⌨️ Terminal Insights"]
choice = st.sidebar.selectbox("Navigazione", menu)

# --- 1. MARKET OVERVIEW (MERCATI GLOBALI) ---
if choice == "🌍 Market Overview":
    st.title("Market Overview - Global Indices")
    
    # Indici Internazionali
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
            close = data['Close'].iloc[-1]
            prev = data['Close'].iloc[-2]
            delta = ((close - prev) / prev) * 100
            cols[i % 3].metric(name, f"{close:,.2f}", f"{delta:+.2f}%")
        except:
            cols[i % 3].metric(name, "N/D", "0%")

    st.divider()
    st.subheader("🔥 Top Movers (USA)")
    stocks = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "META"]
    s_cols = st.columns(len(stocks))
    for i, s in enumerate(stocks):
        s_data = yf.Ticker(s).history(period="2d")
        s_close = s_data['Close'].iloc[-1]
        s_cols[i].metric(s, f"${s_close:,.2f}")

# --- 3. MULTI-COMPARE (AZIENDE A SCELTA) ---
elif choice == "📊 Multi-Compare":
    st.title("Confronto Custom Aziende")
    input_tickers = st.text_input("Inserisci i Ticker separati da virgola (es: AAPL, TSLA, NVDA, GOOGL)", "AAPL, MSFT")
    list_tickers = [x.strip().upper() for x in input_tickers.split(",")]
    
    if list_tickers:
        period = st.selectbox("Periodo", ["1mo", "3mo", "6mo", "1y", "5y"], index=3)
        data = yf.download(list_tickers, period=period)['Close']
        if len(list_tickers) > 1:
            norm_data = (data / data.iloc[0]) * 100
            st.subheader("Performance Relativa (Base 100)")
            st.line_chart(norm_data)
        else:
            st.line_chart(data)
            
        st.subheader("Dati Statistici")
        st.dataframe(data.tail(10).style.format("{:.2f}"), use_container_width=True)

# --- 4. BACKTESTING LAB (ETF & ASSETS) ---
elif choice == "🧪 Backtesting Lab":
    st.title("Simulatore Backtesting")
    assets_input = st.text_input("Asset da testare (es: CSSPX.MI, VWCE.DE, BTC-USD)", "VWCE.DE, QQQ")
    assets = [x.strip().upper() for x in assets_input.split(",")]
    
    years = st.slider("Anni di Backtest", 1, 20, 5)
    start = datetime.now() - timedelta(days=365*years)
    
    if assets:
        data = yf.download(assets, start=start)['Close']
        norm = (data / data.iloc[0]) * 100
        st.line_chart(norm)
        
        st.subheader("Rendimento Finale Stimato")
        for a in assets:
            total_ret = ((data[a].iloc[-1] / data[a].iloc[0]) - 1) * 100
            st.write(f"🟢 **{a}**: {total_ret:.2f}%")

# --- 5. TERMINAL INSIGHTS (PEER COMPARISON) ---
elif choice == "⌨️ Terminal Insights":
    st.title("Bloomberg Style - Peer Analysis")
    target = st.text_input("Inserisci Ticker principale (es. NVDA)", "NVDA").upper()
    
    if target:
        t_info = yf.Ticker(target).info
        st.header(f"Report: {t_info.get('longName')}")
        
        # Peer Analysis manuale o dinamica
        st.subheader("Peer Comparison (Valutazione & P/E)")
        # Esempio: Se cerchi NVDA, confrontiamo con AMD e INTC
        sector = t_info.get('sector')
        industry = t_info.get('industry')
        st.write(f"Settore: **{sector}** | Industria: **{industry}**")
        
        peers = st.text_input("Modifica competitor da confrontare:", "AMD, INTC, AVGO, TSM")
        peer_list = [target] + [x.strip().upper() for x in peers.split(",")]
        
        peer_data = []
        for p in peer_list:
            p_tick = yf.Ticker(p).info
            peer_data.append({
                "Ticker": p,
                "Price": p_tick.get('currentPrice'),
                "P/E (Forward)": p_tick.get('forwardPE'),
                "P/S": p_tick.get('priceToSalesTrailing12Months'),
                "EV/EBITDA": p_tick.get('enterpriseToEbitda'),
                "Market Cap (B)": p_tick.get('marketCap', 0) / 1e9
            })
        
        df_peers = pd.DataFrame(peer_data).set_index("Ticker")
        st.table(df_peers.style.highlight_max(axis=0, color='#113311').highlight_min(axis=0, color='#331111'))

# (Il codice del DCF rimane invariato, basta inserirlo qui come prima)
elif choice == "🧮 Analisi DCF":
    st.title("Valutazione Discounted Cash Flow")
    st.info("Configura i flussi di cassa per stimare il valore intrinseco.")
    # ... (inserisci qui il codice DCF del messaggio precedente)

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

# Configurazione Layout Dark Bloomberg Style
st.set_page_config(page_title="Terminal Finanziario Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stMetric { background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Menu di navigazione laterale
st.sidebar.title("FinLens Terminal")
menu = ["🌍 Mercati Generali", "🧮 Calcolatore DCF", "📊 Confronto Aziende", "🧪 Backtesting ETF", "⌨️ Bloomberg Terminal"]
choice = st.sidebar.selectbox("Vai a:", menu)

# --- 1. MERCATI GENERALI ---
if choice == "🌍 Mercati Generali":
    st.title("Stato dei Mercati Globali")
    indices = {'S&P 500': '^GSPC', 'Nasdaq 100': '^IXIC', 'DAX': '^GDAXI', 'FTSE MIB': 'FTSEMIB.MI'}
    cols = st.columns(len(indices))
    
    for i, (name, ticker) in enumerate(indices.items()):
        data = yf.Ticker(ticker).history(period="2d")
        if not data.empty:
            close = data['Close'].iloc[-1]
            delta = close - data['Close'].iloc[-2]
            cols[i].metric(name, f"{close:,.2f}", f"{delta:+.2f}")

# --- 2. CALCOLATORE DCF ---
elif choice == "🧮 Calcolatore DCF":
    st.title("Valutazione Discounted Cash Flow (DCF)")
    col1, col2 = st.columns(2)
    with col1:
        fcf = st.number_input("Free Cash Flow Attuale ($)", value=1000000000)
        growth = st.slider("Tasso di Crescita stimato (Primi 5 anni %)", 1, 50, 10) / 100
    with col2:
        wacc = st.slider("WACC (Tasso di sconto %)", 5, 20, 9) / 100
        terminal_growth = st.slider("Crescita Perpetua (%)", 1, 5, 2) / 100

    # Calcolo DCF
    proiezioni = [fcf * (1 + growth)**i for i in range(1, 6)]
    valori_attuali = [val / (1 + wacc)**i for i, val in enumerate(proiezioni, 1)]
    terminal_value = (proiezioni[-1] * (1 + terminal_growth)) / (wacc - terminal_growth)
    pv_tv = terminal_value / (1 + wacc)**5
    valore_intrinseco = sum(valori_attuali) + pv_tv
    
    st.metric("Valore Intrinseco Stimato", f"${valore_intrinseco:,.2F}")
    st.info("Nota: Questo è un modello semplificato a 5 anni.")

# --- 3. CONFRONTO AZIENDE ---
elif choice == "📊 Confronto Aziende":
    st.title("Comparazione Multipla Performance")
    tickers = st.multiselect("Aggiungi Ticker da confrontare", ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMD"], ["AAPL", "NVDA"])
    
    if tickers:
        data = yf.download(tickers, period="1y")['Close']
        # Normalizzazione a 100
        norm_data = (data / data.iloc[0]) * 100
        st.line_chart(norm_data)
        st.subheader("Statistiche storiche (Ultimo anno)")
        st.dataframe(data.describe(), use_container_width=True)

# --- 4. BACKTESTING ETF ---
elif choice == "🧪 Backtesting ETF":
    st.title("🧪 Backtest Strategie Personalizzate")
    assets = st.text_input("Inserisci i Ticker separati da virgola (es: VWCE.DE, CSPX.L, QQQ)", "VWCE.DE, QQQ")
    lista_assets = [x.strip() for x in assets.split(",")]
    
    start_date = st.date_input("Data inizio test", datetime.now() - timedelta(days=365*5))
    
    if lista_assets:
        data = yf.download(lista_assets, start=start_date)['Close']
        if isinstance(data, pd.Series): data = data.to_frame()
        
        norm_data = (data / data.iloc[0]) * 100
        st.subheader("Rendimento Cumulato (Base 100)")
        st.line_chart(norm_data)
        
        # Calcolo rendimento finale
        st.subheader("Risultati Finali")
        for asset in lista_assets:
            rendimento = ((data[asset].iloc[-1] / data[asset].iloc[0]) - 1) * 100
            st.write(f"**{asset}**: {rendimento:.2f}% di rendimento totale nel periodo.")

# --- 5. BLOOMBERG TERMINAL ---
elif choice == "⌨️ Bloomberg Terminal":
    st.title("Terminal Insights & Peer Search")
    search = st.text_input("SEARCH COMMAND (es. AAPL)", "AAPL").upper()
    
    if search:
        info = yf.Ticker(search).info
        st.header(f"> {info.get('longName', search)}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(info.get('longBusinessSummary', 'Descrizione non disponibile.'))
        with col2:
            st.metric("Price", f"${info.get('currentPrice', 'N/D')}")
            st.write(f"**Settore:** {info.get('sector')}")
            st.write(f"**Industry:** {info.get('industry')}")
            st.write(f"**Sede:** {info.get('city')}, {info.get('country')}")

        st.divider()
        st.subheader("Aziende correlate (Peer Group)")
        st.info(f"Ricerca di altre aziende nel settore: {info.get('sector')}")
        # Qui potremmo espandere con una chiamata API specifica

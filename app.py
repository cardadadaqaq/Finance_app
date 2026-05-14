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

# Configurazione Layout Navy & White
st.set_page_config(page_title="FinLens Terminal Navy", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #000080; color: #FFFFFF; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #F0F0F0 !important; }
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #FFFFFF !important; }
    .stSelectbox label, .stTextInput label, .stSlider label { color: #FFFFFF !important; }
    .stDataFrame { border: 1px solid #FFFFFF; background-color: #000066; }
    /* Forza il testo delle tabelle in bianco */
    .dataframe { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Menu laterale
st.sidebar.title("⚓ Navy Terminal")
if API_KEY == "INCOLLA_QUI_LA_TUA_CHIAVE_TWELVE_DATA":
    st.sidebar.warning("⚠️ API Key mancante")
else:
    st.sidebar.success("✅ API Key caricata")

menu = ["🌍 Global Overview", "🧮 Analisi DCF", "📊 Multi-Compare", "🧪 Backtesting & Benchmark", "⌨️ Bloomberg Insights"]
choice = st.sidebar.selectbox("Navigazione", menu)

# --- 1. GLOBAL OVERVIEW (20 TITOLI: INDICI + TOP STOCKS) ---
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
            data = yf.Ticker(ticker).history(period="2d")
            close = data['Close'].iloc[-1]
            prev = data['Close'].iloc[-2]
            delta = ((close - prev) / prev) * 100
            cols[i % 4].metric(name, f"{close:,.2f}", f"{delta:+.2f}%")
        except:
            continue

# --- 2. ANALISI DCF ---
elif choice == "🧮 Analisi DCF":
    st.title("Valutazione Discounted Cash Flow")
    col1, col2 = st.columns(2)
    with col1:
        fcf = st.number_input("Free Cash Flow Attuale ($)", value=1000000000)
        growth = st.slider("Crescita (Primi 5 anni %)", 1, 50, 10) / 100
    with col2:
        wacc = st.slider("WACC %", 5, 20, 9) / 100
        t_growth = st.slider("Crescita Perpetua %", 1, 5, 2) / 100
    
    # Calcolo rapido
    fair_value = (fcf * (1 + growth)) / (wacc - t_growth)
    st.metric("Fair Value Stimato", f"${fair_value:,.2f}")

# --- 3. MULTI-COMPARE (RETURN % & TIME HORIZON) ---
elif choice == "📊 Multi-Compare":
    st.title("Percent Return Comparison")
    input_tickers = st.text_input("Inserisci Ticker (es: AAPL, MSFT, BTC-USD)", "AAPL, MSFT")
    list_tickers = [x.strip().upper() for x in input_tickers.split(",")]
    
    horizon = st.selectbox("Orizzonte Temporale", ["Mesi", "Anni"])
    val_durata = st.slider("Durata", 1, 24 if horizon == "Mesi" else 10, 6)
    
    days = val_durata * 30 if horizon == "Mesi" else val_durata * 365
    start_date = datetime.now() - timedelta(days=days)
    
    if list_tickers:
        data = yf.download(list_tickers, start=start_date)['Close']
        if isinstance(data, pd.Series): data = data.to_frame()
        # Calcolo Ritorno Percentuale
        returns = ((data / data.iloc[0]) - 1) * 100
        
        fig = go.Figure()
        for col in returns.columns:
            fig.add_trace(go.Scatter(x=returns.index, y=returns[col], name=col))
        
        fig.update_layout(
            yaxis_title="Rendimento %", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color="white"),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

# --- 4. BACKTESTING & BENCHMARK ---
elif choice == "🧪 Backtesting & Benchmark":
    st.title("Backtesting vs Benchmark")
    col1, col2 = st.columns(2)
    with col1:
        asset = st.text_input("Asset da testare (es: QQQ)", "QQQ").upper()
    with col2:
        benchmark = st.selectbox("Seleziona Benchmark", ["^GSPC", "^IXIC", "IWDA.AS", "EIMI.L"])
    
    years = st.slider("Orizzonte (Anni)", 1, 20, 5)
    start = datetime.now() - timedelta(days=365*years)
    
    data = yf.download([asset, benchmark], start=start)['Close']
    norm = ((data / data.iloc[0]) - 1) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=norm.index, y=norm[asset], name=f"Asset: {asset}", line=dict(width=3, color='#00FF00')))
    fig.add_trace(go.Scatter(x=norm.index, y=norm[benchmark], name=f"Benchmark: {benchmark}", line=dict(dash='dash', color='white')))
    
    fig.update_layout(yaxis_title="Rendimento %", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# --- 5. BLOOMBERG INSIGHTS ---
elif choice == "⌨️ Bloomberg Insights":
    st.title("Company Terminal Insights")
    target = st.text_input("Ticker principale", "NVDA").upper()
    
    if target:
        tk = yf.Ticker(target)
        info = tk.info
        
        st.header(f"🏛️ {info.get('longName', target)}")
        
        # Descrizione e News
        col_desc, col_news = st.columns([2, 1])
        with col_desc:
            st.subheader("Business Summary")
            st.write(info.get('longBusinessSummary', "Descrizione non disponibile."))
        with col_news:
            st.subheader("Recent News")
            news = tk.news[:5]
            for item in news:
                st.markdown(f"- [{item['title']}]({item['link']})")
        
        st.divider()
        
        # Tabella Comparativa Professionale
        st.subheader("📊 Statistics & Peer Comparison")
        peers_in = st.text_input("Modifica Competitor", "AMD, INTC, AVGO, TSM")
        p_list = [target] + [x.strip().upper() for x in peers_in.split(",")]
        
        p_data = []
        for p in p_list:
            try:
                p_tk = yf.Ticker(p).info
                p_data.append({
                    "Ticker": p,
                    "Price": p_tk.get('currentPrice'),
                    "P/E": p_tk.get('forwardPE'),
                    "Beta": p_tk.get('beta'),
                    "P/B Ratio": p_tk.get('priceToBook'),
                    "EPS": p_tk.get('forwardEps'),
                    "Market Cap (B)": p_tk.get('marketCap', 0) / 1e9,
                    "Div. Yield %": (p_tk.get('dividendYield', 0) or 0) * 100
                })
            except: continue
        
        df_peers = pd.DataFrame(p_data).set_index("Ticker")
        st.dataframe(df_peers.style.format("{:.2f}"), use_container_width=True)

        # Settore e Connessioni
        st.divider()
        st.subheader("⛓️ Sector Connections & Industry Exposure")
        st.write(f"**Settore:** {info.get('sector')} | **Industria:** {info.get('industry')}")
        st.info(f"L'azienda {target} è un nodo centrale nel settore {info.get('industry')}. Le performance sono strettamente correlate ai competitor {peers_in} e all'andamento della domanda globale nel comparto {info.get('sector')}.")

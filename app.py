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
    .stApp, [data-testid="stSidebar"], [data-testid="stHeader"], .main {
        background-color: #000080 !important;
    }
    /* Testi globali e scritte bianche lucenti */
    h1, h2, h3, p, span, label, li, .stMarkdown {
        color: #FFFFFF !important;
        font-family: 'Helvetica', sans-serif;
    }
    /* Forza il bianco sui titoli dei grafici e widget */
    .stSelectbox label, .stTextInput label, .stSlider label, .stMultiSelect label {
        color: #FFFFFF !important;
    }
    /* Metriche */
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #F0F0F0 !important; }
    /* Input Fields */
    input {
        background-color: #000066 !important;
        color: white !important;
    }
    /* Tabelle */
    .dataframe, [data-testid="stTable"], table {
        background-color: #000066 !important;
        color: white !important;
    }
    thead tr th { color: white !important; background-color: #000044 !important; }
    tbody tr td { color: white !important; }
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
    growth = st.slider("Crescita %", 1, 50, 10) / 100
    wacc = st.slider("WACC %", 5, 20, 9) / 100
    fair_value = (fcf * (1 + growth)) / (wacc - 0.02)
    st.metric("Fair Value", f"${fair_value:,.2f}")

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
        if isinstance(rets, pd.Series):
            fig.add_trace(go.Scatter(x=rets.index, y=rets, name=tk_list[0]))
        else:
            for c in rets.columns:
                fig.add_trace(go.Scatter(x=rets.index, y=rets[c], name=c))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)

# --- 4. PORTFOLIO BACKTEST (STRATEGIA COMPOSTA) ---
elif choice == "🧪 Portfolio Backtest":
    st.title("Backtest: Strategia Composita")
    st.write("Confronta un mix di asset (es: 60% Azioni, 40% Oro) contro il Benchmark.")
    
    c1, c2 = st.columns(2)
    with c1:
        assets_in = st.text_input("Asset (es: VOO, GLD)", "VOO, GLD")
    with c2:
        weights_in = st.text_input("Pesi % (es: 60, 40)", "60, 40")
    
    bench = st.selectbox("Seleziona Benchmark", ["^GSPC", "VWCE.DE"])
    y = st.slider("Anni", 1, 15, 5)
    start = datetime.now() - timedelta(days=365*y)

    a_list = [x.strip().upper() for x in assets_in.split(",")]
    try:
        w_list = [float(x.strip())/100 for x in weights_in.split(",")]
        if len(a_list) == len(w_list):
            data = yf.download(a_list + [bench], start=start)['Close']
            norm = (data / data.iloc[0]) - 1
            
            # Calcolo Strategia
            strat = (norm[a_list] * w_list).sum(axis=1)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=norm.index, y=strat*100, name="LA TUA STRATEGIA", line=dict(width=4, color="gold")))
            fig.add_trace(go.Scatter(x=norm.index, y=norm[bench]*100, name=f"Benchmark ({bench})", line=dict(dash='dash', color='white')))
            for a in a_list:
                fig.add_trace(go.Scatter(x=norm.index, y=norm[a]*100, name=f"Solo {a}", line=dict(width=1, opacity=0.4)))
            
            fig.update_layout(yaxis_title="Rendimento %", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Errore: Il numero di asset e di pesi deve coincidere.")
    except: st.warning("Inserisci i pesi correttamente (es: 50, 50)")

# --- 5. BLOOMBERG INSIGHTS ---
elif choice == "⌨️ Bloomberg Insights":
    st.title("Company Terminal Insights")
    target = st.text_input("Ticker principale", "NVDA").upper()
    if target:
        try:
            tk = yf.Ticker(target)
            inf = tk.info
            st.header(f"🏛️ {inf.get('longName', target)}")
            
            col_desc, col_news = st.columns([2, 1])
            with col_desc:
                st.subheader("Business Summary")
                st.write(inf.get('longBusinessSummary', "N/A"))
            with col_news:
                st.subheader("Latest News")
                for n in tk.news[:5]:
                    st.markdown(f"- [{n['title']}]({n['link']})")
            
            st.divider()
            st.subheader("📊 Fundamental Peer Analysis")
            peers_in = st.text_input("Competitor", "AMD, INTC, AVGO")
            p_list = [target] + [x.strip().upper() for x in peers_in.split(",")]
            
            rows = []
            for p in p_list:
                try:
                    pi = yf.Ticker(p).info
                    rows.append({
                        "Ticker": p,
                        "Price": pi.get('currentPrice', 0),
                        "P/E": pi.get('forwardPE', 0),
                        "Beta": pi.get('beta', 0),
                        "P/B Ratio": pi.get('priceToBook', 0),
                        "EPS": pi.get('forwardEps', 0),
                        "Cap (B)": pi.get('marketCap', 0)/1e9,
                        "Yield %": (pi.get('dividendYield', 0) or 0)*100
                    })
                except: continue
            
            st.table(pd.DataFrame(rows).set_index("Ticker"))
            
            st.divider()
            st.subheader("⛓️ Sector Connections")
            st.write(f"**Settore:** {inf.get('sector')} | **Industria:** {inf.get('industry')}")
            st.info(f"L'azienda è strettamente collegata a {peers_in} tramite la supply chain del settore {inf.get('industry')}.")
        except: st.error("Ticker non trovato.")

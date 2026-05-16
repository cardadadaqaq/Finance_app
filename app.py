import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Navy Terminal Pro", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
    html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        background-color: #0A1628 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    [data-testid="stSidebar"] {
        background-color: #060E1E !important;
        border-right: 1px solid #1E3A5F !important;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #0D1F38 !important;
        border: 1px solid #1E3A5F !important;
        color: #FFFFFF !important;
    }
    [data-testid="stHeader"] {
        background-color: #060E1E !important;
        border-bottom: 1px solid #1E3A5F !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
    }
    p, span, li, div, label, .stMarkdown {
        color: #E8EDF5 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    .page-title {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.6rem;
        font-weight: 600;
        color: #FFFFFF !important;
        letter-spacing: 0.08em;
        border-left: 3px solid #4A9EFF;
        padding-left: 1rem;
        margin-bottom: 1.8rem;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 1.3rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #A8BDD4 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    [data-testid="metric-container"] {
        background-color: #0D1F38 !important;
        border: 1px solid #1E3A5F !important;
        border-radius: 6px !important;
        padding: 0.8rem 1rem !important;
    }
    .stTextInput label, .stSelectbox label, .stMultiSelect label,
    .stSlider label, .stNumberInput label, .stRadio label, label[data-testid] {
        color: #FFFFFF !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #4A9EFF !important;
        border-color: #4A9EFF !important;
    }
    .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
        color: #FFFFFF !important;
        background-color: #4A9EFF !important;
    }
    .stSlider [data-baseweb="slider"] div[class*="Track"] div:first-child {
        background-color: #4A9EFF !important;
    }
    .stSlider span { color: #A8BDD4 !important; }
    .stNumberInput input {
        background-color: #0D1F38 !important;
        color: #FFFFFF !important;
        border: 1px solid #1E3A5F !important;
        border-radius: 4px !important;
    }
    .stNumberInput button {
        background-color: #1E3A5F !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    input[type="text"], textarea, .stTextInput input {
        background-color: #0D1F38 !important;
        color: #FFFFFF !important;
        border: 1px solid #1E3A5F !important;
        border-radius: 4px !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    input[type="text"]:focus, textarea:focus {
        border-color: #4A9EFF !important;
        box-shadow: 0 0 0 1px #4A9EFF !important;
    }
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #0D1F38 !important;
        border: 1px solid #1E3A5F !important;
        color: #FFFFFF !important;
    }
    /* Dropdown aperto: sfondo bianco testo nero */
    [data-baseweb="popover"], [data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        border: 1px solid #1E3A5F !important;
    }
    [data-baseweb="option"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    [data-baseweb="option"]:hover {
        background-color: #E8F0FF !important;
        color: #000000 !important;
    }
    li[role="option"] {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    li[role="option"]:hover {
        background-color: #E8F0FF !important;
    }
    .dataframe, table {
        background-color: #0D1F38 !important;
        color: #FFFFFF !important;
        border-collapse: collapse !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.82rem !important;
    }
    thead tr th {
        color: #A8BDD4 !important;
        background-color: #060E1E !important;
        border-bottom: 1px solid #1E3A5F !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.6rem 1rem !important;
    }
    tbody tr td {
        color: #FFFFFF !important;
        border-bottom: 1px solid #111E33 !important;
        padding: 0.5rem 1rem !important;
    }
    tbody tr:hover td { background-color: #1E3A5F !important; }
    hr { border-color: #1E3A5F !important; }
    .stAlert, .stInfo, [data-testid="stNotification"] {
        background-color: #0D1F38 !important;
        border: 1px solid #1E3A5F !important;
        color: #E8EDF5 !important;
    }
    .stButton > button {
        background-color: #1E3A5F !important;
        color: #FFFFFF !important;
        border: 1px solid #4A9EFF !important;
        border-radius: 4px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.06em !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover { background-color: #4A9EFF !important; color: #000 !important; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #060E1E; }
    ::-webkit-scrollbar-thumb { background: #1E3A5F; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #4A9EFF; }
    </style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; margin-bottom:1.5rem;'>
            <div style='font-family: IBM Plex Mono, monospace; font-size:1.3rem; font-weight:700;
                        color:#FFFFFF; letter-spacing:0.15em;'>⚓ NAVY</div>
            <div style='font-family: IBM Plex Mono, monospace; font-size:0.65rem; color:#4A9EFF;
                        letter-spacing:0.3em; margin-top:2px;'>TERMINAL PRO</div>
        </div>
        <div style='height:1px; background: linear-gradient(90deg, transparent, #4A9EFF, transparent);
                    margin-bottom:1.5rem;'></div>
    """, unsafe_allow_html=True)

    menu_items = [
        ("🌍", "Global Overview"),
        ("🧮", "Analisi DCF"),
        ("📊", "Multi-Compare"),
        ("🧪", "Portfolio Backtest"),
        ("🔍", "Stock Screener"),
        ("⌨️", "Bloomberg Insights"),
    ]

    if "page" not in st.session_state:
        st.session_state.page = "Global Overview"
    if "screener_selected" not in st.session_state:
        st.session_state.screener_selected = None
    if "screener_results" not in st.session_state:
        st.session_state.screener_results = None

    for icon, label in menu_items:
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label

    st.markdown("""
        <div style='height:1px; background: linear-gradient(90deg, transparent, #1E3A5F, transparent);
                    margin-top:2rem; margin-bottom:1rem;'></div>
        <div style='font-family: IBM Plex Mono, monospace; font-size:0.6rem; color:#2E4A6E;
                    text-align:center; letter-spacing:0.12em;'>
            MARKET DATA · REAL-TIME<br>POWERED BY YFINANCE
        </div>
    """, unsafe_allow_html=True)

choice = st.session_state.page


# =========================================================
# UTILITY
# =========================================================
def page_title(text, subtitle=""):
    sub_html = (f'<p style="color:#A8BDD4; font-size:0.88rem; margin-top:-1rem; '
                f'margin-bottom:1.5rem;">{subtitle}</p>') if subtitle else ""
    st.markdown(f"<div class='page-title'>{text}</div>{sub_html}", unsafe_allow_html=True)


def interactive_xaxis():
    return dict(
        gridcolor='#111E33',
        showgrid=True,
        zeroline=False,
        rangeslider=dict(visible=True, bgcolor="#060E1E", thickness=0.04),
        rangeselector=dict(
            bgcolor="#0D1F38",
            activecolor="#4A9EFF",
            bordercolor="#1E3A5F",
            font=dict(color="#FFFFFF", size=10),
            buttons=[
                dict(count=1,  label="1M", step="month", stepmode="backward"),
                dict(count=6,  label="6M", step="month", stepmode="backward"),
                dict(count=1,  label="1A", step="year",  stepmode="backward"),
                dict(count=3,  label="3A", step="year",  stepmode="backward"),
                dict(step="all", label="Tutto"),
            ]
        )
    )


PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor='rgba(6,14,30,0.0)',
    plot_bgcolor='rgba(13,31,56,0.5)',
    font=dict(color="#E8EDF5", family="IBM Plex Mono, monospace", size=11),
    legend=dict(bgcolor='rgba(6,14,30,0.8)', bordercolor='#1E3A5F', borderwidth=1),
    xaxis=dict(gridcolor='#111E33', showgrid=True, zeroline=False),
    yaxis=dict(gridcolor='#111E33', showgrid=True, zeroline=False),
    margin=dict(l=40, r=20, t=40, b=40),
    hovermode="x unified",
    dragmode="zoom",
)


# =========================================================
# CACHING
# =========================================================
@st.cache_data(ttl=300, show_spinner=False)
def get_ticker_info(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info or len(info) <= 3:
            import time
            time.sleep(0.4)
            info = t.info
        if not info or len(info) <= 3:
            return {}
        has_price = (info.get('regularMarketPrice') is not None or
                     info.get('currentPrice') is not None or
                     info.get('previousClose') is not None)
        has_name = (info.get('longName') is not None or
                    info.get('shortName') is not None)
        if not has_price and not has_name:
            return {}
        return info
    except Exception:
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def get_ticker_history(ticker, period="2d"):
    try:
        return yf.Ticker(ticker).history(period=period)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def get_ticker_news(ticker):
    try:
        return yf.Ticker(ticker).news
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def download_single(ticker, start_str=None, period=None):
    try:
        if period:
            raw = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        else:
            raw = yf.download(ticker, start=start_str, auto_adjust=True, progress=False)
        if raw.empty:
            return pd.Series(dtype=float, name=ticker)
        if isinstance(raw.columns, pd.MultiIndex):
            close = raw['Close']
            if isinstance(close, pd.DataFrame):
                return close.iloc[:, 0].rename(ticker)
            return close.squeeze()
        close = raw['Close']
        if isinstance(close, pd.DataFrame):
            return close.iloc[:, 0].rename(ticker)
        return close.squeeze()
    except Exception:
        return pd.Series(dtype=float, name=ticker)


# =========================================================
# SUPPLY CHAIN MAP
# =========================================================
SUPPLY_CHAIN_MAP = {
    "Technology": {
        "suppliers": ["Taiwan Semiconductor (TSM)", "Samsung Electronics", "ASML (ASML.AS)",
                      "Applied Materials (AMAT)", "Lam Research (LRCX)"],
        "customers": ["Apple (AAPL)", "Microsoft (MSFT)", "Meta (META)",
                      "Amazon AWS (AMZN)", "Alphabet (GOOGL)"],
        "notes": "La supply chain tech è dominata dai foundry asiatici per la produzione di chip e dai big tech USA come clienti finali."
    },
    "Consumer Electronics": {
        "suppliers": ["Foxconn (2317.TW)", "Qualcomm (QCOM)", "Corning (GLW)", "Murata Manufacturing"],
        "customers": ["Retailer globali", "Operatori telecom", "Consumatori B2C"],
        "notes": "Fortemente dipendente da componentistica asiatica e da cicli di upgrade dei consumatori."
    },
    "Semiconductors": {
        "suppliers": ["ASML (ASML.AS)", "Applied Materials (AMAT)", "Air Products (APD)", "Shin-Etsu Chemical"],
        "customers": ["Apple (AAPL)", "Nvidia (NVDA)", "AMD", "Qualcomm (QCOM)", "Data center hyperscalers"],
        "notes": "Settore capital-intensive con altissime barriere d'ingresso. I fornitori di litografia (ASML) sono monopolisti de facto."
    },
    "Communication Services": {
        "suppliers": ["Ericsson (ERIC)", "Nokia (NOK)", "Akamai (AKAM)", "Infrastrutture cloud"],
        "customers": ["Advertiser B2B", "Consumatori B2C", "PMI globali"],
        "notes": "I ricavi dipendono prevalentemente dalla pubblicità digitale e dagli abbonamenti."
    },
    "Financial Services": {
        "suppliers": ["Bloomberg LP", "Refinitiv/LSEG", "Broadridge (BR)", "Fiserv (FISV)"],
        "customers": ["Retail banking clienti", "Investitori istituzionali", "Aziende corporate"],
        "notes": "Il settore si affida a fornitori di dati e infrastrutture IT finanziarie specializzate."
    },
    "Healthcare": {
        "suppliers": ["Thermo Fisher (TMO)", "Danaher (DHR)", "Lonza Group", "Wuxi Biologics"],
        "customers": ["Ospedali", "Assicurazioni sanitarie", "Governi", "Distributori farmaceutici"],
        "notes": "Pipeline R&D lunga e costosa; i CDMO (contract manufacturers) sono fornitori critici."
    },
    "Energy": {
        "suppliers": ["Halliburton (HAL)", "Baker Hughes (BKR)", "SLB (SLB)", "Caterpillar (CAT)"],
        "customers": ["Utility elettriche", "Raffinerie", "Industria chimica", "Governi"],
        "notes": "Ciclico, fortemente legato al prezzo del petrolio e alle politiche energetiche governative."
    },
    "Industrials": {
        "suppliers": ["3M (MMM)", "Honeywell (HON)", "Parker Hannifin (PH)", "Eaton (ETN)"],
        "customers": ["Settore aerospaziale", "Automotive", "Costruzioni", "Difesa"],
        "notes": "Ampio spettro B2B; molto sensibile al ciclo economico e agli ordini governativi."
    },
    "Consumer Defensive": {
        "suppliers": ["Archer-Daniels (ADM)", "Bunge (BG)", "Packaging Corp (PKG)", "IFF (IFF)"],
        "customers": ["Grande distribuzione (WMT, COST)", "Consumatori finali B2C"],
        "notes": "Settore anticiclico con pricing power nei brand premium. Margini sotto pressione per inflazione input."
    },
    "Consumer Cyclical": {
        "suppliers": ["Li & Fung", "Produttori asiatici OEM", "Fornitori materie prime"],
        "customers": ["Consumatori finali", "E-commerce", "Retail fisico"],
        "notes": "Fortemente correlato al ciclo del credito al consumo e alla fiducia dei consumatori."
    },
    "Real Estate": {
        "suppliers": ["Costruttori", "Gestori immobiliari", "Società di property management"],
        "customers": ["Tenant retail", "Tenant uffici", "Residenziale"],
        "notes": "Sensibile ai tassi d'interesse. I REIT distribuiscono almeno il 90% degli utili come dividendi."
    },
    "Utilities": {
        "suppliers": ["GE Vernova (GEV)", "Siemens Energy", "NextEra (NEE)", "Fuel suppliers"],
        "customers": ["Residenziale", "Industria", "Data center (domanda in forte crescita)"],
        "notes": "Settore regolato, cash flow stabile. La crescente domanda da AI/data center è un catalizzatore strutturale."
    },
    "Basic Materials": {
        "suppliers": ["Minatori di materie prime", "Produttori chimici di base"],
        "customers": ["Manifatturiero", "Costruzioni", "Automotive", "Farmaceutico"],
        "notes": "Altamente ciclico, dipendente da domanda cinese e prezzi delle commodity globali."
    },
}


# =========================================================
# BLOOMBERG INSIGHTS — funzione riutilizzabile
# =========================================================
def show_bloomberg_insights(target):
    with st.spinner(f"Recupero dati per {target}..."):
        inf = get_ticker_info(target)

        # Secondo tentativo diretto senza cache se il primo fallisce
        if not inf:
            try:
                import time
                time.sleep(0.5)
                t = yf.Ticker(target)
                inf = t.info
                if not inf or len(inf) <= 3:
                    inf = {}
            except Exception:
                inf = {}

        if not inf:
            st.error(f"❌  Ticker **{target}** non trovato. Verifica il simbolo.")
            st.markdown("""
                **Esempi di formato corretto:**
                - USA: `AAPL`, `MSFT`, `NVDA`
                - Italia: `ENI.MI`, `ENEL.MI`
                - Francia: `MC.PA`, `TTE.PA`
                - Germania: `SAP.DE`, `BMW.DE`
                - ETF: `VWCE.DE`, `SWDA.MI`
            """)
            return

        company_name = inf.get('longName') or inf.get('shortName') or inf.get('symbol')
        current_price = (inf.get('currentPrice') or inf.get('regularMarketPrice')
                         or inf.get('previousClose'))
        display_name = company_name if company_name else target

        st.markdown(f"""
            <div style='background:#0D1F38; border:1px solid #1E3A5F; border-radius:8px;
                        padding:1.2rem 1.5rem; margin-bottom:1.5rem;'>
                <div style='font-family: IBM Plex Mono, monospace; font-size:0.7rem;
                            color:#4A9EFF; letter-spacing:0.2em; margin-bottom:4px;'>EQUITY</div>
                <div style='font-size:1.6rem; font-weight:700; color:#FFFFFF;'>{display_name}</div>
                <div style='font-family: IBM Plex Mono, monospace; font-size:0.85rem;
                            color:#A8BDD4; margin-top:4px;'>
                    {target} · {inf.get('exchange', 'N/A')} · {inf.get('currency', 'N/A')}
                </div>
            </div>
        """, unsafe_allow_html=True)

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Prezzo", f"{current_price:,.2f}" if current_price else "N/A")
        k2.metric("P/E Forward", f"{inf.get('forwardPE'):.1f}" if inf.get('forwardPE') else "N/A")
        k3.metric("EPS Forward", f"{inf.get('forwardEps'):.2f}" if inf.get('forwardEps') else "N/A")
        k4.metric("Beta", f"{inf.get('beta'):.2f}" if inf.get('beta') else "N/A")
        k5.metric("Market Cap", f"${inf.get('marketCap', 0)/1e9:.1f}B" if inf.get('marketCap') else "N/A")

        st.markdown("---")

        col_desc, col_news = st.columns([2, 1])
        with col_desc:
            st.markdown("#### Business Summary")
            summary = inf.get('longBusinessSummary', '')
            st.write(summary if summary else "Descrizione non disponibile.")

        with col_news:
            st.markdown("#### Latest News")
            yahoo_url = f"https://finance.yahoo.com/quote/{target}/news/"
            st.markdown(f"""
                <div style='background:#0D1F38; border:1px solid #1E3A5F; border-radius:6px;
                            padding:1rem; margin-bottom:0.8rem;'>
                    <div style='font-family: IBM Plex Mono, monospace; font-size:0.7rem;
                                color:#4A9EFF; letter-spacing:0.15em; margin-bottom:6px;'>FONTE ESTERNA</div>
                    <div style='font-size:0.88rem; color:#E8EDF5; margin-bottom:10px;'>
                        Notizie in tempo reale su <b>{target}</b> disponibili su Yahoo Finance.
                    </div>
                    <a href='{yahoo_url}' target='_blank'
                       style='display:inline-block; background:#1E3A5F; color:#FFFFFF;
                              border:1px solid #4A9EFF; border-radius:4px;
                              padding:6px 14px; font-family: IBM Plex Mono, monospace;
                              font-size:0.78rem; letter-spacing:0.06em; text-decoration:none;'>
                        📰 Apri News su Yahoo Finance →
                    </a>
                </div>
            """, unsafe_allow_html=True)
            try:
                news_items = get_ticker_news(target)
                if news_items:
                    st.markdown("**Titoli recenti:**")
                    for n in news_items[:4]:
                        title = n.get('title', '')
                        link = n.get('link', yahoo_url)
                        if title:
                            st.markdown(f"→ [{title}]({link})")
            except Exception:
                pass

        st.markdown("---")

        st.markdown("#### Fundamental Peer Analysis")
        peers_in = st.text_input("Competitors (separati da virgola)", "AMD, INTC, AVGO",
                                 key=f"peers_{target}")
        p_list = [target] + [x.strip().upper() for x in peers_in.split(",") if x.strip()]

        with st.spinner("Caricamento dati peers..."):
            rows = []
            for p in p_list:
                try:
                    pi = get_ticker_info(p)
                    price_p = (pi.get('currentPrice') or pi.get('regularMarketPrice')
                               or pi.get('previousClose') or 0)
                    rows.append({
                        "Ticker":    p,
                        "Price":     f"{price_p:,.2f}" if price_p else "N/A",
                        "P/E Fwd":   f"{pi.get('forwardPE'):.1f}" if pi.get('forwardPE') else "N/A",
                        "EPS Fwd":   f"{pi.get('forwardEps'):.2f}" if pi.get('forwardEps') else "N/A",
                        "Beta":      f"{pi.get('beta'):.2f}" if pi.get('beta') else "N/A",
                        "P/B":       f"{pi.get('priceToBook'):.1f}" if pi.get('priceToBook') else "N/A",
                        "Cap (B$)":  f"{pi.get('marketCap',0)/1e9:.1f}" if pi.get('marketCap') else "N/A",
                        "Div Yield": f"{(pi.get('dividendYield') or 0)*100:.2f}%",
                        "52W High":  f"{pi.get('fiftyTwoWeekHigh'):.2f}" if pi.get('fiftyTwoWeekHigh') else "N/A",
                    })
                except Exception:
                    rows.append({"Ticker": p, "Price": "ERR", "P/E Fwd": "—",
                                 "EPS Fwd": "—", "Beta": "—", "P/B": "—",
                                 "Cap (B$)": "—", "Div Yield": "—", "52W High": "—"})
            if rows:
                st.dataframe(pd.DataFrame(rows).set_index("Ticker"), use_container_width=True)

        st.markdown("---")

        st.markdown("#### Sector & Industry")
        sector = inf.get('sector', 'N/A')
        industry = inf.get('industry', 'N/A')
        country = inf.get('country', 'N/A')
        exchange_name = inf.get('exchange', 'N/A')

        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Settore", sector)
        sc2.metric("Industria", industry)
        sc3.metric("Paese", country)
        sc4.metric("Exchange", exchange_name)

        st.markdown("---")

        st.markdown("#### Supply Chain & Ecosystem")
        sc_data = SUPPLY_CHAIN_MAP.get(sector, None)
        if sc_data:
            chain_col1, chain_col2 = st.columns(2)
            with chain_col1:
                st.markdown("##### 🔼 Da chi acquista — Fornitori chiave")
                for s in sc_data["suppliers"]:
                    st.markdown(f"- {s}")
            with chain_col2:
                st.markdown("##### 🔽 A chi vende — Clienti / Sbocchi")
                for c in sc_data["customers"]:
                    st.markdown(f"- {c}")
            st.info(f"💡 {sc_data['notes']}")
        else:
            st.info(f"Mappa supply chain non disponibile per il settore '{sector}'.")

        st.markdown("---")

        st.markdown("#### Andamento relativo vs Peers (12 mesi)")
        peer_tickers = [target] + [x.strip().upper() for x in peers_in.split(",") if x.strip()]
        try:
            frames = {}
            for tkr in peer_tickers:
                s = download_single(tkr, period="1y")
                if not s.empty:
                    frames[tkr] = s
            if frames:
                peer_data = pd.DataFrame(frames).dropna(how='all').ffill()
                peer_norm = ((peer_data / peer_data.iloc[0]) - 1) * 100
                peer_colors = ['#4A9EFF', '#2ECC71', '#F39C12', '#E74C3C', '#9B59B6', '#1ABC9C']
                fig_peer = go.Figure()
                for idx, col in enumerate(peer_norm.columns):
                    fig_peer.add_trace(go.Scatter(
                        x=peer_norm.index, y=peer_norm[col], name=col,
                        line=dict(width=2.5 if col == target else 1.5,
                                  color=peer_colors[idx % len(peer_colors)]),
                        hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>" + col + "</extra>"
                    ))
                fig_peer.add_hline(y=0, line_dash="dot", line_color="#2E4A6E", line_width=1)
                fig_peer.update_layout(
                    **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                    yaxis_title="Rendimento % (norm.)",
                    height=420,
                    title=f"Performance relativa: {target} vs peers (1 anno)"
                )
                st.plotly_chart(fig_peer, use_container_width=True)
        except Exception:
            st.info("Grafico peers non disponibile.")


# =========================================================
# 1. GLOBAL OVERVIEW
# =========================================================
if choice == "Global Overview":
    page_title("🌍  Global Market Overview", "Snapshot in tempo reale dei principali indici e titoli globali")

    titles = {
        "S&P 500": "^GSPC", "Nasdaq 100": "^IXIC", "Dow Jones": "^DJI", "Nikkei 225": "^N225",
        "FTSE MIB": "FTSEMIB.MI", "DAX 40": "^GDAXI", "CAC 40": "^FCHI", "Hang Seng": "^HSI",
        "Shanghai": "000001.SS", "Euro Stoxx 50": "^STOXX50E", "Russell 2000": "^RUT", "Nifty 50": "^NSEI",
        "Apple": "AAPL", "Microsoft": "MSFT", "Nvidia": "NVDA", "Google": "GOOGL",
        "Tesla": "TSLA", "Amazon": "AMZN", "LVMH": "MC.PA", "ASML": "ASML.AS"
    }

    with st.spinner("Caricamento dati di mercato..."):
        cols = st.columns(4)
        for i, (name, ticker) in enumerate(titles.items()):
            try:
                d = get_ticker_history(ticker, "2d")
                if len(d) >= 2:
                    c, p = d['Close'].iloc[-1], d['Close'].iloc[-2]
                    pct = ((c - p) / p) * 100
                    cols[i % 4].metric(name, f"{c:,.2f}", f"{pct:+.2f}%")
                else:
                    cols[i % 4].metric(name, "N/A", "—")
            except Exception:
                cols[i % 4].metric(name, "N/A", "—")


# =========================================================
# 2. ANALISI DCF
# =========================================================
elif choice == "Analisi DCF":
    page_title("🧮  Discounted Cash Flow", "Stima il fair value di un'azienda tramite il modello DCF")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Parametri di Input")
        fcf = st.number_input("Free Cash Flow Attuale ($)", value=1_000_000_000, step=50_000_000, format="%d")
        growth = st.slider("Tasso di Crescita (%)", min_value=1, max_value=50, value=10)
        wacc = st.slider("WACC (%)", min_value=5, max_value=20, value=9)
        terminal_growth = st.slider("Terminal Growth Rate (%)", min_value=0, max_value=5, value=2)
        years_dcf = st.slider("Anni di Proiezione", min_value=3, max_value=15, value=10)
        shares = st.number_input("Azioni in Circolazione", value=1_000_000_000, step=10_000_000, format="%d")

    g = growth / 100
    w = wacc / 100
    tg = terminal_growth / 100

    cash_flows, pv_flows = [], []
    for yr in range(1, years_dcf + 1):
        cf = fcf * ((1 + g) ** yr)
        pv = cf / ((1 + w) ** yr)
        cash_flows.append(cf)
        pv_flows.append(pv)

    terminal_value = (cash_flows[-1] * (1 + tg)) / (w - tg) if w > tg else 0
    pv_terminal = terminal_value / ((1 + w) ** years_dcf)
    enterprise_value = sum(pv_flows) + pv_terminal
    fair_value_per_share = enterprise_value / shares if shares > 0 else 0

    with col2:
        st.markdown("#### Risultati")
        st.metric("Enterprise Value", f"${enterprise_value/1e9:,.2f}B")
        st.metric("Fair Value per Azione", f"${fair_value_per_share:,.2f}")
        st.metric("Terminal Value (PV)", f"${pv_terminal/1e9:,.2f}B")
        st.metric("PV Cash Flows (operativi)", f"${sum(pv_flows)/1e9:,.2f}B")

    st.markdown("---")
    st.markdown("#### Proiezione Cash Flows")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[f"Anno {i+1}" for i in range(years_dcf)],
                         y=[v/1e6 for v in cash_flows], name="FCF Proiettato",
                         marker_color='#4A9EFF', opacity=0.8))
    fig.add_trace(go.Bar(x=[f"Anno {i+1}" for i in range(years_dcf)],
                         y=[v/1e6 for v in pv_flows], name="PV dei Cash Flows",
                         marker_color='#2ECC71', opacity=0.8))
    fig.update_layout(**PLOTLY_LAYOUT, yaxis_title="$ Milioni", barmode='group',
                      title="Cash Flow Proiettato vs Present Value")
    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# 3. MULTI-COMPARE
# =========================================================
elif choice == "Multi-Compare":
    page_title("📊  Multi-Asset Comparison", "Confronto rendimenti, inflazione e fondamentali aziendali")

    # --- Modalità ---
    mode = st.radio(
        "Cosa vuoi visualizzare?",
        ["📈 Rendimento % Asset", "📉 Inflazione", "🏢 Fondamentali Aziendali"],
        horizontal=True
    )

    st.markdown("---")

    # -------------------------------------------------------
    # MODALITÀ 1 — Rendimento % (identica a prima)
    # -------------------------------------------------------
    if mode == "📈 Rendimento % Asset":
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            tk_in = st.text_input("Ticker (separati da virgola)", "AAPL, MSFT, TSLA, NVDA")
        with col2:
            horizon = st.selectbox("Orizzonte", ["Mesi", "Anni"])
        with col3:
            val = st.slider("Durata", min_value=1, max_value=24 if horizon == "Mesi" else 10, value=12)

        tk_list = [x.strip().upper() for x in tk_in.split(",") if x.strip()]
        start_str = (datetime.now() - timedelta(days=val * 30 if horizon == "Mesi" else val * 365)).strftime("%Y-%m-%d")

        if tk_list:
            with st.spinner("Download dati..."):
                try:
                    frames = {}
                    for tkr in tk_list:
                        s = download_single(tkr, start_str=start_str)
                        if not s.empty:
                            frames[tkr] = s
                        else:
                            st.warning(f"⚠️ Nessun dato per {tkr}")
                    if frames:
                        data = pd.DataFrame(frames).dropna(how='all').ffill()
                        rets = ((data / data.iloc[0]) - 1) * 100
                        colors = ['#4A9EFF', '#2ECC71', '#F39C12', '#E74C3C', '#9B59B6',
                                  '#1ABC9C', '#E67E22', '#3498DB', '#EC407A', '#AB47BC']
                        fig = go.Figure()
                        for idx, col in enumerate(rets.columns):
                            fig.add_trace(go.Scatter(
                                x=rets.index, y=rets[col], name=col,
                                line=dict(width=2, color=colors[idx % len(colors)]),
                                hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>" + col + "</extra>"
                            ))
                        fig.add_hline(y=0, line_dash="dot", line_color="#2E4A6E", line_width=1)
                        fig.update_layout(
                            **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                            title="Rendimento % Normalizzato",
                            yaxis_title="Rendimento (%)",
                            height=460
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown("#### Riepilogo Rendimenti")
                        summary = pd.DataFrame({
                            "Rendimento Totale (%)": rets.iloc[-1].round(2),
                            "Max (%)": rets.max().round(2),
                            "Min (%)": rets.min().round(2),
                        })
                        st.dataframe(summary, use_container_width=True)
                except Exception as e:
                    st.error(f"Errore: {e}")

    # -------------------------------------------------------
    # MODALITÀ 2 — Inflazione
    # -------------------------------------------------------
    elif mode == "📉 Inflazione":
        st.markdown("#### Inflazione — Proxy tramite ETF")
        st.info(
            "L'inflazione ufficiale (CPI) non è disponibile via yfinance. "
            "Usiamo proxy di mercato standard: **TIP** (TIPS USA), **RINF** (aspettative inflazione USA), "
            "**ITIP** (TIPS Internazionali), e **CPIAUCSL** tramite FRED se disponibile. "
            "Puoi aggiungere ticker custom."
        )

        inflation_defaults = "TIP, RINF, ITIP, STIP"
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            infl_tickers_in = st.text_input("Ticker inflazione/TIPS", inflation_defaults)
        with col2:
            infl_horizon = st.selectbox("Orizzonte ", ["Mesi", "Anni"], key="infl_h")
        with col3:
            infl_val = st.slider("Durata ", min_value=1,
                                 max_value=24 if infl_horizon == "Mesi" else 20, value=5,
                                 key="infl_v")

        compare_asset = st.text_input(
            "Aggiungi asset da confrontare con l'inflazione (es: SPY, GLD, BTC-USD)",
            "SPY, GLD"
        )

        infl_list = [x.strip().upper() for x in infl_tickers_in.split(",") if x.strip()]
        comp_list = [x.strip().upper() for x in compare_asset.split(",") if x.strip()]
        all_infl = list(dict.fromkeys(infl_list + comp_list))

        infl_start = (datetime.now() - timedelta(
            days=infl_val * 30 if infl_horizon == "Mesi" else infl_val * 365
        )).strftime("%Y-%m-%d")

        with st.spinner("Download proxy inflazione..."):
            try:
                frames = {}
                for tkr in all_infl:
                    s = download_single(tkr, start_str=infl_start)
                    if not s.empty:
                        frames[tkr] = s
                    else:
                        st.warning(f"⚠️ Nessun dato per {tkr}")

                if frames:
                    data = pd.DataFrame(frames).dropna(how='all').ffill()
                    rets = ((data / data.iloc[0]) - 1) * 100

                    infl_colors = {
                        "TIP":  "#F39C12", "RINF": "#E74C3C",
                        "ITIP": "#E67E22", "STIP": "#F1C40F",
                        "SPY":  "#4A9EFF", "GLD":  "#2ECC71",
                        "BTC-USD": "#9B59B6",
                    }
                    default_colors = ['#4A9EFF', '#2ECC71', '#F39C12', '#E74C3C',
                                      '#9B59B6', '#1ABC9C', '#E67E22', '#AB47BC']

                    fig = go.Figure()
                    for idx, col in enumerate(rets.columns):
                        is_infl = col in infl_list
                        color = infl_colors.get(col, default_colors[idx % len(default_colors)])
                        fig.add_trace(go.Scatter(
                            x=rets.index, y=rets[col], name=col,
                            line=dict(
                                width=2.5 if is_infl else 1.5,
                                dash="solid" if is_infl else "dot",
                                color=color
                            ),
                            hovertemplate="%{x|%d %b %Y}<br>%{y:.2f}%<extra>" + col + "</extra>"
                        ))

                    fig.add_hline(y=0, line_dash="dot", line_color="#2E4A6E", line_width=1)
                    fig.update_layout(
                        **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                        title="Proxy Inflazione vs Asset (rendimento % normalizzato)",
                        yaxis_title="Rendimento % (base 100)",
                        height=480
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("#### Legenda Proxy")
                    st.markdown("""
                    | Ticker | Cosa rappresenta |
                    |--------|-----------------|
                    | **TIP** | iShares TIPS Bond ETF — obbligazioni USA indicizzate all'inflazione |
                    | **RINF** | ProShares Inflation Expectations ETF — aspettative di inflazione a 10 anni USA |
                    | **ITIP** | iShares International Inflation-Linked Bond ETF |
                    | **STIP** | iShares 0-5 Year TIPS Bond ETF — inflazione a breve termine |
                    | **GLD** | Oro — tradizionale hedge contro l'inflazione |
                    """)
            except Exception as e:
                st.error(f"Errore: {e}")

    # -------------------------------------------------------
    # MODALITÀ 3 — Fondamentali Aziendali
    # -------------------------------------------------------
    elif mode == "🏢 Fondamentali Aziendali":
        st.markdown("#### Andamento Fondamentali nel Tempo")

        col1, col2 = st.columns([3, 2])
        with col1:
            fund_tickers_in = st.text_input("Ticker aziende (separati da virgola)", "AAPL, MSFT, GOOGL")
        with col2:
            fund_metric = st.selectbox("Metrica da visualizzare", [
                "P/E Ratio (trailingPE)",
                "P/B Ratio",
                "EPS (trailingEps)",
                "Revenue (totalRevenue)",
                "EBITDA",
                "Debt/Equity",
                "Operating Margin %",
                "ROE %",
                "Free Cash Flow",
                "Market Cap (B$)",
            ])

        fund_list = [x.strip().upper() for x in fund_tickers_in.split(",") if x.strip()]

        METRIC_MAP = {
            "P/E Ratio (trailingPE)":   ("trailingPE",           1,      "P/E"),
            "P/B Ratio":                ("priceToBook",           1,      "P/B"),
            "EPS (trailingEps)":        ("trailingEps",           1,      "EPS ($)"),
            "Revenue (totalRevenue)":   ("totalRevenue",          1e9,    "Revenue (B$)"),
            "EBITDA":                   ("ebitda",                1e9,    "EBITDA (B$)"),
            "Debt/Equity":              ("debtToEquity",          100,    "D/E (x)"),
            "Operating Margin %":       ("operatingMargins",      0.01,   "Op. Margin %"),
            "ROE %":                    ("returnOnEquity",        0.01,   "ROE %"),
            "Free Cash Flow":           ("freeCashflow",          1e9,    "FCF (B$)"),
            "Market Cap (B$)":          ("marketCap",             1e9,    "Market Cap (B$)"),
        }

        yf_key, divisor, y_label = METRIC_MAP[fund_metric]

        st.info(
            f"I fondamentali tramite yfinance sono valori **puntuali** (ultimo report), "
            f"non storici. Il grafico mostra il confronto tra aziende per la metrica **{y_label}**."
        )

        if fund_list:
            with st.spinner("Caricamento fondamentali..."):
                # Dati puntuali — bar chart comparativo
                bar_data = {}
                for tkr in fund_list:
                    info = get_ticker_info(tkr)
                    val_raw = info.get(yf_key)
                    if val_raw is not None:
                        try:
                            bar_data[tkr] = float(val_raw) / divisor
                        except Exception:
                            pass

                if bar_data:
                    colors_bar = ['#4A9EFF', '#2ECC71', '#F39C12', '#E74C3C',
                                  '#9B59B6', '#1ABC9C', '#E67E22', '#AB47BC']
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(
                        x=list(bar_data.keys()),
                        y=list(bar_data.values()),
                        marker_color=colors_bar[:len(bar_data)],
                        text=[f"{v:.2f}" for v in bar_data.values()],
                        textposition='outside',
                        textfont=dict(color='#FFFFFF'),
                        hovertemplate="%{x}<br>" + y_label + ": %{y:.2f}<extra></extra>"
                    ))
                    fig_bar.update_layout(
                        **PLOTLY_LAYOUT,
                        title=f"Confronto {y_label} — Dati più recenti disponibili",
                        yaxis_title=y_label,
                        height=420,
                        showlegend=False
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                # Dati storici trimestrali — earnings e revenue
                st.markdown("---")
                st.markdown("#### 📅 Storico Trimestrale — Earnings & Revenue")
                st.caption("Dati trimestrali reali da yfinance (ultimi 4-8 trimestri disponibili)")

                hist_metric = st.selectbox("Metrica storica", [
                    "Earnings per Share (EPS)",
                    "Revenue Trimestrale",
                    "Gross Profit",
                    "Net Income",
                ], key="hist_metric_sel")

                HIST_MAP = {
                    "Earnings per Share (EPS)":  ("quarterly_earnings",    "EPS ($)"),
                    "Revenue Trimestrale":        ("quarterly_financials",  "Revenue (B$)"),
                    "Gross Profit":              ("quarterly_financials",  "Gross Profit (B$)"),
                    "Net Income":                ("quarterly_financials",  "Net Income (B$)"),
                }

                hist_key, hist_label = HIST_MAP[hist_metric]

                fig_hist = go.Figure()
                colors_hist = ['#4A9EFF', '#2ECC71', '#F39C12', '#E74C3C',
                               '#9B59B6', '#1ABC9C', '#E67E22', '#AB47BC']
                has_data = False

                for idx, tkr in enumerate(fund_list):
                    try:
                        t = yf.Ticker(tkr)
                        if hist_metric == "Earnings per Share (EPS)":
                            df_q = t.quarterly_earnings
                            if df_q is not None and not df_q.empty and 'EPS' in df_q.columns:
                                fig_hist.add_trace(go.Bar(
                                    x=df_q.index.astype(str),
                                    y=df_q['EPS'],
                                    name=tkr,
                                    marker_color=colors_hist[idx % len(colors_hist)],
                                    hovertemplate="%{x}<br>EPS: $%{y:.2f}<extra>" + tkr + "</extra>"
                                ))
                                has_data = True
                        else:
                            df_f = t.quarterly_financials
                            if df_f is not None and not df_f.empty:
                                row_map = {
                                    "Revenue Trimestrale": "Total Revenue",
                                    "Gross Profit":        "Gross Profit",
                                    "Net Income":          "Net Income",
                                }
                                row_key = row_map[hist_metric]
                                if row_key in df_f.index:
                                    series = df_f.loc[row_key].sort_index()
                                    fig_hist.add_trace(go.Bar(
                                        x=series.index.astype(str),
                                        y=series.values / 1e9,
                                        name=tkr,
                                        marker_color=colors_hist[idx % len(colors_hist)],
                                        hovertemplate="%{x}<br>" + hist_label + ": $%{y:.2f}B<extra>" + tkr + "</extra>"
                                    ))
                                    has_data = True
                    except Exception:
                        continue

                if has_data:
                    fig_hist.update_layout(
                        **PLOTLY_LAYOUT,
                        title=f"Storico Trimestrale — {hist_label}",
                        yaxis_title=hist_label,
                        barmode='group',
                        height=420
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                else:
                    st.warning("Dati trimestrali non disponibili per i ticker selezionati.")

                # Tabella riepilogativa fondamentali
                st.markdown("---")
                st.markdown("#### Tabella Fondamentali Completa")
                rows = []
                for tkr in fund_list:
                    info = get_ticker_info(tkr)
                    if not info:
                        continue
                    rows.append({
                        "Ticker":      tkr,
                        "P/E":         f"{info.get('trailingPE'):.1f}"            if info.get('trailingPE')       else "N/A",
                        "P/E Fwd":     f"{info.get('forwardPE'):.1f}"             if info.get('forwardPE')        else "N/A",
                        "P/B":         f"{info.get('priceToBook'):.1f}"           if info.get('priceToBook')      else "N/A",
                        "EPS Ttm":     f"{info.get('trailingEps'):.2f}"           if info.get('trailingEps')      else "N/A",
                        "EPS Fwd":     f"{info.get('forwardEps'):.2f}"            if info.get('forwardEps')       else "N/A",
                        "Rev (B$)":    f"{info.get('totalRevenue',0)/1e9:.1f}"    if info.get('totalRevenue')     else "N/A",
                        "EBITDA (B$)": f"{info.get('ebitda',0)/1e9:.1f}"          if info.get('ebitda')           else "N/A",
                        "FCF (B$)":    f"{info.get('freeCashflow',0)/1e9:.1f}"    if info.get('freeCashflow')     else "N/A",
                        "D/E (x)":     f"{info.get('debtToEquity',0)/100:.2f}"    if info.get('debtToEquity')     else "N/A",
                        "Op.Mgn %":    f"{info.get('operatingMargins',0)*100:.1f}" if info.get('operatingMargins') else "N/A",
                        "ROE %":       f"{info.get('returnOnEquity',0)*100:.1f}"  if info.get('returnOnEquity')   else "N/A",
                    })
                if rows:
                    st.dataframe(pd.DataFrame(rows).set_index("Ticker"), use_container_width=True)

# =========================================================
# 4. PORTFOLIO BACKTEST
# =========================================================
elif choice == "Portfolio Backtest":
    page_title("🧪  Portfolio Backtest", "Costruisci una strategia composita e confrontala con un benchmark")

    st.markdown("---")
    st.markdown("#### 1 · Composizione del Portafoglio")

    col1, _ = st.columns([1, 2])
    with col1:
        n_assets = st.slider("Numero di asset", min_value=2, max_value=8, value=3)

    assets_defaults = ["VOO", "GLD", "TLT", "QQQ", "BND", "VNQ", "EEM", "PDBC"]
    asset_list, weight_list = [], []

    st.markdown("##### Ticker")
    cols_a = st.columns(n_assets)
    for i in range(n_assets):
        with cols_a[i]:
            ticker = st.text_input(f"Asset {i+1}",
                                   value=assets_defaults[i] if i < len(assets_defaults) else "",
                                   key=f"asset_{i}")
            asset_list.append(ticker.strip().upper())

    st.markdown("##### Pesi (%)")
    cols_w = st.columns(n_assets)
    default_weight = round(100 / n_assets)
    for i in range(n_assets):
        with cols_w[i]:
            w = st.slider(f"{asset_list[i] or f'Asset {i+1}'}",
                          min_value=0, max_value=100, value=default_weight, key=f"weight_{i}")
            weight_list.append(w)

    total_weight = sum(weight_list)
    if total_weight != 100:
        st.warning(f"⚠️  La somma dei pesi è {total_weight}% — deve essere esattamente 100%.")
    else:
        st.success(f"✅  Pesi bilanciati: {total_weight}%")

    st.markdown("---")
    st.markdown("#### 2 · Benchmark e Orizzonte")

    col3, col4 = st.columns(2)
    with col3:
        bench_options = {
            "S&P 500 (^GSPC)": "^GSPC",
            "MSCI World (VWCE.DE)": "VWCE.DE",
            "Nasdaq 100 (^IXIC)": "^IXIC",
            "60/40 Custom": None
        }
        bench_label = st.selectbox("Benchmark", list(bench_options.keys()))
        bench = bench_options[bench_label]

    years = st.slider("Orizzonte temporale (anni)", min_value=1, max_value=20, value=5, key="bt_years")

    bench_eq, bench_bond = "SPY", "AGG"
    if bench is None:
        bcol1, bcol2 = st.columns(2)
        with bcol1:
            bench_eq = st.text_input("Benchmark Equity Ticker", "SPY")
        with bcol2:
            bench_bond = st.text_input("Benchmark Bond Ticker", "AGG")

    run = st.button("▶  Esegui Backtest", use_container_width=True)

    if run and total_weight == 100:
        valid_pairs = [(a, weight_list[i]) for i, a in enumerate(asset_list) if a]
        valid_assets = [p[0] for p in valid_pairs]
        w_norm = [p[1] / 100 for p in valid_pairs]
        start_str = (datetime.now() - timedelta(days=365 * years)).strftime("%Y-%m-%d")
        bench_tickers = [bench] if bench else [bench_eq.upper(), bench_bond.upper()]
        all_tickers = valid_assets + bench_tickers

        with st.spinner("Download dati storici (ticker per ticker)..."):
            try:
                frames = {}
                for tkr in all_tickers:
                    s = download_single(tkr, start_str=start_str)
                    if not s.empty:
                        frames[tkr] = s
                    else:
                        st.warning(f"⚠️ Nessun dato per {tkr} — escluso.")

                if not frames:
                    st.error("Nessun dato scaricato.")
                else:
                    data = pd.DataFrame(frames).dropna(how='all').ffill()
                    norm = (data / data.iloc[0]) - 1

                    strat_df = pd.DataFrame(index=norm.index)
                    for i, a in enumerate(valid_assets):
                        if a in norm.columns:
                            strat_df[a] = norm[a] * w_norm[i]
                        else:
                            st.warning(f"⚠️ {a} non presente — peso ignorato.")
                    strategy = strat_df.sum(axis=1)

                    if bench is None:
                        beq, bbd = bench_eq.upper(), bench_bond.upper()
                        if beq in norm.columns and bbd in norm.columns:
                            bench_series = norm[beq] * 0.6 + norm[bbd] * 0.4
                            bench_name = f"60% {beq} + 40% {bbd}"
                            bench_col = None
                        else:
                            bench_series, bench_name, bench_col = None, "", None
                    else:
                        bench_col = bench
                        bench_name = bench_label
                        bench_series = None

                    # Grafico principale
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=strategy.index, y=strategy * 100,
                        name="📐 La Tua Strategia",
                        line=dict(width=3, color="#4A9EFF"),
                        fill='tozeroy', fillcolor='rgba(74,158,255,0.07)',
                        hovertemplate="%{x|%d %b %Y}<br><b>Strategia: %{y:.2f}%</b><extra></extra>"
                    ))
                    if bench_col and bench_col in norm.columns:
                        fig.add_trace(go.Scatter(
                            x=norm.index, y=norm[bench_col] * 100,
                            name=f"📌 {bench_name}",
                            line=dict(width=2, dash='dash', color='#FFFFFF'),
                            hovertemplate="%{x|%d %b %Y}<br>Benchmark: %{y:.2f}%<extra></extra>"
                        ))
                    elif bench_series is not None:
                        fig.add_trace(go.Scatter(
                            x=bench_series.index, y=bench_series * 100,
                            name=f"📌 {bench_name}",
                            line=dict(width=2, dash='dash', color='#FFFFFF'),
                            hovertemplate="%{x|%d %b %Y}<br>Benchmark: %{y:.2f}%<extra></extra>"
                        ))
                    asset_colors = ['#2ECC71', '#F39C12', '#E74C3C', '#9B59B6',
                                    '#1ABC9C', '#E67E22', '#EC407A', '#AB47BC']
                    for idx, a in enumerate(valid_assets):
                        if a in norm.columns:
                            fig.add_trace(go.Scatter(
                                x=norm.index, y=norm[a] * 100,
                                name=f"  {a} ({valid_pairs[idx][1]}%)",
                                line=dict(width=1.2, color=asset_colors[idx % len(asset_colors)]),
                                opacity=0.5,
                                hovertemplate="%{x|%d %b %Y}<br>" + a + ": %{y:.2f}%<extra></extra>"
                            ))
                    fig.add_hline(y=0, line_dash="dot", line_color="#2E4A6E", line_width=1)
                    fig.update_layout(
                        **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                        title="Rendimento Cumulativo (%)",
                        yaxis_title="Rendimento (%)",
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Statistiche
                    st.markdown("#### Statistiche di Performance")
                    s1, s2, s3, s4 = st.columns(4)
                    total_ret = strategy.iloc[-1] * 100
                    annual_ret = ((1 + strategy.iloc[-1]) ** (1 / years) - 1) * 100 if years > 0 else 0
                    daily_rets = strategy.diff().dropna()
                    vol = daily_rets.std() * (252 ** 0.5) * 100
                    sharpe = (annual_ret / vol) if vol > 0 else 0
                    drawdown = ((strategy + 1) / (strategy + 1).cummax() - 1).min() * 100

                    s1.metric("Rendimento Totale", f"{total_ret:+.2f}%")
                    s2.metric("CAGR (annualizzato)", f"{annual_ret:+.2f}%")
                    s3.metric("Volatilità Annua", f"{vol:.2f}%")
                    s4.metric("Max Drawdown", f"{drawdown:.2f}%")
                    st.metric("Sharpe Ratio (approx)", f"{sharpe:.2f}")

                    delta_vs_bench = None
                    if bench_col and bench_col in norm.columns:
                        bench_total = norm[bench_col].iloc[-1] * 100
                        delta_vs_bench = total_ret - bench_total
                        st.metric(f"Alpha vs {bench_name}", f"{delta_vs_bench:+.2f}%",
                                  delta="Sovraperforma" if delta_vs_bench > 0 else "Sottoperforma")

                    # TIR
                    st.markdown("---")
                    st.markdown("#### Tasso Interno di Rendimento (TIR)")
                    try:
                        import numpy_financial as npf
                        n_months = years * 12
                        cash_flows_irr = [-100] + [0] * (n_months - 1) + [100 * (1 + strategy.iloc[-1])]
                        irr_monthly = npf.irr(cash_flows_irr)
                        irr_annual = (1 + irr_monthly) ** 12 - 1
                        st.metric("TIR Annualizzato", f"{irr_annual*100:+.2f}%")
                    except ImportError:
                        st.metric("TIR (approx = CAGR)", f"{annual_ret:+.2f}%",
                                  help="Per il TIR esatto: pip install numpy-financial")
                    except Exception:
                        st.info("TIR non calcolabile con i dati disponibili.")

                    # Grafico drawdown
                    st.markdown("---")
                    st.markdown("#### Drawdown nel Tempo")
                    dd_series = ((strategy + 1) / (strategy + 1).cummax() - 1) * 100
                    fig_dd = go.Figure()
                    fig_dd.add_trace(go.Scatter(
                        x=dd_series.index, y=dd_series,
                        name="Drawdown",
                        fill='tozeroy',
                        line=dict(color='#E74C3C', width=1.5),
                        fillcolor='rgba(231,76,60,0.15)',
                        hovertemplate="%{x|%d %b %Y}<br>Drawdown: %{y:.2f}%<extra></extra>"
                    ))
                    fig_dd.update_layout(
                        **{**PLOTLY_LAYOUT, "xaxis": interactive_xaxis()},
                        yaxis_title="Drawdown (%)",
                        height=300,
                        title="Drawdown dalla Massima Equity"
                    )
                    st.plotly_chart(fig_dd, use_container_width=True)

                    # Correlazione tra asset
                    st.markdown("---")
                    st.markdown("#### Matrice di Correlazione")
                    available = [a for a in valid_assets if a in norm.columns]
                    if len(available) >= 2:
                        corr_df = norm[available].pct_change().dropna().corr()
                        fig_corr = go.Figure(go.Heatmap(
                            z=corr_df.values,
                            x=corr_df.columns.tolist(),
                            y=corr_df.index.tolist(),
                            colorscale=[[0, '#E74C3C'], [0.5, '#0D1F38'], [1, '#2ECC71']],
                            zmin=-1, zmax=1,
                            text=corr_df.round(2).values,
                            texttemplate="%{text}",
                            hovertemplate="%{x} / %{y}: %{z:.2f}<extra></extra>"
                        ))
                        fig_corr.update_layout(
                            **PLOTLY_LAYOUT,
                            height=350,
                            title="Correlazione tra Asset (rendimenti giornalieri)"
                        )
                        st.plotly_chart(fig_corr, use_container_width=True)

                    # SUGGERIMENTI SPECIFICI
                    st.markdown("---")
                    st.markdown("#### 💡 Analisi e Suggerimenti Specifici")

                    suggestions = []

                    # Sharpe
                    if sharpe < 0:
                        suggestions.append(
                            f"🔴 <b>Sharpe negativo ({sharpe:.2f})</b> — Il portafoglio sta distruggendo valore "
                            f"rispetto al risk-free. Con una volatilità del {vol:.1f}% e rendimento negativo "
                            f"stai assumendo rischio senza compensazione. Individua l'asset con il peggior "
                            f"contributo al rendimento (guarda il grafico sopra) e considera di ridurne il peso "
                            f"o sostituirlo con un ETF a bassa volatilità come USMV o SPLV."
                        )
                    elif sharpe < 0.5:
                        suggestions.append(
                            f"📉 <b>Sharpe inefficiente ({sharpe:.2f})</b> — Per ogni punto percentuale di volatilità "
                            f"stai ottenendo solo {sharpe*vol/100:.2f}% di rendimento extra. "
                            f"La frontiera efficiente di Markowitz suggerisce che potresti ottenere lo stesso "
                            f"rendimento con meno rischio aggiungendo asset decorrelati: oro (correlazione storica "
                            f"con S&P ~0.0), TIPS inflation-linked, o REITs internazionali."
                        )
                    elif sharpe >= 1.5:
                        suggestions.append(
                            f"🏆 <b>Sharpe eccellente ({sharpe:.2f})</b> — Attenzione al survivorship bias: "
                            f"Sharpe così alti su finestre temporali recenti tendono a normalizzarsi. "
                            f"Verifica se il periodo analizzato include il 2020-2024 (bull market eccezionale). "
                            f"Testa la stessa strategia su un orizzonte 15-20 anni per una stima più robusta."
                        )
                    else:
                        suggestions.append(
                            f"✅ <b>Sharpe accettabile ({sharpe:.2f})</b> — Profilo rischio/rendimento nella norma "
                            f"per un portafoglio diversificato. L'obiettivo dovrebbe essere superare 1.0 "
                            f"per battere costantemente il mercato su base risk-adjusted."
                        )

                    # Volatilità con confronto esplicito
                    if vol > 25:
                        suggestions.append(
                            f"📊 <b>Volatilità molto alta ({vol:.1f}% annua vs ~16% S&P 500 storico)</b> — "
                            f"In uno scenario di stress tipo 2008 o Covid 2020, potresti sperimentare un "
                            f"drawdown temporaneo superiore al 50%. Una regola pratica: ogni 1% di volatilità "
                            f"in più rispetto al benchmark richiede +0.1 di Sharpe per giustificarsi. "
                            f"Valuta di aggiungere un 15-20% in obbligazioni aggregate (AGG) o in asset reali."
                        )
                    elif vol > 15:
                        suggestions.append(
                            f"📊 <b>Volatilità in linea con l'azionario ({vol:.1f}%)</b> — "
                            f"Se il tuo orizzonte è inferiore a 7 anni, considera di ridurre l'esposizione "
                            f"ciclica introducendo un buffer del 20-30% in bond o in asset a bassa correlazione. "
                            f"Con orizzonte lungo (10+ anni) la volatilità attuale è accettabile."
                        )

                    # Drawdown con benchmarking storico
                    if drawdown < -40:
                        suggestions.append(
                            f"⚠️ <b>Drawdown estremo ({drawdown:.1f}%)</b> — Per confronto: il Nasdaq ha impiegato "
                            f"15 anni a recuperare dal -78% del 2000-2002. Un drawdown così profondo "
                            f"implica che dovresti guadagnare {abs(drawdown)/(100+drawdown)*100:.1f}% "
                            f"dal minimo solo per tornare al pareggio. Analizza quale asset ha generato "
                            f"il drawdown maggiore dalla matrice di correlazione e considera un position sizing "
                            f"proporzionale al rischio (Kelly Criterion o risk parity)."
                        )
                    elif drawdown < -20:
                        suggestions.append(
                            f"⚠️ <b>Drawdown significativo ({drawdown:.1f}%)</b> — "
                            f"Per recuperare servono {abs(drawdown)/(100+drawdown)*100:.1f}% dal minimo. "
                            f"Un ribilanciamento trimestrale sistematico (sell high, buy low) tende a ridurre "
                            f"il drawdown medio del 15-25% su orizzonti lunghi senza sacrificare rendimento."
                        )

                    # Concentrazione con teoria
                    if len(valid_assets) < 3:
                        suggestions.append(
                            f"🔀 <b>Concentrazione elevata ({len(valid_assets)} asset)</b> — "
                            f"Con 2 soli asset il rischio idiosincratico pesa ancora significativamente. "
                            f"La ricerca di Fama-French mostra che gran parte dei benefici della diversificazione "
                            f"si ottiene con 8-15 asset non correlati. Considera di aggiungere un'esposizione "
                            f"a small-cap value (VBR), mercati emergenti (VWO) o commodities (PDBC) "
                            f"per catturare premi di rischio aggiuntivi."
                        )

                    # Correlazione alta tra asset (se disponibile)
                    if len(available) >= 2:
                        corr_vals = corr_df.values
                        import numpy as np
                        upper = corr_vals[np.triu_indices_from(corr_vals, k=1)]
                        avg_corr = upper.mean() if len(upper) > 0 else 0
                        if avg_corr > 0.7:
                            suggestions.append(
                                f"🔗 <b>Correlazione media alta tra asset ({avg_corr:.2f})</b> — "
                                f"Gli asset del portafoglio si muovono in modo molto simile, "
                                f"riducendo i benefici della diversificazione. In una fase di sell-off "
                                f"generalizzato scenderebbero tutti insieme. Considera asset con correlazione "
                                f"negativa o nulla: oro (GLD), Treasury a lungo termine (TLT), o volatilità (VXX)."
                            )
                        elif avg_corr < 0.2:
                            suggestions.append(
                                f"🌐 <b>Ottima decorrelazione tra asset (corr. media: {avg_corr:.2f})</b> — "
                                f"Il portafoglio è ben diversificato in termini di correlazione. "
                                f"Questo è uno dei fattori più importanti per la resilienza in fasi di stress."
                            )

                    # Alpha vs benchmark
                    if delta_vs_bench is not None:
                        if delta_vs_bench < -5:
                            suggestions.append(
                                f"🔴 <b>Sottoperformance rilevante vs {bench_name} ({delta_vs_bench:+.1f}%)</b> — "
                                f"Stai pagando un costo opportunità significativo rispetto al benchmark. "
                                f"Prima di modificare la strategia, verifica se la sottoperformance è concentrata "
                                f"in un periodo specifico (es. post-2022) o è strutturale. "
                                f"Se strutturale, un semplice ETF sul benchmark avrebbe fatto meglio a costo zero."
                            )
                        elif delta_vs_bench > 10:
                            suggestions.append(
                                f"🟢 <b>Alpha forte vs {bench_name} ({delta_vs_bench:+.1f}%)</b> — "
                                f"Risultato eccellente, ma attenzione: alfa così elevati tendono a ridursi "
                                f"nel tempo per mean reversion. Considera di 'cristallizzare' parte dei guadagni "
                                f"aumentando la quota in asset difensivi, o implementando un trailing stop "
                                f"sull'asset che ha contribuito maggiormente alla sovraperformance."
                            )

                    if not suggestions:
                        suggestions.append(
                            "ℹ️ Il portafoglio ha parametri nella norma. "
                            "Nessun segnale critico rilevato — continua a monitorare periodicamente."
                        )

                    for sg in suggestions:
                        st.markdown(
                            f"<div style='background:#0D1F38; border-left:3px solid #4A9EFF; "
                            f"border-radius:4px; padding:0.8rem 1rem; margin-bottom:0.6rem; "
                            f"font-size:0.88rem; line-height:1.6;'>{sg}</div>",
                            unsafe_allow_html=True
                        )

            except Exception as e:
                st.error(f"Errore durante il backtest: {e}")

    elif run and total_weight != 100:
        st.error("Correggi i pesi prima di eseguire il backtest (devono sommare a 100%).")


# =========================================================
# 5. STOCK SCREENER
# =========================================================
elif choice == "Stock Screener":

    if st.session_state.screener_selected:
        target = st.session_state.screener_selected
        col_back, _ = st.columns([1, 6])
        with col_back:
            if st.button("← Torna allo Screener"):
                st.session_state.screener_selected = None
                st.rerun()
        page_title(f"⌨️  Analisi Dettagliata — {target}")
        show_bloomberg_insights(target)

    else:
        page_title("🔍  Stock Screener", "Filtra aziende per fondamentali e identifica opportunità di investimento")

        UNIVERSE = [
            "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","BRK-B","JPM","V",
            "UNH","XOM","JNJ","PG","MA","HD","ABBV","MRK","CVX","PEP","KO","AVGO",
            "COST","WMT","BAC","MCD","CSCO","ACN","LIN","TMO","DHR","NEE","AMD",
            "INTC","QCOM","TXN","AMAT","LRCX","ASML","TSM","NVO",
            "MC.PA","TTE.PA","SAN.PA","SAP.DE","BMW.DE","SIE.DE",
            "ENI.MI","ENEL.MI","UCG.MI","ISP.MI","STLAM.MI","RACE.MI","ATL.MI"
        ]

        st.markdown("#### Parametri di Filtro")
        col1, col2, col3 = st.columns(3)
        with col1:
            pe_max       = st.slider("P/E massimo",               0, 200, 50)
            pb_max       = st.slider("P/B massimo",               0, 30,  10)
            ps_max       = st.slider("P/S massimo",               0, 50,  15)
        with col2:
            cap_min      = st.slider("Market Cap min (B$)",       0, 500, 10)
            de_max       = st.slider("Debt/Equity massimo",       0, 10,   3)
            margin_min   = st.slider("Margine Operativo min (%)", -50, 60,  5)
        with col3:
            roic_min     = st.slider("ROIC min (%)",              -20, 60,  5)
            evebitda_max = st.slider("EV/EBITDA massimo",          0, 80,  25)
            sector_filter = st.selectbox("Settore", [
                "Tutti","Technology","Healthcare","Financials","Industrials",
                "Consumer Defensive","Consumer Cyclical","Energy",
                "Communication Services","Utilities","Real Estate","Basic Materials"
            ])

        product_filter = st.text_input(
            "Filtra per prodotto / servizio / business (lascia vuoto per ignorare)",
            "",
            placeholder="Es: cloud, semiconductor, oil, insurance, electric vehicle, pharma, streaming..."
        )

        custom_in = st.text_input("Aggiungi ticker custom all'universo (separati da virgola)", "")
        if custom_in.strip():
            extras = [x.strip().upper() for x in custom_in.split(",") if x.strip()]
            UNIVERSE = list(set(UNIVERSE + extras))

        run_screen = st.button("▶  Esegui Screening", use_container_width=True)

        if run_screen:
            results = []
            progress = st.progress(0)
            status = st.empty()

            for i, tkr in enumerate(UNIVERSE):
                progress.progress((i + 1) / len(UNIVERSE))
                status.markdown(
                    f"<span style='color:#A8BDD4; font-size:0.8rem;'>Analisi: {tkr} "
                    f"({i+1}/{len(UNIVERSE)})</span>", unsafe_allow_html=True)
                try:
                    info = get_ticker_info(tkr)
                    if not info:
                        continue

                    pe        = info.get('forwardPE') or info.get('trailingPE')
                    pb        = info.get('priceToBook')
                    ps        = info.get('priceToSalesTrailing12Months')
                    mcap      = info.get('marketCap')
                    de        = info.get('debtToEquity')
                    op_margin = info.get('operatingMargins')
                    roic      = info.get('returnOnEquity')
                    ev_ebitda = info.get('enterpriseToEbitda')
                    sector_v  = info.get('sector', '')
                    name      = info.get('shortName', tkr)
                    price     = (info.get('currentPrice') or info.get('regularMarketPrice')
                                 or info.get('previousClose'))

                    if sector_filter != "Tutti" and sector_v != sector_filter:
                        continue

                    if product_filter.strip():
                        keyword = product_filter.strip().lower()
                        business_text = (
                            (info.get('longBusinessSummary') or '') + ' ' +
                            (info.get('industry') or '') + ' ' +
                            (info.get('longName') or '') + ' ' +
                            (info.get('sector') or '')
                        ).lower()
                        if keyword not in business_text:
                            continue

                    if pe        is not None and pe              > pe_max:        continue
                    if pb        is not None and pb              > pb_max:        continue
                    if ps        is not None and ps              > ps_max:        continue
                    if de        is not None and de / 100        > de_max:        continue
                    if ev_ebitda is not None and ev_ebitda       > evebitda_max:  continue
                    if mcap      is not None and mcap / 1e9      < cap_min:       continue
                    if op_margin is not None and op_margin * 100 < margin_min:    continue
                    if roic      is not None and roic * 100      < roic_min:      continue

                    results.append({
                        "Ticker":      tkr,
                        "Nome":        name,
                        "Settore":     sector_v,
                        "Prezzo":      f"{price:.2f}"         if price     else "N/A",
                        "P/E":         f"{pe:.1f}"            if pe        else "N/A",
                        "P/B":         f"{pb:.1f}"            if pb        else "N/A",
                        "P/S":         f"{ps:.1f}"            if ps        else "N/A",
                        "EV/EBITDA":   f"{ev_ebitda:.1f}"     if ev_ebitda else "N/A",
                        "Op.Margin %": f"{op_margin*100:.1f}" if op_margin else "N/A",
                        "ROE %":       f"{roic*100:.1f}"      if roic      else "N/A",
                        "D/E (x)":     f"{de/100:.2f}"        if de        else "N/A",
                        "Cap (B$)":    f"{mcap/1e9:.1f}"      if mcap      else "N/A",
                    })
                except Exception:
                    continue

            progress.empty()
            status.empty()
            st.session_state.screener_results = results if results else []

        if st.session_state.screener_results:
            results = st.session_state.screener_results
            st.success(f"✅  {len(results)} aziende trovate che rispettano i filtri")
            st.markdown("---")
            st.markdown("#### Risultati")
            st.dataframe(pd.DataFrame(results).set_index("Ticker"), use_container_width=True)

            st.markdown("#### Analizza un'azienda in dettaglio")
            ticker_options = [f"{r['Ticker']} — {r['Nome']}" for r in results]
            selected_option = st.selectbox("Seleziona azienda", ticker_options, key="screener_select_box")

            if st.button("🔎  Apri Analisi Dettagliata", use_container_width=True):
                selected_ticker = selected_option.split(" — ")[0].strip()
                st.session_state.screener_selected = selected_ticker
                st.rerun()

        elif st.session_state.screener_results is not None and len(st.session_state.screener_results) == 0:
            st.warning("Nessuna azienda trovata con i filtri selezionati. Prova ad allargare i parametri.")


# =========================================================
# 6. BLOOMBERG INSIGHTS
# =========================================================
elif choice == "Bloomberg Insights":
    page_title("⌨️  Company Terminal Insights", "Analisi fondamentale, notizie, supply chain e peer comparison")

    target = st.text_input("Ticker principale", "NVDA",
                           placeholder="Es: AAPL, MSFT, MC.PA, ENI.MI ...").strip().upper()
    if target:
        show_bloomberg_insights(target)

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
    [data-baseweb="popover"], [data-baseweb="menu"] {
        background-color: #0D1F38 !important;
        border: 1px solid #1E3A5F !important;
    }
    [data-baseweb="option"] {
        background-color: #0D1F38 !important;
        color: #FFFFFF !important;
    }
    [data-baseweb="option"]:hover { background-color: #1E3A5F !important; }
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
    .stButton > button:hover {
        background-color: #4A9EFF !important;
        color: #000 !important;
    }
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
# UTILITY & CACHING
# =========================================================
def page_title(text, subtitle=""):
    sub_html = (f'<p style="color:#A8BDD4; font-size:0.88rem; margin-top:-1rem; '
                f'margin-bottom:1.5rem;">{subtitle}</p>') if subtitle else ""
    st.markdown(f"<div class='page-title'>{text}</div>{sub_html}", unsafe_allow_html=True)


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
)


@st.cache_data(ttl=300, show_spinner=False)
def get_ticker_info(ticker):
    try:
        return yf.Ticker(ticker).info
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
def download_data(tickers, start=None, period=None):
    try:
        if period:
            return yf.download(tickers, period=period, auto_adjust=True, progress=False)
        return yf.download(tickers, start=start, auto_adjust=True, progress=False)
    except Exception:
        return pd.DataFrame()


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
    """Mostra l'analisi completa di un ticker. Usata sia dalla schermata 6 che dallo Screener."""
    with st.spinner(f"Recupero dati per {target}..."):
        try:
            inf = get_ticker_info(target)

            company_name = inf.get('longName') or inf.get('shortName') or inf.get('symbol')
            current_price = (inf.get('currentPrice') or inf.get('regularMarketPrice')
                             or inf.get('previousClose'))

            if not company_name and not current_price:
                raise ValueError("Ticker non trovato.")

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
                st.markdown(
                    f"""
                    <div style='background:#0D1F38; border:1px solid #1E3A5F; border-radius:6px;
                                padding:1rem; margin-bottom:0.8rem;'>
                        <div style='font-family: IBM Plex Mono, monospace; font-size:0.7rem;
                                    color:#4A9EFF; letter-spacing:0.15em; margin-bottom:6px;'>
                            FONTE ESTERNA
                        </div>
                        <div style='font-size:0.88rem; color:#E8EDF5; margin-bottom:10px;'>
                            Le notizie in tempo reale su <b>{target}</b> sono disponibili
                            direttamente su Yahoo Finance.
                        </div>
                        <a href='{yahoo_url}' target='_blank'
                           style='display:inline-block; background:#1E3A5F; color:#FFFFFF;
                                  border:1px solid #4A9EFF; border-radius:4px;
                                  padding:6px 14px; font-family: IBM Plex Mono, monospace;
                                  font-size:0.78rem; letter-spacing:0.06em;
                                  text-decoration:none;'>
                            📰 Apri News su Yahoo Finance →
                        </a>
                    </div>
                    <div style='font-family: IBM Plex Mono, monospace; font-size:0.7rem;
                                color:#A8BDD4; margin-top:0.5rem;'>
                        Link diretto alla sezione news di {target}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # Prova comunque a caricare titoli da yfinance come fallback
                try:
                    news_items = get_ticker_news(target)
                    if news_items:
                        st.markdown("**Titoli recenti (yfinance):**")
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
                peer_raw = download_data(peer_tickers, period="1y")
                if isinstance(peer_raw.columns, pd.MultiIndex):
                    peer_data = peer_raw['Close']
                else:
                    peer_data = peer_raw

                peer_norm = ((peer_data / peer_data.iloc[0]) - 1) * 100
                peer_colors = ['#4A9EFF', '#2ECC71', '#F39C12', '#E74C3C', '#9B59B6', '#1ABC9C']

                fig_peer = go.Figure()
                peer_cols = peer_norm.columns if hasattr(peer_norm, 'columns') else [target]
                for idx, col in enumerate(peer_cols):
                    fig_peer.add_trace(go.Scatter(
                        x=peer_norm.index, y=peer_norm[col], name=col,
                        line=dict(width=2.5 if col == target else 1.5,
                                  color=peer_colors[idx % len(peer_colors)])
                    ))
                fig_peer.add_hline(y=0, line_dash="dot", line_color="#2E4A6E", line_width=1)
                fig_peer.update_layout(**PLOTLY_LAYOUT, yaxis_title="Rendimento % (norm.)",
                                       height=380, title=f"Performance relativa: {target} vs peers (1 anno)")
                st.plotly_chart(fig_peer, use_container_width=True)
            except Exception:
                st.info("Grafico peers non disponibile.")

        except ValueError:
            st.error(f"❌  Ticker **{target}** non trovato. Verifica il simbolo.")
            st.markdown("""
                **Esempi di formato corretto:**
                - USA: `AAPL`, `MSFT`, `NVDA`
                - Italia: `ENI.MI`, `ENEL.MI`
                - Francia: `MC.PA`, `TTE.PA`
                - Germania: `SAP.DE`, `BMW.DE`
                - ETF: `VWCE.DE`, `SWDA.MI`
            """)
        except Exception as e:
            st.error(f"❌  Errore nel recupero dati per **{target}**: {str(e)}")


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
        years = st.slider("Anni di Proiezione", min_value=3, max_value=15, value=10)
        shares = st.number_input("Azioni in Circolazione", value=1_000_000_000, step=10_000_000, format="%d")

    g = growth / 100
    w = wacc / 100
    tg = terminal_growth / 100

    cash_flows, pv_flows = [], []
    for yr in range(1, years + 1):
        cf = fcf * ((1 + g) ** yr)
        pv = cf / ((1 + w) ** yr)
        cash_flows.append(cf)
        pv_flows.append(pv)

    terminal_value = (cash_flows[-1] * (1 + tg)) / (w - tg) if w > tg else 0
    pv_terminal = terminal_value / ((1 + w) ** years)
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
    fig.add_trace(go.Bar(x=[f"Anno {i+1}" for i in range(years)],
                         y=[v/1e6 for v in cash_flows], name="FCF Proiettato",
                         marker_color='#4A9EFF', opacity=0.8))
    fig.add_trace(go.Bar(x=[f"Anno {i+1}" for i in range(years)],
                         y=[v/1e6 for v in pv_flows], name="PV dei Cash Flows",
                         marker_color='#2ECC71', opacity=0.8))
    fig.update_layout(**PLOTLY_LAYOUT, yaxis_title="$ Milioni", barmode='group',
                      title="Cash Flow Proiettato vs Present Value")
    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# 3. MULTI-COMPARE
# =========================================================
elif choice == "Multi-Compare":
    page_title("📊  Multi-Asset Comparison", "Confronto del rendimento percentuale normalizzato tra più ticker")

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        tk_in = st.text_input("Ticker (separati da virgola)", "AAPL, MSFT, TSLA, NVDA")
    with col2:
        horizon = st.selectbox("Orizzonte", ["Mesi", "Anni"])
    with col3:
        val = st.slider("Durata", min_value=1, max_value=24 if horizon == "Mesi" else 10, value=12)

    tk_list = [x.strip().upper() for x in tk_in.split(",") if x.strip()]
    start = datetime.now() - timedelta(days=val * 30 if horizon == "Mesi" else val * 365)

    if tk_list:
        with st.spinner("Download dati..."):
            try:
                raw = download_data(tk_list, start=start)
                if isinstance(raw.columns, pd.MultiIndex):
                    data = raw['Close']
                else:
                    data = raw[['Close']] if 'Close' in raw.columns else raw

                data = data.dropna(how='all')
                rets = ((data / data.iloc[0]) - 1) * 100

                colors = ['#4A9EFF', '#2ECC71', '#F39C12', '#E74C3C', '#9B59B6',
                          '#1ABC9C', '#E67E22', '#3498DB', '#EC407A', '#AB47BC']

                fig = go.Figure()
                if isinstance(rets, pd.Series):
                    fig.add_trace(go.Scatter(x=rets.index, y=rets.values, name=tk_list[0],
                                             line=dict(width=2, color=colors[0])))
                else:
                    for idx, col in enumerate(rets.columns):
                        fig.add_trace(go.Scatter(x=rets.index, y=rets[col], name=col,
                                                 line=dict(width=2, color=colors[idx % len(colors)])))

                fig.add_hline(y=0, line_dash="dot", line_color="#2E4A6E", line_width=1)
                fig.update_layout(**PLOTLY_LAYOUT, title="Rendimento % Normalizzato",
                                  yaxis_title="Rendimento (%)", xaxis_title="")
                st.plotly_chart(fig, use_container_width=True)

                if not isinstance(rets, pd.Series):
                    st.markdown("#### Riepilogo Rendimenti")
                    summary = pd.DataFrame({
                        "Rendimento Totale (%)": rets.iloc[-1].round(2),
                        "Max (%)": rets.max().round(2),
                        "Min (%)": rets.min().round(2),
                    })
                    st.dataframe(summary, use_container_width=True)
            except Exception as e:
                st.error(f"Errore nel download dei dati: {e}")


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
    with col4:
        years = st.slider("Orizzonte temporale (anni)", min_value=1, max_value=20, value=5)

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
        start = datetime.now() - timedelta(days=365 * years)
        tickers_to_dl = valid_assets + ([bench] if bench else [bench_eq.upper(), bench_bond.upper()])

        with st.spinner("Download dati storici..."):
            try:
                raw = download_data(tickers_to_dl, start=start)
                if isinstance(raw.columns, pd.MultiIndex):
                    data = raw['Close']
                else:
                    data = raw

                data = data.dropna(how='all').ffill()
                norm = (data / data.iloc[0]) - 1

                strat_df = pd.DataFrame(index=norm.index)
                for i, a in enumerate(valid_assets):
                    if a in norm.columns:
                        strat_df[a] = norm[a] * w_norm[i]
                strategy = strat_df.sum(axis=1)

                if bench is None:
                    bench_series = norm[bench_eq.upper()] * 0.6 + norm[bench_bond.upper()] * 0.4
                    bench_name = f"60% {bench_eq.upper()} + 40% {bench_bond.upper()}"
                    bench_col = None
                else:
                    bench_col = bench
                    bench_name = bench_label

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=strategy.index, y=strategy * 100,
                                         name="📐 La Tua Strategia",
                                         line=dict(width=3, color="#4A9EFF"),
                                         fill='tozeroy', fillcolor='rgba(74,158,255,0.07)'))

                if bench_col and bench_col in norm.columns:
                    fig.add_trace(go.Scatter(x=norm.index, y=norm[bench_col] * 100,
                                             name=f"📌 {bench_name}",
                                             line=dict(width=2, dash='dash', color='#FFFFFF')))
                elif bench is None:
                    fig.add_trace(go.Scatter(x=bench_series.index, y=bench_series * 100,
                                             name=f"📌 {bench_name}",
                                             line=dict(width=2, dash='dash', color='#FFFFFF')))

                asset_colors = ['#2ECC71', '#F39C12', '#E74C3C', '#9B59B6',
                                '#1ABC9C', '#E67E22', '#EC407A', '#AB47BC']
                for idx, a in enumerate(valid_assets):
                    if a in norm.columns:
                        fig.add_trace(go.Scatter(x=norm.index, y=norm[a] * 100,
                                                 name=f"  {a} ({weight_list[idx]}%)",
                                                 line=dict(width=1.2, color=asset_colors[idx % len(asset_colors)]),
                                                 opacity=0.5))

                fig.add_hline(y=0, line_dash="dot", line_color="#2E4A6E", line_width=1)
                fig.update_layout(**PLOTLY_LAYOUT, title="Rendimento Cumulativo (%)",
                                  yaxis_title="Rendimento (%)", height=480)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("#### Statistiche di Performance")
                s1, s2, s3, s4 = st.columns(4)
                total_ret = strategy.iloc[-1] * 100
                annual_ret = ((1 + strategy.iloc[-1]) ** (1 / years) - 1) * 100
                daily_rets = strategy.diff().dropna()
                vol = daily_rets.std() * (252 ** 0.5) * 100
                sharpe = (annual_ret / vol) if vol > 0 else 0
                drawdown = ((strategy + 1) / (strategy + 1).cummax() - 1).min() * 100

                s1.metric("Rendimento Totale", f"{total_ret:+.2f}%")
                s2.metric("CAGR (annualizzato)", f"{annual_ret:+.2f}%")
                s3.metric("Volatilità Annua", f"{vol:.2f}%")
                s4.metric("Max Drawdown", f"{drawdown:.2f}%")
                st.metric("Sharpe Ratio (approx)", f"{sharpe:.2f}")

                if bench_col and bench_col in norm.columns:
                    bench_total = norm[bench_col].iloc[-1] * 100
                    delta_vs_bench = total_ret - bench_total
                    st.metric(f"Alpha vs {bench_name}", f"{delta_vs_bench:+.2f}%",
                              delta="Sovraperforma" if delta_vs_bench > 0 else "Sottoperforma")

            except Exception as e:
                st.error(f"Errore durante il backtest: {e}")

    elif run and total_weight != 100:
        st.error("Correggi i pesi prima di eseguire il backtest (devono sommare a 100%).")


# =========================================================
# 5. STOCK SCREENER
# =========================================================
elif choice == "Stock Screener":

    # Se è stata selezionata un'azienda dallo screener, mostra l'analisi dettagliata
    if st.session_state.screener_selected:
        target = st.session_state.screener_selected
        col_back, col_title = st.columns([1, 6])
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
            pe_max      = st.slider("P/E massimo",               0, 200, 50)
            pb_max      = st.slider("P/B massimo",               0, 30,  10)
            ps_max      = st.slider("P/S massimo",               0, 50,  15)
        with col2:
            cap_min     = st.slider("Market Cap min (B$)",       0, 500, 10)
            de_max      = st.slider("Debt/Equity massimo",       0, 10,   3)
            margin_min  = st.slider("Margine Operativo min (%)", -50, 60,  5)
        with col3:
            roic_min    = st.slider("ROIC min (%)",              -20, 60,  5)
            evebitda_max= st.slider("EV/EBITDA massimo",          0, 80,  25)
            sector_filter = st.selectbox("Settore", [
                "Tutti","Technology","Healthcare","Financials","Industrials",
                "Consumer Defensive","Consumer Cyclical","Energy",
                "Communication Services","Utilities","Real Estate","Basic Materials"
            ])

        custom_in = st.text_input("Aggiungi ticker custom all'universo (separati da virgola)", "")
        if custom_in.strip():
            extras = [x.strip().upper() for x in custom_in.split(",") if x.strip()]
            UNIVERSE = list(set(UNIVERSE + extras))

        run_screen = st.button("▶  Esegui Screening", use_container_width=True)

        if run_screen:
            results = []
            progress = st.progress(0)
            status   = st.empty()

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
                    de        = info.get('debtToEquity')      # yfinance dà già in % (es. 150 = 1.5x)
                    op_margin = info.get('operatingMargins')  # decimale (es. 0.25 = 25%)
                    roic      = info.get('returnOnEquity')    # proxy ROIC, decimale
                    ev_ebitda = info.get('enterpriseToEbitda')
                    sector_v  = info.get('sector', '')
                    name      = info.get('shortName', tkr)
                    price     = (info.get('currentPrice') or info.get('regularMarketPrice')
                                 or info.get('previousClose'))

                    # Filtro settore
                    if sector_filter != "Tutti" and sector_v != sector_filter:
                        continue

                    # Filtri numerici
                    if pe        is not None and pe          > pe_max:              continue
                    if pb        is not None and pb          > pb_max:              continue
                    if ps        is not None and ps          > ps_max:              continue
                    if de        is not None and de / 100    > de_max:              continue
                    if ev_ebitda is not None and ev_ebitda   > evebitda_max:        continue
                    if mcap      is not None and mcap / 1e9  < cap_min:             continue
                    if op_margin is not None and op_margin * 100 < margin_min:      continue
                    if roic      is not None and roic * 100  < roic_min:            continue

                    results.append({
                        "Ticker":       tkr,
                        "Nome":         name,
                        "Settore":      sector_v,
                        "Prezzo":       f"{price:.2f}"        if price     else "N/A",
                        "P/E":          f"{pe:.1f}"           if pe        else "N/A",
                        "P/B":          f"{pb:.1f}"           if pb        else "N/A",
                        "P/S":          f"{ps:.1f}"           if ps        else "N/A",
                        "EV/EBITDA":    f"{ev_ebitda:.1f}"    if ev_ebitda else "N/A",
                        "Op.Margin %":  f"{op_margin*100:.1f}"if op_margin else "N/A",
                        "ROE %":        f"{roic*100:.1f}"     if roic      else "N/A",
                        "D/E (x)":      f"{de/100:.2f}"       if de        else "N/A",
                        "Cap (B$)":     f"{mcap/1e9:.1f}"     if mcap      else "N/A",
                    })
                except Exception:
                    continue

            progress.empty()
            status.empty()

            if results:
                st.session_state.screener_results = results
            
        # Mostra risultati (persistono tra run senza re-eseguire)
        if st.session_state.screener_results:
            results = st.session_state.screener_results
            st.success(f"✅  {len(results)} aziende trovate che rispettano i filtri")
            st.markdown("---")
            st.markdown("#### Risultati — clicca su un'azienda per analizzarla")

            df_results = pd.DataFrame(results)
            st.dataframe(df_results.set_index("Ticker"), use_container_width=True)

            st.markdown("#### Analizza un'azienda dal risultato")
            ticker_options = [f"{r['Ticker']} — {r['Nome']}" for r in results]
            selected_option = st.selectbox("Seleziona azienda", ticker_options, key="screener_select_box")

            if st.button("🔎  Apri Analisi Dettagliata", use_container_width=True):
                selected_ticker = selected_option.split(" — ")[0].strip()
                st.session_state.screener_selected = selected_ticker
                st.rerun()

        elif run_screen:
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

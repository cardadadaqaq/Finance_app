"""
╔══════════════════════════════════════════════════════════════════╗
║   NAVY TERMINAL PRO  v6.0  ·  Data Engine                        ║
║   Unified Market Data · Finviz Screener · FRED · yFinance        ║
╚══════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import warnings
import time
import concurrent.futures
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════
#  FRED SERIES CATALOGUE
# ══════════════════════════════════════════════════════════
FRED_SERIES: dict[str, str] = {
    "Fed Funds Rate":          "FEDFUNDS",
    "10Y Treasury Yield":      "DGS10",
    "2Y Treasury Yield":       "DGS2",
    "3M Treasury Yield":       "DGS3MO",
    "30Y Treasury Yield":      "DGS30",
    "10Y-2Y Spread":           "T10Y2Y",
    "CPI (All Urban)":         "CPIAUCSL",
    "Core CPI":                "CPILFESL",
    "PCE Price Index":         "PCEPI",
    "Unemployment Rate":       "UNRATE",
    "Non-Farm Payrolls":       "PAYEMS",
    "Initial Claims":          "ICSA",
    "Real GDP QoQ":            "A191RL1Q225SBEA",
    "Industrial Production":   "INDPRO",
    "Retail Sales":            "RSAFS",
    "HY Spread":               "BAMLH0A0HYM2",
    "IG Spread":               "BAMLC0A0CM",
    "TED Spread":              "TEDRATE",
    "VIX (FRED)":              "VIXCLS",
}

# ══════════════════════════════════════════════════════════
#  SCREENER TICKER UNIVERSE  (~1,500 global names)
# ══════════════════════════════════════════════════════════
SCREENER_UNIVERSE_FULL: list[str] = list(dict.fromkeys([
    # ── US Mega/Large Cap ─────────────────────────────────
    "AAPL","MSFT","NVDA","GOOGL","GOOG","AMZN","META","TSLA","AVGO","JPM",
    "V","UNH","XOM","JNJ","PG","MA","HD","ABBV","MRK","CVX","PEP","KO","LIN",
    "TMO","DHR","AMD","INTC","QCOM","TXN","AMAT","LRCX","MU","ORCL","IBM",
    "CSCO","DELL","ACN","NOW","CRM","ADBE","PANW","FTNT","CRWD","ZS","SNPS",
    "CDNS","INTU","NFLX","SPOT","UBER","ABNB","BKNG","SNOW","PLTR","COIN",
    "ARM","SMCI","MRVL","KLAC","MPWR","DDOG","MDB","NET","HUBS","TTD","ROKU",
    "BAC","WFC","GS","MS","BLK","SCHW","C","AXP","COF","BX","KKR","APO",
    "LLY","PFE","BMY","AMGN","GILD","REGN","VRTX","BIIB","MRNA","NVAX",
    "COST","WMT","TGT","DG","NKE","LULU","MCD","SBUX","CMG","DPZ","YUM",
    "GE","HON","MMM","EMR","ETN","PH","ROK","BA","RTX","LMT","NOC","GD","CAT",
    "DE","UPS","FDX","COP","EOG","OXY","SLB","HAL","BKR","LNG",
    "NEE","CEG","DUK","SO","AEP","XEL","NRG","VST","TLN","SMR",
    "AMT","PLD","EQIX","CCI","SPG","O","WELL","DLR","VICI","IRM",
    "NEM","GOLD","FCX","ALB","SQM","DD","DOW","LYB","NUE","STLD","APD","SHW",
    "DIS","CMCSA","WBD","EA","TTWO","DKNG","MGM","WYNN","LVS",
    "ENPH","FSLR","RUN","SEDG","PLUG","BE","CHPT",
    "ABNB","DASH","LYFT","GRAB","SE","MELI","NU",
    # ── US Mid/Small Cap ─────────────────────────────────
    "OKTA","BILL","DOCN","GTLB","MNDY","TOST","IOT","S","SAMSF",
    "CELH","HIMS","ROIV","RXRX","ACMR","AXON","HOOD","SOFI","AFRM",
    "RIVN","LCID","FSR","GOEV","NKLA","HYLN",
    "VRT","NVENT","EMCOR","FWRD","MODG","JCI","CARR",
    "OKE","KMI","WMB","EPD","ET","MMP","PAA",
    "MTCH","BMBL","PINS","SNAP","RDDT","DUOL",
    "ZM","DBX","BOX","TWLO","FROG","ESTC","SUMO",
    "NFLX","ROKU","FUBO","SIRI",
    "BLDR","PHM","DHI","LEN","TOL","MDC","CCS",
    # ── European Large Cap ────────────────────────────────
    "ASML.AS","ADYEN.AS","HEIA.AS","PHIA.AS","UNA.AS","NN.AS","IMCD.AS",
    "SAP.DE","BAYN.DE","BMW.DE","MBG.DE","ALV.DE","SIE.DE","IFX.DE",
    "DB1.DE","MUV2.DE","VOW3.DE","RWE.DE","EOAN.DE","BAS.DE","HEN3.DE",
    "MC.PA","TTE.PA","SAN.PA","BNP.PA","AXA.PA","OR.PA","AIR.PA","SU.PA",
    "RI.PA","DSY.PA","CAP.PA","SGO.PA","VIE.PA","STM.PA","DG.PA",
    "HSBA.L","BP.L","SHEL.L","AZN.L","GSK.L","ULVR.L","RIO.L","BARC.L",
    "LLOY.L","VOD.L","BT-A.L","CNA.L","EXPN.L","JD.L","PRU.L","STJ.L",
    "NESN.SW","ROG.SW","NOVN.SW","ABB.SW","UBS.SW","CFR.SW","ZURN.SW","LONN.SW",
    # ── Italian Stocks ────────────────────────────────────
    "ENI.MI","ENEL.MI","UCG.MI","ISP.MI","STLAM.MI","RACE.MI","ATL.MI",
    "G.MI","MB.MI","PRY.MI","TIT.MI","BMED.MI","FBK.MI","A2A.MI",
    "TEN.MI","CPR.MI","PIRC.MI","SRG.MI","AZM.MI","BGN.MI",
    # ── Spanish / Nordic / Other EU ──────────────────────
    "ITX.MC","SAN.MC","BBVA.MC","REP.MC","TEF.MC","IBE.MC","ELE.MC",
    "EQNR.OL","YAR.OL","DNO.OL","AKRBP.OL",
    "NOVO-B.CO","DSV.CO","MAERSK-B.CO","NZYM-B.CO",
    "ERIC-B.ST","VOLV-B.ST","ATCO-A.ST","SEB-A.ST","SHB-A.ST",
    # ── Asian / Global ───────────────────────────────────
    "SONY","TM","HMC","MUFG","SMFG","MFG","7203.T","6758.T","6861.T",
    "TSM","2330.TW","005930.KS","000660.KS","BABA","JD","PDD","BIDU","NIO","LI","XPEV",
    "INFY","WIT","HDB","ICICIBC.BO","RELIANCE.BO",
    "SHOP","RY","TD","BNS","ENB","CNQ","SU","CP","CNR","MFC","SLF",
    "BHP","RIO","CBA.AX","ANZ.AX","WBC.AX","NAB.AX","CSL.AX","FMG.AX",
    # ── Crypto / ETFs ────────────────────────────────────
    "BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD","ADA-USD",
    "GLD","SLV","GDX","GDXJ","IAU","PPLT",
    "SPY","QQQ","IWM","DIA","VTI","VOO","VWCE.DE","IWDA.AS",
    "TLT","AGG","LQD","HYG","BND","SHY","IEF",
    "XLE","XLF","XLV","XLK","XLI","XLU","XLRE","XLB","XLP","XLY",
    "EEM","EFA","VGK","FXI","MCHI","EWJ","EWG","EWU","EWP","EWI",
    "DBA","DBC","USO","UNG","PDBC","CPER",
    "ARKK","ARKG","ARKW","ARKF","ARKQ",
]))

# ══════════════════════════════════════════════════════════
#  FINVIZ COLUMN NORMALISER
# ══════════════════════════════════════════════════════════
_FINVIZ_RENAME: dict[str, str] = {
    "No.":           "_row",
    "Ticker":        "Ticker",
    "Company":       "Name",
    "Sector":        "Sector",
    "Industry":      "Industry",
    "Country":       "Country",
    "Market Cap":    "MarketCap_raw",
    "P/E":           "PE_raw",
    "Price":         "Price_raw",
    "Change":        "Change_raw",
    "Volume":        "Volume_raw",
}

def _parse_finviz_market_cap(s: str) -> float:
    """Convert Finviz market-cap strings like '2.31T', '450.12B', '12.5M' → float USD."""
    if not isinstance(s, str) or s.strip() in ("-", "", "N/A"):
        return float("nan")
    s = s.strip()
    multipliers = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}
    suffix = s[-1].upper()
    try:
        if suffix in multipliers:
            return float(s[:-1]) * multipliers[suffix]
        return float(s)
    except ValueError:
        return float("nan")


def _parse_finviz_pct(s: str) -> float:
    """Convert '3.52%', '-1.20%' → float."""
    if not isinstance(s, str) or s.strip() in ("-", "", "N/A"):
        return float("nan")
    try:
        return float(s.strip().replace("%", ""))
    except ValueError:
        return float("nan")


def _parse_finviz_price(s: str) -> float:
    if not isinstance(s, str) or s.strip() in ("-", "", "N/A"):
        return float("nan")
    try:
        return float(s.strip().replace(",", ""))
    except ValueError:
        return float("nan")


def _parse_finviz_pe(s: str) -> float:
    if not isinstance(s, str) or s.strip() in ("-", "", "N/A"):
        return float("nan")
    try:
        return float(s.strip())
    except ValueError:
        return float("nan")


def _parse_finviz_volume(s) -> float:
    if isinstance(s, (int, float)):
        return float(s)
    if not isinstance(s, str) or s.strip() in ("-", "", "N/A"):
        return float("nan")
    try:
        return float(s.strip().replace(",", ""))
    except ValueError:
        return float("nan")


# ══════════════════════════════════════════════════════════
#  EMPTY SCREENER SCHEMA  (used on catastrophic failure)
# ══════════════════════════════════════════════════════════
_SCREENER_EMPTY_COLS = [
    "Ticker", "Name", "Sector", "Industry", "Country",
    "MarketCap_B", "PE", "Price", "Change_Pct", "Volume",
    "Source",
]

def _empty_screener_df() -> pd.DataFrame:
    return pd.DataFrame(columns=_SCREENER_EMPTY_COLS)


# ══════════════════════════════════════════════════════════
#  PRIMARY ENGINE: FINVIZ SCRAPER
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=600, show_spinner=False)
def fetch_finviz_screener_data() -> pd.DataFrame:
    """
    Pull the full Finviz screener table via finvizfinance.
    Returns a clean, normalised DataFrame with typed numeric columns.
    Caches for 10 minutes.  On ANY failure returns _empty_screener_df().
    """
    try:
        from finvizfinance.screener.overview import Overview  # lazy import

        foverview = Overview()
        raw: pd.DataFrame = foverview.screener_view()

        if raw is None or raw.empty:
            return _empty_screener_df()

        # ── Rename columns we care about ──────────────────
        rename_map: dict[str, str] = {}
        for col in raw.columns:
            if col in _FINVIZ_RENAME:
                rename_map[col] = _FINVIZ_RENAME[col]
        raw = raw.rename(columns=rename_map)

        # ── Guarantee required columns exist ──────────────
        required = ["Ticker", "Name", "Sector", "Industry", "Country",
                    "MarketCap_raw", "PE_raw", "Price_raw", "Change_raw", "Volume_raw"]
        for col in required:
            if col not in raw.columns:
                raw[col] = None

        # ── Parse numeric columns ─────────────────────────
        raw["MarketCap_B"]  = raw["MarketCap_raw"].apply(_parse_finviz_market_cap) / 1e9
        raw["PE"]           = raw["PE_raw"].apply(_parse_finviz_pe)
        raw["Price"]        = raw["Price_raw"].apply(_parse_finviz_price)
        raw["Change_Pct"]   = raw["Change_raw"].apply(_parse_finviz_pct)
        raw["Volume"]       = raw["Volume_raw"].apply(_parse_finviz_volume)

        # ── Fill string columns ───────────────────────────
        for col in ["Ticker", "Name", "Sector", "Industry", "Country"]:
            raw[col] = raw[col].fillna("N/A").astype(str)

        raw["Source"] = "Finviz"

        # ── Return only the clean columns ─────────────────
        out = raw[_SCREENER_EMPTY_COLS].copy()
        out = out[out["Ticker"].str.strip().ne("") & out["Ticker"].ne("N/A")]
        out = out.reset_index(drop=True)
        return out

    except Exception:
        return _empty_screener_df()


# ══════════════════════════════════════════════════════════
#  BACKUP ENGINE: MULTI-THREADED BATCH YFINANCE
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=600, show_spinner=False)
def fetch_backup_yfinance_screener(
    universe: tuple[str, ...] | None = None,
    chunk_size: int = 100,
) -> pd.DataFrame:
    """
    Batch-download price data for the curated universe using yf.download()
    with multi-threading.  Price, Change%, Volume are computed vectorially.
    Metadata (Sector, Industry, Country, MarketCap, PE) is fetched in parallel
    via a ThreadPoolExecutor — one yf.Ticker.info call per stock, capped to
    avoid hammering Yahoo.  On any failure returns _empty_screener_df().
    """
    if universe is None:
        # Strip crypto/ETF-heavy prefixes that have no PE/sector metadata
        universe = tuple(SCREENER_UNIVERSE_FULL)

    try:
        # ── 1. Batch price download (vectorised) ──────────
        tickers_str = " ".join(universe)
        raw_px = yf.download(
            tickers=tickers_str,
            period="5d",
            interval="1d",
            threads=True,
            progress=False,
            auto_adjust=True,
        )

        if raw_px.empty:
            return _empty_screener_df()

        # Handle both MultiIndex and flat Index (single ticker edge case)
        if isinstance(raw_px.columns, pd.MultiIndex):
            close_df  = raw_px["Close"]   if "Close"  in raw_px.columns.get_level_values(0) else pd.DataFrame()
            volume_df = raw_px["Volume"]  if "Volume" in raw_px.columns.get_level_values(0) else pd.DataFrame()
        else:
            # Single-ticker flat case — wrap into DataFrame with ticker as column
            single = list(universe)[0]
            close_df  = raw_px[["Close"]].rename(columns={"Close": single})
            volume_df = raw_px[["Volume"]].rename(columns={"Volume": single})

        if close_df.empty:
            return _empty_screener_df()

        close_df  = close_df.dropna(how="all").ffill()
        volume_df = volume_df.dropna(how="all").ffill()

        if len(close_df) < 2:
            return _empty_screener_df()

        last_close  = close_df.iloc[-1]
        prev_close  = close_df.iloc[-2]
        last_volume = volume_df.iloc[-1] if not volume_df.empty else pd.Series(dtype=float)

        change_pct = ((last_close - prev_close) / prev_close.replace(0, float("nan"))) * 100

        # ── 2. Parallel metadata fetch ────────────────────
        valid_tickers = [t for t in last_close.index if pd.notna(last_close[t])]

        def _fetch_meta(tkr: str) -> dict:
            """Fetch a single ticker's metadata; return empty dict on failure."""
            try:
                info = yf.Ticker(tkr).info
                if not info:
                    return {"Ticker": tkr}
                return {
                    "Ticker":     tkr,
                    "Name":       (info.get("longName") or info.get("shortName") or tkr)[:40],
                    "Sector":     info.get("sector",   "N/A"),
                    "Industry":   info.get("industry", "N/A"),
                    "Country":    info.get("country",  "N/A"),
                    "MarketCap_B": (info.get("marketCap") or 0) / 1e9,
                    "PE":          info.get("forwardPE") or info.get("trailingPE") or float("nan"),
                }
            except Exception:
                return {"Ticker": tkr}

        meta_rows: list[dict] = []
        # Use at most 40 workers; don't flood Yahoo Finance
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as pool:
            futures = {pool.submit(_fetch_meta, t): t for t in valid_tickers}
            for fut in concurrent.futures.as_completed(futures):
                try:
                    meta_rows.append(fut.result(timeout=8))
                except Exception:
                    meta_rows.append({"Ticker": futures[fut]})

        meta_df = pd.DataFrame(meta_rows)
        if meta_df.empty or "Ticker" not in meta_df.columns:
            meta_df = pd.DataFrame({"Ticker": valid_tickers})

        # ── 3. Assemble final DataFrame ───────────────────
        price_records = []
        for tkr in valid_tickers:
            price_records.append({
                "Ticker":     tkr,
                "Price":      round(float(last_close[tkr]), 4) if pd.notna(last_close[tkr]) else float("nan"),
                "Change_Pct": round(float(change_pct[tkr]), 2)  if pd.notna(change_pct.get(tkr, float("nan"))) else float("nan"),
                "Volume":     float(last_volume[tkr]) if tkr in last_volume.index and pd.notna(last_volume[tkr]) else float("nan"),
            })

        price_df = pd.DataFrame(price_records)

        # Merge price + meta
        merged = price_df.merge(meta_df, on="Ticker", how="left")

        # Fill missing string columns
        for col in ["Name", "Sector", "Industry", "Country"]:
            if col not in merged.columns:
                merged[col] = "N/A"
            merged[col] = merged[col].fillna("N/A").astype(str)

        for col in ["MarketCap_B", "PE"]:
            if col not in merged.columns:
                merged[col] = float("nan")

        merged["Source"] = "yFinance"

        out = merged[_SCREENER_EMPTY_COLS].copy().reset_index(drop=True)
        return out

    except Exception:
        return _empty_screener_df()


# ══════════════════════════════════════════════════════════
#  UNIFIED SCREENER ENTRY POINT
# ══════════════════════════════════════════════════════════
def load_screener_master_data(
    force_fallback: bool = False,
) -> tuple[pd.DataFrame, str]:
    """
    Attempt Finviz first; fall back to yFinance batch on any failure.
    Returns (DataFrame, source_label).
    """
    if not force_fallback:
        df = fetch_finviz_screener_data()
        if not df.empty:
            return df, "Finviz"

    df = fetch_backup_yfinance_screener(universe=tuple(SCREENER_UNIVERSE_FULL))
    if not df.empty:
        return df, "yFinance Batch"

    return _empty_screener_df(), "None (Network Error)"


# ══════════════════════════════════════════════════════════
#  SCREENER FILTER ENGINE  (pure pandas — no web requests)
# ══════════════════════════════════════════════════════════
def apply_screener_filters(
    df: pd.DataFrame,
    sector: str = "All",
    country: str = "All",
    min_marketcap_b: float = 0.0,
    max_marketcap_b: float = 100_000.0,
    max_pe: float = 500.0,
    min_pe: float = 0.0,
    min_change_pct: float = -100.0,
    max_change_pct: float = 100.0,
    keyword: str = "",
) -> pd.DataFrame:
    """Apply all screener filter criteria to the master DataFrame locally."""
    out = df.copy()

    if sector != "All":
        out = out[out["Sector"].str.strip() == sector]

    if country != "All":
        out = out[out["Country"].str.strip() == country]

    mc = pd.to_numeric(out["MarketCap_B"], errors="coerce")
    out = out[(mc >= min_marketcap_b) | mc.isna()]
    out = out[(mc <= max_marketcap_b) | mc.isna()]

    pe = pd.to_numeric(out["PE"], errors="coerce")
    if max_pe < 500:
        out = out[(pe <= max_pe) | pe.isna()]
    if min_pe > 0:
        out = out[pe >= min_pe]

    chg = pd.to_numeric(out["Change_Pct"], errors="coerce")
    out = out[(chg >= min_change_pct) | chg.isna()]
    out = out[(chg <= max_change_pct) | chg.isna()]

    if keyword.strip():
        kw = keyword.strip().lower()
        mask = (
            out["Name"].str.lower().str.contains(kw, na=False) |
            out["Sector"].str.lower().str.contains(kw, na=False) |
            out["Industry"].str.lower().str.contains(kw, na=False) |
            out["Ticker"].str.lower().str.contains(kw, na=False)
        )
        out = out[mask]

    return out.reset_index(drop=True)


# ══════════════════════════════════════════════════════════
#  UNIFIED MARKET DATA ENGINE  (unchanged from v5)
# ══════════════════════════════════════════════════════════
class UnifiedMarketDataEngine:
    """
    Attempts SEC EDGAR / OpenBB first, then yFinance as fallback.
    For v6 the open-source yFinance path is the primary live path.
    """

    def __init__(self, ticker: str):
        self.ticker      = ticker.strip().upper()
        self.data_source = "yFinance"
        self._info_cache: dict | None = None

    def info(self) -> dict:
        if self._info_cache is not None:
            return self._info_cache
        try:
            obj  = yf.Ticker(self.ticker)
            info = obj.info
            if info and len(info) > 5:
                self._info_cache = info
                return info
        except Exception:
            pass
        self._info_cache = {}
        return {}

    def deep_financials(self) -> dict[str, pd.Series]:
        """
        Returns a dict of metric_name → annual time-series (pd.Series).
        Falls back gracefully to empty dict.
        """
        results: dict[str, pd.Series] = {}
        try:
            t     = yf.Ticker(self.ticker)
            inc_a = t.income_stmt
            bal_a = t.balance_sheet
            cf_a  = t.cashflow

            def _row(df: pd.DataFrame, *keys: str) -> pd.Series:
                for k in keys:
                    for idx in df.index:
                        if k.lower() in str(idx).lower():
                            row = df.loc[idx].dropna()
                            if not row.empty:
                                return row.sort_index()
                return pd.Series(dtype=float)

            if inc_a is not None and not inc_a.empty:
                results["Revenue"]      = _row(inc_a, "Total Revenue", "Revenue")
                results["Gross Profit"] = _row(inc_a, "Gross Profit")
                results["Operating Income"] = _row(inc_a, "Operating Income", "EBIT")
                results["Net Income"]   = _row(inc_a, "Net Income")
                results["EBITDA"]       = _row(inc_a, "EBITDA", "Normalized EBITDA")

            if cf_a is not None and not cf_a.empty:
                results["Operating CF"] = _row(cf_a, "Operating Cash Flow", "Total Cash From Operating")
                results["Capex"]        = _row(cf_a, "Capital Expenditure", "Capex")
                fcf_op  = results.get("Operating CF", pd.Series(dtype=float))
                fcf_cap = results.get("Capex", pd.Series(dtype=float))
                if not fcf_op.empty and not fcf_cap.empty:
                    aligned = fcf_op.align(fcf_cap, join="inner")
                    results["Free Cash Flow"] = aligned[0] - aligned[1].abs()

            if bal_a is not None and not bal_a.empty:
                results["Total Assets"]  = _row(bal_a, "Total Assets")
                results["Total Debt"]    = _row(bal_a, "Total Debt", "Long Term Debt")
                results["Total Equity"]  = _row(bal_a, "Stockholders Equity", "Total Equity")
                results["Cash"]          = _row(bal_a, "Cash And Cash Equivalents", "Cash")

            results = {k: v for k, v in results.items() if isinstance(v, pd.Series) and not v.empty}

        except Exception:
            pass

        return results


# ══════════════════════════════════════════════════════════
#  INDIVIDUAL YF HELPER FUNCTIONS  (unchanged API surface)
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def yf_info(ticker: str) -> dict:
    try:
        obj  = yf.Ticker(ticker)
        info = obj.info
        return info if info and len(info) > 5 else {}
    except Exception:
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def yf_close(ticker: str, period: str = "1y", start: str | None = None) -> pd.Series:
    try:
        if start:
            df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        else:
            df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if df.empty:
            return pd.Series(dtype=float)
        if isinstance(df.columns, pd.MultiIndex):
            close = df["Close"].squeeze()
        else:
            close = df["Close"] if "Close" in df.columns else df.iloc[:, 0]
        return close.dropna()
    except Exception:
        return pd.Series(dtype=float)


@st.cache_data(ttl=300, show_spinner=False)
def yf_ohlcv(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def yf_price_chg(ticker: str) -> tuple[float | None, float | None]:
    try:
        info = yf_info(ticker)
        price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        prev  = info.get("previousClose") or price
        if price and prev and prev != 0:
            return float(price), float((price - prev) / prev * 100)
        return float(price) if price else None, None
    except Exception:
        return None, None


@st.cache_data(ttl=600, show_spinner=False)
def yf_financials(ticker: str) -> dict[str, pd.DataFrame]:
    try:
        t = yf.Ticker(ticker)
        return {
            "income_a":   t.income_stmt         if t.income_stmt   is not None else pd.DataFrame(),
            "balance_a":  t.balance_sheet        if t.balance_sheet is not None else pd.DataFrame(),
            "cashflow_a": t.cashflow             if t.cashflow      is not None else pd.DataFrame(),
            "income_q":   t.quarterly_income_stmt if t.quarterly_income_stmt is not None else pd.DataFrame(),
            "balance_q":  t.quarterly_balance_sheet if t.quarterly_balance_sheet is not None else pd.DataFrame(),
            "cashflow_q": t.quarterly_cashflow   if t.quarterly_cashflow is not None else pd.DataFrame(),
        }
    except Exception:
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def yf_options(ticker: str) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    try:
        t    = yf.Ticker(ticker)
        exps = list(t.options) if t.options else []
        if not exps:
            return pd.DataFrame(), pd.DataFrame(), []
        ch = t.option_chain(exps[0])
        return ch.calls, ch.puts, exps
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), []


@st.cache_data(ttl=600, show_spinner=False)
def yf_holders(ticker: str) -> pd.DataFrame:
    try:
        t = yf.Ticker(ticker)
        ih = t.institutional_holders
        return ih if ih is not None and not ih.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def yf_recommendations(ticker: str) -> pd.DataFrame:
    try:
        t = yf.Ticker(ticker)
        rec = t.recommendations
        return rec if rec is not None and not rec.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def yf_earnings_dates(ticker: str) -> pd.DataFrame:
    try:
        t  = yf.Ticker(ticker)
        ed = t.earnings_dates
        return ed if ed is not None and not ed.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════
#  FRED DATA ENGINE
# ══════════════════════════════════════════════════════════
_FRED_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fred(series_id: str, start: str | None = None) -> pd.Series:
    """
    Download a FRED series directly via CSV endpoint (no API key required).
    Returns a pd.Series indexed by date.  Returns empty Series on failure.
    """
    try:
        params: dict[str, str] = {"id": series_id}
        if start:
            params["vintage_date"] = start
        r = requests.get(_FRED_BASE, params=params, timeout=15)
        r.raise_for_status()
        from io import StringIO
        df = pd.read_csv(StringIO(r.text), index_col=0, parse_dates=True)
        df.columns = ["value"]
        s = pd.to_numeric(df["value"], errors="coerce").dropna()
        if start:
            s = s[s.index >= pd.to_datetime(start)]
        return s
    except Exception:
        return pd.Series(dtype=float)

"""
╔══════════════════════════════════════════════════════════════════╗
║   NAVY TERMINAL PRO  v6.1  ·  Data Engine                        ║
║   Unified Market Data · Finviz Screener · FRED · yFinance        ║
║   + Fama-French Factor Data (Ken French / ETF proxy)             ║
╚══════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import io
import warnings
import time
import zipfile
import concurrent.futures
from datetime import datetime, timedelta
from io import StringIO
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
#  EMPTY SCREENER SCHEMA
# ══════════════════════════════════════════════════════════
_SCREENER_EMPTY_COLS = [
    "Ticker", "Name", "Sector", "Industry", "Country",
    "MarketCap_B", "PE", "Price", "Change_Pct", "Volume", "Source",
]

def _empty_screener_df() -> pd.DataFrame:
    return pd.DataFrame(columns=_SCREENER_EMPTY_COLS)

# ══════════════════════════════════════════════════════════
#  FINVIZ HTTP SESSION
# ══════════════════════════════════════════════════════════
_FINVIZ_SESSION = requests.Session()
_FINVIZ_SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
    "Referer":         "https://finviz.com/screener.ashx",
    "DNT":             "1",
})

_FINVIZ_EXPORT_URL    = "https://finviz.com/export.ashx"
_FINVIZ_SCREENER_URL  = "https://finviz.com/screener.ashx"
_FINVIZ_PAGE_SIZE     = 20


@st.cache_data(ttl=600, show_spinner=False)
def fetch_finviz_screener_data() -> pd.DataFrame:
    df = _fetch_via_export_ashx()
    if not df.empty:
        return df
    df = _fetch_via_parallel_html()
    if not df.empty:
        return df
    return _empty_screener_df()


def _fetch_via_export_ashx() -> pd.DataFrame:
    try:
        params = {"v": "152", "r": "1", "c": "0,1,2,3,4,5,6,7,8,9"}
        r = _FINVIZ_SESSION.get(_FINVIZ_EXPORT_URL, params=params, timeout=20)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "")
        if "text/html" in content_type or r.text.strip().startswith("<"):
            _finviz_warmup()
            r = _FINVIZ_SESSION.get(_FINVIZ_EXPORT_URL, params=params, timeout=20)
            r.raise_for_status()
            content_type = r.headers.get("Content-Type", "")
            if "text/html" in content_type or r.text.strip().startswith("<"):
                return _empty_screener_df()
        df = pd.read_csv(StringIO(r.text))
        if df.empty or "Ticker" not in df.columns:
            return _empty_screener_df()
        return _normalise_finviz_csv(df)
    except Exception:
        return _empty_screener_df()


def _finviz_warmup() -> None:
    try:
        _FINVIZ_SESSION.get(_FINVIZ_SCREENER_URL, params={"v": "111"}, timeout=10)
    except Exception:
        pass


def _fetch_via_parallel_html() -> pd.DataFrame:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return _empty_screener_df()
    try:
        page1_soup, total_rows = _fetch_screener_page_html(1)
        if page1_soup is None or total_rows == 0:
            return _empty_screener_df()
        headers, rows_p1 = _parse_screener_table(page1_soup)
        if not headers or not rows_p1:
            return _empty_screener_df()
        total_pages = max(1, (total_rows + _FINVIZ_PAGE_SIZE - 1) // _FINVIZ_PAGE_SIZE)
        total_pages = min(total_pages, 500)
        all_rows: list[list] = rows_p1
        remaining_start_rows = [1 + p * _FINVIZ_PAGE_SIZE for p in range(1, total_pages)]
        if remaining_start_rows:
            def _worker(start_row: int) -> list[list]:
                soup, _ = _fetch_screener_page_html(start_row)
                if soup is None:
                    return []
                _, rows = _parse_screener_table(soup)
                return rows or []
            with concurrent.futures.ThreadPoolExecutor(max_workers=30) as pool:
                futures = {pool.submit(_worker, sr): sr for sr in remaining_start_rows}
                for fut in concurrent.futures.as_completed(futures):
                    try:
                        all_rows.extend(fut.result(timeout=15))
                    except Exception:
                        pass
        if not all_rows:
            return _empty_screener_df()
        df = pd.DataFrame(all_rows, columns=headers)
        return _normalise_finviz_html_df(df)
    except Exception:
        return _empty_screener_df()


def _fetch_screener_page_html(start_row: int) -> tuple:
    try:
        from bs4 import BeautifulSoup
        r = _FINVIZ_SESSION.get(
            _FINVIZ_SCREENER_URL, params={"v": "111", "r": str(start_row)}, timeout=12
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        total = 0
        try:
            td_total = soup.find("td", {"class": "count-text"})
            if td_total:
                import re
                m = re.search(r"Total:\s*([\d,]+)", td_total.get_text())
                if m:
                    total = int(m.group(1).replace(",", ""))
        except Exception:
            pass
        return soup, total
    except Exception:
        return None, 0


def _parse_screener_table(soup) -> tuple:
    try:
        table = soup.find("table", {"class": "screener_table"})
        if table is None:
            return [], []
        tr_list = table.find_all("tr")
        if len(tr_list) < 2:
            return [], []
        headers = [th.get_text(strip=True) for th in tr_list[0].find_all("th")][1:]
        rows: list[list] = []
        for tr in tr_list[1:]:
            cells = tr.find_all("td")
            if len(cells) < 2:
                continue
            row = [td.get_text(strip=True) for td in cells[1:]]
            while len(row) < len(headers):
                row.append("")
            rows.append(row[: len(headers)])
        return headers, rows
    except Exception:
        return [], []


def _normalise_finviz_csv(df: pd.DataFrame) -> pd.DataFrame:
    csv_rename = {
        "Ticker": "Ticker", "Company": "Name", "Sector": "Sector",
        "Industry": "Industry", "Country": "Country",
        "Market Cap": "MarketCap_raw", "P/E": "PE_raw",
        "Price": "Price_raw", "Change": "Change_raw", "Volume": "Volume_raw",
    }
    rename_map = {c: csv_rename[c] for c in df.columns if c in csv_rename}
    df = df.rename(columns=rename_map)
    for col in ["MarketCap_raw", "PE_raw", "Price_raw", "Change_raw", "Volume_raw"]:
        if col not in df.columns:
            df[col] = None
    return _build_clean_df(df, source="Finviz")


def _normalise_finviz_html_df(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {c: _FINVIZ_RENAME[c] for c in df.columns if c in _FINVIZ_RENAME}
    df = df.rename(columns=rename_map)
    for col in ["MarketCap_raw", "PE_raw", "Price_raw", "Change_raw", "Volume_raw"]:
        if col not in df.columns:
            df[col] = None
    return _build_clean_df(df, source="Finviz")


def _build_clean_df(df: pd.DataFrame, source: str) -> pd.DataFrame:
    df["MarketCap_B"] = df["MarketCap_raw"].apply(_parse_finviz_market_cap) / 1e9
    df["PE"]          = df["PE_raw"].apply(_parse_finviz_pe)
    df["Price"]       = df["Price_raw"].apply(_parse_finviz_price)
    df["Change_Pct"]  = df["Change_raw"].apply(_parse_finviz_pct)
    df["Volume"]      = df["Volume_raw"].apply(_parse_finviz_volume)
    for col in ["Ticker", "Name", "Sector", "Industry", "Country"]:
        if col not in df.columns:
            df[col] = "N/A"
        df[col] = df[col].fillna("N/A").astype(str)
    df["Source"] = source
    for col in _SCREENER_EMPTY_COLS:
        if col not in df.columns:
            df[col] = float("nan") if col not in ("Ticker", "Name", "Sector", "Industry", "Country", "Source") else "N/A"
    out = df[_SCREENER_EMPTY_COLS].copy()
    out = out[out["Ticker"].str.strip().ne("") & out["Ticker"].ne("N/A")]
    return out.reset_index(drop=True)


@st.cache_data(ttl=600, show_spinner=False)
def fetch_backup_yfinance_screener(
    universe: tuple[str, ...] | None = None,
    chunk_size: int = 100,
) -> pd.DataFrame:
    if universe is None:
        universe = tuple(SCREENER_UNIVERSE_FULL)
    try:
        tickers_str = " ".join(universe)
        raw_px = yf.download(
            tickers=tickers_str, period="5d", interval="1d",
            threads=True, progress=False, auto_adjust=True,
        )
        if raw_px.empty:
            return _empty_screener_df()
        if isinstance(raw_px.columns, pd.MultiIndex):
            close_df  = raw_px["Close"]  if "Close"  in raw_px.columns.get_level_values(0) else pd.DataFrame()
            volume_df = raw_px["Volume"] if "Volume" in raw_px.columns.get_level_values(0) else pd.DataFrame()
        else:
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
        change_pct  = ((last_close - prev_close) / prev_close.replace(0, float("nan"))) * 100
        valid_tickers = [t for t in last_close.index if pd.notna(last_close[t])]

        def _fetch_meta(tkr: str) -> dict:
            try:
                info = yf.Ticker(tkr).info
                if not info:
                    return {"Ticker": tkr}
                return {
                    "Ticker":      tkr,
                    "Name":        (info.get("longName") or info.get("shortName") or tkr)[:40],
                    "Sector":      info.get("sector",   "N/A"),
                    "Industry":    info.get("industry", "N/A"),
                    "Country":     info.get("country",  "N/A"),
                    "MarketCap_B": (info.get("marketCap") or 0) / 1e9,
                    "PE":          info.get("forwardPE") or info.get("trailingPE") or float("nan"),
                }
            except Exception:
                return {"Ticker": tkr}

        meta_rows: list[dict] = []
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

        price_records = []
        for tkr in valid_tickers:
            price_records.append({
                "Ticker":     tkr,
                "Price":      round(float(last_close[tkr]), 4) if pd.notna(last_close[tkr]) else float("nan"),
                "Change_Pct": round(float(change_pct[tkr]), 2) if pd.notna(change_pct.get(tkr, float("nan"))) else float("nan"),
                "Volume":     float(last_volume[tkr]) if tkr in last_volume.index and pd.notna(last_volume[tkr]) else float("nan"),
            })

        price_df = pd.DataFrame(price_records)
        merged   = price_df.merge(meta_df, on="Ticker", how="left")
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


def load_screener_master_data(force_fallback: bool = False) -> tuple[pd.DataFrame, str]:
    if not force_fallback:
        df = fetch_finviz_screener_data()
        if not df.empty:
            return df, "Finviz"
    df = fetch_backup_yfinance_screener(universe=tuple(SCREENER_UNIVERSE_FULL))
    if not df.empty:
        return df, "yFinance Batch"
    return _empty_screener_df(), "None (Network Error)"


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
#  UNIFIED MARKET DATA ENGINE
# ══════════════════════════════════════════════════════════
class UnifiedMarketDataEngine:
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
                results["Revenue"]          = _row(inc_a, "Total Revenue", "Revenue")
                results["Gross Profit"]     = _row(inc_a, "Gross Profit")
                results["Operating Income"] = _row(inc_a, "Operating Income", "EBIT")
                results["Net Income"]       = _row(inc_a, "Net Income")
                results["EBITDA"]           = _row(inc_a, "EBITDA", "Normalized EBITDA")
            if cf_a is not None and not cf_a.empty:
                results["Operating CF"] = _row(cf_a, "Operating Cash Flow", "Total Cash From Operating")
                results["Capex"]        = _row(cf_a, "Capital Expenditure", "Capex")
                fcf_op  = results.get("Operating CF", pd.Series(dtype=float))
                fcf_cap = results.get("Capex",        pd.Series(dtype=float))
                if not fcf_op.empty and not fcf_cap.empty:
                    aligned = fcf_op.align(fcf_cap, join="inner")
                    results["Free Cash Flow"] = aligned[0] - aligned[1].abs()
            if bal_a is not None and not bal_a.empty:
                results["Total Assets"] = _row(bal_a, "Total Assets")
                results["Total Debt"]   = _row(bal_a, "Total Debt", "Long Term Debt")
                results["Total Equity"] = _row(bal_a, "Stockholders Equity", "Total Equity")
                results["Cash"]         = _row(bal_a, "Cash And Cash Equivalents", "Cash")
            results = {k: v for k, v in results.items() if isinstance(v, pd.Series) and not v.empty}
        except Exception:
            pass
        return results


# ══════════════════════════════════════════════════════════
#  INDIVIDUAL YF HELPER FUNCTIONS
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
        info  = yf_info(ticker)
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
            "income_a":   t.income_stmt              if t.income_stmt              is not None else pd.DataFrame(),
            "balance_a":  t.balance_sheet             if t.balance_sheet            is not None else pd.DataFrame(),
            "cashflow_a": t.cashflow                  if t.cashflow                 is not None else pd.DataFrame(),
            "income_q":   t.quarterly_income_stmt     if t.quarterly_income_stmt    is not None else pd.DataFrame(),
            "balance_q":  t.quarterly_balance_sheet   if t.quarterly_balance_sheet  is not None else pd.DataFrame(),
            "cashflow_q": t.quarterly_cashflow        if t.quarterly_cashflow       is not None else pd.DataFrame(),
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
        t  = yf.Ticker(ticker)
        ih = t.institutional_holders
        return ih if ih is not None and not ih.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def yf_recommendations(ticker: str) -> pd.DataFrame:
    try:
        t   = yf.Ticker(ticker)
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
    try:
        params: dict[str, str] = {"id": series_id}
        if start:
            params["vintage_date"] = start
        r = requests.get(_FRED_BASE, params=params, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text), index_col=0, parse_dates=True)
        df.columns = ["value"]
        s = pd.to_numeric(df["value"], errors="coerce").dropna()
        if start:
            s = s[s.index >= pd.to_datetime(start)]
        return s
    except Exception:
        return pd.Series(dtype=float)


# ══════════════════════════════════════════════════════════
#  FAMA-FRENCH FACTOR DATA ENGINE  (NEW)
# ══════════════════════════════════════════════════════════

# Factor proxy ETF tickers used when Ken French website is unavailable
# Each factor is approximated as a long-short spread between two ETFs
_FF_PROXY_ETF_MAP = {
    # Factor:   (long_etf, short_etf)  — spread approximates the factor premium
    "Mkt-RF":   ("SPY",  None),       # Market excess return (vs risk-free)
    "SMB":      ("IWM",  "IVV"),      # Small - Large cap
    "HML":      ("IVE",  "IVW"),      # Value - Growth
    "MOM":      ("MTUM", "SPY"),      # Momentum vs broad market
    "RMW":      ("QUAL", "SPY"),      # Profitability (Quality) vs broad
    "CMA":      ("USMV", "SPY"),      # Conservative investment (Low-Vol) vs broad
    # Risk-free proxy: 3-month T-bill annualised → daily
    "RF":       ("SHY",  None),       # Short-term T-bill ETF as RF proxy
}

# Ken French data library — CSV zip endpoints (no API key needed, sometimes 403)
_KF_BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp"
_KF_DATASETS = {
    "FF3":  "F-F_Research_Data_Factors_daily_CSV.zip",
    "FF5":  "F-F_Research_Data_5_Factors_2x3_daily_CSV.zip",
    "MOM":  "F-F_Momentum_Factor_daily_CSV.zip",
}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ff_factors_kf(
    dataset_key: str = "FF3",
    start: str = "2018-01-01",
    end: str | None = None,
) -> pd.DataFrame:
    """
    Attempt to download Fama-French factors directly from Ken French's data
    library (CSV zip files, no API key required).

    Parameters
    ----------
    dataset_key : "FF3" | "FF5" | "MOM"
    start       : start date string YYYY-MM-DD
    end         : end date string YYYY-MM-DD (defaults to today)

    Returns
    -------
    DataFrame with date index and factor columns as decimals (÷ 100).
    Columns: Mkt-RF, SMB, HML, [MOM], [RMW, CMA], RF
    Empty DataFrame on failure.
    """
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")

    fname = _KF_DATASETS.get(dataset_key, _KF_DATASETS["FF3"])
    url   = f"{_KF_BASE}/{fname}"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
            "Referer":    "https://mba.tuck.dartmouth.edu/",
        }
        r = requests.get(url, headers=headers, timeout=25)
        if r.status_code != 200:
            return pd.DataFrame()

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            csv_name = [n for n in z.namelist() if n.endswith(".CSV") or n.endswith(".csv")]
            if not csv_name:
                return pd.DataFrame()
            raw = z.read(csv_name[0]).decode("utf-8", errors="replace")

        # Ken French CSVs have a preamble before the data starts
        lines = raw.splitlines()
        # Find header line containing "Mkt-RF" or "Mkt_RF"
        header_idx = None
        for i, line in enumerate(lines):
            if "Mkt" in line and ("SMB" in line or "HML" in line):
                header_idx = i
                break

        if header_idx is None:
            return pd.DataFrame()

        data_str = "\n".join(lines[header_idx:])
        df = pd.read_csv(StringIO(data_str), index_col=0)
        # Drop footer rows (non-numeric index)
        df.index = pd.to_numeric(df.index, errors="coerce")
        df = df[df.index.notna()].copy()
        df.index = pd.to_datetime(df.index.astype(int).astype(str), format="%Y%m%d")
        df.index.name = "Date"

        # Normalise column names
        df.columns = [c.strip() for c in df.columns]
        col_map = {}
        for c in df.columns:
            cl = c.lower().replace(" ", "").replace("-", "").replace("_", "")
            if "mkt" in cl:   col_map[c] = "Mkt-RF"
            elif "smb" in cl: col_map[c] = "SMB"
            elif "hml" in cl: col_map[c] = "HML"
            elif cl == "mom" or "moment" in cl: col_map[c] = "MOM"
            elif "rmw" in cl: col_map[c] = "RMW"
            elif "cma" in cl: col_map[c] = "CMA"
            elif cl == "rf":  col_map[c] = "RF"
        df = df.rename(columns=col_map)

        # Convert percentage to decimal
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce") / 100

        df = df.dropna(how="all")
        df = df[df.index >= pd.to_datetime(start)]
        if end:
            df = df[df.index <= pd.to_datetime(end)]

        return df

    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ff_factors_proxy(
    start: str = "2018-01-01",
    end:   str | None = None,
    model: str = "FF5",
) -> pd.DataFrame:
    """
    Build Fama-French-style factor returns from ETF proxies via yFinance.
    Used as fallback when Ken French website is inaccessible.

    Factor construction:
      Mkt-RF = SPY daily ret - daily RF (SHY proxy)
      SMB    = IWM ret - IVV ret   (Small - Large)
      HML    = IVE ret - IVW ret   (Value - Growth)
      MOM    = MTUM ret - QUAL ret  (Momentum - Quality)
      RMW    = QUAL ret - SPY ret   (Profitability premium)
      CMA    = USMV ret - SPY ret   (Conservative investment / Low vol premium)
      RF     = SHY daily ret (T-bill proxy, annualised /252)

    Returns decimals (not percentages).
    """
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")

    # Download all proxy ETFs in a single batch call
    proxy_tickers = ["SPY", "IWM", "IVV", "IVE", "IVW", "MTUM", "QUAL", "USMV", "SHY"]
    try:
        raw = yf.download(
            tickers=" ".join(proxy_tickers),
            start=start, end=end,
            progress=False, auto_adjust=True,
        )
        if raw.empty:
            return pd.DataFrame()

        if isinstance(raw.columns, pd.MultiIndex):
            px = raw["Close"]
        else:
            px = raw[["Close"]].rename(columns={"Close": proxy_tickers[0]})

        # Drop columns with too many NaNs
        px = px.dropna(how="all", axis=0).ffill().bfill()
        ret = px.pct_change().dropna(how="all")

        factors = pd.DataFrame(index=ret.index)

        # Daily risk-free rate from SHY (annualised T-bill → daily)
        rf_daily = ret["SHY"] if "SHY" in ret.columns else pd.Series(0, index=ret.index)
        factors["RF"] = rf_daily

        # Mkt-RF
        if "SPY" in ret.columns:
            factors["Mkt-RF"] = ret["SPY"] - rf_daily

        # SMB: IWM (small) - IVV (large)
        if "IWM" in ret.columns and "IVV" in ret.columns:
            factors["SMB"] = ret["IWM"] - ret["IVV"]
        elif "IWM" in ret.columns and "SPY" in ret.columns:
            factors["SMB"] = ret["IWM"] - ret["SPY"]

        # HML: IVE (value) - IVW (growth)
        if "IVE" in ret.columns and "IVW" in ret.columns:
            factors["HML"] = ret["IVE"] - ret["IVW"]

        # MOM: MTUM - SPY
        if "MTUM" in ret.columns and "SPY" in ret.columns:
            factors["MOM"] = ret["MTUM"] - ret["SPY"]

        # RMW: QUAL - SPY (quality/profitability premium)
        if "QUAL" in ret.columns and "SPY" in ret.columns:
            factors["RMW"] = ret["QUAL"] - ret["SPY"]

        # CMA: USMV - SPY (low-vol / conservative investment proxy)
        if "USMV" in ret.columns and "SPY" in ret.columns:
            factors["CMA"] = ret["USMV"] - ret["SPY"]

        return factors.dropna(how="all")

    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ff_factors(
    start: str = "2018-01-01",
    end:   str | None = None,
    model: str = "FF5",
) -> tuple[pd.DataFrame, str]:
    """
    Unified Fama-French factor loader.

    Strategy (first success wins):
      1. Ken French data library (most accurate)
      2. ETF proxy construction via yFinance (always available)

    Parameters
    ----------
    start : start date YYYY-MM-DD
    end   : end date YYYY-MM-DD
    model : "CAPM" | "FF3" | "CARHART4" | "FF5"

    Returns
    -------
    (factors_df, source_label)
    factors_df has columns: Mkt-RF, SMB, HML, [MOM], [RMW, CMA], RF
    Values are decimals (daily returns, not percentages).
    """
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")

    # Map model to Ken French dataset
    kf_map = {
        "CAPM":     ("FF3",  ["Mkt-RF", "RF"]),
        "FF3":      ("FF3",  ["Mkt-RF", "SMB", "HML", "RF"]),
        "CARHART4": ("FF3",  ["Mkt-RF", "SMB", "HML", "RF"]),  # + MOM separate
        "FF5":      ("FF5",  ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"]),
    }
    kf_key, needed_cols = kf_map.get(model, ("FF3", ["Mkt-RF", "SMB", "HML", "RF"]))

    # ── Layer 1: Ken French website ──────────────────────
    df_kf = fetch_ff_factors_kf(kf_key, start=start, end=end)

    # For Carhart, also need MOM from separate dataset
    if model == "CARHART4" and not df_kf.empty:
        df_mom = fetch_ff_factors_kf("MOM", start=start, end=end)
        if not df_mom.empty and "MOM" in df_mom.columns:
            df_kf = df_kf.join(df_mom[["MOM"]], how="left")

    if not df_kf.empty:
        available = [c for c in needed_cols if c in df_kf.columns]
        if len(available) >= 2:
            return df_kf[available].dropna(), "Ken French Library"

    # ── Layer 2: ETF proxy ───────────────────────────────
    df_proxy = fetch_ff_factors_proxy(start=start, end=end, model=model)
    if not df_proxy.empty:
        available = [c for c in needed_cols if c in df_proxy.columns]
        if available:
            return df_proxy[available].dropna(), "ETF Proxy (yFinance)"

    return pd.DataFrame(), "Unavailable"


@st.cache_data(ttl=600, show_spinner=False)
def fetch_asset_returns_for_regression(
    input_type: str,
    ticker:     str = "",
    portfolio_tickers: list[str] | None = None,
    portfolio_weights: list[float] | None = None,
    start: str = "2018-01-01",
    end:   str | None = None,
) -> tuple[pd.Series, str]:
    """
    Fetch and compute daily returns for the target asset or portfolio.

    Parameters
    ----------
    input_type          : "Single Ticker / ETF" | "Custom Portfolio"
    ticker              : yfinance ticker string (for single asset mode)
    portfolio_tickers   : list of tickers (for portfolio mode)
    portfolio_weights   : list of weights summing to 1.0 (for portfolio mode)
    start, end          : date range

    Returns
    -------
    (daily_returns_series, label_string)
    """
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")

    if input_type == "Single Ticker / ETF":
        tkr = ticker.strip().upper()
        if not tkr:
            return pd.Series(dtype=float), ""
        try:
            px = yf.download(tkr, start=start, end=end, progress=False, auto_adjust=True)
            if px.empty:
                return pd.Series(dtype=float), tkr
            if isinstance(px.columns, pd.MultiIndex):
                px.columns = px.columns.get_level_values(0)
            close = px["Close"].dropna()
            ret = close.pct_change().dropna()
            ret.name = tkr
            return ret, tkr
        except Exception:
            return pd.Series(dtype=float), tkr

    elif input_type == "Custom Portfolio":
        if not portfolio_tickers or not portfolio_weights:
            return pd.Series(dtype=float), "Portfolio"

        # Normalise weights
        w = np.array(portfolio_weights, dtype=float)
        w = w / w.sum()

        tickers_str = " ".join([t.strip().upper() for t in portfolio_tickers])
        try:
            raw = yf.download(
                tickers=tickers_str, start=start, end=end,
                progress=False, auto_adjust=True,
            )
            if raw.empty:
                return pd.Series(dtype=float), "Portfolio"

            if isinstance(raw.columns, pd.MultiIndex):
                px = raw["Close"]
            else:
                px = raw[["Close"]].rename(columns={"Close": portfolio_tickers[0]})

            px = px.dropna(how="all").ffill()
            ret_df = px.pct_change().dropna(how="all")

            # Align weights to available columns
            valid = [(t.strip().upper(), wt) for t, wt in zip(portfolio_tickers, w) if t.strip().upper() in ret_df.columns]
            if not valid:
                return pd.Series(dtype=float), "Portfolio"

            tks_v, wts_v = zip(*valid)
            wts_v_arr = np.array(wts_v)
            wts_v_arr = wts_v_arr / wts_v_arr.sum()

            port_ret = (ret_df[list(tks_v)] * wts_v_arr).sum(axis=1)
            port_ret.name = "Portfolio"
            port_ret = port_ret.dropna()
            label = " + ".join([f"{t}({wt*100:.0f}%)" for t, wt in zip(tks_v, wts_v_arr)])
            return port_ret, label
        except Exception:
            return pd.Series(dtype=float), "Portfolio"

    return pd.Series(dtype=float), ""


def build_regression_dataset(
    asset_returns:  pd.Series,
    factors_df:     pd.DataFrame,
    rf_col:         str = "RF",
) -> tuple[pd.Series, pd.DataFrame]:
    """
    Align asset returns with factor data and compute excess returns.

    Returns
    -------
    (excess_returns, factor_columns_df)
    excess_returns = asset_ret - RF (daily)
    factor_columns_df = all factor columns except RF
    """
    # Align on common dates
    aligned = pd.concat([asset_returns.rename("Asset"), factors_df], axis=1, join="inner").dropna()

    if aligned.empty or len(aligned) < 30:
        return pd.Series(dtype=float), pd.DataFrame()

    # Daily risk-free rate
    if rf_col in aligned.columns:
        rf_series = aligned[rf_col]
    else:
        # Fallback: use 4.2% annual → daily
        rf_series = pd.Series(0.042 / 252, index=aligned.index)

    excess_ret = aligned["Asset"] - rf_series
    factor_cols = [c for c in aligned.columns if c not in ("Asset", rf_col)]
    factor_data = aligned[factor_cols]

    return excess_ret, factor_data
DATAENGINE_EOF
echo "data_engine.py written: $(wc -l < /home/claude/data_engine.py) lines"

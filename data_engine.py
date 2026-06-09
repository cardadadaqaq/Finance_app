"""
NAVY TERMINAL PRO  v6.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
data_engine.py  ·  UnifiedMarketDataEngine
Hybrid router: SEC Edgar (US) → OpenBB (Non-US) → yfinance (fallback)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from __future__ import annotations

import json
import warnings
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────
SEC_HEADERS = {
    "User-Agent": "NavyTerminal/6.0 (research@navyterminal.com)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_FACTS_URL   = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
FRED_CSV_URL    = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"

NON_US_SUFFIXES = (
    ".DE", ".AS", ".PA", ".MI", ".MC", ".L", ".SW", ".OL", ".ST",
    ".CO", ".HE", ".BR", ".LI", ".VI", ".IS", ".WA", ".PR",
    ".HK", ".T",  ".KS", ".AX", ".NZ", ".SA", ".MX", ".BO", ".NS", ".TW",
)

# XBRL concept keys → human-readable label
# Order matters: first match per label wins
XBRL_CONCEPTS: list[tuple[str, str]] = [
    ("us-gaap:Revenues",                                              "Revenue"),
    ("us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",   "Revenue"),
    ("us-gaap:SalesRevenueNet",                                       "Revenue"),
    ("us-gaap:NetIncomeLoss",                                         "Net Income"),
    ("us-gaap:OperatingIncomeLoss",                                   "Operating Income"),
    ("us-gaap:GrossProfit",                                           "Gross Profit"),
    ("us-gaap:CostOfRevenue",                                         "Cost of Revenue"),
    ("us-gaap:ResearchAndDevelopmentExpense",                         "R&D Expense"),
    ("us-gaap:SellingGeneralAndAdministrativeExpense",                "SG&A"),
    ("us-gaap:InterestExpense",                                       "Interest Expense"),
    ("us-gaap:IncomeTaxExpenseBenefit",                               "Income Tax"),
    ("us-gaap:EarningsPerShareBasic",                                 "EPS Basic"),
    ("us-gaap:EarningsPerShareDiluted",                               "EPS Diluted"),
    ("us-gaap:Assets",                                                "Total Assets"),
    ("us-gaap:Liabilities",                                           "Total Liabilities"),
    ("us-gaap:StockholdersEquity",                                    "Stockholders Equity"),
    ("us-gaap:CashAndCashEquivalentsAtCarryingValue",                 "Cash & Equivalents"),
    ("us-gaap:LongTermDebt",                                          "Long-Term Debt"),
    ("us-gaap:ShortTermBorrowings",                                   "Short-Term Debt"),
    ("us-gaap:CommonStockSharesOutstanding",                          "Shares Outstanding"),
    ("us-gaap:NetCashProvidedByUsedInOperatingActivities",            "Operating Cash Flow"),
    ("us-gaap:PaymentsToAcquirePropertyPlantAndEquipment",            "CapEx"),
    ("us-gaap:DepreciationDepletionAndAmortization",                  "D&A"),
    ("us-gaap:DividendsCommonStock",                                  "Dividends Paid"),
    ("us-gaap:RetainedEarningsAccumulatedDeficit",                    "Retained Earnings"),
]

FRED_SERIES: dict[str, str] = {
    "10Y Treasury":          "DGS10",
    "2Y Treasury":           "DGS2",
    "3M Treasury":           "DGS3MO",
    "5Y Treasury":           "DGS5",
    "30Y Treasury":          "DGS30",
    "Fed Funds Rate":        "FEDFUNDS",
    "CPI YoY":               "CPIAUCSL",
    "Core CPI":              "CPILFESL",
    "PCE Inflation":         "PCEPI",
    "Unemployment":          "UNRATE",
    "GDP QoQ":               "A191RL1Q225SBEA",
    "Industrial Production": "INDPRO",
    "Retail Sales":          "RSAFS",
    "Consumer Sentiment":    "UMCSENT",
    "M2 Money Supply":       "M2SL",
    "HY Spread":             "BAMLH0A0HYM2",
    "IG Spread":             "BAMLC0A0CM",
    "TED Spread":            "TEDRATE",
    "10Y-2Y Spread":         "T10Y2Y",
    "10Y-3M Spread":         "T10Y3M",
    "VIX (FRED)":            "VIXCLS",
}


# ─────────────────────────────────────────────────────────
#  SEC EDGAR LAYER
# ─────────────────────────────────────────────────────────
@st.cache_data(ttl=86_400, show_spinner=False)
def _load_sec_cik_map() -> dict[str, str]:
    """Download and cache the full SEC ticker→CIK mapping (refreshes once per day)."""
    try:
        resp = requests.get(
            SEC_TICKERS_URL,
            headers={"User-Agent": "NavyTerminal/6.0 (research@navyterminal.com)"},
            timeout=15,
        )
        resp.raise_for_status()
        raw: dict = resp.json()
        mapping: dict[str, str] = {}
        for entry in raw.values():
            ticker = str(entry.get("ticker", "")).upper().strip()
            cik    = str(entry.get("cik_str", "")).strip().zfill(10)
            if ticker and cik:
                mapping[ticker] = cik
        return mapping
    except Exception:
        return {}


def _resolve_cik(ticker: str) -> Optional[str]:
    mapping = _load_sec_cik_map()
    return mapping.get(ticker.upper().strip())


@st.cache_data(ttl=3_600, show_spinner=False)
def _fetch_sec_facts(cik: str) -> dict:
    """Fetch raw XBRL company facts JSON from SEC Edgar for a padded CIK."""
    url = SEC_FACTS_URL.format(cik=cik)
    try:
        resp = requests.get(url, headers=SEC_HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


def _extract_xbrl_concept(facts: dict, concept_key: str) -> pd.Series:
    """
    Parse one XBRL concept from SEC company facts JSON.
    Returns pd.Series(date → float) for annual 10-K filings only.
    """
    try:
        taxonomy, tag = concept_key.split(":", 1)
        units = (
            facts.get("facts", {})
                 .get(taxonomy, {})
                 .get(tag, {})
                 .get("units", {})
        )
        values_list = (
            units.get("USD")
            or units.get("shares")
            or units.get("pure")
            or []
        )
        records: list[dict] = []
        for entry in values_list:
            if entry.get("form") in ("10-K", "20-F") and entry.get("end") and entry.get("val") is not None:
                records.append({
                    "date":  pd.to_datetime(entry["end"]),
                    "value": float(entry["val"]),
                })
        if not records:
            return pd.Series(dtype=float)
        df = pd.DataFrame(records).drop_duplicates("date").sort_values("date")
        return df.set_index("date")["value"]
    except Exception:
        return pd.Series(dtype=float)


def build_sec_financials(ticker: str) -> dict[str, pd.Series]:
    """
    Pull and parse multi-decade SEC XBRL financials for a US ticker.
    Returns {human_label: pd.Series(date → float)}.
    Derives FCF = OCF − CapEx and EBITDA = OpIncome + D&A automatically.
    """
    cik = _resolve_cik(ticker)
    if not cik:
        return {}
    facts = _fetch_sec_facts(cik)
    if not facts:
        return {}

    result: dict[str, pd.Series] = {}
    seen_labels: set[str] = set()

    for concept_key, label in XBRL_CONCEPTS:
        if label in seen_labels:
            continue
        series = _extract_xbrl_concept(facts, concept_key)
        if not series.empty:
            result[label]  = series
            seen_labels.add(label)

    # Derived: Free Cash Flow
    if "Operating Cash Flow" in result and "CapEx" in result:
        aligned = pd.concat(
            [result["Operating Cash Flow"], result["CapEx"]], axis=1, keys=["ocf", "cap"]
        ).dropna()
        if not aligned.empty:
            result["Free Cash Flow"] = aligned["ocf"] - aligned["cap"]

    # Derived: EBITDA
    if "Operating Income" in result and "D&A" in result:
        aligned2 = pd.concat(
            [result["Operating Income"], result["D&A"]], axis=1, keys=["oi", "da"]
        ).dropna()
        if not aligned2.empty:
            result["EBITDA"] = aligned2["oi"] + aligned2["da"]

    return result


# ─────────────────────────────────────────────────────────
#  OPENBB LAYER
# ─────────────────────────────────────────────────────────
def _openbb_available() -> bool:
    try:
        import importlib
        return importlib.util.find_spec("openbb") is not None
    except Exception:
        return False


@st.cache_data(ttl=3_600, show_spinner=False)
def _fetch_openbb_financials(ticker: str) -> dict[str, pd.DataFrame]:
    """Pull annual income / balance / cashflow statements via OpenBB SDK."""
    try:
        from openbb import obb  # type: ignore
        out: dict[str, pd.DataFrame] = {}
        for sheet, method in [
            ("income",   lambda: obb.equity.fundamental.income(ticker,  period="annual", limit=20)),
            ("balance",  lambda: obb.equity.fundamental.balance(ticker, period="annual", limit=20)),
            ("cashflow", lambda: obb.equity.fundamental.cash(ticker,    period="annual", limit=20)),
        ]:
            try:
                res = method()
                out[sheet] = res.to_df() if hasattr(res, "to_df") else pd.DataFrame()
            except Exception:
                out[sheet] = pd.DataFrame()
        return out
    except Exception:
        return {}


_OBB_INCOME_MAP = {
    "revenue": "Revenue",
    "gross_profit": "Gross Profit",
    "operating_income": "Operating Income",
    "net_income": "Net Income",
    "ebitda": "EBITDA",
    "research_and_development": "R&D Expense",
    "selling_general_and_admin": "SG&A",
    "interest_expense": "Interest Expense",
    "income_tax_expense": "Income Tax",
    "eps_diluted": "EPS Diluted",
    "eps_basic": "EPS Basic",
}
_OBB_BALANCE_MAP = {
    "total_assets": "Total Assets",
    "total_liabilities": "Total Liabilities",
    "stockholders_equity": "Stockholders Equity",
    "cash_and_equivalents": "Cash & Equivalents",
    "long_term_debt": "Long-Term Debt",
    "short_term_debt": "Short-Term Debt",
    "retained_earnings": "Retained Earnings",
    "shares_outstanding": "Shares Outstanding",
}
_OBB_CASHFLOW_MAP = {
    "operating_cash_flow": "Operating Cash Flow",
    "capital_expenditures": "CapEx",
    "free_cash_flow": "Free Cash Flow",
    "dividends_paid": "Dividends Paid",
    "depreciation_and_amortization": "D&A",
}


def _normalize_openbb(raw: dict[str, pd.DataFrame]) -> dict[str, pd.Series]:
    """Flatten OpenBB DataFrames → {label: pd.Series(date → float)}."""
    sheet_maps = {
        "income":   _OBB_INCOME_MAP,
        "balance":  _OBB_BALANCE_MAP,
        "cashflow": _OBB_CASHFLOW_MAP,
    }
    result: dict[str, pd.Series] = {}
    for sheet_key, col_map in sheet_maps.items():
        df = raw.get(sheet_key, pd.DataFrame())
        if df is None or df.empty:
            continue
        try:
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index, errors="coerce")
            df = df[~df.index.isna()].sort_index()
        except Exception:
            continue
        for col_name, human_label in col_map.items():
            if human_label in result:
                continue
            matched = None
            if col_name in df.columns:
                matched = col_name
            else:
                needle = col_name.lower().replace("_", "")
                for dc in df.columns:
                    if needle in str(dc).lower().replace("_", ""):
                        matched = dc
                        break
            if matched is not None:
                s = pd.to_numeric(df[matched], errors="coerce").dropna()
                if not s.empty:
                    result[human_label] = s
    return result


# ─────────────────────────────────────────────────────────
#  YFINANCE HELPERS  (price / quote / fallback fundamentals)
# ─────────────────────────────────────────────────────────
@st.cache_data(ttl=180, show_spinner=False)
def yf_info(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info
        if not info or len(info) < 4:
            return {}
        if not any(info.get(k) for k in ["regularMarketPrice", "currentPrice", "previousClose", "longName"]):
            return {}
        return info
    except Exception:
        return {}


@st.cache_data(ttl=180, show_spinner=False)
def yf_close(ticker: str, start: Optional[str] = None, period: Optional[str] = None) -> pd.Series:
    try:
        t   = yf.Ticker(ticker)
        raw = t.history(period=period) if period else t.history(start=start)
        if raw.empty:
            return pd.Series(dtype=float, name=ticker)
        s = raw["Close"].squeeze()
        if hasattr(s.index, "tz") and s.index.tz:
            s.index = s.index.tz_localize(None)
        return s.rename(ticker)
    except Exception:
        return pd.Series(dtype=float, name=ticker)


@st.cache_data(ttl=90, show_spinner=False)
def yf_ohlcv(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        if hasattr(df.index, "tz") and df.index.tz:
            df.index = df.index.tz_localize(None)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=90, show_spinner=False)
def yf_price_chg(ticker: str) -> Tuple[Optional[float], Optional[float]]:
    try:
        d = yf.Ticker(ticker).history(period="2d")
        if len(d) >= 2:
            c, p = float(d["Close"].iloc[-1]), float(d["Close"].iloc[-2])
            return c, (c - p) / p * 100
        elif len(d) == 1:
            return float(d["Close"].iloc[-1]), None
        return None, None
    except Exception:
        return None, None


@st.cache_data(ttl=600, show_spinner=False)
def yf_financials(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        return {
            "income_a":   getattr(t, "income_stmt",              pd.DataFrame()),
            "income_q":   getattr(t, "quarterly_income_stmt",    pd.DataFrame()),
            "balance_a":  getattr(t, "balance_sheet",            pd.DataFrame()),
            "balance_q":  getattr(t, "quarterly_balance_sheet",  pd.DataFrame()),
            "cashflow_a": getattr(t, "cashflow",                 pd.DataFrame()),
            "cashflow_q": getattr(t, "quarterly_cashflow",       pd.DataFrame()),
        }
    except Exception:
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def yf_options(ticker: str):
    try:
        t    = yf.Ticker(ticker)
        exps = t.options
        if not exps:
            return None, None, []
        ch   = t.option_chain(exps[0])
        return ch.calls, ch.puts, list(exps[:12])
    except Exception:
        return None, None, []


@st.cache_data(ttl=300, show_spinner=False)
def yf_holders(ticker: str) -> pd.DataFrame:
    try:
        return yf.Ticker(ticker).institutional_holders or pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def yf_recommendations(ticker: str) -> pd.DataFrame:
    try:
        return yf.Ticker(ticker).recommendations or pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def yf_earnings_dates(ticker: str) -> pd.DataFrame:
    try:
        return yf.Ticker(ticker).earnings_dates or pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def _normalize_yfinance(raw: dict) -> dict[str, pd.Series]:
    """Flatten yfinance annual statement DataFrames → {label: pd.Series(date → float)}."""
    sheet_row_maps = {
        "income_a": {
            "Total Revenue":                         "Revenue",
            "Gross Profit":                          "Gross Profit",
            "Operating Income":                      "Operating Income",
            "Net Income":                            "Net Income",
            "EBITDA":                                "EBITDA",
            "Research And Development":              "R&D Expense",
            "Selling General And Administration":    "SG&A",
            "Interest Expense":                      "Interest Expense",
            "Tax Provision":                         "Income Tax",
            "Basic EPS":                             "EPS Basic",
            "Diluted EPS":                           "EPS Diluted",
        },
        "balance_a": {
            "Total Assets":                          "Total Assets",
            "Total Liabilities Net Minority Interest": "Total Liabilities",
            "Stockholders Equity":                   "Stockholders Equity",
            "Cash And Cash Equivalents":             "Cash & Equivalents",
            "Long Term Debt":                        "Long-Term Debt",
            "Current Debt":                          "Short-Term Debt",
            "Retained Earnings":                     "Retained Earnings",
            "Ordinary Shares Number":                "Shares Outstanding",
        },
        "cashflow_a": {
            "Operating Cash Flow":                   "Operating Cash Flow",
            "Capital Expenditure":                   "CapEx",
            "Free Cash Flow":                        "Free Cash Flow",
            "Cash Dividends Paid":                   "Dividends Paid",
            "Depreciation And Amortization":         "D&A",
        },
    }
    result: dict[str, pd.Series] = {}
    for sheet_key, row_map in sheet_row_maps.items():
        df = raw.get(sheet_key, pd.DataFrame())
        if df is None or df.empty:
            continue
        try:
            date_index = pd.to_datetime(df.columns, errors="coerce")
            df.columns = date_index
            df = df.loc[:, ~df.columns.isna()]
        except Exception:
            continue
        for row_label, human_label in row_map.items():
            if human_label in result:
                continue
            matched = None
            if row_label in df.index:
                matched = row_label
            else:
                needle = str(row_label).lower().replace(" ", "")
                for idx_lbl in df.index:
                    if needle in str(idx_lbl).lower().replace(" ", ""):
                        matched = idx_lbl
                        break
            if matched is not None:
                s = pd.to_numeric(df.loc[matched], errors="coerce").dropna().sort_index()
                if not s.empty:
                    result[human_label] = s
    return result


# ─────────────────────────────────────────────────────────
#  UNIFIED MARKET DATA ENGINE  (main router)
# ─────────────────────────────────────────────────────────
class UnifiedMarketDataEngine:
    """
    Single public interface for all fundamental + price data.

    Routing logic:
      US ticker  → SEC Edgar primary → OpenBB secondary → yfinance tertiary
      Non-US     → OpenBB primary → yfinance tertiary
      Crypto/FX  → yfinance only
    """

    def __init__(self, ticker: str) -> None:
        self.ticker    = ticker.upper().strip()
        self.is_us     = not any(self.ticker.endswith(sfx) for sfx in NON_US_SUFFIXES)
        self.is_crypto = "-USD" in self.ticker or "-EUR" in self.ticker
        self._info: Optional[dict]              = None
        self._deep_fin: Optional[dict]          = None
        self._data_source: str                  = "yfinance"

    # ── Quote / price data (always yfinance) ───────────────
    def info(self) -> dict:
        if self._info is None:
            self._info = yf_info(self.ticker)
        return self._info

    def price_change(self) -> Tuple[Optional[float], Optional[float]]:
        return yf_price_chg(self.ticker)

    def close_series(self, period: str = "1y") -> pd.Series:
        return yf_close(self.ticker, period=period)

    def ohlcv(self, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        return yf_ohlcv(self.ticker, period=period, interval=interval)

    # ── Deep fundamentals (routed) ─────────────────────────
    def deep_financials(self) -> dict[str, pd.Series]:
        """
        Returns {label: pd.Series(date → float)} with multi-decade annual data.
        Tries sources in priority order; sets self._data_source for provenance display.
        """
        if self._deep_fin is not None:
            return self._deep_fin

        if self.is_crypto:
            self._deep_fin = {}
            return {}

        # ── Path 1: SEC Edgar (US only) ────────────────────
        if self.is_us:
            try:
                sec_data = build_sec_financials(self.ticker)
                if sec_data:
                    self._deep_fin  = sec_data
                    self._data_source = "SEC Edgar"
                    return self._deep_fin
            except Exception:
                pass

        # ── Path 2: OpenBB ─────────────────────────────────
        if _openbb_available():
            try:
                obb_raw  = _fetch_openbb_financials(self.ticker)
                obb_data = _normalize_openbb(obb_raw)
                if obb_data:
                    self._deep_fin  = obb_data
                    self._data_source = "OpenBB"
                    return self._deep_fin
            except Exception:
                pass

        # ── Path 3: yfinance fallback ──────────────────────
        try:
            yf_raw  = yf_financials(self.ticker)
            yf_data = _normalize_yfinance(yf_raw)
            self._deep_fin  = yf_data
            self._data_source = "yFinance"
            return self._deep_fin
        except Exception:
            self._deep_fin = {}
            return {}

    @property
    def data_source(self) -> str:
        return self._data_source


# ─────────────────────────────────────────────────────────
#  FRED MACRO DATA
# ─────────────────────────────────────────────────────────
@st.cache_data(ttl=3_600, show_spinner=False)
def fetch_fred(series_id: str, start: str = "1995-01-01") -> pd.Series:
    """Fetch a FRED time-series via public CSV endpoint (no API key required)."""
    try:
        from io import StringIO
        url  = FRED_CSV_URL.format(series_id=series_id)
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text), parse_dates=["DATE"], index_col="DATE")
        df.index = pd.to_datetime(df.index, errors="coerce")
        df = df[~df.index.isna()].sort_index()
        s  = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna()
        return s[s.index >= start]
    except Exception:
        return pd.Series(dtype=float, name=series_id)

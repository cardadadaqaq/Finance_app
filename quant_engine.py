"""
NAVY TERMINAL PRO  v6.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
quant_engine.py  ·  Quantitative Analytics Engine
DCF · WACC/CAPM · Monte Carlo · Technical Indicators · Vectorized Backtester
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from scipy.optimize import brentq


# ═══════════════════════════════════════════════════════
#  TECHNICAL INDICATORS
# ═══════════════════════════════════════════════════════
def sma(s: pd.Series, w: int) -> pd.Series:
    return s.rolling(w, min_periods=1).mean()

def ema(s: pd.Series, w: int) -> pd.Series:
    return s.ewm(span=w, adjust=False).mean()

def bollinger(s: pd.Series, w: int = 20, n: float = 2.0):
    mid = s.rolling(w).mean()
    std = s.rolling(w).std()
    return mid + n * std, mid, mid - n * std

def rsi(s: pd.Series, w: int = 14) -> pd.Series:
    d    = s.diff()
    gain = d.clip(lower=0).rolling(w).mean()
    loss = (-d.clip(upper=0)).rolling(w).mean()
    return 100 - 100 / (1 + gain / loss.replace(0, np.nan))

def macd(s: pd.Series, fast: int = 12, slow: int = 26, sig: int = 9):
    f = s.ewm(span=fast, adjust=False).mean()
    sl= s.ewm(span=slow, adjust=False).mean()
    m = f - sl
    sg= m.ewm(span=sig,  adjust=False).mean()
    return m, sg, m - sg

def stochastic(df: pd.DataFrame, k: int = 14, d: int = 3):
    lo  = df["Low"].rolling(k).min()
    hi  = df["High"].rolling(k).max()
    ks  = 100 * (df["Close"] - lo) / (hi - lo + 1e-10)
    return ks, ks.rolling(d).mean()

def atr(df: pd.DataFrame, w: int = 14) -> pd.Series:
    hl = df["High"] - df["Low"]
    hc = (df["High"] - df["Close"].shift()).abs()
    lc = (df["Low"]  - df["Close"].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(w).mean()

def obv(df: pd.DataFrame) -> pd.Series:
    return (np.sign(df["Close"].diff().fillna(0)) * df["Volume"]).cumsum()

def vwap(df: pd.DataFrame) -> pd.Series:
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    return (tp * df["Volume"]).cumsum() / df["Volume"].cumsum()

def ichimoku(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Full Ichimoku with Span A & B shifted +26 bars (future cloud projection)."""
    h9 = df["High"].rolling(9).max();   l9 = df["Low"].rolling(9).min()
    h26= df["High"].rolling(26).max();  l26= df["Low"].rolling(26).min()
    h52= df["High"].rolling(52).max();  l52= df["Low"].rolling(52).min()
    tk  = (h9  + l9)  / 2
    kj  = (h26 + l26) / 2
    sa  = ((tk + kj) / 2).shift(26)
    sb  = ((h52 + l52) / 2).shift(26)
    ch  = df["Close"].shift(-26)
    return {"tenkan": tk, "kijun": kj, "span_a": sa, "span_b": sb, "chikou": ch}

def fibonacci(df: pd.DataFrame) -> dict[str, float]:
    hi, lo = float(df["High"].max()), float(df["Low"].min())
    d = hi - lo
    return {
        "0.0%":  hi, "23.6%": hi - 0.236*d, "38.2%": hi - 0.382*d,
        "50.0%": hi - 0.5*d, "61.8%": hi - 0.618*d, "78.6%": hi - 0.786*d, "100%": lo,
    }

def williams_r(df: pd.DataFrame, w: int = 14) -> pd.Series:
    hi = df["High"].rolling(w).max()
    lo = df["Low"].rolling(w).min()
    return -100 * (hi - df["Close"]) / (hi - lo + 1e-10)

def cci(df: pd.DataFrame, w: int = 20) -> pd.Series:
    tp  = (df["High"] + df["Low"] + df["Close"]) / 3
    ma  = tp.rolling(w).mean()
    mad = tp.rolling(w).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    return (tp - ma) / (0.015 * mad + 1e-10)


# ═══════════════════════════════════════════════════════
#  WACC / CAPM
# ═══════════════════════════════════════════════════════
@dataclass
class WACCInputs:
    equity_value:           float
    debt_value:             float
    beta:                   float
    risk_free_rate:         float
    market_risk_premium:    float = 0.055
    tax_rate:               float = 0.21
    cost_of_debt:           float = 0.045
    cost_of_equity_override: Optional[float] = None


def compute_wacc(inp: WACCInputs) -> dict[str, float]:
    total = max(inp.equity_value + inp.debt_value, 1.0)
    we    = inp.equity_value / total
    wd    = inp.debt_value   / total
    ke    = inp.cost_of_equity_override or (inp.risk_free_rate + inp.beta * inp.market_risk_premium)
    kd_at = inp.cost_of_debt * (1 - inp.tax_rate)
    wacc  = we * ke + wd * kd_at
    return {
        "wacc": wacc, "cost_of_equity": ke, "after_tax_kd": kd_at,
        "weight_equity": we, "weight_debt": wd, "total_capital": total,
    }


# ═══════════════════════════════════════════════════════
#  MULTI-STAGE DCF
# ═══════════════════════════════════════════════════════
@dataclass
class DCFInputs:
    base_fcf:             float
    wacc:                 float
    g1:                   float   # Stage 1 growth
    g2:                   float   # Stage 2 growth
    tg:                   float   # Terminal growth
    n1:                   int     # Stage 1 years
    n2:                   int     # Stage 2 years
    shares:               float
    net_debt:             float
    tv_method:            str     = "gordon"   # "gordon" | "exit_multiple"
    exit_multiple:        float   = 12.0
    last_ebitda:          float   = 0.0


@dataclass
class DCFResult:
    fcfs_s1:        list[float] = field(default_factory=list)
    fcfs_s2:        list[float] = field(default_factory=list)
    pv_s1:          float = 0.0
    pv_s2:          float = 0.0
    terminal_value: float = 0.0
    pv_tv:          float = 0.0
    ev:             float = 0.0
    equity_value:   float = 0.0
    fair_value:     float = 0.0
    tv_pct:         float = 0.0
    total_years:    int   = 0


def run_dcf(inp: DCFInputs) -> DCFResult:
    res = DCFResult(total_years=inp.n1 + inp.n2)
    w   = inp.wacc
    cf  = inp.base_fcf

    for yr in range(1, inp.n1 + 1):
        cf *= (1 + inp.g1)
        res.fcfs_s1.append(cf)
        res.pv_s1 += cf / ((1 + w) ** yr)

    for yr in range(1, inp.n2 + 1):
        cf *= (1 + inp.g2)
        res.fcfs_s2.append(cf)
        res.pv_s2 += cf / ((1 + w) ** (inp.n1 + yr))

    total_yrs = inp.n1 + inp.n2
    if inp.tv_method == "exit_multiple" and inp.last_ebitda > 0:
        res.terminal_value = inp.last_ebitda * inp.exit_multiple
    elif w > inp.tg:
        res.terminal_value = (cf * (1 + inp.tg)) / (w - inp.tg)
    else:
        res.terminal_value = (cf * (1 + inp.tg)) / max(w - inp.tg, 0.001)

    res.pv_tv        = res.terminal_value / ((1 + w) ** total_yrs)
    res.ev           = res.pv_s1 + res.pv_s2 + res.pv_tv
    res.equity_value = res.ev - inp.net_debt
    res.fair_value   = res.equity_value / inp.shares if inp.shares > 0 else 0.0
    res.tv_pct       = res.pv_tv / res.ev * 100 if res.ev > 0 else 0.0
    return res


def dcf_sensitivity(
    base: DCFInputs,
    wacc_range: list[float],
    growth_range: list[float],
) -> pd.DataFrame:
    rows: dict[str, dict[str, str]] = {}
    for g in growth_range:
        rl = f"G {g*100:.1f}%"
        rows[rl] = {}
        for w in wacc_range:
            cl = f"W {w*100:.1f}%"
            if w <= base.tg or w <= 0:
                rows[rl][cl] = "N/A"
                continue
            mod = DCFInputs(
                base_fcf=base.base_fcf, wacc=w, g1=g, g2=g*0.6, tg=base.tg,
                n1=base.n1, n2=base.n2, shares=base.shares, net_debt=base.net_debt,
                tv_method=base.tv_method, exit_multiple=base.exit_multiple, last_ebitda=base.last_ebitda,
            )
            try:
                r = run_dcf(mod)
                rows[rl][cl] = f"${r.fair_value:,.0f}"
            except Exception:
                rows[rl][cl] = "ERR"
    return pd.DataFrame(rows).T


def monte_carlo_dcf(
    base_fcf: float, shares: float, net_debt: float,
    n1: int, n2: int, tg: float,
    wacc_mu: float, wacc_sigma: float,
    g_mu: float,    g_sigma: float,
    n_sim: int = 1000, seed: int = 42,
) -> np.ndarray:
    rng   = np.random.default_rng(seed)
    waccs = rng.normal(wacc_mu,  wacc_sigma,  n_sim).clip(0.03, 0.40)
    gs    = rng.normal(g_mu,     g_sigma,     n_sim).clip(-0.20, 1.50)
    out: list[float] = []
    for w, g in zip(waccs, gs):
        if w <= tg:
            continue
        try:
            inp = DCFInputs(
                base_fcf=base_fcf, wacc=w, g1=g, g2=g * 0.5, tg=tg,
                n1=n1, n2=n2, shares=shares, net_debt=net_debt,
            )
            r = run_dcf(inp)
            if 0 < r.fair_value < 1e7:
                out.append(r.fair_value)
        except Exception:
            pass
    return np.array(out)


def reverse_dcf(
    market_ev: float, base_fcf: float,
    wacc: float, tg: float, n1: int, n2: int,
) -> Optional[float]:
    def ev_diff(g: float) -> float:
        if wacc <= tg:
            return float("inf")
        cf = base_fcf
        pv = 0.0
        for yr in range(1, n1 + 1):
            cf *= (1 + g)
            pv += cf / ((1 + wacc) ** yr)
        for yr in range(1, n2 + 1):
            cf *= (1 + g * 0.6)
            pv += cf / ((1 + wacc) ** (n1 + yr))
        tv   = (cf * (1 + tg)) / (wacc - tg)
        pv_tv= tv / ((1 + wacc) ** (n1 + n2))
        return (pv + pv_tv) - market_ev
    try:
        return brentq(ev_diff, -0.50, 2.0, maxiter=300, xtol=1e-6)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════
#  VECTORIZED PORTFOLIO BACKTESTER
# ═══════════════════════════════════════════════════════
@dataclass
class BacktestResult:
    equity_curve:        pd.Series
    drawdown:            pd.Series
    daily_returns:       pd.Series
    total_return:        float
    cagr:                float
    ann_vol:             float
    max_dd:              float
    sharpe:              float
    sortino:             float
    calmar:              float
    omega:               float
    var95:               float
    cvar95:              float
    win_rate:            float
    beta:                Optional[float]
    alpha:               Optional[float]
    monthly_heatmap:     pd.DataFrame
    rolling_sharpe:      pd.Series
    rolling_vol:         pd.Series
    contributions:       pd.DataFrame


def run_backtest(
    prices: pd.DataFrame,
    weights: dict[str, float],
    benchmark: Optional[pd.Series],
    rf: float = 0.042,
    rebalance: str = "none",
    roll_window: int = 63,
) -> BacktestResult:
    """
    Fully vectorized portfolio backtester with optional periodic rebalancing.
    weights values are fractions (must sum to ~1.0 after normalization).
    """
    avail = {t: w for t, w in weights.items() if t in prices.columns and w > 0}
    if not avail:
        raise ValueError("No valid tickers with price data found in weights.")

    px   = prices[list(avail.keys())].dropna(how="all").ffill().bfill()
    wts  = np.array([avail[t] for t in px.columns], dtype=float)
    wts /= wts.sum()

    # ── Build portfolio equity curve ──────────────────────
    if rebalance == "none":
        norm = px / px.iloc[0]
        curve = (norm * wts).sum(axis=1)
    else:
        freq_map = {"M": "ME", "Q": "QE", "A": "YE"}
        rebal_dates = px.resample(freq_map[rebalance]).last().index
        curve = pd.Series(index=px.index, dtype=float)
        prev  = px.index[0]
        for rb in [px.index[0]] + list(rebal_dates):
            if rb not in px.index:
                idx = px.index.searchsorted(rb, side="right") - 1
                rb  = px.index[max(idx, 0)]
            seg = px.loc[prev:rb]
            if seg.empty:
                continue
            seg_norm   = seg / seg.iloc[0]
            seg_values = (seg_norm * wts).sum(axis=1)
            prev_val   = curve.get(prev, np.nan)
            if not math.isnan(prev_val):
                seg_values = seg_values * prev_val / seg_values.iloc[0]
            curve.loc[seg.index] = seg_values
            prev = rb
        curve = curve.dropna()

    # ── Core metrics ──────────────────────────────────────
    dr    = curve.pct_change().dropna()
    dr    = dr[dr.abs() < 0.5]
    years = max((curve.index[-1] - curve.index[0]).days / 365.25, 0.1)

    total_ret = float((curve.iloc[-1] / curve.iloc[0] - 1) * 100)
    cagr_val  = float(((1 + total_ret / 100) ** (1 / years) - 1) * 100)
    ann_vol   = float(dr.std() * np.sqrt(252) * 100)

    peak  = curve.cummax()
    dd    = (curve / peak - 1) * 100
    maxdd = float(dd.min())

    rf_d      = rf / 252
    excess    = dr - rf_d
    sharpe_v  = float(excess.mean() / dr.std() * np.sqrt(252)) if dr.std() > 0 else 0.0

    neg       = dr[dr < rf_d]
    dv        = float(neg.std() * np.sqrt(252)) if len(neg) > 1 else 0.0
    sortino_v = float((cagr_val / 100 - rf) / dv) if dv > 0 else 0.0

    calmar_v  = float(cagr_val / abs(maxdd)) if maxdd < 0 else float("inf")
    gains     = dr[dr > rf_d] - rf_d
    losses    = rf_d - dr[dr < rf_d]
    omega_v   = float(gains.sum() / losses.sum()) if losses.sum() > 0 else 999.0
    arr       = dr.dropna().values
    var95_v   = float(np.percentile(arr, 5) * 100)  if len(arr) > 20 else 0.0
    cvar95_v  = float(arr[arr <= np.percentile(arr, 5)].mean() * 100) if len(arr) > 20 else 0.0
    win_rate_v= float((dr > 0).mean() * 100)

    # ── Beta / Alpha ──────────────────────────────────────
    beta_v  = None
    alpha_v = None
    if benchmark is not None and len(benchmark) > 30:
        br    = benchmark.pct_change().dropna()
        br    = br[br.abs() < 0.5]
        align = pd.concat([dr, br], axis=1, join="inner").dropna()
        align.columns = ["port", "bench"]
        if len(align) > 30:
            cov = align.cov()
            vb  = float(align["bench"].var())
            if vb > 1e-10:
                beta_v   = float(cov.iloc[0, 1] / vb)
                bench_cagr = float(((benchmark.iloc[-1] / benchmark.iloc[0]) ** (1 / years) - 1))
                alpha_v  = float(cagr_val / 100 - (rf + beta_v * (bench_cagr - rf))) * 100

    # ── Monthly heatmap ───────────────────────────────────
    monthly = curve.resample("ME").last().pct_change().dropna() * 100
    monthly = monthly[monthly.abs() < 50]
    mdf     = pd.DataFrame({"Y": monthly.index.year, "M": monthly.index.month, "R": monthly.values})
    try:
        pivot = mdf.pivot(index="Y", columns="M", values="R")
        pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][:len(pivot.columns)]
    except Exception:
        pivot = pd.DataFrame()

    # ── Rolling Sharpe / Vol ──────────────────────────────
    rm = roll_window
    r_std  = dr.rolling(rm, min_periods=rm // 2).std()
    r_mean = dr.rolling(rm, min_periods=rm // 2).mean()
    r_sh   = ((r_mean - rf_d) / r_std * np.sqrt(252)).replace([np.inf, -np.inf], np.nan)
    r_vol  = r_std * np.sqrt(252) * 100

    # ── Asset contributions ───────────────────────────────
    da = px.pct_change().dropna()
    contrib_rows: list[dict] = []
    for col, w in zip(px.columns, wts):
        if col in da.columns:
            contrib_rows.append({
                "Asset":         col,
                "Weight %":      round(w * 100, 2),
                "Ann. Contrib %": round(float(da[col].mean() * 252 * w * 100), 2),
            })
    contrib_df = pd.DataFrame(contrib_rows).set_index("Asset") if contrib_rows else pd.DataFrame()

    return BacktestResult(
        equity_curve=curve, drawdown=dd, daily_returns=dr,
        total_return=total_ret, cagr=cagr_val, ann_vol=ann_vol, max_dd=maxdd,
        sharpe=sharpe_v, sortino=sortino_v, calmar=calmar_v, omega=omega_v,
        var95=var95_v, cvar95=cvar95_v, win_rate=win_rate_v,
        beta=beta_v, alpha=alpha_v,
        monthly_heatmap=pivot, rolling_sharpe=r_sh, rolling_vol=r_vol,
        contributions=contrib_df,
    )


# ── Helpers ───────────────────────────────────────────────
def fmt_bn(x) -> str:
    try:
        v = float(x)
        if abs(v) >= 1e12: return f"${v/1e12:.2f}T"
        if abs(v) >= 1e9:  return f"${v/1e9:.2f}B"
        if abs(v) >= 1e6:  return f"${v/1e6:.1f}M"
        return f"${v:,.0f}"
    except Exception:
        return str(x)

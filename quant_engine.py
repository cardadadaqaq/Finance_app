"""
╔══════════════════════════════════════════════════════════════════╗
║   NAVY TERMINAL PRO  v6.0  ·  Quantitative Engine                ║
║   DCF · WACC/CAPM · Monte Carlo · Backtest · Technicals          ║
╚══════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from scipy.optimize import brentq

warnings.filterwarnings("ignore")


# ══════════════════════════════════════════════════════════
#  FORMATTING HELPERS
# ══════════════════════════════════════════════════════════

def fmt_bn(value) -> str:
    """Format a large dollar value as T / B / M string."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "N/A"
    if v == 0:
        return "$0"
    sign = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1e12:
        return f"{sign}${v / 1e12:.2f}T"
    if v >= 1e9:
        return f"{sign}${v / 1e9:.2f}B"
    if v >= 1e6:
        return f"{sign}${v / 1e6:.2f}M"
    return f"{sign}${v:,.0f}"


# ══════════════════════════════════════════════════════════
#  DCF DATACLASSES
# ══════════════════════════════════════════════════════════

@dataclass
class DCFInputs:
    base_fcf:     float          # Base free cash flow ($)
    wacc:         float          # Weighted average cost of capital (decimal)
    g1:           float          # Stage 1 growth rate (decimal)
    g2:           float          # Stage 2 growth rate (decimal)
    tg:           float          # Terminal growth rate (decimal)
    n1:           int            # Stage 1 years
    n2:           int            # Stage 2 years
    shares:       float          # Shares outstanding
    net_debt:     float          # Net debt ($) — positive = more debt than cash
    tv_method:    str = "gordon" # "gordon" | "exit_multiple"
    exit_multiple: float = 12.0  # EV/EBITDA exit multiple (exit_multiple method)
    last_ebitda:  float = 0.0    # Last EBITDA for exit multiple method


@dataclass
class DCFResult:
    ev:           float          # Enterprise value
    equity_value: float          # Equity value (ev - net_debt)
    fair_value:   float          # Fair value per share
    pv_s1:        float          # PV of Stage 1 FCFs
    pv_s2:        float          # PV of Stage 2 FCFs
    pv_tv:        float          # PV of terminal value
    tv_pct:       float          # Terminal value as % of EV
    fcfs_s1:      list[float] = field(default_factory=list)
    fcfs_s2:      list[float] = field(default_factory=list)


@dataclass
class WACCInputs:
    equity_value:        float   # Market capitalisation ($)
    debt_value:          float   # Total debt ($)
    beta:                float   # Equity beta
    risk_free_rate:      float   # Risk-free rate (decimal)
    market_risk_premium: float   # Equity risk premium (decimal)
    tax_rate:            float   # Effective tax rate (decimal)
    cost_of_debt:        float   # Pre-tax cost of debt (decimal)


# ══════════════════════════════════════════════════════════
#  DCF ENGINE
# ══════════════════════════════════════════════════════════

def run_dcf(inp: DCFInputs) -> DCFResult:
    """Two-stage DCF model.  Supports Gordon Growth or Exit Multiple TV."""
    if inp.wacc <= inp.tg:
        raise ValueError("WACC must be strictly greater than terminal growth rate.")

    # ── Stage 1 ──────────────────────────────────────────
    fcfs_s1: list[float] = []
    pv_s1 = 0.0
    fcf = inp.base_fcf
    for yr in range(1, inp.n1 + 1):
        fcf *= (1 + inp.g1)
        fcfs_s1.append(fcf)
        pv_s1 += fcf / (1 + inp.wacc) ** yr

    # ── Stage 2 ──────────────────────────────────────────
    fcfs_s2: list[float] = []
    pv_s2 = 0.0
    for yr in range(1, inp.n2 + 1):
        fcf *= (1 + inp.g2)
        fcfs_s2.append(fcf)
        total_yr = inp.n1 + yr
        pv_s2 += fcf / (1 + inp.wacc) ** total_yr

    # ── Terminal Value ────────────────────────────────────
    total_years = inp.n1 + inp.n2
    if inp.tv_method == "exit_multiple":
        terminal_value = inp.exit_multiple * (inp.last_ebitda if inp.last_ebitda > 0 else fcf)
    else:  # gordon growth
        terminal_value = fcf * (1 + inp.tg) / (inp.wacc - inp.tg)

    pv_tv = terminal_value / (1 + inp.wacc) ** total_years

    ev           = pv_s1 + pv_s2 + pv_tv
    equity_value = ev - inp.net_debt
    fair_value   = equity_value / inp.shares if inp.shares > 0 else 0.0
    tv_pct       = (pv_tv / ev * 100) if ev > 0 else 0.0

    return DCFResult(
        ev=ev,
        equity_value=equity_value,
        fair_value=fair_value,
        pv_s1=pv_s1,
        pv_s2=pv_s2,
        pv_tv=pv_tv,
        tv_pct=tv_pct,
        fcfs_s1=fcfs_s1,
        fcfs_s2=fcfs_s2,
    )


def dcf_sensitivity(
    inp: DCFInputs,
    wacc_range: list[float],
    g1_range: list[float],
) -> pd.DataFrame:
    """
    5×5 sensitivity table of fair values across WACC × Stage-1 growth.
    Rows = WACC, Columns = Growth.
    """
    rows: list[dict] = []
    for w in wacc_range:
        row: dict[str, str] = {"WACC \\ G1": f"{w * 100:.1f}%"}
        for g in g1_range:
            try:
                mod = DCFInputs(
                    base_fcf=inp.base_fcf, wacc=w, g1=g, g2=inp.g2,
                    tg=inp.tg, n1=inp.n1, n2=inp.n2,
                    shares=inp.shares, net_debt=inp.net_debt,
                    tv_method=inp.tv_method,
                    exit_multiple=inp.exit_multiple,
                    last_ebitda=inp.last_ebitda,
                )
                res = run_dcf(mod)
                row[f"G={g * 100:.1f}%"] = f"${res.fair_value:,.0f}"
            except Exception:
                row[f"G={g * 100:.1f}%"] = "N/A"
        rows.append(row)
    df = pd.DataFrame(rows).set_index("WACC \\ G1")
    return df


def monte_carlo_dcf(
    base_fcf:    float,
    shares:      float,
    net_debt:    float,
    n1:          int,
    n2:          int,
    tg:          float,
    wacc_mu:     float,
    wacc_sigma:  float,
    g_mu:        float,
    g_sigma:     float,
    n_sim:       int = 1000,
) -> list[float]:
    """
    Run n_sim DCF simulations with normally-distributed WACC and growth inputs.
    Returns list of valid fair-value estimates.
    """
    rng        = np.random.default_rng(seed=42)
    wacc_draws = rng.normal(wacc_mu,  wacc_sigma,  n_sim)
    g1_draws   = rng.normal(g_mu,     g_sigma,     n_sim)
    g2_draws   = rng.normal(g_mu * 0.6, g_sigma,   n_sim)
    fair_vals: list[float] = []

    for i in range(n_sim):
        w  = float(np.clip(wacc_draws[i], 0.03, 0.35))
        g1 = float(np.clip(g1_draws[i],  0.00, 0.60))
        g2 = float(np.clip(g2_draws[i],  0.00, 0.40))
        if w <= tg:
            continue
        try:
            inp = DCFInputs(
                base_fcf=base_fcf, wacc=w, g1=g1, g2=g2, tg=tg,
                n1=n1, n2=n2, shares=shares, net_debt=net_debt,
            )
            res = run_dcf(inp)
            if math.isfinite(res.fair_value) and res.fair_value > 0:
                fair_vals.append(res.fair_value)
        except Exception:
            continue

    return fair_vals


def reverse_dcf(
    market_ev:  float,
    base_fcf:   float,
    wacc:       float,
    tg:         float,
    n1:         int,
    n2:         int,
    g_min:      float = -0.05,
    g_max:      float = 1.00,
) -> float | None:
    """
    Solve for the implied annual FCF growth rate that justifies the observed
    Enterprise Value, using Brent's method.  Returns None if no solution found.
    """
    def _objective(g: float) -> float:
        try:
            inp = DCFInputs(
                base_fcf=base_fcf, wacc=wacc, g1=g, g2=g * 0.6,
                tg=tg, n1=n1, n2=n2,
                shares=1.0, net_debt=0.0,
            )
            res = run_dcf(inp)
            return res.ev - market_ev
        except Exception:
            return float("nan")

    try:
        # Check sign change exists
        fa = _objective(g_min)
        fb = _objective(g_max)
        if math.isnan(fa) or math.isnan(fb):
            return None
        if fa * fb > 0:
            return None
        root = brentq(_objective, g_min, g_max, xtol=1e-6, maxiter=200)
        return float(root)
    except Exception:
        return None


# ══════════════════════════════════════════════════════════
#  WACC / CAPM ENGINE
# ══════════════════════════════════════════════════════════

def compute_wacc(inp: WACCInputs) -> dict[str, float]:
    """
    CAPM-based WACC calculation.
    Returns dict: wacc, cost_of_equity, after_tax_kd, weight_equity, weight_debt.
    """
    total = inp.equity_value + inp.debt_value
    if total <= 0:
        total = inp.equity_value if inp.equity_value > 0 else 1.0

    we = inp.equity_value / total
    wd = inp.debt_value   / total

    ke         = inp.risk_free_rate + inp.beta * inp.market_risk_premium
    kd_at      = inp.cost_of_debt * (1 - inp.tax_rate)
    wacc_value = ke * we + kd_at * wd

    return {
        "wacc":           wacc_value,
        "cost_of_equity": ke,
        "after_tax_kd":   kd_at,
        "weight_equity":  we,
        "weight_debt":    wd,
    }


# ══════════════════════════════════════════════════════════
#  PORTFOLIO BACKTEST ENGINE
# ══════════════════════════════════════════════════════════

@dataclass
class BacktestResult:
    equity_curve:    pd.Series
    daily_returns:   pd.Series
    drawdown:        pd.Series
    rolling_sharpe:  pd.Series
    monthly_heatmap: pd.DataFrame
    contributions:   pd.DataFrame
    total_return:    float
    cagr:            float
    ann_vol:         float
    max_dd:          float
    sharpe:          float
    sortino:         float
    calmar:          float
    omega:           float
    var95:           float
    cvar95:          float
    win_rate:        float
    beta:            Optional[float] = None
    alpha:           Optional[float] = None


def run_backtest(
    prices:    pd.DataFrame,
    weights:   dict[str, float],
    benchmark: Optional[pd.Series] = None,
    rf:        float = 0.042,
    rebalance: str  = "none",
) -> BacktestResult:
    """
    Vectorised portfolio backtest.

    Parameters
    ----------
    prices    : DataFrame of adjusted close prices, one column per asset.
    weights   : dict {ticker: weight_decimal}.  Must sum ≈ 1.0.
    benchmark : Optional price series for beta/alpha computation.
    rf        : Annual risk-free rate (decimal).
    rebalance : 'none' | 'M' | 'Q' | 'A'  — rebalancing frequency.
    """
    # ── Align weights to available columns ───────────────
    tickers = [t for t in weights if t in prices.columns]
    if not tickers:
        raise ValueError("No valid tickers found in price DataFrame.")

    w_raw  = np.array([weights[t] for t in tickers], dtype=float)
    w_norm = w_raw / w_raw.sum()
    w_dict = dict(zip(tickers, w_norm))

    px = prices[tickers].dropna(how="all").ffill().bfill()
    px = px.dropna(how="all")

    if len(px) < 5:
        raise ValueError("Insufficient price history for backtest.")

    # ── Compute returns ───────────────────────────────────
    ret_df = px.pct_change().dropna(how="all")

    # ── Build equity curve with optional rebalancing ──────
    if rebalance == "none":
        port_ret = (ret_df * pd.Series(w_dict)).sum(axis=1)
        equity   = (1 + port_ret).cumprod()
    else:
        equity_values = [1.0]
        current_w     = pd.Series(w_dict)
        port_rets: list[float] = []

        for i in range(1, len(ret_df)):
            row_ret  = ret_df.iloc[i]
            day_ret  = float((current_w * row_ret).sum())
            port_rets.append(day_ret)
            equity_values.append(equity_values[-1] * (1 + day_ret))

            # Check if rebalance day
            current_date = ret_df.index[i]
            prev_date    = ret_df.index[i - 1]
            should_rebalance = False
            if rebalance == "M" and current_date.month != prev_date.month:
                should_rebalance = True
            elif rebalance == "Q" and current_date.quarter != prev_date.quarter:
                should_rebalance = True
            elif rebalance == "A" and current_date.year != prev_date.year:
                should_rebalance = True

            if should_rebalance:
                current_w = pd.Series(w_dict)
            else:
                # Drift weights
                new_prices = (1 + row_ret)
                current_w  = current_w * new_prices
                total_w    = current_w.sum()
                if total_w > 0:
                    current_w = current_w / total_w

        port_ret = pd.Series([0.0] + port_rets, index=ret_df.index[:len(port_rets) + 1])
        equity   = pd.Series(equity_values, index=ret_df.index[:len(equity_values)])

    equity.name    = "Portfolio"
    port_ret.name  = "DailyReturn"
    port_ret_clean = port_ret.dropna()

    # ── Core statistics ───────────────────────────────────
    n_years      = max((equity.index[-1] - equity.index[0]).days / 365.25, 0.01)
    total_ret    = float((equity.iloc[-1] / equity.iloc[0] - 1) * 100)
    cagr_val     = float(((1 + total_ret / 100) ** (1 / n_years) - 1) * 100)
    ann_vol_val  = float(port_ret_clean.std() * np.sqrt(252) * 100)
    rf_daily     = (1 + rf) ** (1 / 252) - 1

    # ── Drawdown series ───────────────────────────────────
    rolling_max = equity.cummax()
    drawdown    = ((equity / rolling_max) - 1) * 100
    max_dd_val  = float(drawdown.min())

    # ── Sharpe ───────────────────────────────────────────
    excess_ret   = port_ret_clean - rf_daily
    ann_excess   = float(excess_ret.mean() * 252)
    sharpe_val   = ann_excess / (port_ret_clean.std() * np.sqrt(252)) if port_ret_clean.std() > 0 else float("nan")

    # ── Sortino ───────────────────────────────────────────
    neg_ret      = port_ret_clean[port_ret_clean < rf_daily]
    downside_std = float(neg_ret.std() * np.sqrt(252)) if len(neg_ret) > 1 else float("nan")
    sortino_val  = ann_excess / downside_std if (not math.isnan(downside_std) and downside_std > 0) else float("nan")

    # ── Calmar ───────────────────────────────────────────
    calmar_val = (cagr_val / abs(max_dd_val)) if max_dd_val < 0 else float("inf")

    # ── Omega ratio ──────────────────────────────────────
    threshold  = rf_daily
    gains      = port_ret_clean[port_ret_clean > threshold] - threshold
    losses     = threshold - port_ret_clean[port_ret_clean <= threshold]
    omega_val  = float(gains.sum() / losses.sum()) if losses.sum() > 0 else 999.0

    # ── VaR and CVaR (95%) ───────────────────────────────
    var95_val  = float(np.percentile(port_ret_clean.values, 5) * 100)
    cvar_mask  = port_ret_clean <= np.percentile(port_ret_clean.values, 5)
    cvar95_val = float(port_ret_clean[cvar_mask].mean() * 100) if cvar_mask.sum() > 0 else var95_val

    # ── Win rate ─────────────────────────────────────────
    win_rate_val = float((port_ret_clean > 0).mean() * 100)

    # ── Rolling Sharpe (63-day) ───────────────────────────
    roll_mean = port_ret_clean.rolling(63).mean()
    roll_std  = port_ret_clean.rolling(63).std()
    rolling_sharpe = (roll_mean / roll_std * np.sqrt(252)).fillna(0)

    # ── Monthly returns heatmap ───────────────────────────
    monthly_ret = port_ret_clean.copy()
    monthly_ret.index = pd.to_datetime(monthly_ret.index)
    monthly_pct = monthly_ret.resample("ME").apply(lambda x: (1 + x).prod() - 1) * 100
    try:
        heatmap = monthly_pct.groupby([
            monthly_pct.index.year,
            monthly_pct.index.month,
        ]).first().unstack()
        heatmap.columns = [
            pd.Timestamp(2000, m, 1).strftime("%b")
            for m in heatmap.columns
        ]
    except Exception:
        heatmap = pd.DataFrame()

    # ── Asset contributions ───────────────────────────────
    contribs: list[dict] = []
    for t in tickers:
        if t not in px.columns:
            continue
        t_ret  = px[t].pct_change().dropna()
        t_tot  = float((1 + t_ret).prod() - 1) * 100
        t_vol  = float(t_ret.std() * np.sqrt(252) * 100)
        t_cont = t_tot * w_dict[t]
        contribs.append({
            "Asset":       t,
            "Weight %":    f"{w_dict[t] * 100:.1f}%",
            "Return %":    f"{t_tot:+.2f}%",
            "Volatility %":f"{t_vol:.2f}%",
            "Contribution %": f"{t_cont:+.2f}%",
        })
    contributions_df = pd.DataFrame(contribs).set_index("Asset") if contribs else pd.DataFrame()

    # ── Beta and Alpha vs benchmark ───────────────────────
    beta_val  = None
    alpha_val = None
    if benchmark is not None and not benchmark.empty:
        try:
            bench_ret = benchmark.pct_change().dropna()
            aligned   = port_ret_clean.align(bench_ret, join="inner")
            p_ret_a, b_ret_a = aligned[0], aligned[1]
            if len(p_ret_a) > 20 and b_ret_a.std() > 0:
                cov  = np.cov(p_ret_a.values, b_ret_a.values)
                beta_val  = float(cov[0, 1] / np.var(b_ret_a.values))
                bench_ann = float(b_ret_a.mean() * 252 * 100)
                alpha_val = float(cagr_val - (rf * 100 + beta_val * (bench_ann - rf * 100)))
        except Exception:
            pass

    return BacktestResult(
        equity_curve   = equity,
        daily_returns  = port_ret_clean,
        drawdown       = drawdown,
        rolling_sharpe = rolling_sharpe,
        monthly_heatmap= heatmap,
        contributions  = contributions_df,
        total_return   = total_ret,
        cagr           = cagr_val,
        ann_vol        = ann_vol_val,
        max_dd         = max_dd_val,
        sharpe         = sharpe_val   if not math.isnan(sharpe_val)  else 0.0,
        sortino        = sortino_val  if not math.isnan(sortino_val) else 0.0,
        calmar         = calmar_val,
        omega          = omega_val,
        var95          = var95_val,
        cvar95         = cvar95_val,
        win_rate       = win_rate_val,
        beta           = beta_val,
        alpha          = alpha_val,
    )


# ══════════════════════════════════════════════════════════
#  TECHNICAL INDICATORS
# ══════════════════════════════════════════════════════════

def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta  = close.diff()
    gain   = delta.clip(lower=0)
    loss   = (-delta).clip(lower=0)
    avg_g  = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_l  = loss.ewm(com=period - 1, min_periods=period).mean()
    rs     = avg_g / avg_l.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))


def macd(
    close:      pd.Series,
    fast:       int = 12,
    slow:       int = 26,
    signal_win: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD line, Signal line, Histogram."""
    ema_fast   = close.ewm(span=fast,   adjust=False).mean()
    ema_slow   = close.ewm(span=slow,   adjust=False).mean()
    macd_line  = ema_fast - ema_slow
    signal     = macd_line.ewm(span=signal_win, adjust=False).mean()
    histogram  = macd_line - signal
    return macd_line, signal, histogram


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range (requires OHLC DataFrame)."""
    high  = df["High"]
    low   = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low  - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(com=period - 1, min_periods=period).mean()


def fibonacci(df: pd.DataFrame, lookback: int = 120) -> dict[str, float]:
    """
    Fibonacci retracement levels from the highest high and lowest low
    over the last `lookback` bars.
    """
    window = df.tail(lookback)
    high   = float(window["High"].max())
    low    = float(window["Low"].min())
    diff   = high - low
    levels = {
        "0.0%":   high,
        "23.6%":  high - 0.236 * diff,
        "38.2%":  high - 0.382 * diff,
        "50.0%":  high - 0.500 * diff,
        "61.8%":  high - 0.618 * diff,
        "78.6%":  high - 0.786 * diff,
        "100.0%": low,
    }
    return levels


def stochastic(
    df:     pd.DataFrame,
    k_win:  int = 14,
    d_win:  int = 3,
) -> tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator %K and %D."""
    lowest_low   = df["Low"].rolling(k_win).min()
    highest_high = df["High"].rolling(k_win).max()
    denom        = (highest_high - lowest_low).replace(0, float("nan"))
    k = ((df["Close"] - lowest_low) / denom) * 100
    d = k.rolling(d_win).mean()
    return k, d


def williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Williams %R oscillator."""
    hh = df["High"].rolling(period).max()
    ll = df["Low"].rolling(period).min()
    denom = (hh - ll).replace(0, float("nan"))
    return ((hh - df["Close"]) / denom) * -100


def cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Commodity Channel Index."""
    tp    = (df["High"] + df["Low"] + df["Close"]) / 3
    ma    = tp.rolling(period).mean()
    mad   = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    return (tp - ma) / (0.015 * mad.replace(0, float("nan")))


def obv(df: pd.DataFrame) -> pd.Series:
    """On-Balance Volume."""
    direction = np.sign(df["Close"].diff().fillna(0))
    vol       = df["Volume"].fillna(0)
    return (direction * vol).cumsum()


def vwap(df: pd.DataFrame) -> pd.Series:
    """Volume-Weighted Average Price (intraday reset not applicable for daily bars)."""
    tp      = (df["High"] + df["Low"] + df["Close"]) / 3
    vol     = df["Volume"].fillna(0)
    cum_tp  = (tp * vol).cumsum()
    cum_vol = vol.cumsum().replace(0, float("nan"))
    return cum_tp / cum_vol


def ichimoku(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Ichimoku Cloud components."""
    high = df["High"]
    low  = df["Low"]

    tenkan  = (high.rolling(9).max()  + low.rolling(9).min())  / 2
    kijun   = (high.rolling(26).max() + low.rolling(26).min()) / 2
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
    chikou   = df["Close"].shift(-26)

    return {
        "tenkan":   tenkan,
        "kijun":    kijun,
        "senkou_a": senkou_a,
        "senkou_b": senkou_b,
        "chikou":   chikou,
    }


def bollinger_bands(
    close:  pd.Series,
    period: int   = 20,
    std:    float = 2.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands: upper, middle (SMA), lower."""
    middle = close.rolling(period).mean()
    sigma  = close.rolling(period).std()
    upper  = middle + std * sigma
    lower  = middle - std * sigma
    return upper, middle, lower

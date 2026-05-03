"""Yahoo Finance adapter — covers KR/US/JP/CN/HK/TW/VN tickers (with appropriate suffix).

Provides:
- price_history(ticker, period, interval) → list of OHLCV dicts
- quote(ticker) → latest snapshot
- financials(ticker) → income/balance/cashflow as dicts
- earnings_history(ticker) → list of past earnings dates with EPS surprise

Free, no API key. Subject to Yahoo rate limits.
"""

from __future__ import annotations

from typing import Any

from .base import cache_get, cache_put

try:
    import yfinance as yf
except Exception:  # pragma: no cover
    yf = None


def _require():
    if yf is None:
        raise RuntimeError("yfinance not installed. Run: pip install yfinance")


def price_history(ticker: str, period: str = "6mo", interval: str = "1d") -> list[dict]:
    _require()
    cache_key = f"{ticker}-{period}-{interval}"
    if (cached := cache_get("yf_history", cache_key, max_age_seconds=3600)) is not None:
        return cached
    df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
    rows = [
        {
            "date": idx.isoformat(),
            "open": float(row.Open),
            "high": float(row.High),
            "low": float(row.Low),
            "close": float(row.Close),
            "volume": int(row.Volume) if row.Volume == row.Volume else 0,
        }
        for idx, row in df.iterrows()
    ]
    cache_put("yf_history", cache_key, rows)
    return rows


def quote(ticker: str) -> dict[str, Any]:
    _require()
    if (cached := cache_get("yf_quote", ticker, max_age_seconds=60)) is not None:
        return cached
    t = yf.Ticker(ticker)
    last = currency = market_cap = year_high = year_low = None
    try:
        info = t.fast_info
        last = float(info.last_price) if info.last_price else None
        currency = info.currency
        market_cap = getattr(info, "market_cap", None)
        year_high = getattr(info, "year_high", None)
        year_low = getattr(info, "year_low", None)
    except Exception:
        pass
    if last is None:
        # Fallback: last close from intraday history (1d/1m → 5d/1d).
        for period, interval in (("1d", "1m"), ("5d", "1d")):
            try:
                df = t.history(period=period, interval=interval, auto_adjust=False)
                if not df.empty:
                    last = float(df["Close"].iloc[-1])
                    break
            except Exception:
                continue
    if last is None:
        raise RuntimeError(f"yfinance quote failed for {ticker} (network or ticker invalid)")
    out = {
        "ticker": ticker,
        "last": last,
        "currency": currency,
        "market_cap": market_cap,
        "year_high": year_high,
        "year_low": year_low,
    }
    cache_put("yf_quote", ticker, out)
    return out


def financials(ticker: str) -> dict[str, Any]:
    _require()
    if (cached := cache_get("yf_financials", ticker, max_age_seconds=86400)) is not None:
        return cached
    t = yf.Ticker(ticker)
    out = {
        "income_quarterly": _df_to_records(t.quarterly_financials),
        "balance_quarterly": _df_to_records(t.quarterly_balance_sheet),
        "cashflow_quarterly": _df_to_records(t.quarterly_cashflow),
        "income_annual": _df_to_records(t.financials),
    }
    cache_put("yf_financials", ticker, out)
    return out


def earnings_history(ticker: str) -> list[dict]:
    _require()
    if (cached := cache_get("yf_earnings", ticker, max_age_seconds=86400)) is not None:
        return cached
    t = yf.Ticker(ticker)
    df = t.earnings_history if hasattr(t, "earnings_history") else None
    if df is None or df.empty:
        return []
    rows = []
    for idx, row in df.iterrows():
        rows.append({
            "date": str(idx),
            "eps_estimate": float(row.get("epsEstimate", 0) or 0),
            "eps_actual": float(row.get("epsActual", 0) or 0),
            "surprise_pct": float(row.get("surprisePercent", 0) or 0),
        })
    cache_put("yf_earnings", ticker, rows)
    return rows


def _df_to_records(df) -> list[dict]:
    if df is None or df.empty:
        return []
    out = []
    for col in df.columns:
        rec = {"period": str(col)}
        for idx in df.index:
            rec[str(idx)] = _safe_float(df.loc[idx, col])
        out.append(rec)
    return out


def _safe_float(v) -> float | None:
    try:
        f = float(v)
        return None if f != f else f
    except Exception:
        return None


if __name__ == "__main__":
    import json
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "quote"
    ticker = sys.argv[2] if len(sys.argv) > 2 else "AAPL"
    if cmd == "history":
        print(json.dumps(price_history(ticker), default=str, indent=2))
    elif cmd == "financials":
        print(json.dumps(financials(ticker), default=str, indent=2))
    elif cmd == "earnings":
        print(json.dumps(earnings_history(ticker), default=str, indent=2))
    else:
        print(json.dumps(quote(ticker), default=str, indent=2))

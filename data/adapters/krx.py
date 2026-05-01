"""KRX adapter — uses pykrx (free, no key) for KOSPI/KOSDAQ data.

Provides:
- index_history(name, start, end)
- foreign_net(start, end) — daily foreign net buying KRW
- ohlcv(ticker, start, end) — OHLCV for KR ticker (6-digit)
"""

from __future__ import annotations

from .base import cache_get, cache_put

try:
    from pykrx import stock
except Exception:
    stock = None


def _require():
    if stock is None:
        raise RuntimeError("pykrx not installed. Run: pip install pykrx")


def index_history(name: str = "코스피", start: str = "20240101", end: str | None = None) -> list[dict]:
    """name: 코스피, 코스닥, KRX100, etc."""
    _require()
    import datetime as dt
    end = end or dt.date.today().strftime("%Y%m%d")
    cache_key = f"{name}-{start}-{end}"
    if (cached := cache_get("krx_index", cache_key, max_age_seconds=3600)) is not None:
        return cached
    df = stock.get_index_ohlcv(start, end, _index_code(name))
    rows = [
        {"date": idx.strftime("%Y-%m-%d"), "open": float(r.시가), "high": float(r.고가),
         "low": float(r.저가), "close": float(r.종가), "volume": int(r.거래량)}
        for idx, r in df.iterrows()
    ]
    cache_put("krx_index", cache_key, rows)
    return rows


def _index_code(name: str) -> str:
    return {"코스피": "1001", "코스닥": "2001", "KRX100": "1035"}.get(name, "1001")


def ohlcv(ticker: str, start: str, end: str | None = None) -> list[dict]:
    _require()
    import datetime as dt
    end = end or dt.date.today().strftime("%Y%m%d")
    cache_key = f"{ticker}-{start}-{end}"
    if (cached := cache_get("krx_ohlcv", cache_key, max_age_seconds=3600)) is not None:
        return cached
    df = stock.get_market_ohlcv(start, end, ticker)
    rows = [
        {"date": idx.strftime("%Y-%m-%d"), "open": float(r.시가), "high": float(r.고가),
         "low": float(r.저가), "close": float(r.종가), "volume": int(r.거래량)}
        for idx, r in df.iterrows()
    ]
    cache_put("krx_ohlcv", cache_key, rows)
    return rows


def foreign_net(start: str, end: str | None = None, market: str = "KOSPI") -> list[dict]:
    _require()
    import datetime as dt
    end = end or dt.date.today().strftime("%Y%m%d")
    cache_key = f"{market}-{start}-{end}"
    if (cached := cache_get("krx_foreign", cache_key, max_age_seconds=3600)) is not None:
        return cached
    df = stock.get_market_trading_value_by_date(start, end, market, "외국인")
    rows = [{"date": idx.strftime("%Y-%m-%d"), "net_krw": float(r.iloc[0])} for idx, r in df.iterrows()]
    cache_put("krx_foreign", cache_key, rows)
    return rows


if __name__ == "__main__":
    import json
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "index"
    if cmd == "ohlcv":
        print(json.dumps(ohlcv(sys.argv[2], sys.argv[3]), indent=2))
    elif cmd == "foreign":
        print(json.dumps(foreign_net(sys.argv[2]), indent=2))
    else:
        print(json.dumps(index_history(), indent=2))

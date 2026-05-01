"""Unified OHLCV fetcher — picks the best free source per ticker.

Heuristic:
- 6-digit (e.g., 005930) or .KS/.KQ → pykrx for cleaner KR data
- Anything else → yfinance (handles US, JP .T, CN .SS/.SZ, HK .HK, TW .TW, VN .VN)

Usage:
    python -m data.adapters.ohlcv 005930 1d
    python -m data.adapters.ohlcv AAPL 1w
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys

from . import krx, yfinance_adapter

KR_NUM = re.compile(r"^\d{6}$")


def is_kr(ticker: str) -> bool:
    if KR_NUM.match(ticker):
        return True
    if ticker.endswith(".KS") or ticker.endswith(".KQ"):
        return True
    return False


def fetch(ticker: str, timeframe: str = "1d", lookback_days: int = 252) -> list[dict]:
    end = dt.date.today()
    start = end - dt.timedelta(days=lookback_days * 1.5)
    if is_kr(ticker):
        ticker6 = ticker.split(".")[0]
        try:
            return krx.ohlcv(ticker6, start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))
        except RuntimeError:
            pass
    period_map = {"1d": "1y", "1w": "5y", "1m": "10y"}
    interval_map = {"1d": "1d", "1w": "1wk", "1m": "1mo"}
    return yfinance_adapter.price_history(
        ticker, period=period_map.get(timeframe, "1y"), interval=interval_map.get(timeframe, "1d")
    )


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    timeframe = sys.argv[2] if len(sys.argv) > 2 else "1d"
    print(json.dumps(fetch(ticker, timeframe), default=str, indent=2))

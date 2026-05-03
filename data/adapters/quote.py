"""Unified current-quote router.

Routing:
- KR (6-digit / .KS / .KQ) → Naver Finance (near real-time KRW)
- Everything else        → Yahoo Finance (US/JP/CN/HK/TW/VN)

Output schema (all sources):
    {ticker, last, change, change_pct, currency, source, asof}

Usage:
    python -m data.adapters.quote 005930
    python -m data.adapters.quote AAPL
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

from . import naver, yfinance_adapter

_KR_NUM = re.compile(r"^\d{6}$")


def _is_kr(ticker: str) -> bool:
    return bool(_KR_NUM.match(ticker)) or ticker.endswith((".KS", ".KQ"))


def quote(ticker: str) -> dict[str, Any]:
    if _is_kr(ticker):
        return naver.quote(ticker)
    yq = yfinance_adapter.quote(ticker)
    return {
        "ticker": ticker,
        "last": yq.get("last"),
        "change": None,
        "change_pct": None,
        "currency": yq.get("currency"),
        "source": "yahoo",
        "asof": None,
        "market_cap": yq.get("market_cap"),
        "year_high": yq.get("year_high"),
        "year_low": yq.get("year_low"),
    }


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    print(json.dumps(quote(ticker), ensure_ascii=False, indent=2))

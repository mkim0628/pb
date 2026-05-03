"""Naver Finance adapter — current quote for KR tickers (KOSPI/KOSDAQ).

Uses Naver's public polling endpoint when available, falls back to scraping the
item main page. Both are unauthenticated; latency is ~real-time during market hours
(체결 후 수 초).

Ticker normalization:
    "005930", "005930.KS", "005930.KQ" → "005930"
"""

from __future__ import annotations

import json
import re
from typing import Any

from .base import cache_get, cache_put

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
_KR6 = re.compile(r"^\d{6}$")


def _require():
    if requests is None:
        raise RuntimeError("requests not installed. Run: pip install requests")


def _to_code(ticker: str) -> str:
    code = ticker.split(".")[0]
    if not _KR6.match(code):
        raise ValueError(f"Not a Korean 6-digit code: {ticker}")
    return code


def quote(ticker: str) -> dict[str, Any]:
    """Latest snapshot for a KR ticker.

    Returns: {ticker, last, change, change_pct, currency, source, asof}
    """
    _require()
    code = _to_code(ticker)
    if (cached := cache_get("naver_quote", code, max_age_seconds=15)) is not None:
        return cached

    out = _polling_quote(code) or _html_quote(code)
    if out is None:
        raise RuntimeError(f"Naver quote failed for {ticker}")
    out["ticker"] = ticker
    cache_put("naver_quote", code, out)
    return out


def _polling_quote(code: str) -> dict[str, Any] | None:
    """Polling JSON endpoint — fastest, used by Naver's own widgets."""
    url = f"https://polling.finance.naver.com/api/realtime/domestic/stock/{code}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=5)
        if r.status_code != 200:
            return None
        body = r.json()
    except (requests.RequestException, json.JSONDecodeError, ValueError):
        return None

    datas = (
        body.get("datas")
        or body.get("result", {}).get("areas", [{}])[0].get("datas")
        or []
    )
    if not datas:
        return None
    d = datas[0]
    last = _num(d.get("nv") or d.get("closePrice"))
    if last is None:
        return None
    return {
        "last": last,
        "change": _num(d.get("cv") or d.get("compareToPreviousClosePrice")),
        "change_pct": _num(d.get("cr") or d.get("fluctuationsRatio")),
        "currency": "KRW",
        "source": "naver_polling",
        "asof": d.get("aa") or d.get("localTradedAt"),
    }


_PRICE_PATTERNS = [
    # <dl class="blind"> ... <dd>현재가 70,000 전일대비 ...
    re.compile(r"현재가\s*([0-9,]+)"),
    # og:title sometimes includes price
    re.compile(r'property="og:title"\s+content="[^"]*?([0-9,]+)\s*원'),
]
_CHANGE_PATTERN = re.compile(
    r"전일대비\s*(상승|하락|보합)?\s*([0-9,]+)\s*(?:플러스|마이너스)?\s*([0-9.]+)\s*퍼센트"
)


def _html_quote(code: str) -> dict[str, Any] | None:
    """Fallback: parse finance.naver.com/item/main.naver page."""
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=5)
        if r.status_code != 200:
            return None
        html = r.text
    except requests.RequestException:
        return None

    last = None
    for pat in _PRICE_PATTERNS:
        m = pat.search(html)
        if m:
            last = _num(m.group(1))
            break
    if last is None:
        return None

    change = change_pct = None
    if (m := _CHANGE_PATTERN.search(html)) is not None:
        sign = -1 if m.group(1) == "하락" else 1
        change = sign * (_num(m.group(2)) or 0)
        change_pct = sign * (_num(m.group(3)) or 0)
    return {
        "last": last,
        "change": change,
        "change_pct": change_pct,
        "currency": "KRW",
        "source": "naver_html",
        "asof": None,
    }


def _num(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace(",", "").replace("+", "").strip()
    if not s or s == "-":
        return None
    try:
        return float(s)
    except ValueError:
        return None


if __name__ == "__main__":
    import sys
    code = sys.argv[1] if len(sys.argv) > 1 else "005930"
    print(json.dumps(quote(code), ensure_ascii=False, indent=2))

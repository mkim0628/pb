"""DART (전자공시) adapter — Korean disclosures.

Free public OpenAPI but requires an API key from https://opendart.fss.or.kr.
Falls back gracefully when key is missing.
"""

from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import urlopen

from .base import cache_get, cache_put, env

BASE = "https://opendart.fss.or.kr/api"


def disclosures(corp_code: str, begin: str, end: str) -> list[dict]:
    """List of recent disclosures for a corp_code (8-digit DART code).

    Args:
        corp_code: DART corp_code (different from stock ticker)
        begin/end: YYYYMMDD strings
    """
    api_key = env("DART_API_KEY")
    if not api_key:
        return [{"_warning": "Set DART_API_KEY env var to fetch live data"}]

    cache_key = f"{corp_code}-{begin}-{end}"
    if (cached := cache_get("dart_disclosure", cache_key, max_age_seconds=3600)) is not None:
        return cached

    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bgn_de": begin,
        "end_de": end,
        "page_count": 100,
    }
    url = f"{BASE}/list.json?{urlencode(params)}"
    with urlopen(url, timeout=15) as r:
        data = json.loads(r.read().decode())
    items = data.get("list", [])
    cache_put("dart_disclosure", cache_key, items)
    return items


def financial_statement(corp_code: str, year: int, report_code: str = "11014") -> dict:
    """Quarterly/annual report. report_code: 11013=Q1, 11012=Q2, 11014=Q3, 11011=annual."""
    api_key = env("DART_API_KEY")
    if not api_key:
        return {"_warning": "Set DART_API_KEY env var"}

    cache_key = f"{corp_code}-{year}-{report_code}"
    if (cached := cache_get("dart_fs", cache_key, max_age_seconds=86400)) is not None:
        return cached

    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(year),
        "reprt_code": report_code,
    }
    url = f"{BASE}/fnlttSinglAcnt.json?{urlencode(params)}"
    with urlopen(url, timeout=15) as r:
        data = json.loads(r.read().decode())
    cache_put("dart_fs", cache_key, data)
    return data


if __name__ == "__main__":
    import sys
    corp = sys.argv[1] if len(sys.argv) > 1 else "00126380"
    print(json.dumps(disclosures(corp, "20250101", "20251231"), ensure_ascii=False, indent=2))

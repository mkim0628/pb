"""FRED adapter — US macro series (free, requires FRED API key for high volume but works without via CSV download).

Series of interest:
- DGS10, DGS2 — Treasury yields
- DFF — Fed funds effective rate
- DTWEXBGS — Dollar index broad
- CPIAUCSL — CPI
- UNRATE — Unemployment
"""

from __future__ import annotations

import csv
import io
from urllib.request import urlopen

from .base import cache_get, cache_put, env

CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"


def series(series_id: str) -> list[dict]:
    if (cached := cache_get("fred", series_id, max_age_seconds=86400)) is not None:
        return cached
    api_key = env("FRED_API_KEY")
    if api_key:
        url = (
            f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}"
            f"&api_key={api_key}&file_type=json"
        )
        import json
        with urlopen(url, timeout=15) as r:
            data = json.loads(r.read().decode())
        rows = [
            {"date": o["date"], "value": float(o["value"])}
            for o in data.get("observations", [])
            if o.get("value") not in (".", "")
        ]
    else:
        with urlopen(CSV_URL.format(series=series_id), timeout=15) as r:
            text = r.read().decode()
        reader = csv.DictReader(io.StringIO(text))
        rows = []
        for r0 in reader:
            v = r0.get(series_id) or list(r0.values())[1]
            if v in (".", "", None):
                continue
            try:
                rows.append({"date": r0["DATE"] if "DATE" in r0 else list(r0.values())[0], "value": float(v)})
            except (TypeError, ValueError):
                continue
    cache_put("fred", series_id, rows)
    return rows


if __name__ == "__main__":
    import json as _json
    import sys
    sid = sys.argv[1] if len(sys.argv) > 1 else "DGS10"
    print(_json.dumps(series(sid)[-30:], indent=2))

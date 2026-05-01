"""Base interface and small helpers for data adapters.

All adapters return plain dicts/lists (JSON-serializable) so agents can ingest them
without provider-specific objects leaking through.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

CACHE_ROOT = Path(__file__).resolve().parent.parent / "cache"
CACHE_ROOT.mkdir(parents=True, exist_ok=True)


def cache_path(namespace: str, key: str) -> Path:
    safe = key.replace("/", "_").replace(":", "_")
    p = CACHE_ROOT / namespace
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{safe}.json"


def cache_get(namespace: str, key: str, max_age_seconds: int) -> Any | None:
    path = cache_path(namespace, key)
    if not path.exists():
        return None
    age = dt.datetime.now().timestamp() - path.stat().st_mtime
    if age > max_age_seconds:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def cache_put(namespace: str, key: str, value: Any) -> None:
    path = cache_path(namespace, key)
    path.write_text(json.dumps(value, default=str, ensure_ascii=False), encoding="utf-8")


def env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)

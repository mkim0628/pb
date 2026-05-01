#!/usr/bin/env python3
"""Print tickers from portfolio.yaml that have earnings today.

Used by run_scheduled.sh to fire /earnings-alert for the right names.
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.adapters import yfinance_adapter  # noqa: E402


def main() -> int:
    portfolio_path = ROOT / "portfolio.yaml"
    if not portfolio_path.exists():
        return 0
    data = yaml.safe_load(portfolio_path.read_text(encoding="utf-8")) or {}
    tickers = {h["ticker"] for h in data.get("holdings", [])}
    tickers |= {w["ticker"] for w in data.get("watchlist", [])}

    today = dt.date.today()
    for t in sorted(tickers):
        try:
            history = yfinance_adapter.earnings_history(t)
            if any(_is_today(item.get("date"), today) for item in history):
                print(t)
        except Exception as e:
            print(f"# error {t}: {e}", file=sys.stderr)
    return 0


def _is_today(date_str, today) -> bool:
    if not date_str:
        return False
    try:
        d = dt.datetime.fromisoformat(str(date_str).split()[0]).date()
        return d == today
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main())

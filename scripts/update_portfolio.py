#!/usr/bin/env python3
"""Append-only portfolio ledger.

Records buy/sell/cash/watchlist events to portfolio.yaml. Holdings are derived
from the ledger (lots-based FIFO for realized P&L).

Usage:
    python scripts/update_portfolio.py buy --account kr-main --ticker 005930.KS \
        --name "삼성전자" --qty 100 --price 70000 --date 2024-03-15

    python scripts/update_portfolio.py sell --account kr-main --ticker 005930.KS \
        --qty 50 --price 75000 --date 2024-09-20

    python scripts/update_portfolio.py cash --account kr-main --delta 5000000

    python scripts/update_portfolio.py watch --ticker NVDA --note "AI 사이클"

    python scripts/update_portfolio.py show
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from collections import defaultdict, deque
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_PATH = ROOT / "portfolio.yaml"


def load() -> dict:
    with PORTFOLIO_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save(data: dict) -> None:
    with PORTFOLIO_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def today() -> str:
    return dt.date.today().isoformat()


def derive_holdings(ledger: list[dict]) -> list[dict]:
    """Replay ledger to compute current holdings (FIFO lots)."""
    lots: dict[tuple[str, str], deque] = defaultdict(deque)
    for ev in ledger:
        if ev["op"] == "buy":
            key = (ev["account"], ev["ticker"])
            lots[key].append({
                "qty": ev["qty"],
                "price": ev["price"],
                "date": ev["date"],
                "name": ev.get("name"),
            })
        elif ev["op"] == "sell":
            key = (ev["account"], ev["ticker"])
            remaining = ev["qty"]
            while remaining > 0 and lots[key]:
                lot = lots[key][0]
                if lot["qty"] <= remaining:
                    remaining -= lot["qty"]
                    lots[key].popleft()
                else:
                    lot["qty"] -= remaining
                    remaining = 0

    holdings = []
    for (account, ticker), lot_queue in lots.items():
        if not lot_queue:
            continue
        name = next((l.get("name") for l in lot_queue if l.get("name")), None)
        holdings.append({
            "account": account,
            "ticker": ticker,
            "name": name,
            "lots": [
                {"qty": l["qty"], "price": l["price"], "date": l["date"]}
                for l in lot_queue
            ],
        })
    holdings.sort(key=lambda h: (h["account"], h["ticker"]))
    return holdings


def cmd_buy(args):
    data = load()
    event = {
        "op": "buy",
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "account": args.account,
        "ticker": args.ticker,
        "name": args.name,
        "qty": args.qty,
        "price": args.price,
        "date": args.date or today(),
        "fee": args.fee,
    }
    data.setdefault("ledger", []).append(event)
    data["holdings"] = derive_holdings(data["ledger"])
    save(data)
    print(f"[buy] {args.ticker} {args.qty}@{args.price} on {event['date']} → {args.account}")


def cmd_sell(args):
    data = load()
    event = {
        "op": "sell",
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "account": args.account,
        "ticker": args.ticker,
        "qty": args.qty,
        "price": args.price,
        "date": args.date or today(),
        "fee": args.fee,
    }
    data.setdefault("ledger", []).append(event)
    data["holdings"] = derive_holdings(data["ledger"])
    save(data)
    print(f"[sell] {args.ticker} {args.qty}@{args.price} on {event['date']} ← {args.account}")


def cmd_cash(args):
    data = load()
    found = False
    for c in data.setdefault("cash", []):
        if c["account"] == args.account:
            c["amount"] = c.get("amount", 0) + args.delta
            found = True
            break
    if not found:
        data["cash"].append({"account": args.account, "amount": args.delta, "currency": args.currency or "KRW"})
    data.setdefault("ledger", []).append({
        "op": "cash",
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "account": args.account,
        "delta": args.delta,
        "note": args.note,
    })
    save(data)
    print(f"[cash] {args.account} delta={args.delta:+}")


def cmd_watch(args):
    data = load()
    wl = data.setdefault("watchlist", [])
    if any(w.get("ticker") == args.ticker for w in wl):
        print(f"[watch] {args.ticker} already in watchlist")
        return
    wl.append({"ticker": args.ticker, "added": today(), "note": args.note})
    save(data)
    print(f"[watch] +{args.ticker}")


def cmd_unwatch(args):
    data = load()
    wl = data.setdefault("watchlist", [])
    before = len(wl)
    data["watchlist"] = [w for w in wl if w.get("ticker") != args.ticker]
    save(data)
    print(f"[unwatch] {args.ticker} ({before - len(data['watchlist'])} removed)")


def cmd_profile(args):
    data = load()
    profile = data.setdefault("profile", {})
    if args.risk:
        profile["risk_tolerance"] = args.risk
    if args.horizon is not None:
        profile["horizon_years"] = args.horizon
    if args.currency:
        profile["base_currency"] = args.currency
    save(data)
    print(f"[profile] {profile}")


def cmd_show(_args):
    data = load()
    print(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Portfolio ledger updater")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("buy")
    b.add_argument("--account", required=True)
    b.add_argument("--ticker", required=True)
    b.add_argument("--name")
    b.add_argument("--qty", type=float, required=True)
    b.add_argument("--price", type=float, required=True)
    b.add_argument("--date")
    b.add_argument("--fee", type=float, default=0)
    b.set_defaults(func=cmd_buy)

    s = sub.add_parser("sell")
    s.add_argument("--account", required=True)
    s.add_argument("--ticker", required=True)
    s.add_argument("--qty", type=float, required=True)
    s.add_argument("--price", type=float, required=True)
    s.add_argument("--date")
    s.add_argument("--fee", type=float, default=0)
    s.set_defaults(func=cmd_sell)

    c = sub.add_parser("cash")
    c.add_argument("--account", required=True)
    c.add_argument("--delta", type=float, required=True)
    c.add_argument("--currency")
    c.add_argument("--note")
    c.set_defaults(func=cmd_cash)

    w = sub.add_parser("watch")
    w.add_argument("--ticker", required=True)
    w.add_argument("--note")
    w.set_defaults(func=cmd_watch)

    u = sub.add_parser("unwatch")
    u.add_argument("--ticker", required=True)
    u.set_defaults(func=cmd_unwatch)

    pr = sub.add_parser("profile")
    pr.add_argument("--risk", choices=["conservative", "moderate", "aggressive"])
    pr.add_argument("--horizon", type=int)
    pr.add_argument("--currency")
    pr.set_defaults(func=cmd_profile)

    sh = sub.add_parser("show")
    sh.set_defaults(func=cmd_show)

    return p


if __name__ == "__main__":
    args = build_parser().parse_args()
    args.func(args)

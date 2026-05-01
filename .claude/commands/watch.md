---
description: Add a ticker to watchlist (or remove with --remove).
argument-hint: "[ticker] [--note '...'] [--remove]"
---

Parse `$ARGUMENTS`:
- If `--remove`: `python scripts/update_portfolio.py unwatch --ticker <T>`
- Else: `python scripts/update_portfolio.py watch --ticker <T> [--note "..."]`

Confirm with one line.

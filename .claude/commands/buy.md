---
description: Record a buy transaction in portfolio.yaml. Validates required fields, then runs scripts/update_portfolio.py.
argument-hint: "[ticker] [qty] [price] [account] [date?]"
---

You are recording a buy. Parse `$ARGUMENTS` and call `python scripts/update_portfolio.py buy` with the right flags.

## Required fields
- `ticker` (e.g., 005930.KS, AAPL, 9988.HK)
- `qty` (number of shares)
- `price` (per share, in account currency)
- `account` (must match an `id` from `portfolio.yaml`)

## Optional
- `date` (defaults to today, format YYYY-MM-DD)
- `name` (Korean/English name; lookup if missing)
- `fee`

## Steps
1. Read `portfolio.yaml` to validate `account` exists. If not, list valid account ids and ask.
2. If any required field is missing, ask the user — DO NOT guess price/qty.
3. Run:
   ```
   python scripts/update_portfolio.py buy --account <id> --ticker <T> --qty <Q> --price <P> --date <D> [--name "..."] [--fee F]
   ```
4. Print the resulting holding line and the running average cost.
5. Briefly summarize: "OK, recorded {qty} {ticker} @ {price} on {date} → {account}. Updated holding: {avg_cost}."

Be terse. No analysis here.

---
description: Record a sell transaction in portfolio.yaml with FIFO realized P&L.
argument-hint: "[ticker] [qty] [price] [account] [date?]"
---

You are recording a sell. Parse `$ARGUMENTS`.

## Required
- ticker, qty, price, account

## Steps
1. Read `portfolio.yaml`; verify the user actually holds at least `qty` of `ticker` in `account`. If not, error out — never invent a position.
2. Run:
   ```
   python scripts/update_portfolio.py sell --account <id> --ticker <T> --qty <Q> --price <P> --date <D> [--fee F]
   ```
3. Compute realized P&L using FIFO (script handles ledger; you compute display):
   - cost basis from the consumed lots
   - realized P&L = (price - avg_consumed_cost) × qty - fee
4. Output:
   ```
   매도 기록: {qty} {ticker} @ {price}
   실현 손익: {profit:+,} ({pct:+.1%}) — {account}
   잔여 수량: {remaining}
   ```
5. Note any tax implications briefly (e.g., "해외주식 양도세 대상, YTD 실현이익 X원").

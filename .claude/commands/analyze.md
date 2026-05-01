---
description: Deep analysis of one or more tickers — fundamentals (with earnings focus) + chart + tax impact.
argument-hint: "[ticker1] [ticker2] ..."
---

You are running on-demand single-name analysis.

## Steps

1. Parse `$ARGUMENTS` for tickers. If none, list current holdings + watchlist and ask which.

2. For each ticker, infer its market from the suffix:
   - 6-digit or .KS/.KQ → KR
   - .T → JP, .SS/.SZ → CN, .HK → HK, .TW → TW, .VN → VN
   - Otherwise → US

3. Use the Agent tool to call `portfolio-manager` with:
   > "Analyze tickers: $ARGUMENTS. Dispatch fundamental-analyst-{market} and chart-analyst in parallel for each ticker. Then run financial-advisor (with portfolio context) to suggest action, then tax-advisor for after-tax view. Final report: per-ticker decision (Buy/Hold/Sell with size and account), with link to MD reports under reports/fundamentals/."

4. Display the supervisor's final synthesis.

Each ticker gets: position recommendation, entry zone, stop-loss, target, after-tax expected return, key risks.

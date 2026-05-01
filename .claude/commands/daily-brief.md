---
description: Daily pre-market brief — runs automatically via cron, but can also be invoked manually.
---

Use the Agent tool with `subagent_type: "portfolio-manager"`:

> "Daily brief mode (scheduled). Read portfolio.yaml. Dispatch market-analyst-{kr,us,asia} ONLY for markets present in holdings. For each currently-held ticker with an earnings event in the next 5 trading days, dispatch fundamental-analyst-{market}. Save reports/daily/<DATE>.md with:
>   - Holdings P&L day-over-day (use yfinance quote)
>   - Market summary per region (1 paragraph each)
>   - Today's calendar items affecting holdings
>   - Top 3 actionable signals (no recommendation, just signals)
> Length: under 1 page. No financial-advisor or tax-advisor calls — this is informational."

Save the result to `reports/daily/<YYYY-MM-DD>.md` and print path.

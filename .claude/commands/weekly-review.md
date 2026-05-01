---
description: Weekly Friday review — full pipeline run with strategy + tax. Saves to reports/weekly/.
---

Use the Agent tool with `subagent_type: "portfolio-manager"`:

> "Weekly review mode (scheduled). Read portfolio.yaml. Run full pipeline:
>   1. All relevant market-analysts in parallel
>   2. fundamental-analyst for each holding (parallel batches per market)
>   3. chart-analyst for each holding (1w timeframe)
>   4. financial-advisor with portfolio context — produce 3 scenarios
>   5. tax-advisor — re-rank by after-tax
> Save full report to reports/weekly/<YYYY-MM-DD>.md including:
>   - Week-over-week portfolio performance
>   - Material news per holding
>   - Earnings calendar for next 2 weeks (★ critical)
>   - Recommended actions with after-tax numbers
>   - Alerts: positions hitting stop-loss / target / overbought"

Save and print path.

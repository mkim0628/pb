---
description: Run when an earnings event happens for a holding — produces post-earnings analysis with surprise vs reaction comparison to history.
argument-hint: "[ticker]"
---

Triggered automatically by `scripts/run_scheduled.sh` when an earnings date is detected.

Use the Agent tool with `subagent_type: "portfolio-manager"`:

> "Earnings event for $ARGUMENTS. Dispatch fundamental-analyst-{market} with explicit instruction to:
>   - Pull just-released numbers
>   - Compute actual vs consensus surprise (EPS and revenue)
>   - Compare to historical surprise→reaction pattern (e.g., 'past +5% beats produced avg T+5 +3.2%')
>   - Forecast T+1/T+5/T+20 based on history conditional on this surprise
>   - Highlight guidance changes
>   - Update risks
> Then chart-analyst for entry/exit zones if user holds. Then financial-advisor for action recommendation, then tax-advisor for after-tax view if action involves trade.
> Save reports/events/<TICKER>-earnings-<YYYY-MM-DD>.md."

Push the result inline (this is event-driven, user wants to see it now).

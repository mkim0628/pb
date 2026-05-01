---
description: Today's market brief, focused on the user's holdings and watchlist. Dispatches market-analysts in parallel.
argument-hint: "[--scope kr|us|asia|all] (default: all relevant to portfolio)"
---

You are running an on-demand market brief.

## Steps

1. **Invoke the supervisor**: use the Agent tool with `subagent_type: "portfolio-manager"` and prompt:
   > "Run a market brief for $ARGUMENTS. Read portfolio.yaml; dispatch market-analyst-{kr,us,asia} in parallel only for markets present in the portfolio (or all if scope=all). Save MD reports to reports/market/. Return a 1-page summary highlighting what matters for my holdings and watchlist."

2. The supervisor will call analysts in parallel and synthesize.

3. Display the supervisor's final output to the user.

Do NOT do the analysis yourself — delegate to the supervisor.

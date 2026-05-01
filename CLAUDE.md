# Stock Advisor — Multi-Agent System

Korean-resident global stock advisory. 10 agents across 3 tiers, optimizing **after-tax** returns.

## Architecture

```
Tier 3:  portfolio-manager (supervisor, user entry point)
Tier 2:  financial-advisor → tax-advisor (chained)
Tier 1:  market-analyst-{kr,us,asia}
         fundamental-analyst-{kr,us,asia}    (★ earnings-focused full fundamentals)
         chart-analyst                        (market-agnostic)
```

Inter-agent comm is JSON (`schemas/`). User-facing reports are Markdown (`reports/`).

## On-demand commands

| Command | Purpose |
|---|---|
| `/brief [scope]` | Today's market brief, holdings-focused |
| `/analyze <tickers>` | Per-ticker deep dive (fundamentals + chart + tax) |
| `/strategy` | Portfolio-wide 3-scenario plan (after-tax ranked) |
| `/tax-sim <plan>` | What-if tax simulation |
| `/rebalance [target]` | Rebalancing trades minimizing tax cost |

Portfolio updates:
| Command | Purpose |
|---|---|
| `/buy <ticker> <qty> <price> <account>` | Record buy |
| `/sell <ticker> <qty> <price> <account>` | Record sell (FIFO realized P&L) |
| `/cash <account> <delta>` | Adjust cash |
| `/watch <ticker>` | Watchlist add/remove |
| `/portfolio` | Summary |
| `/profile` | Update risk/horizon/currency |

Free-form natural language also works ("어제 삼성전자 100주 7만원에 샀어") — supervisor parses and routes to `scripts/update_portfolio.py`.

## Scheduled (cron)

See `scripts/run_scheduled.sh` for crontab examples.

| Frequency | Command | Output |
|---|---|---|
| Daily 08:00 (Mon-Fri) | `/daily-brief` | `reports/daily/<DATE>.md` |
| Friday 18:00 | `/weekly-review` | `reports/weekly/<DATE>.md` |
| Quarterly | `/quarterly-tax` | `reports/quarterly/<YYYY-Q#>.md` |
| Daily 07:30 (event) | `/earnings-alert <T>` | `reports/events/<T>-earnings-<DATE>.md` |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # optional API keys
python scripts/update_portfolio.py show
```

## File map

```
portfolio.yaml              # ledger + profile (single source of truth)
schemas/                    # 5 inter-agent JSON schemas
data/
  tax_rules/                # KR/US/JP/CN/HK/TW/VN tax YAML
  adapters/                 # yfinance, krx (pykrx), fred, dart, ohlcv (unified)
  cache/                    # adapter caches (gitignored)
.claude/
  agents/                   # 10 agent definitions
  commands/                 # 13 slash commands
scripts/
  update_portfolio.py       # /buy /sell /cash /watch /profile backend
  run_scheduled.sh          # cron entry point
  detect_earnings.py        # finds holdings with earnings today
reports/                    # generated artifacts (gitignored)
  market/  fundamentals/  charts/
  strategy/  tax/
  daily/  weekly/  quarterly/  events/
```

## Design principles

1. **After-tax decisions**: financial-advisor proposes → tax-advisor re-ranks by `after_tax_return_pct`. Always show post-tax numbers.
2. **Portfolio-aware**: every recommendation reads `portfolio.yaml` (current allocation, cash, profile, ledger).
3. **Surprise-reaction patterns**: fundamental analysts compute historical buckets ("when surprise > +5%, T+5 avg +3.2% with 75% hit ratio") so users see how price has reacted to past surprises.
4. **Conflict surfacing**: when chart and fundamentals disagree, expose the conflict rather than averaging.
5. **Free-tier first**: yfinance + pykrx + FRED CSV. Optional keys (DART, Finnhub) for richer data.
6. **Append-only ledger**: `portfolio.yaml.ledger[]` is auditable; holdings are derived (FIFO).

## Adding a new market

1. Create `data/tax_rules/<CODE>.yaml`
2. Extend `market_report.json` enum
3. Add a region branch in `market-analyst-asia.md` (or split into a new analyst if scope is large)
4. Update `data/adapters/ohlcv.py` heuristic if ticker suffix is non-Yahoo

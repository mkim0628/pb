---
description: Show current portfolio summary (holdings, cash, allocation by market/sector).
---

Read `portfolio.yaml` and produce a concise markdown summary:

## Steps
1. `python scripts/update_portfolio.py show` to load the structured state
2. Compute (in base_currency = `profile.base_currency`):
   - Total value = Σ(qty × current_price) + cash. Use `data/adapters/yfinance_adapter.py quote` for prices.
   - Allocation by market (KR/US/JP/CN/HK/...)
   - Top 5 positions by weight
   - Cash %

## Output
```
## 포트폴리오 ({asof})
- 총 평가금액: ₩{total} ({base_currency})
- 현금 비중: {cash_pct}%

### 시장별 비중
| Market | Value | % |

### 보유 종목 (Top 5 by weight)
| Ticker | Name | Qty | Avg Cost | Last | P&L | Weight |

### 워치리스트
- {ticker} — {note}
```

Keep it under 30 lines. If the user wants drilldown, they'll ask.

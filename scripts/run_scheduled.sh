#!/usr/bin/env bash
# Cron-friendly runner for scheduled reports.
#
# Example crontab entries (add via `crontab -e`):
#
#   # Daily pre-market brief (Mon-Fri 08:00 KST)
#   0 8 * * 1-5  cd /home/user/pb && ./scripts/run_scheduled.sh daily
#
#   # Weekly review (Fri 18:00 KST)
#   0 18 * * 5   cd /home/user/pb && ./scripts/run_scheduled.sh weekly
#
#   # Quarterly tax (1st day of Mar/Jun/Sep/Dec, 09:00)
#   0 9 1 3,6,9,12 * cd /home/user/pb && ./scripts/run_scheduled.sh quarterly-tax
#
#   # Earnings event detector (every weekday 07:30; checks holdings for today's earnings)
#   30 7 * * 1-5 cd /home/user/pb && ./scripts/run_scheduled.sh earnings-check

set -euo pipefail

KIND="${1:-daily}"
LOG_DIR="${LOG_DIR:-./logs}"
mkdir -p "$LOG_DIR"
DATE=$(date +%F)

case "$KIND" in
  daily)
    claude -p "/daily-brief" >>"$LOG_DIR/daily-$DATE.log" 2>&1
    ;;
  weekly)
    claude -p "/weekly-review" >>"$LOG_DIR/weekly-$DATE.log" 2>&1
    ;;
  quarterly-tax)
    claude -p "/quarterly-tax" >>"$LOG_DIR/quarterly-$DATE.log" 2>&1
    ;;
  earnings-check)
    # Detect any holding with earnings today, then trigger /earnings-alert per ticker.
    python scripts/detect_earnings.py | while read -r TICKER; do
      [ -z "$TICKER" ] && continue
      claude -p "/earnings-alert $TICKER" >>"$LOG_DIR/earnings-$DATE.log" 2>&1
    done
    ;;
  *)
    echo "Unknown kind: $KIND" >&2
    exit 1
    ;;
esac

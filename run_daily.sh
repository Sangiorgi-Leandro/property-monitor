#!/bin/bash

# Performs daily real estate scraping

# Go to the script directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR" || exit 1

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
  source venv/bin/activate
fi

# Main Python script path
SCRIPT="src/property_monitor/main.py"

# Log directory and file
LOG_DIR="output"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/log_scrape.log"

# Run the script with logging
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting scraping..." >> "$LOG_FILE"

if python "$SCRIPT" >> "$LOG_FILE" 2>&1; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Scraping completed successfully." >> "$LOG_FILE"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error during scraping!" >> "$LOG_FILE"
fi

# ===================================================
# Usage with cron (optional):
# Note: crontab is available only on Unix/Linux/macOS systems.
# If you use Windows, consider alternatives like Task Scheduler.
#
# To run the script every day at 7:00 AM,
# open the crontab with:
#     crontab -e
# and add this line (modify the path accordingly):
#
# 0 7 * * * /absolute/path/property-monitor/run_daily.sh
#
# ===================================================

name: Scheduled Scrape

on:
  schedule:
    - cron: '0 * * * *'   # setiap jam pada menit ke-0 (UTC). Ubah sesuai kebutuhan.
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run scraper once
        env:
          MODE: "once"
          RATE_LIMIT_INTERVAL_SECONDS: "1.0"  # atur sesuai rate limit
          PER_PAGE: "50"
          PAGE: "1"
        run: |
          python -m src.main

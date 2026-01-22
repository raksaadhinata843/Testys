# coin-scraper-pipeline

Simple pipeline untuk mengambil data koin dari CoinGecko dan menyimpannya secara lokal.  
Sumber data: https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1&sparkline=false

Fitur awal:
- Fetch dengan retry dan timeout
- Validasi data menggunakan Pydantic
- Penyimpanan lokal (JSON)
- Unit tests untuk model
- GitHub Actions workflow untuk menjalankan test

Quickstart:
1. Buat virtualenv dan install dependency:
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Jalankan test:
   ```
   pytest -q
   ```
3. Jalankan scraper:
   ```
   python -m src.main
   ```

Struktur:
```
coin-scraper-pipeline/
├── .github/
│   └── workflows/
│       └── scrape_coin.yml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── scraper.py
│   ├── models.py
│   └── database.py
├── tests/
│   ├── __init__.py
│   └── test_models.py
├── data/
├── .gitignore
├── requirements.txt
└── README.md
```

Catatan:
- API rate limits harus diperhatikan jika membuat job periodic. Tambahkan backoff/ratelimit lebih lanjut bila perlu.
- Untuk production, ganti penyimpanan file lokal ke database (Postgres, SQLite, dsb.) sesuai kebutuhan.

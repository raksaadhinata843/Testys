# coin-scraper-pipeline

Pipeline otomatis untuk mengambil data cryptocurrency dari CoinGecko API dan menyimpannya secara lokal (JSON atau SQLite).

**API Source:** https://api.coingecko.com/api/v3/coins/markets

## Fitur

- ✅ **Fetch dengan Retry & Timeout** — Menggunakan `tenacity` untuk retry otomatis jika ada kegagalan network
- ✅ **Rate Limiting** — Pembatasan kecepatan request untuk menghindari throttling API
- ✅ **Validasi Data** — Pydantic models untuk memastikan integritas data (termasuk validasi timestamp)
- ✅ **Logging Komprehensif** — Log ke console dan file (`logs/coin_scraper.log`) dengan rotating file handler
- ✅ **Dua Opsi Penyimpanan** — Simpan ke JSON (`data/coins.json`) atau SQLite (`data/coins.db`)
- ✅ **Scheduler Lokal** — APScheduler untuk menjalankan scraping berkala (mode daemon)
- ✅ **CI/CD Testing** — GitHub Actions untuk menjalankan unit tests
- ✅ **Scheduled CI/CD Job** — GitHub Actions workflow untuk menjalankan scraping terjadwal di cloud

## Quick Start

### 1. Setup Environment

```bash
git clone <repo-url>
cd coin-scraper-pipeline
python -m venv .venv
source .venv/bin/activate  # atau .venv\Scripts\activate di Windows
pip install -r requirements.txt
```

### 2. Jalankan Sekali (One-shot)

#### Simpan ke JSON:
```bash
MODE=once STORAGE=file python -m src.main
```
Output: `data/coins.json`

#### Simpan ke SQLite:
```bash
MODE=once STORAGE=sqlite python -m src.main
```
Output: `data/coins.db`

### 3. Jalankan dengan Scheduler Lokal (Daemon Mode)

```bash
MODE=daemon SCHEDULE_MINUTES=60 STORAGE=sqlite python -m src.main
```

Scraper akan berjalan setiap 60 menit. Tekan `Ctrl+C` untuk stop.

### 4. Jalankan Unit Tests

```bash
pytest -q
```

## Konfigurasi (Environment Variables)

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `MODE` | `daemon` | `once` (jalankan sekali) atau `daemon` (scheduler berkelanjutan) |
| `STORAGE` | `file` | `file` (JSON) atau `sqlite` (SQLite database) |
| `SCHEDULE_MINUTES` | `60` | Interval scraping dalam menit (hanya untuk mode daemon) |
| `RATE_LIMIT_INTERVAL_SECONDS` | `1.0` | Jeda minimal antar request (detik) — naikkan untuk reduce beban API |
| `PER_PAGE` | `50` | Jumlah koin per halaman API |
| `PAGE` | `1` | Halaman mana yang diambil |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FILE` | `logs/coin_scraper.log` | Path file log |

### Contoh Konfigurasi Konservatif (Hemat Beban API)

```bash
export RATE_LIMIT_INTERVAL_SECONDS=2.0      # 2 detik antar request
export SCHEDULE_MINUTES=120                 # Scraping setiap 2 jam
export STORAGE=sqlite                       # Gunakan SQLite (lebih efisien)
export LOG_LEVEL=INFO

MODE=daemon python -m src.main
```

## Struktur Folder

```
coin-scraper-pipeline/
├── .github/
│   └── workflows/
│       ├── scrape_coin.yml                 # CI/CD testing
│       └── scheduled_scrape.yml            # Scheduled scraping (GitHub Actions)
├── src/
│   ├── __init__.py
│   ├── main.py                             # Entry point & scheduler
│   ├── scraper.py                          # API fetching + retry + rate limiting
│   ├── models.py                           # Pydantic schemas & validasi
│   ├── database.py                         # Penyimpanan JSON
│   ├── database_sqlite.py                  # Penyimpanan SQLite
│   └── logger.py                           # Konfigurasi logging
├── tests/
│   ├── __init__.py
│   └── test_models.py                      # Unit tests
├── data/                                   # Output folder (ignored by git)
│   ├── coins.json                          # Output JSON (jika STORAGE=file)
│   ├── coins.db                            # Output SQLite (jika STORAGE=sqlite)
│   └── logs/
│       └── coin_scraper.log                # Log file
├── .gitignore
├── requirements.txt
└── README.md
```

## Penjelasan Komponen Utama

### Logging (`src/logger.py`)

Logger otomatis disiapkan dengan dua handler:
- **Console** — Log real-time ke terminal
- **File** — Rotating file handler (max 5MB per file, simpan 3 backup)

Ubah level logging atau path file via env vars:
```bash
LOG_LEVEL=DEBUG LOG_FILE=custom_logs/app.log MODE=once STORAGE=file python -m src.main
```

### Rate Limiting (`src/scraper.py`)

SimpleRateLimiter memastikan minimal jarak antar request:

```python
# Default: 1 detik antar request (30 req/menit max)
RATE_LIMIT_INTERVAL_SECONDS=1.0

# Untuk reduce beban (contoh: 2 detik = 30 req/menit max)
RATE_LIMIT_INTERVAL_SECONDS=2.0

# Untuk API yang sangat ketat (contoh: 5 detik = 12 req/menit max)
RATE_LIMIT_INTERVAL_SECONDS=5.0
```

Strategi: naikkan nilai ini jika API memberikan `429 Too Many Requests` atau rate limit error.

### Penyimpanan Data

#### Option 1: JSON (`data/coins.json`)
- Format: Array of coin objects (JSON)
- Cocok untuk: Data kecil, export manual, simple pipeline
- Kecepatan: Cepat untuk < 500 koin
- Ukuran file: ~50KB untuk 50 koin

#### Option 2: SQLite (`data/coins.db`)
- Format: Database terstruktur dengan upsert berdasarkan coin ID
- Cocok untuk: Data besar, query kompleks, historical tracking
- Kecepatan: Optimal untuk > 500 koin
- Fitur: Timestamp update otomatis, raw JSON backup per row

**Bagaimana memilih?**
- Gunakan **file (JSON)** jika hanya scraping 50 koin sekali-sekali.
- Gunakan **SQLite** jika scraping berkala (scheduler) atau ingin query historical data.

### Scheduler

#### Mode Lokal (APScheduler)

Jalankan dengan `MODE=daemon`:
```bash
SCHEDULE_MINUTES=60 STORAGE=sqlite MODE=daemon python -m src.main
```

Scheduler akan:
- Jalankan scraping setiap 60 menit
- Otomatis restart setelah kegagalan (dengan logging)
- Graceful shutdown saat menerima SIGINT/SIGTERM (Ctrl+C)

#### Mode CI/CD (GitHub Actions)

File: `.github/workflows/scheduled_scrape.yml`

Jalankan scraping di GitHub Actions terjadwal (default: setiap jam UTC):
```yaml
on:
  schedule:
    - cron: '0 * * * *'   # 0 menit setiap jam
```

Ubah cron schedule sesuai kebutuhan:
- `0 */4 * * *` — Setiap 4 jam
- `0 0 * * *` — Setiap hari jam 00:00 UTC
- `*/30 * * * *` — Setiap 30 menit

**Catatan:** GitHub Actions ada fair use policy. Untuk sering-sering (< 1 jam interval), lebih baik gunakan scheduler lokal atau external job scheduler (celery, airflow, etc).

## Troubleshooting

### Error: `429 Too Many Requests`
- Naikkan `RATE_LIMIT_INTERVAL_SECONDS` (contoh: dari 1.0 ke 2.0 atau 5.0)
- Atau kurangi `PER_PAGE` atau hanya fetch halaman tertentu

### Database Lock (SQLite)
- SQLite hanya support 1 writer sekaligus. Jika scheduler berjalan, jangan jalankan scraper manual di instance yang sama.
- Solusi: Gunakan PostgreSQL atau MySQL jika perlu concurrent writes.

### Log File Terlalu Besar
- Default: max 5MB per file (3 backups disimpan)
- Ubah di `src/logger.py` parameter `maxBytes` dan `backupCount`

### Validasi Data Gagal
- Jika ada item dari API yang tidak sesuai schema, item itu akan di-skip (dengan warning log)
- Ubah tolerance validasi di `src/models.py` atau di scraper's parse logic

## Development & Testing

### Menjalankan Tests

```bash
# Quick test
pytest -q

# Verbose output
pytest -v

# Test dengan coverage
pytest --cov=src
```

### Format Code (Optional)

```bash
pip install black isort
black src/ tests/
isort src/ tests/
```

## Production Deployment

Untuk deployment production:

1. **Gunakan SQLite atau dedicated database** (`src/database_sqlite.py` atau upgrade ke Postgres)
2. **Simpan logs di persistent storage** atau centralized logging (ELK, Datadog, etc)
3. **Monitor scheduler health** — setup alert jika job gagal berkali-kali
4. **Backup data berkala** — khususnya jika menggunakan SQLite, backup `data/coins.db` secara regular
5. **Use environment files** — simpan secrets & config di `.env` (jangan commit)

Contoh `.env`:
```
SCHEDULE_MINUTES=60
RATE_LIMIT_INTERVAL_SECONDS=1.5
STORAGE=sqlite
LOG_LEVEL=INFO
```

Load di script atau gunakan `python-dotenv`:
```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()
```

## FAQ

**Q: Apakah data hasil scraping disimpan di repo?**
A: Tidak. File di folder `data/` di-ignore oleh `.gitignore`. Jika ingin commit data, hapus rule `data/*` dari `.gitignore` (tapi tidak direkomendasikan untuk dataset besar).

**Q: Bisakah saya fetch multiple pages sekaligus?**
A: Belum ada loop otomatis. Tapi kamu bisa modifikasi `src/main.py` untuk loop dari PAGE=1 sampai PAGE=N (dengan rate limiting di antara requests). Beri tahu jika mau saya bikinin.

**Q: Gimana cara export data dari SQLite ke CSV?**
A: Gunakan perintah SQLite CLI atau library `pandas`:
```python
import pandas as pd
df = pd.read_sql_table('coins', 'sqlite:///data/coins.db')
df.to_csv('coins.csv', index=False)
```

**Q: Bisa integrate dengan Telegram/Slack untuk notifikasi?**
A: Ya, tambahkan handler logging atau callback di `src/main.py` untuk send alert ke webhook/bot. Tanya jika mau contohnya.

## License

MIT

## Kontribusi

Issues & PRs welcome!

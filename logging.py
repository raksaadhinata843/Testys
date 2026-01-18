import pandas as pd
import numpy as np
import logging
import io

# Konfigurasi Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("etl_process.log"), # Simpan ke file
        logging.StreamHandler()                # Muncul di terminal
    ]
)
logger = logging.getLogger(__name__)

# --- 1. EXTRACT ---
def extract(source_type='csv', **kwargs):
    logger.info(f"Memulai proses EXTRACT dari: {source_type}")
    try:
        if source_type == 'csv':
            df = pd.read_csv(kwargs.get('path'))
        # elif source_type == 'api': ...
        logger.info(f"Extract berhasil. Mendapatkan {len(df)} baris.")
        return df
    except Exception as e:
        logger.error(f"Gagal saat Extract: {str(e)}")
        raise

# --- 2. VALIDATE ---
def validate(df, mode='soft'):
    logger.info("Memulai proses VALIDATE...")
    if df.empty:
        logger.warning("DataFrame yang diterima kosong!")
        return df

    null_count = df.isnull().sum().sum()
    if null_count > 0:
        msg = f"Ditemukan {null_count} nilai kosong."
        if mode == 'strict':
            logger.critical(f"Validasi Gagal (Strict Mode): {msg}")
            raise ValueError(msg)
        else:
            logger.warning(f"Validasi (Soft Mode): {msg}")
    
    logger.info("Validasi selesai tanpa error kritikal.")
    return df

# --- 3. TRANSFORM ---
def transform(df, mode='calculate'):
    logger.info(f"Memulai proses TRANSFORM mode: {mode}")
    try:
        if mode == 'calculate':
            # Contoh operasi NumPy
            logger.debug("Melakukan perhitungan vektor dengan NumPy")
            # df['val'] = np.log1p(df['val']) 
            pass
        logger.info("Transformasi selesai.")
        return df
    except Exception as e:
        logger.error(f"Gagal saat Transform: {str(e)}")
        raise

# --- 4. LOAD ---
def load(df, mode='local'):
    logger.info(f"Memulai proses LOAD ke: {mode}")
    try:
        if mode == 'local':
            df.to_csv("output.csv", index=False)
            logger.info("Data berhasil disimpan ke output.csv")
        # elif mode == 'cloud': ...
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Gagal saat Load: {str(e)}")
        raise

# --- 5. THE RUNNER (PIPELINE) ---
def run_etl():
    logger.info("=== ETL PIPELINE DIMULAI ===")
    try:
        data = extract(source_type='csv', path='data.csv')
        data = validate(data, mode='soft')
        data = transform(data)
        load(data)
        logger.info("=== ETL PIPELINE SELESAI DENGAN SUKSES ===")
    except Exception as e:
        logger.critical(f"!!! ETL PIPELINE BERHENTI KARENA ERROR: {str(e)}")

if __name__ == "__main__":
    run_etl()

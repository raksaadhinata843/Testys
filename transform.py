import pandas as pd
import numpy as np
from typing import List, Dict, Any

def normalize_crypto_data(valid_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Menormalisasi data pasar kripto yang sudah divalidasi.
    Mengembalikan Pandas DataFrame yang bersih dan siap pakai.
    """
    df = pd.DataFrame(valid_data)
    print(f"[NORMALIZER] Memulai normalisasi pada {len(df)} baris data.")

    # Normalisasi 1: Standardisasi format simbol (uppercase)
    df['symbol'] = df['symbol'].str.upper().str.strip()
    print("[NORMALIZER] Simbol dikonversi menjadi UPPERCASE.")
    
    # Normalisasi 2: Menangani nilai hilang (NaN) di kolom numerik
    # Mengisi total volume yang NaN (jika lolos validator tapi masih NaN) dengan 0
    df['total_volume'] = df['total_volume'].fillna(0)
    print("[NORMALIZER] NaN pada Volume diisi dengan 0.")

    # Normalisasi 3: Pembulatan (Rounding) untuk konsistensi presentasi
    df['current_price'] = df['current_price'].round(4) # 4 desimal untuk presisi harga
    df['price_change_percentage_24h'] = df['price_change_percentage_24h'].round(2) # 2 desimal untuk persentase
    print("[NORMALIZER] Harga dan Persentase dibulatkan.")

    # Normalisasi 4: Konversi tipe data tanggal ke objek datetime yang siap diolah
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    print("[NORMALIZER] last_updated dikonversi ke tipe datetime.")

    # Normalisasi 5: Konversi tipe data numerik yang tepat
    df['market_cap_rank'] = df['market_cap_rank'].astype(np.int16)
    df['market_cap'] = df['market_cap'].astype(np.int64) # Market cap bisa sangat besar

    print("[NORMALIZER] Normalisasi selesai. Data siap digunakan.")

    return df



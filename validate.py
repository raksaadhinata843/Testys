import pandas as pd
import numpy as np
from typing import List, Dict, Any

def validate_crypto_values(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Memvalidasi nilai data pasar kripto.
    Mengembalikan list of dictionaries yang valid saja.
    """
    df = pd.DataFrame(data)
    initial_count = len(df)
    print(f"[VALIDATOR] Memulai validasi pada {initial_count} baris data.")

    # Rule 1: Harga saat ini (current_price) harus > 0
    invalid_prices = df['current_price'] <= 0
    if invalid_prices.any():
        print(f"[VALIDATOR] Menemukan {invalid_prices.sum()} entri dengan harga <= 0. Data ini dihapus.")
        df = df[~invalid_prices] # Filter keluar yang invalid

    # Rule 2: Volume total (total_volume) harus >= 0
    invalid_volumes = df['total_volume'] < 0
    if invalid_volumes.any():
        print(f"[VALIDATOR] Menemukan {invalid_volumes.sum()} entri dengan volume < 0. Data ini dihapus.")
        df = df[~invalid_volumes]

    # Rule 3: market_cap_rank harus integer positif >= 1
    # Ini memerlukan penanganan NaN terlebih dahulu
    df['market_cap_rank'] = pd.to_numeric(df['market_cap_rank'], errors='coerce')
    invalid_ranks = df['market_cap_rank'].isna() | (df['market_cap_rank'] < 1)
    if invalid_ranks.any():
         print(f"[VALIDATOR] Menemukan {invalid_ranks.sum()} entri dengan ranking tidak valid. Data ini dihapus.")
         df = df[~invalid_ranks]

    final_count = len(df)
    print(f"[VALIDATOR] Validasi selesai. Tersisa {final_count} baris valid.")
    
    return df.to_dict(orient='records') # Kembalikan sebagai list of dicts



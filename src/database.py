import boto3
import json
import os
from datetime import datetime
from typing import List
from src.models import Coin

# Ambil nama bucket dari Environment Variable (Best Practice)
S3_BUCKET = os.environ.get("coingecko-data.lake")

def save_coins_to_s3(coins: List[Coin]) -> dict:
    """
    Simpan data ke S3 sebagai JSON file dengan partisi waktu.
    """
    s3 = boto3.client('s3')
    
    # 1. Convert List of Pydantic models ke list of dicts
    serializable_data = [c.dict(by_alias=True) for c in coins]
    
    # 2. Bikin struktur folder (Partitioning) untuk Athena
    # Format: raw/year=YYYY/month=MM/day=DD/coins_HHMMSS.json
    now = datetime.now()
    partition_path = f"year={now.year}/month={now.strftime('%m')}/day={now.strftime('%d')}"
    file_name = f"coins_{now.strftime('%H%M%S')}.json"
    s3_key = f"raw_coingecko/{partition_path}/{file_name}"

    # 3. Upload ke S3
    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(serializable_data, default=str),
            ContentType='application/json'
        )
        return {"status": "success", "path": s3_key}
    except Exception as e:
        print(f"Error upload ke S3: {str(e)}")
        raise e

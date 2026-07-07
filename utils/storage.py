import pandas as pd
import os
from datetime import datetime
import uuid

def ensure_dir(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

def append_to_csv(file_path, data_dict):
    ensure_dir(file_path)
    data_dict['id'] = str(uuid.uuid4())
    data_dict['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_new = pd.DataFrame([data_dict])
    if os.path.exists(file_path):
        df_existing = pd.read_csv(file_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.to_csv(file_path, index=False)

def delete_last_row(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if not df.empty:
            df = df.iloc[:-1]
            df.to_csv(file_path, index=False)
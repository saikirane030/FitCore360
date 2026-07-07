import pandas as pd
import os

def save_uploaded_csv(df, file_path="data/upload_data.csv"):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)

def get_uploaded_csv(file_path="data/upload_data.csv"):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

def delete_csv(file_path="data/upload_data.csv"):
    if os.path.exists(file_path):
        os.remove(file_path)

def delete_row_csv(index, file_path="data/upload_data.csv"):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if index in df.index:
            df = df.drop(index)
            df.to_csv(file_path, index=False)
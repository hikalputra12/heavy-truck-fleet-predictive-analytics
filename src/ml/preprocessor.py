import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KAGGLE_RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "aps_failure_training_set.csv")


def load_kaggle_data(filepath=KAGGLE_RAW_PATH, sample_size=10000):
    """
    Membaca dataset resmi Kaggle Scania APS Failure dari data/raw/.
    Mengubah label 'neg' -> 0 (sehat) dan 'pos' -> 1 (rusak).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File dataset Kaggle tidak ditemukan di: {filepath}")

    print(f"Membaca dataset asli Kaggle dari: {filepath} ...")
    # Dataset Kaggle menandai nilai kosong dengan string 'na'
    df = pd.read_csv(filepath, na_values="na")
    
    # Jika dataset sangat besar (60.000 baris), kita ambil sampel representatif agar training cepat di laptop
    if sample_size and len(df) > sample_size:
        print(f"Mengambil sampel acak berbobot {sample_size} baris untuk efisiensi komputasi...")
        # Stratified sampling agar proporsi kelas 'pos' (rusak) tetap terjaga
        pos_df = df[df["class"] == "pos"]
        neg_df = df[df["class"] == "neg"].sample(n=sample_size - len(pos_df), random_state=42)
        df = pd.concat([pos_df, neg_df]).sample(frac=1, random_state=42).reset_index(drop=True)

    # Encode target: pos (rusak) = 1, neg (sehat) = 0
    df["class"] = df["class"].map({"neg": 0, "pos": 1})
    
    return df


class TelemetryPreprocessor:
    """Pipeline pembersihan data: seleksi fitur, imputasi missing values, dan penskalaan robust"""
    
    def __init__(self, missing_threshold=0.5):
        # Kolom dengan data kosong > 50% akan dieliminasi agar tidak menambah noise
        self.missing_threshold = missing_threshold
        self.selected_features = []
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = RobustScaler()

    def fit_transform(self, X):
        # 1. Hapus kolom yang memiliki terlalu banyak missing values
        missing_ratio = X.isna().mean()
        self.selected_features = missing_ratio[missing_ratio <= self.missing_threshold].index.tolist()
        X_filtered = X[self.selected_features]

        # 2. Imputasi nilai kosong dengan median
        X_imp = self.imputer.fit_transform(X_filtered)

        # 3. Penskalaan dengan RobustScaler (IQR) agar kebal terhadap lonjakan sensor ekstrem
        X_scaled = self.scaler.fit_transform(X_imp)
        return X_scaled

    def transform(self, X):
        X_filtered = X[self.selected_features]
        X_imp = self.imputer.transform(X_filtered)
        X_scaled = self.scaler.transform(X_imp)
        return X_scaled


if __name__ == "__main__":
    # Tes memuat data riil Kaggle
    raw_df = load_kaggle_data()
    print("Ukuran data yang dimuat:", raw_df.shape)
    print("Jumlah armada sehat (class 0):", (raw_df["class"] == 0).sum())
    print("Jumlah armada rusak (class 1):", (raw_df["class"] == 1).sum())

    # Pisahkan fitur X dan target y
    X = raw_df.drop(columns=["class"])
    y = raw_df["class"]

    # Jalankan preprocessing
    preprocessor = TelemetryPreprocessor()
    X_clean = preprocessor.fit_transform(X)

    print(f"\nFitur awal: {X.shape[1]} kolom sensor.")
    print(f"Fitur setelah filter missing values: {len(preprocessor.selected_features)} kolom sensor terpilih.")
    print("Data siap dilatih ke model Machine Learning!")
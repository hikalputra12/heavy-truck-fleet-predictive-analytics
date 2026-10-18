import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, recall_score, precision_score, confusion_matrix
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from src.ml.preprocessor import load_kaggle_data, TelemetryPreprocessor


class FleetPredictiveModel:
    """Model klasifikasi deteksi dini kerusakan sistem rem angin (APS) armada truk"""

    def __init__(self):
        self.preprocessor = TelemetryPreprocessor()
        # Menggunakan class_weight='balanced' untuk menangani data tidak seimbang
        self.model = HistGradientBoostingClassifier(
            class_weight="balanced",
            random_state=42,
            max_iter=150
        )
        self.metrics = {}
        self.feature_importance_df = pd.DataFrame()

    def train_and_evaluate(self):
        """Melatih model pada data Kaggle dan mengukur metrik evaluasinya"""
        # 1. Muat dataset asli Kaggle
        df = load_kaggle_data()
        X = df.drop(columns=["class"])
        y = df["class"].values

        # 2. Split data: 75% untuk pelatihan (training), 25% untuk pengujian (test)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        # 3. Jalankan pipeline preprocessing
        print("Melakukan preprocessing dan scaling data...")
        X_train_proc = self.preprocessor.fit_transform(X_train)
        X_test_proc = self.preprocessor.transform(X_test)

        # 4. Latih model Machine Learning
        print("Melatih model Gradient Boosting...")
        self.model.fit(X_train_proc, y_train)

        # 5. Prediksi probabilitas kerusakan pada data uji
        y_scores = self.model.predict_proba(X_test_proc)[:, 1]
        y_pred = (y_scores >= 0.50).astype(int)

        # 6. Hitung metrik evaluasi industri
        roc_auc = roc_auc_score(y_test, y_scores)
        recall = recall_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred)

        self.metrics = {
            "roc_auc": round(float(roc_auc), 4),
            "recall": round(float(recall), 4),
            "precision": round(float(precision), 4),
            "confusion_matrix": cm,
            "y_test": y_test,
            "y_scores": y_scores
        }

        return self.metrics


if __name__ == "__main__":
    print("Memulai pelatihan model Machine Learning pada dataset Scania Kaggle...\n")
    fleet_model = FleetPredictiveModel()
    results = fleet_model.train_and_evaluate()

    print("\n--- HASIL EVALUASI MODEL MACHINE LEARNING ---")
    print(f"ROC-AUC Score : {results['roc_auc']:.4f}  (Kemampuan membedakan truk sehat vs rusak)")
    print(f"Recall        : {results['recall']:.4f}  (Persentase kerusakan yang berhasil dicegah)")
    print(f"Precision     : {results['precision']:.4f}  (Ketepatan tebakan alarm kerusakan)")
    
    cm = results['confusion_matrix']
    print("\nConfusion Matrix:")
    print(f"  True Negatives  (Truk Sehat tertebak Sehat)  : {cm[0][0]}")
    print(f"  False Positives (Salah Alarm, Inspeksi $10)  : {cm[0][1]}")
    print(f"  False Negatives (Mogok di Jalan, Rugi $500)  : {cm[1][0]}")
    print(f"  True Positives  (Truk Rusak tertangkap Servis): {cm[1][1]}")
import os
import sys
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from src.ml.model import FleetPredictiveModel


def compute_cost_curve(y_true, y_scores, cost_fp=10.0, cost_fn=500.0, steps=100):
    """
    Menghitung kurva total biaya perawatan pada berbagai ambang batas probabilitas (threshold)
    Cost Function = (False Positives * $10) + (False Negatives * $500)
    """
    thresholds = np.linspace(0.01, 0.95, steps)
    results = []

    for thresh in thresholds:
        y_pred = (y_scores >= thresh).astype(int)
        
        tp = int(np.sum((y_true == 1) & (y_pred == 1)))
        tn = int(np.sum((y_true == 0) & (y_pred == 0)))
        fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        fn = int(np.sum((y_true == 1) & (y_pred == 0)))
        
        # Biaya riil finansial: FP * $10 + FN * $500
        total_cost = (fp * cost_fp) + (fn * cost_fn)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        results.append({
            "threshold": round(float(thresh), 4),
            "true_positives": tp,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "recall": round(recall, 4),
            "precision": round(precision, 4),
            "total_cost_usd": round(float(total_cost), 2)
        })

    return pd.DataFrame(results)


def find_optimal_threshold(cost_df):
    """
    Mencari titik ambang batas probabilitas yang menghasilkan total pengeluaran paling minimum
    dan membandingkannya dengan threshold default (0.50)
    """
    if cost_df.empty:
        return {}

    # Titik biaya terendah (global minimum)
    min_idx = cost_df["total_cost_usd"].idxmin()
    best_row = cost_df.loc[min_idx].to_dict()

    # Titik biaya standar (threshold 0.50)
    default_row = cost_df.iloc[(cost_df["threshold"] - 0.50).abs().argsort()[:1]].iloc[0].to_dict()

    cost_saved = default_row["total_cost_usd"] - best_row["total_cost_usd"]
    pct_saved = (cost_saved / default_row["total_cost_usd"] * 100.0) if default_row["total_cost_usd"] > 0 else 0.0

    return {
        "optimal_threshold": best_row["threshold"],
        "optimal_total_cost_usd": best_row["total_cost_usd"],
        "optimal_false_positives": int(best_row["false_positives"]),
        "optimal_false_negatives": int(best_row["false_negatives"]),
        "optimal_recall": best_row["recall"],
        "default_threshold": default_row["threshold"],
        "default_total_cost_usd": default_row["total_cost_usd"],
        "default_false_positives": int(default_row["false_positives"]),
        "default_false_negatives": int(default_row["false_negatives"]),
        "cost_savings_usd": round(cost_saved, 2),
        "percentage_saved": round(pct_saved, 1)
    }


if __name__ == "__main__":
    print("1. Melatih model untuk mengambil skor prediksi...")
    fleet_model = FleetPredictiveModel()
    results = fleet_model.train_and_evaluate()

    y_test = results["y_test"]
    y_scores = results["y_scores"]

    print("2. Menghitung kurva optimasi biaya perawatan ($10 FP vs $500 FN)...")
    curve_df = compute_cost_curve(y_test, y_scores, cost_fp=10.0, cost_fn=500.0)
    opt = find_optimal_threshold(curve_df)

    print("\n--- HASIL OPTIMASI BIAYA PRESKRIPTIF (BUDGET PLANNING) ---")
    print(f"Ambang Batas Default (p = 0.50) : Total Biaya = ${opt['default_total_cost_usd']:,.2f}")
    print(f"  - Truk Mogok di Jalan (FN)    : {opt['default_false_negatives']} unit")
    print(f"  - Inspeksi Rutin (FP)         : {opt['default_false_positives']} unit")

    print(f"\nAmbang Batas Optimal (p* = {opt['optimal_threshold']:.3f}) : Total Biaya = ${opt['optimal_total_cost_usd']:,.2f}")
    print(f"  - Truk Mogok di Jalan (FN)    : {opt['optimal_false_negatives']} unit (Berkurang drastis!)")
    print(f"  - Inspeksi Rutin (FP)         : {opt['optimal_false_positives']} unit")

    print(f"\nTotal Penghematan Anggaran : ${opt['cost_savings_usd']:,.2f} ({opt['percentage_saved']}% Cost Reduction)")
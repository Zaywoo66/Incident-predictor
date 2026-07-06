import os
import argparse
import json
import joblib
import pandas as pd
import shap
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-data", default="test_data.csv", help="Path to test CSV")
    parser.add_argument("--model-dir", default="models", help="Directory with model artifacts")
    parser.add_argument("--metrics-dir", default="metrics", help="Directory to save metrics")
    args = parser.parse_args()

    model_path = os.path.join(args.model_dir, "model.pkl")

    if not os.path.exists(args.test_data) or not os.path.exists(model_path):
        print("ERROR: Test data or model missing. Run train.py first.")
        return

    print(f"[*] Loading test data from {args.test_data}")
    test_df = pd.read_csv(args.test_data)
    y_true = test_df["incident_label"]
    X_test = test_df.drop(columns=["incident_label"])

    print(f"[*] Loading model from {model_path}")
    model = joblib.load(model_path)

    # Generate predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # Calculate metrics
    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except ValueError:
        roc_auc = 0.0

    metrics = {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc
    }

    if metrics["recall"] < 0.5:
        print("WARNING: Recall is below 0.5. Model may be sacrificing recall for accuracy.")

    # Save report.json
    os.makedirs(args.metrics_dir, exist_ok=True)
    report_path = os.path.join(args.metrics_dir, "report.json")
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"[*] Evaluation report saved to {report_path}")
    print(json.dumps(metrics, indent=2))

    # SHAP analysis
    print("[*] Generating SHAP summary...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    plt.figure()
    shap.summary_plot(shap_values, X_test, show=False)
    shap_path = os.path.join(args.metrics_dir, "shap_summary.png")
    plt.savefig(shap_path, bbox_inches="tight")
    plt.close()

    print(f"[*] SHAP summary plot saved to {shap_path}")


if __name__ == "__main__":
    main()


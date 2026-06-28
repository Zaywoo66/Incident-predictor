import os
import json
import joblib
import pandas as pd
import shap
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

def main():
    test_data_path = "test_data.csv"
    model_path = "models/model.pkl"
    metrics_dir = "metrics"
    
    if not os.path.exists(test_data_path) or not os.path.exists(model_path):
        print("ERROR: Test data or model missing. Run train.py first.")
        return
        
    print(f"[*] Loading test data from {test_data_path}")
    test_df = pd.read_csv(test_data_path)
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
        # Happens if only one class is present in y_true
        roc_auc = 0.0
        
    metrics = {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc
    }
    
    # Check criteria: recall not sacrificed for accuracy
    if metrics["recall"] < 0.5:
        print("WARNING: Recall is below 0.5. Model may be sacrificing recall for accuracy.")
        
    # Save report.json
    os.makedirs(metrics_dir, exist_ok=True)
    report_path = os.path.join(metrics_dir, "report.json")
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
    shap_path = os.path.join(metrics_dir, "shap_summary.png")
    plt.savefig(shap_path, bbox_inches='tight')
    plt.close()
    
    print(f"[*] SHAP summary plot saved to {shap_path}")

if __name__ == "__main__":
    main()

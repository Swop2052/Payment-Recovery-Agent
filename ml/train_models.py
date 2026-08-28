"""
Trains two models:
1. retry_success_model  -> predicts P(retry succeeds) for a failed transaction
2. best_hour_model      -> predicts best retry hour

Run: python ml/train_models.py
Saves models to models/*.joblib
"""

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
DATA_PATH = "data/transactions.csv"
MODEL_DIR = "models"

import os
os.makedirs(MODEL_DIR, exist_ok=True)




def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    return df


def build_features(df: pd.DataFrame):
    df = df.copy()
    le_reason = LabelEncoder()
    le_method = LabelEncoder()
    le_device = LabelEncoder()

    df["failure_reason_enc"] = le_reason.fit_transform(df["failure_reason"])
    df["payment_method_enc"] = le_method.fit_transform(df["payment_method"])
    df["device_type_enc"] = le_device.fit_transform(df["device_type"])

    feature_cols = [
        "amount",
        "failure_reason_enc",
        "payment_method_enc",
        "device_type_enc",
        "hour_of_day",
        "day_of_week",
        "retry_count",
        "past_success_rate",
    ]
    encoders = {"reason": le_reason, "method": le_method, "device": le_device}
    return df, feature_cols, encoders


def train_retry_success_model(df, feature_cols):
    X = df[feature_cols]
    y = df["retry_success"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = GradientBoostingClassifier(
        n_estimators=150, max_depth=3, learning_rate=0.08, random_state=42
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    print(f"[retry_success_model] Accuracy: {accuracy_score(y_test, preds):.3f}")
    print(f"[retry_success_model] ROC-AUC : {roc_auc_score(y_test, probs):.3f}")

    importance = pd.Series(model.feature_importances_, index=feature_cols).sort_values(
        ascending=False
    )
    print("Feature importance:\n", importance)

    return model


def train_best_hour_model(df, feature_cols):
    success_df = df[df["retry_success"] == 1]
    X = success_df[feature_cols]
    y = success_df["hour_of_day"]

    model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
    model.fit(X, y)
    return model


if __name__ == "__main__":
    df = load_data()
    df, feature_cols, encoders = build_features(df)

    retry_model = train_retry_success_model(df, feature_cols)
    hour_model = train_best_hour_model(df, feature_cols)

    joblib.dump(retry_model, f"{MODEL_DIR}/retry_success_model.joblib")
    joblib.dump(hour_model, f"{MODEL_DIR}/best_hour_model.joblib")
    joblib.dump(encoders, f"{MODEL_DIR}/encoders.joblib")
    joblib.dump(feature_cols, f"{MODEL_DIR}/feature_cols.joblib")

    print("\nModels saved to /models")

   
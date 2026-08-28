"""
Agent orchestration layer.

Takes a failed transaction and autonomously decides:
1. Is this worth recovering (predicted success probability)?
2. What channel to use (WhatsApp / SMS / Email)?
3. When to retry (best predicted hour)?
4. What message to send (GenAI + RAG)?
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

import joblib
import pandas as pd

from agent.message_generator import generate_recovery_message

MODEL_DIR = "models"


@dataclass
class RecoveryPlan:
    transaction_id: str
    predicted_success_prob: float
    recommended_channel: str
    recommended_retry_time: datetime
    generated_message: str
    should_attempt_recovery: bool


class RecoveryAgent:
    def __init__(self):
        self.retry_model = joblib.load(f"{MODEL_DIR}/retry_success_model.joblib")
        self.hour_model = joblib.load(f"{MODEL_DIR}/best_hour_model.joblib")
        self.encoders = joblib.load(f"{MODEL_DIR}/encoders.joblib")
        self.feature_cols = joblib.load(f"{MODEL_DIR}/feature_cols.joblib")

    def tool_predict_success(self, txn: dict) -> float:
        row = self._encode_txn(txn)
        prob = self.retry_model.predict_proba(row[self.feature_cols])[0][1]
        return float(prob)

    def tool_predict_best_hour(self, txn: dict) -> int:
        row = self._encode_txn(txn)
        hour = self.hour_model.predict(row[self.feature_cols])[0]
        return int(round(hour)) % 24

    def tool_choose_channel(self, txn: dict) -> str:
        if txn.get("amount", 0) > 3000:
            return "whatsapp"
        return txn.get("preferred_channel", "sms")

    def tool_generate_message(self, txn: dict, channel: str) -> str:
        return generate_recovery_message(
            failure_reason=txn["failure_reason"],
            channel=channel,
            amount=txn["amount"],
            user_name=txn.get("user_name", "there"),
        )

    def run(self, txn: dict, min_prob_threshold: float = 0.35) -> RecoveryPlan:
        prob = self.tool_predict_success(txn)
        should_attempt = prob >= min_prob_threshold

        if not should_attempt:
            return RecoveryPlan(
                transaction_id=txn["transaction_id"],
                predicted_success_prob=prob,
                recommended_channel="none",
                recommended_retry_time=datetime.now(),
                generated_message="(Skipped - low predicted recovery value)",
                should_attempt_recovery=False,
            )

        best_hour = self.tool_predict_best_hour(txn)
        channel = self.tool_choose_channel(txn)
        message = self.tool_generate_message(txn, channel)

        now = datetime.now()
        retry_time = now.replace(hour=best_hour, minute=0, second=0, microsecond=0)
        if retry_time <= now:
            retry_time += timedelta(days=1)

        return RecoveryPlan(
            transaction_id=txn["transaction_id"],
            predicted_success_prob=round(prob, 3),
            recommended_channel=channel,
            recommended_retry_time=retry_time,
            generated_message=message,
            should_attempt_recovery=True,
        )

    def explain_decision(self, txn: dict) -> list[str]:
        importances = dict(zip(self.feature_cols, self.retry_model.feature_importances_))
        top_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:3]

        readable_names = {
            "past_success_rate": "the customer's past payment success rate",
            "failure_reason_enc": "the reason this payment failed",
            "amount": "the transaction amount",
            "hour_of_day": "the time of day it failed",
            "day_of_week": "the day of the week",
            "retry_count": "how many times it's already been retried",
            "device_type_enc": "the device used",
            "payment_method_enc": "the payment method used",
        }

        reasons = []
        for feat, weight in top_features:
            label = readable_names.get(feat, feat)
            reasons.append(f"{label} (influence: {weight*100:.0f}%)")

        return reasons

    def _encode_txn(self, txn: dict) -> pd.DataFrame:
        df = pd.DataFrame([txn])
        df["failure_reason_enc"] = self._safe_encode("reason", df["failure_reason"])
        df["payment_method_enc"] = self._safe_encode("method", df["payment_method"])
        df["device_type_enc"] = self._safe_encode("device", df["device_type"])
        return df

    def _safe_encode(self, key, series):
        le = self.encoders[key]
        return series.map(lambda v: le.transform([v])[0] if v in le.classes_ else 0)


def rank_transactions_by_recovery_value(agent, transactions, top_n=10):
    scored = []
    for txn in transactions:
        prob = agent.tool_predict_success(txn)
        recovery_value = prob * txn["amount"]
        scored.append({
            "transaction_id": txn["transaction_id"],
            "amount": txn["amount"],
            "failure_reason": txn["failure_reason"],
            "predicted_success_prob": round(prob, 3),
            "expected_recovery_value": round(recovery_value, 2),
        })

    scored.sort(key=lambda x: x["expected_recovery_value"], reverse=True)
    return scored[:top_n]


if __name__ == "__main__":
    agent = RecoveryAgent()
    test_txn = {
        "transaction_id": "TEST-001",
        "user_name": "Priya",
        "amount": 2499.0,
        "payment_method": "upi",
        "failure_reason": "insufficient_balance",
        "hour_of_day": 15,
        "day_of_week": 3,
        "device_type": "android",
        "retry_count": 0,
        "past_success_rate": 0.72,
        "preferred_channel": "sms",
    }

    plan = agent.run(test_txn)
    print("=" * 50)
    print(f"Transaction ID     : {plan.transaction_id}")
    print(f"Success Probability: {plan.predicted_success_prob*100:.1f}%")
    print(f"Attempt Recovery?  : {plan.should_attempt_recovery}")
    print(f"Recommended Channel: {plan.recommended_channel}")
    print(f"Recommended Time   : {plan.recommended_retry_time}")
    print(f"Message            : {plan.generated_message}")
    print("=" * 50)

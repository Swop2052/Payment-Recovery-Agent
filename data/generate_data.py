"""
Synthetic failed-payment dataset generator.
Simulates what a Razorpay-style payment gateway would log for failed transactions.
Run: python data/generate_data.py
"""

import random
import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh",
               "Ananya", "Diya", "Ishaan", "Kabir", "Meera", "Priya", "Rohan",
               "Saanvi", "Neha", "Karan", "Pooja", "Rahul", "Sneha"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Iyer", "Reddy", "Nair", "Patel",
              "Singh", "Rao", "Mehta", "Kapoor", "Joshi", "Chatterjee", "Pillai"]


def fake_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def fake_email(name):
    return f"{name.split()[0].lower()}{random.randint(1,999)}@example.com"


def fake_phone():
    return f"{random.choice(['6','7','8','9'])}{random.randint(100000000, 999999999)}"


def fake_date_between(start_days_ago, end_days_ago):
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, max(delta, 0)))).date()


def fake_datetime_between(start_days_ago, end_days_ago=0):
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    delta_seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, max(delta_seconds, 1)))


FAILURE_REASONS = [
    "insufficient_balance",
    "bank_server_down",
    "wrong_otp",
    "network_timeout",
    "card_declined_by_bank",
    "daily_limit_exceeded",
    "expired_card",
]

PAYMENT_METHODS = ["upi", "credit_card", "debit_card", "netbanking", "wallet"]
DEVICE_TYPES = ["android", "ios", "desktop_web", "mobile_web"]
CHANNELS = ["whatsapp", "sms", "email"]

N_USERS = 1000
N_TRANSACTIONS = 10000


def generate_users(n=N_USERS):
    users = []
    for i in range(n):
        name = fake_name()
        users.append(
            {
                "user_id": f"U{i:05d}",
                "name": name,
                "phone": fake_phone(),
                "email": fake_email(name),
                "signup_date": fake_date_between(730, 30),
                "past_success_rate": round(np.clip(np.random.normal(0.78, 0.15), 0.1, 0.99), 2),
                "preferred_channel": random.choice(CHANNELS),
            }
        )
    return pd.DataFrame(users)


def generate_transactions(users_df, n=N_TRANSACTIONS):
    rows = []
    for i in range(n):
        user = users_df.sample(1).iloc[0]
        method = random.choices(PAYMENT_METHODS, weights=[0.45, 0.25, 0.15, 0.1, 0.05])[0]
        reason = random.choices(
            FAILURE_REASONS, weights=[0.28, 0.15, 0.18, 0.14, 0.12, 0.08, 0.05]
        )[0]
        ts = fake_datetime_between(90, 0)
        amount = round(np.random.lognormal(mean=6.5, sigma=1.0), 2)

        base_prob = user["past_success_rate"]
        reason_penalty = {
            "insufficient_balance": -0.25,
            "bank_server_down": -0.05,
            "wrong_otp": 0.05,
            "network_timeout": 0.0,
            "card_declined_by_bank": -0.15,
            "daily_limit_exceeded": -0.30,
            "expired_card": -0.40,
        }[reason]
        prob_success_on_retry = np.clip(base_prob + reason_penalty + np.random.normal(0, 0.05), 0.02, 0.97)
        retry_success = np.random.rand() < prob_success_on_retry

        rows.append(
            {
                "transaction_id": str(uuid.uuid4())[:12],
                "user_id": user["user_id"],
                "amount": amount,
                "payment_method": method,
                "failure_reason": reason,
                "timestamp": ts,
                "hour_of_day": ts.hour,
                "day_of_week": ts.weekday(),
                "device_type": random.choice(DEVICE_TYPES),
                "retry_count": random.randint(0, 3),
                "past_success_rate": user["past_success_rate"],
                "preferred_channel": user["preferred_channel"],
                "retry_success": int(retry_success),
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    users_df = generate_users()
    txn_df = generate_transactions(users_df)

    users_df.to_csv("data/users.csv", index=False)
    txn_df.to_csv("data/transactions.csv", index=False)

    print(f"Generated {len(users_df)} users and {len(txn_df)} failed transactions.")
    print(txn_df.head())
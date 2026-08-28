"""
DB connection helper. Uses local SQLite so the project runs with
zero setup. Swap DB_URL to Postgres later for production.
"""

import os

import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./payment_recovery.db")
engine = create_engine(DB_URL, echo=False)


def init_db_from_csv(users_csv="data/users.csv", txn_csv="data/transactions.csv"):
    """Load generated CSVs into the DB. Run once after generate_data.py."""
    users = pd.read_csv(users_csv)
    txns = pd.read_csv(txn_csv, parse_dates=["timestamp"])

    users.to_sql("users", engine, if_exists="replace", index=False)
    txns.to_sql("transactions", engine, if_exists="replace", index=False)
    print(f"Loaded {len(users)} users and {len(txns)} transactions into {DB_URL}")


def run_query(sql: str) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


if __name__ == "__main__":
    init_db_from_csv()
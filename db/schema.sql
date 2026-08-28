CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(15),
    email VARCHAR(120),
    signup_date DATE,
    past_success_rate FLOAT,
    preferred_channel VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(10) REFERENCES users(user_id),
    amount FLOAT,
    payment_method VARCHAR(30),
    failure_reason VARCHAR(50),
    timestamp TIMESTAMP,
    hour_of_day INT,
    day_of_week INT,
    device_type VARCHAR(30),
    retry_count INT,
    past_success_rate FLOAT,
    preferred_channel VARCHAR(20),
    retry_success INT
);

CREATE TABLE IF NOT EXISTS recovery_actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id VARCHAR(20) REFERENCES transactions(transaction_id),
    predicted_success_prob FLOAT,
    recommended_channel VARCHAR(20),
    recommended_retry_time TIMESTAMP,
    generated_message TEXT,
    sent_at TIMESTAMP,
    actual_outcome VARCHAR(20) DEFAULT 'pending'
);

CREATE INDEX IF NOT EXISTS idx_txn_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_txn_reason ON transactions(failure_reason);
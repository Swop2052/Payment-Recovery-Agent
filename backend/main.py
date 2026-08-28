"""
FastAPI backend for the Smart Payment Recovery Agent.

Run: uvicorn backend.main:app --reload
Docs: http://localhost:8000/docs
"""

import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.recovery_agent import RecoveryAgent, rank_transactions_by_recovery_value
from db.database import run_query
from agent.chatbot import chat_with_assistant

app = FastAPI(
    title="Smart Payment Recovery Agent API",
    description="AI-powered failed payment recovery — Razorpay Buildathon",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = RecoveryAgent()


class TransactionInput(BaseModel):
    transaction_id: str
    user_id: str = "U00000"
    user_name: str = "there"
    amount: float
    payment_method: str
    failure_reason: str
    hour_of_day: int
    day_of_week: int
    device_type: str
    retry_count: int
    past_success_rate: float
    preferred_channel: str


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatInput(BaseModel):
    message: str
    history: list[ChatMessage] = []


@app.get("/")
def root():
    return {"status": "ok", "service": "smart-payment-recovery-agent"}


@app.post("/predict-failure-success")
def predict_failure_success(txn: TransactionInput):
    try:
        prob = agent.tool_predict_success(txn.model_dump())
        best_hour = agent.tool_predict_best_hour(txn.model_dump())
        return {
            "transaction_id": txn.transaction_id,
            "predicted_success_prob": round(prob, 3),
            "recommended_retry_hour": best_hour,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-recovery-message")
def generate_message_endpoint(txn: TransactionInput):
    try:
        channel = agent.tool_choose_channel(txn.model_dump())
        message = agent.tool_generate_message(txn.model_dump(), channel)
        return {"channel": channel, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/trigger-recovery-agent")
def trigger_recovery_agent(txn: TransactionInput):
    try:
        txn_dict = txn.model_dump()
        plan = agent.run(txn_dict)
        reasons = agent.explain_decision(txn_dict)
        return {
            "transaction_id": plan.transaction_id,
            "predicted_success_prob": plan.predicted_success_prob,
            "should_attempt_recovery": plan.should_attempt_recovery,
            "recommended_channel": plan.recommended_channel,
            "recommended_retry_time": plan.recommended_retry_time.isoformat(),
            "generated_message": plan.generated_message,
            "reasons": reasons,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat_endpoint(chat_input: ChatInput):
    try:
        reply = chat_with_assistant(
            user_message=chat_input.message,
            history=[msg.model_dump() for msg in chat_input.history]
        )
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics")
def analytics():
    try:
        total = run_query("SELECT COUNT(*) as total FROM transactions").iloc[0]["total"]
        by_reason = run_query(
            """SELECT failure_reason, COUNT(*) as count,
                      AVG(retry_success) as recovery_rate
               FROM transactions GROUP BY failure_reason
               ORDER BY count DESC"""
        )
        by_method = run_query(
            """SELECT payment_method, COUNT(*) as count,
                      AVG(retry_success) as recovery_rate
               FROM transactions GROUP BY payment_method"""
        )
        revenue_recovered = run_query(
            "SELECT SUM(amount) as recovered FROM transactions WHERE retry_success = 1"
        ).iloc[0]["recovered"]
        revenue_lost = run_query(
            "SELECT SUM(amount) as lost FROM transactions WHERE retry_success = 0"
        ).iloc[0]["lost"]

        return {
            "total_failed_transactions": int(total),
            "revenue_recovered": round(float(revenue_recovered or 0), 2),
            "revenue_lost": round(float(revenue_lost or 0), 2),
            "by_failure_reason": by_reason.to_dict(orient="records"),
            "by_payment_method": by_method.to_dict(orient="records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/priority-queue")
def priority_queue(limit: int = 10):
    """
    Returns the top-N failed transactions ranked by expected recovery value
    (predicted success probability x amount) — tells the business where to
    focus recovery effort first.
    """
    try:
        df = run_query(
            f"""SELECT transaction_id, amount, payment_method, failure_reason,
                       hour_of_day, day_of_week, device_type, retry_count,
                       past_success_rate, preferred_channel
                FROM transactions
                ORDER BY RANDOM() LIMIT 50"""
        )
        transactions = df.to_dict(orient="records")
        ranked = rank_transactions_by_recovery_value(agent, transactions, top_n=limit)
        return {"priority_queue": ranked}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
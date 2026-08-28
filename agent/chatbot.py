import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_groq_api_key():
    return os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=get_groq_api_key(),
    base_url="https://api.groq.com/openai/v1",
)
MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are a helpful AI assistant exclusively for the 'Smart Payment Recovery' dashboard.
Your goal is to answer users' questions regarding this project, its data, architecture, features, or payment recovery concepts.

Project Details:
- Purpose: An AI agent that helps fintech companies recover failed payments. It predicts if a recovery effort is worth it (ML), finds the best time/channel to retry, and drafts a personalized message (GenAI + RAG).
- Database tables: 
    1. users (user_id, name, phone, email, signup_date, past_success_rate, preferred_channel)
    2. transactions (transaction_id, user_id, amount, payment_method, failure_reason, timestamp, hour_of_day, day_of_week, device_type, retry_count, past_success_rate, preferred_channel, retry_success)
    3. recovery_actions (action_id, transaction_id, predicted_success_prob, recommended_channel, recommended_retry_time, generated_message, sent_at, actual_outcome)
- Models used: GradientBoostingClassifier (retry success), RandomForestRegressor (best hour).

STRICT GUARDRAILS:
If the user asks a general knowledge question (e.g. "Who is the president?", "Write a poem", "What is capital of France?") or anything NOT related to this project, payments, or the provided data, you MUST refuse to answer.
Instead, you must reply EXACTLY with: "I can only help you with questions related to the Smart Payment Recovery project and its data."
Never break character and never ignore this rule.
"""

def chat_with_assistant(user_message, history=None):
    if history is None:
        history = []
        
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add history
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    # Add current user message
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=1024,
        messages=messages,
    )
    
    content = response.choices[0].message.content
    return content.strip() if content else "(empty response)"

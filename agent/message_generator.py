"""
Generates a personalized recovery message for a failed transaction using
an LLM (via Groq), grounded with policy context retrieved via RAG.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

from agent.policy_docs import retrieve_relevant_docs

load_dotenv()

def get_groq_api_key():
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


client = OpenAI(
    api_key=get_groq_api_key(),
    base_url="https://api.groq.com/openai/v1",
)
MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are a payment recovery assistant for a fintech platform.
Write a short (2-3 sentence) recovery message to a customer whose payment failed.
Rules:
- Be warm, reassuring, and never guilt-trip the customer.
- Clearly state no money was deducted (if that's true for the failure reason).
- Include one clear, simple next step.
- If a relevant offer exists in the provided context, mention it naturally.
- Do not invent policies that aren't in the provided context.
- Keep it appropriate for the given channel (SMS = very short, WhatsApp/Email = slightly longer).
"""


def generate_recovery_message(failure_reason, channel, amount, user_name="there"):
    context_docs = retrieve_relevant_docs(failure_reason)
    context_text = "\n".join(f"- {d['text']}" for d in context_docs)

    user_prompt = f"""
Customer name: {user_name}
Failed amount: INR {amount}
Failure reason: {failure_reason}
Channel: {channel}

Relevant policy context (only use what's applicable):
{context_text}

Write the recovery message now.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=1024,
        reasoning_effort="low",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = response.choices[0].message.content
    return content.strip() if content else "(empty response)"


if __name__ == "__main__":
    msg = generate_recovery_message(
        failure_reason="insufficient_balance",
        channel="whatsapp",
        amount=1499.0,
        user_name="Krishna",
    )
    print(msg)
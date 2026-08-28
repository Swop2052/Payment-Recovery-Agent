"""
Small in-memory 'knowledge base' standing in for company policy docs
(refund policy, offers, retry rules). In real deployment, these would be
chunked PDFs/Notion pages embedded into a vector DB (Chroma/FAISS/Pinecone).
"""

POLICY_DOCS = [
    {
        "id": "offer_cashback",
        "text": (
            "Customers who complete a payment within 30 minutes of a failed "
            "transaction are eligible for a 5% cashback, capped at INR 100, "
            "credited within 24 hours."
        ),
    },
    {
        "id": "policy_insufficient_balance",
        "text": (
            "For failures due to insufficient balance, recommend the customer "
            "retry via UPI after checking their balance, or suggest an "
            "alternate saved payment method. Do not retry automatically."
        ),
    },
    {
        "id": "policy_otp",
        "text": (
            "For OTP failures, advise the customer to check for network delay "
            "and request a fresh OTP. Never ask the customer to share the OTP "
            "in chat or SMS."
        ),
    },
    {
        "id": "policy_bank_server_down",
        "text": (
            "For bank server downtime failures, recommend retrying after 15-30 "
            "minutes or switching to a different payment method (UPI vs card)."
        ),
    },
    {
        "id": "policy_card_declined",
        "text": (
            "For card declines, recommend contacting the issuing bank or using "
            "an alternate card/UPI. Mention that no charge was made."
        ),
    },
    {
        "id": "tone_guidelines",
        "text": (
            "All recovery messages must be short, friendly, and non-pushy. "
            "Avoid guilt-tripping language. Always reassure the customer that "
            "no amount was deducted if the payment failed before debit."
        ),
    },
]


def retrieve_relevant_docs(failure_reason: str, top_k: int = 2):
    """
    Simple keyword-based retrieval stand-in for a real vector search.
    Swap this for a Chroma/FAISS similarity search once embeddings are wired up.
    """
    reason_map = {
        "insufficient_balance": ["policy_insufficient_balance"],
        "wrong_otp": ["policy_otp"],
        "bank_server_down": ["policy_bank_server_down"],
        "card_declined_by_bank": ["policy_card_declined"],
    }
    ids = reason_map.get(failure_reason, [])
    ids.append("offer_cashback")
    ids.append("tone_guidelines")

    docs = [d for d in POLICY_DOCS if d["id"] in ids]
    return docs[:top_k + 2]
import os
import json
import re

from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

REQUIRED_KEYS = frozenset({
    "invoice_number", "vendor_name", "invoice_date", "amount",
    "tax_amount", "total_amount", "payment_status"
})

SYSTEM_PROMPT = """You are an invoice data extractor. Extract structured data from the given invoice text.
Return ONLY valid JSON with exactly these keys (no other keys, no markdown, no explanation):
- invoice_number: string
- vendor_name: string
- invoice_date: string (YYYY-MM-DD if possible)
- amount: number (subtotal before tax)
- tax_amount: number
- total_amount: number
- payment_status: string (e.g. "paid", "pending", "unpaid")

Use null for any field you cannot find. Use 0 for numeric fields when unknown."""


def normalize_invoice(text: str) -> dict:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set")

    if not text or not text.strip():
        return {k: None for k in REQUIRED_KEYS}

    client = Groq(api_key=GROQ_API_KEY)

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text.strip()},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )
    except Exception as e:
        raise RuntimeError(f"Groq API error: {e}") from e

    raw = completion.choices[0].message.content
    if not raw:
        raise ValueError("Empty response from LLM")

    # Strip markdown code blocks if present
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("LLM response is not a JSON object")

    # Ensure all required keys exist; fill missing with null
    NUMERIC_KEYS = {"amount", "tax_amount", "total_amount"}

    result = {}
    for k in REQUIRED_KEYS:
        v = data.get(k)
        if v is None and k in NUMERIC_KEYS:
            v = 0
        result[k] = v

    return result
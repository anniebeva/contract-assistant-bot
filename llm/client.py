import httpx
import logging
from config.settings import GROQ_API_KEY, GROQ_URL, LLM_MODEL, LLM_TIMEOUT


async def call_groq(messages: list) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 1000,
        "top_p": 1.0,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        resp = await client.post(GROQ_URL, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

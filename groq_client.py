import os

import random
import time

from groq import Groq

try:
    import streamlit as st
except Exception:
    st = None

from core.config import BACKOFF_SECONDS, MAX_RETRIES


class GroqServiceError(RuntimeError):
    pass


def _message_from_error(exc: Exception) -> str:
    text = str(exc)
    lower = text.lower()

    if "429" in lower or "rate limit" in lower:
        return "Groq rate limit reached. Please wait a little and try again."
    if "401" in lower or "invalid api key" in lower or "authentication" in lower:
        return "Groq API key is missing or invalid. Add a valid GROQ_API_KEY secret in Streamlit Cloud."
    if "403" in lower:
        return "Groq rejected the request. Check your API/project permissions."
    if "413" in lower or "too large" in lower:
        return "The request was too large. Please shorten the business description."
    if "500" in lower or "502" in lower or "503" in lower:
        return "Groq is temporarily unavailable. Please try again shortly."
    return "The AI service returned an unexpected error. Please try again."


def _api_key() -> str | None:
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    if st is not None:
        try:
            return st.secrets.get("GROQ_API_KEY")
        except Exception:
            return None
    return None


def chat(messages: list[dict], model: str) -> str:
    key = _api_key()
    if not key:
        raise GroqServiceError(
            "GROQ_API_KEY is not configured. Add it to Streamlit Cloud Secrets."
        )
    client = Groq(api_key=key)
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=5000,
            )
            content = response.choices[0].message.content
            if not content:
                raise GroqServiceError("Groq returned an empty response.")
            return content.strip()

        except Exception as exc:
            last_error = exc
            lower = str(exc).lower()
            retryable = any(
                marker in lower
                for marker in ("429", "rate limit", "500", "502", "503", "timeout", "temporarily")
            )
            if not retryable or attempt == MAX_RETRIES - 1:
                raise GroqServiceError(_message_from_error(exc)) from exc

            delay = BACKOFF_SECONDS * (2 ** attempt) + random.uniform(0, 0.75)
            time.sleep(delay)

    raise GroqServiceError(_message_from_error(last_error or Exception("Unknown error")))

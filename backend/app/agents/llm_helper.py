"""Shared LLM helper — wraps Google Gemini with graceful fallback."""
import google.generativeai as genai
from ..config import settings
import json
import re

_model = None


def _get_model():
    """Lazy-init Gemini model."""
    global _model
    if _model is None and settings.LLM_AVAILABLE:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-2.0-flash")
    return _model


async def call_llm(prompt: str, fallback: str = "") -> str:
    """Call Gemini LLM with automatic fallback to a default response.
    
    Args:
        prompt: The prompt to send to the LLM.
        fallback: Default response if LLM is unavailable or fails.
    
    Returns:
        LLM response text, or fallback string.
    """
    model = _get_model()
    if model is None:
        return fallback

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[LLM FALLBACK] Gemini call failed: {e}")
        return fallback


async def call_llm_json(prompt: str, fallback: dict | list = None) -> dict | list:
    """Call Gemini and parse JSON response, with fallback.
    
    Args:
        prompt: The prompt (should instruct JSON output).
        fallback: Default dict/list if LLM unavailable or parse fails.
    
    Returns:
        Parsed JSON object, or fallback.
    """
    if fallback is None:
        fallback = {}

    model = _get_model()
    if model is None:
        return fallback

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception as e:
        print(f"[LLM FALLBACK] Gemini JSON call failed: {e}")
        return fallback

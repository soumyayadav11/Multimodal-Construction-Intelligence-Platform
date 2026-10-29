"""Configuration module for the Multimodal Construction Intelligence Platform.

Handles environment loading, application settings, API key resolution,
and platform defaults.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Sequence

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class AppConfig:
    """Application-wide constants and configurations."""

    APP_TITLE: str = "Multimodal Construction Intelligence Platform"
    APP_SUBTITLE: str = "AI-Powered Safety Audits, Defect Diagnostics & Site Intelligence"
    APP_ICON: str = "🏗️"
    MAX_FILE_SIZE_MB: int = 10
    SUPPORTED_IMAGE_TYPES: Sequence[str] = ("png", "jpg", "jpeg", "webp")
    DEFAULT_MODEL: str = "gemini-3.8-flash"
    POLLINATIONS_URL: str = "https://image.pollinations.ai/prompt"

    # Base directory paths
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    SRC_DIR: Path = Path(__file__).resolve().parent


def get_api_key() -> Optional[str]:
    """Retrieve the Gemini API key from Streamlit secrets, environment, or session state.

    Resolution order:
    1. Streamlit secrets (`st.secrets["GEMINI_API_KEY"]`)
    2. Environment variable (`GEMINI_API_KEY`)
    3. Streamlit session state (`st.session_state["gemini_api_key"]` or `st.session_state["GEMINI_API_KEY"]`)

    Returns:
        str | None: The sanitized API key if found, or None if unavailable.
        API keys are never logged or exposed.
    """
    # 1. Check Streamlit secrets
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            val = st.secrets["GEMINI_API_KEY"]
            if val and str(val).strip():
                return str(val).strip()
    except Exception:
        # Secrets not configured or running in non-Streamlit context
        pass

    # 2. Check Environment variable
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 3. Check Streamlit session state
    try:
        import streamlit as st

        if hasattr(st, "session_state"):
            session_key = st.session_state.get("gemini_api_key") or st.session_state.get("GEMINI_API_KEY")
            if session_key and str(session_key).strip():
                return str(session_key).strip()
    except Exception:
        pass

    return None


def is_demo_mode() -> bool:
    """Check if the platform is running in demonstration mode (no API key configured).

    Returns:
        bool: True if no Gemini API key is available, False otherwise.
    """
    return get_api_key() is None


def get_model_name() -> str:
    """Return the configured Gemini model name from secrets, environment, or default.

    Resolution order:
    1. Streamlit secrets (`st.secrets["GEMINI_MODEL"]`)
    2. Environment variable (`GEMINI_MODEL`)
    3. Default model (`AppConfig.DEFAULT_MODEL`)

    Returns:
        str: Model identifier string.
    """
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "GEMINI_MODEL" in st.secrets:
            val = st.secrets["GEMINI_MODEL"]
            if val and str(val).strip():
                return str(val).strip()
    except Exception:
        pass

    env_model = os.getenv("GEMINI_MODEL")
    if env_model and env_model.strip():
        return env_model.strip()

    return AppConfig.DEFAULT_MODEL


def format_inr(amount: Optional[float], precision: int = 2) -> str:
    """Format a monetary value in Indian Rupees (INR) with Lakhs and Crores notations.

    Examples:
        format_inr(15000000) -> "₹1.50 Cr"
        format_inr(450000)   -> "₹4.50 Lakhs"
        format_inr(35000)    -> "₹35,000.00"

    Args:
        amount: Numerical value in INR.
        precision: Decimal places for Lakhs/Crores display.

    Returns:
        str: Formatted string representation.
    """
    if amount is None:
        return "₹0.00"

    abs_amount = abs(amount)
    sign = "-" if amount < 0 else ""

    if abs_amount >= 10_000_000:  # 1 Crore
        cr_val = abs_amount / 10_000_000
        return f"{sign}₹{cr_val:.{precision}f} Cr"
    elif abs_amount >= 100_000:  # 1 Lakh
        lakh_val = abs_amount / 100_000
        return f"{sign}₹{lakh_val:.{precision}f} Lakhs"
    else:
        return f"{sign}₹{abs_amount:,.{precision}f}"

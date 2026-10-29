"""Google Gemini AI service for multimodal construction analysis."""
from __future__ import annotations

import json
import os
import re
from typing import Any, Optional
from PIL import Image

try:
    from src.config import get_api_key, get_model_name, is_demo_mode
except ImportError:
    # Fallback configuration accessors if src.config is not yet initialized
    def get_api_key() -> str | None:
        """Get Gemini API key from environment."""
        return os.environ.get("GEMINI_API_KEY")

    def get_model_name() -> str:
        """Get default Gemini model name."""
        return os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

    def is_demo_mode() -> bool:
        """Check if demo mode is enabled."""
        return os.environ.get("DEMO_MODE", "false").lower() in ("true", "1", "yes")


# Prompt templates
SAFETY_AUDIT_PROMPT = """You are a construction site safety analyst. Analyze this construction site image and provide a preliminary safety assessment.

Assess the following PPE categories when visible:
- Safety helmets
- High-visibility vests
- Safety footwear (note: steel-toe protection cannot be confirmed from a photo)
- Safety harnesses (if work at height is visible)

Identify potential hazards such as:
- Unprotected edges or openings
- Work at height without fall protection
- Unsafe material storage
- Exposed electrical hazards
- Missing visible PPE
- Unsafe access routes
- Potential falling-object hazards

Return your analysis as a JSON object with this exact structure:
{
  "analysis_type": "site_safety_audit",
  "safety_score": <integer 0-100>,
  "overall_status": "<Safe|Needs Attention|Critical|Unsafe>",
  "ppe_detection": {
    "helmet": {"status": "<Observed|Not Observed|Unknown|Not Applicable>", "confidence": <float 0-1 or null>, "notes": "<text>"},
    "high_visibility_vest": {"status": "<...>", "confidence": <...>, "notes": "<text>"},
    "safety_footwear": {"status": "<...>", "confidence": <...>, "notes": "<text>"},
    "safety_harness": {"status": "<...>", "confidence": <...>, "notes": "<text>"}
  },
  "hazards": [
    {"hazard": "<description>", "severity": "<Low|Medium|High|Critical>", "evidence": "<what you see>", "corrective_action": "<recommendation>"}
  ],
  "limitations": ["<list of analysis limitations>"]
}

IMPORTANT:
- Only report what you can actually observe in the image
- Use 'Unknown' for items that cannot be determined from the image
- Do not fabricate precise confidence scores - use reasonable estimates or null
- Always include limitations of image-based analysis
- Return ONLY the JSON object, no additional text"""

CRACK_DIAGNOSTICS_PROMPT = """You are a structural engineering analyst. Analyze this image of a concrete or wall surface for defects.

Classify the visible defect into one of these categories:
- Hairline
- Settlement
- Structural Shear
- Thermal Expansion
- Spalling
- Unknown / Insufficient Evidence

Return your analysis as a JSON object with this exact structure:
{
  "analysis_type": "crack_diagnostics",
  "defect_type": "<one of the categories above>",
  "estimated_width_mm": <float or null - only provide if scale reference exists>,
  "severity": "<Low|Medium|High|Critical>",
  "possible_causes": ["<cause1>", "<cause2>"],
  "evidence": ["<visual evidence supporting classification>"],
  "recommended_actions": ["<action1>", "<action2>"],
  "urgency": "<Routine Inspection|Inspect Soon|Urgent|Immediate Action Required>",
  "professional_review_required": true,
  "limitations": ["<limitation1>"]
}

IMPORTANT:
- Set estimated_width_mm to null if no scale reference is available in the image
- A photograph alone cannot reliably establish actual crack width without calibration
- Always set professional_review_required to true
- Do not label a structure as safe based solely on image analysis
- If the crack appears potentially serious, recommend prompt evaluation by a qualified structural engineer
- Return ONLY the JSON object, no additional text"""

ASSISTANT_SYSTEM_PROMPT = """You are a knowledgeable construction industry assistant. You help with questions about:
- Construction planning and project management
- Site safety and PPE requirements
- Concrete defects and structural concerns
- Construction terminology and best practices
- Project budgets and material estimates
- Weather-related precautions for construction sites
- Daily site checklists and procedures

Guidelines:
- Provide concise, practical, and organized answers
- Distinguish general educational advice from project-specific engineering recommendations
- Do not fabricate regulatory citations, material prices, or property values
- Recommend consulting qualified professionals for structural, safety, or legal matters
- If a question involves potentially dangerous conditions, escalate to a qualified professional
- Keep responses helpful and focused on construction industry topics"""


class GeminiService:
    """Wrapper for Google Gemini AI API interactions."""

    def __init__(self, model_name: Optional[str] = None):
        """Initialize the Gemini service.
        
        Args:
            model_name: Optional override for the Gemini model name.
        """
        self._client = None
        self._model_name = model_name or get_model_name()

    def _get_client(self):
        """Lazily initialize and return the Gemini client.
        
        Returns:
            google.genai.Client instance
            
        Raises:
            ValueError: If no API key is configured
            ImportError: If google-genai is not installed
        """
        if self._client is None:
            try:
                from google import genai
                api_key = get_api_key()
                if not api_key:
                    raise ValueError("No API key configured")
                self._client = genai.Client(api_key=api_key)
            except ImportError:
                raise ImportError(
                    "google-genai package is not installed. Run: pip install google-genai"
                )
        return self._client

    @property
    def is_demo(self) -> bool:
        """Check if demo mode is currently enabled."""
        return is_demo_mode()

    def analyze_image(self, image: Image.Image, prompt: str) -> str:
        """Send image and prompt to Gemini for analysis.

        Args:
            image: PIL Image to analyze
            prompt: Analysis prompt

        Returns:
            Raw response text from the model

        Raises:
            ConnectionError: On authentication, quota, or network failures
            ValueError: On empty response or invalid model
        """
        client = self._get_client()
        try:
            response = client.models.generate_content(
                model=self._model_name,
                contents=[image, prompt]
            )
            if response and response.text:
                return response.text
            raise ValueError("Empty response from AI model")
        except Exception as e:
            error_msg = str(e).lower()
            if 'api_key' in error_msg or 'authentication' in error_msg or 'unauthorized' in error_msg:
                raise ConnectionError(
                    f"Authentication error: Please check your Gemini API key. Details: {e}"
                )
            elif 'quota' in error_msg or 'rate' in error_msg:
                raise ConnectionError(
                    f"API quota exceeded. Please try again later. Details: {e}"
                )
            elif 'not found' in error_msg or 'model' in error_msg:
                raise ValueError(
                    f"Model '{self._model_name}' may not be available. Details: {e}"
                )
            else:
                raise ConnectionError(f"AI service error: {e}")

    def chat(self, messages: list[dict[str, str]], system_prompt: str = "") -> str:
        """Send chat messages to Gemini.

        Args:
            messages: List of dicts with 'role' and 'content' keys
            system_prompt: Optional system prompt for context

        Returns:
            Response text from the model
            
        Raises:
            ConnectionError: If API call fails
        """
        client = self._get_client()

        # Build content list from messages
        contents = []
        if system_prompt:
            contents.append(f"System: {system_prompt}")

        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                contents.append(f"User: {content}")
            else:
                contents.append(f"Assistant: {content}")

        try:
            response = client.models.generate_content(
                model=self._model_name,
                contents="\n\n".join(contents)
            )
            if response and response.text:
                return response.text
            return "I'm sorry, I couldn't generate a response. Please try again."
        except Exception as e:
            raise ConnectionError(f"Chat service error: {e}")


def extract_json_from_response(response_text: str) -> dict[str, Any] | None:
    """Extract JSON object from AI response text.

    Handles responses with markdown code fences (```json ... ```) and plain JSON.

    Args:
        response_text: Raw string containing JSON, optionally wrapped in markdown

    Returns:
        Parsed dictionary if successful, None otherwise
    """
    if not response_text:
        return None

    # Try to find JSON in markdown code fence or raw JSON block
    patterns = [
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
        r'\{[\s\S]*\}'
    ]

    for pattern in patterns:
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            json_str = match.group(1) if '```' in pattern else match.group(0)
            try:
                return json.loads(json_str.strip())
            except json.JSONDecodeError:
                continue

    # Final attempt: try parsing the entire response
    try:
        return json.loads(response_text.strip())
    except json.JSONDecodeError:
        return None


__all__ = [
    "SAFETY_AUDIT_PROMPT",
    "CRACK_DIAGNOSTICS_PROMPT",
    "ASSISTANT_SYSTEM_PROMPT",
    "GeminiService",
    "extract_json_from_response",
]

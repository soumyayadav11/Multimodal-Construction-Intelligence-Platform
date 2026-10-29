"""Site Safety & PPE Audit module for construction image analysis."""
from __future__ import annotations

from typing import Optional
from PIL import Image

from src.schemas import (
    SafetyAuditResult,
    PPEItem,
    PPEStatus,
    HazardItem,
    SeverityLevel,
    OverallStatus,
    AnalysisMode,
)
from src.ai_service import GeminiService, SAFETY_AUDIT_PROMPT, extract_json_from_response
from src.config import is_demo_mode


def get_demo_safety_result() -> SafetyAuditResult:
    """Return a clearly-labeled demonstration safety audit result.

    Returns:
        SafetyAuditResult: Demonstration safety audit baseline data.
    """
    return SafetyAuditResult(
        analysis_type="site_safety_audit",
        safety_score=72,
        overall_status=OverallStatus.NEEDS_ATTENTION,
        ppe_detection={
            "helmet": PPEItem(
                status=PPEStatus.OBSERVED,
                confidence=0.85,
                notes="A hard hat appears visible on one worker in the demonstration scenario.",
            ),
            "high_visibility_vest": PPEItem(
                status=PPEStatus.NOT_OBSERVED,
                confidence=0.78,
                notes="No high-visibility vest is clearly visible in this demonstration scenario.",
            ),
            "safety_footwear": PPEItem(
                status=PPEStatus.UNKNOWN,
                confidence=None,
                notes="Footwear protection cannot be verified from a photograph.",
            ),
            "safety_harness": PPEItem(
                status=PPEStatus.NOT_APPLICABLE,
                confidence=None,
                notes="No work-at-height activity is apparent in this demonstration scenario.",
            ),
        },
        hazards=[
            HazardItem(
                hazard="Potential unprotected edge",
                severity=SeverityLevel.HIGH,
                evidence="An exposed edge appears visible in this demonstration scenario.",
                corrective_action="Arrange a competent-person inspection and provide appropriate edge protection.",
            ),
            HazardItem(
                hazard="Missing high-visibility vest",
                severity=SeverityLevel.MEDIUM,
                evidence="At least one worker appears without a high-visibility vest.",
                corrective_action="Ensure all workers wear high-visibility vests as required by the site safety plan.",
            ),
        ],
        limitations=[
            "⚠️ THIS IS A DEMONSTRATION RESULT — not derived from any uploaded image.",
            "Image-based observations may miss hazards outside the camera view.",
            "PPE compliance cannot be fully verified from photographs alone.",
            "Steel-toe protection in footwear cannot be confirmed from an image.",
        ],
    )


def analyze_site_safety(
    image: Image.Image,
    ai_service: Optional[GeminiService] = None,
) -> tuple[SafetyAuditResult, AnalysisMode]:
    """Analyze a construction site image for safety and PPE compliance.

    Args:
        image: PIL Image of the construction site
        ai_service: Optional GeminiService instance (None for demo mode)

    Returns:
        Tuple of (SafetyAuditResult, AnalysisMode)

    Raises:
        ConnectionError: If network connectivity to Gemini API fails.
        ValueError: If JSON extraction or response parsing fails.
    """
    if is_demo_mode() or ai_service is None:
        return get_demo_safety_result(), AnalysisMode.DEMONSTRATION

    try:
        # Get AI analysis
        response_text = ai_service.analyze_image(image, SAFETY_AUDIT_PROMPT)

        # Extract JSON from response
        json_data = extract_json_from_response(response_text)
        if json_data is None:
            raise ValueError("Could not extract valid JSON from AI response")

        # Parse PPE detection - normalize keys
        ppe_raw = json_data.get("ppe_detection", {})
        ppe_detection: dict[str, PPEItem] = {}
        if isinstance(ppe_raw, dict):
            for key, value in ppe_raw.items():
                if isinstance(value, dict):
                    # Normalize status to match enum
                    status_val = value.get("status", "Unknown")
                    try:
                        status = PPEStatus(status_val)
                    except ValueError:
                        # Attempt case-insensitive match
                        found_status = None
                        for s in PPEStatus:
                            if s.value.lower() == str(status_val).strip().lower():
                                found_status = s
                                break
                        status = found_status if found_status is not None else PPEStatus.UNKNOWN

                    confidence = value.get("confidence")
                    if confidence is not None:
                        try:
                            confidence = float(confidence)
                            if not 0 <= confidence <= 1:
                                confidence = None
                        except (TypeError, ValueError):
                            confidence = None

                    ppe_detection[key] = PPEItem(
                        status=status,
                        confidence=confidence,
                        notes=value.get("notes", ""),
                    )

        # Ensure all required PPE categories exist
        for category in ["helmet", "high_visibility_vest", "safety_footwear", "safety_harness"]:
            if category not in ppe_detection:
                ppe_detection[category] = PPEItem(
                    status=PPEStatus.UNKNOWN,
                    confidence=None,
                    notes="Not assessed in AI response.",
                )

        # Parse hazards
        hazards_raw = json_data.get("hazards", [])
        hazards: list[HazardItem] = []
        if isinstance(hazards_raw, list):
            for h in hazards_raw:
                if isinstance(h, dict):
                    severity_val = h.get("severity", "Medium")
                    try:
                        severity = SeverityLevel(severity_val)
                    except ValueError:
                        found_sev = None
                        for s in SeverityLevel:
                            if s.value.lower() == str(severity_val).strip().lower():
                                found_sev = s
                                break
                        severity = found_sev if found_sev is not None else SeverityLevel.MEDIUM

                    hazards.append(
                        HazardItem(
                            hazard=h.get("hazard", "Unspecified hazard"),
                            severity=severity,
                            evidence=h.get("evidence", ""),
                            corrective_action=h.get("corrective_action", ""),
                        )
                    )

        # Parse overall status
        status_val = json_data.get("overall_status", "Needs Attention")
        try:
            overall_status = OverallStatus(status_val)
        except ValueError:
            found_os = None
            for os_enum in OverallStatus:
                if os_enum.value.lower() == str(status_val).strip().lower():
                    found_os = os_enum
                    break
            overall_status = found_os if found_os is not None else OverallStatus.NEEDS_ATTENTION

        # Parse safety score
        safety_score = json_data.get("safety_score", 50)
        try:
            safety_score = int(safety_score)
            safety_score = max(0, min(100, safety_score))
        except (TypeError, ValueError):
            safety_score = 50

        limitations = json_data.get("limitations")
        if not isinstance(limitations, list) or not limitations:
            limitations = [
                "Image-based observations may miss hazards outside the camera view."
            ]

        result = SafetyAuditResult(
            analysis_type="site_safety_audit",
            safety_score=safety_score,
            overall_status=overall_status,
            ppe_detection=ppe_detection,
            hazards=hazards,
            limitations=limitations,
        )

        return result, AnalysisMode.LIVE_AI

    except ConnectionError as e:
        raise e
    except Exception as e:
        raise ValueError(f"Failed to process safety analysis: {e}")

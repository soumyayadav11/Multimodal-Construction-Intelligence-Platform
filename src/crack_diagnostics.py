"""Crack Diagnostics & Structural Integrity module for construction image analysis."""
from __future__ import annotations

from typing import Optional
from PIL import Image

from src.schemas import (
    CrackDiagnosticsResult,
    DefectType,
    SeverityLevel,
    UrgencyLevel,
    AnalysisMode,
)
from src.ai_service import GeminiService, CRACK_DIAGNOSTICS_PROMPT, extract_json_from_response
from src.config import is_demo_mode


def get_demo_crack_result() -> CrackDiagnosticsResult:
    """Return a clearly-labeled demonstration crack diagnostics result.

    Returns:
        CrackDiagnosticsResult: Baseline demo analysis for crack diagnostics.
    """
    return CrackDiagnosticsResult(
        analysis_type="crack_diagnostics",
        defect_type=DefectType.HAIRLINE,
        estimated_width_mm=None,
        severity=SeverityLevel.LOW,
        possible_causes=[
            "Possible surface shrinkage during curing",
            "Minor thermal expansion or contraction",
        ],
        evidence=[
            "A thin visible line appears on the surface in this demonstration scenario.",
            "The crack pattern appears consistent with surface-level shrinkage.",
        ],
        recommended_actions=[
            "Measure the crack using an appropriate crack-width gauge and monitor for changes over time.",
            "Photograph the crack with a scale reference for future comparison.",
            "Consider surface sealant application if the crack is confirmed as non-structural.",
            "Consult a qualified structural engineer if the crack widens or new cracks appear.",
        ],
        urgency=UrgencyLevel.ROUTINE,
        professional_review_required=True,
        limitations=[
            "⚠️ THIS IS A DEMONSTRATION RESULT — not derived from any uploaded image.",
            "The image does not provide a reliable scale for crack-width measurement.",
            "A photograph alone cannot determine whether a crack is structural.",
            "Actual crack assessment requires physical inspection by a qualified engineer.",
        ],
    )


def analyze_crack(
    image: Image.Image,
    ai_service: Optional[GeminiService] = None,
) -> tuple[CrackDiagnosticsResult, AnalysisMode]:
    """Analyze a concrete/wall image for crack diagnostics.

    Args:
        image: PIL Image of the concrete or wall surface
        ai_service: Optional GeminiService instance (None for demo mode)

    Returns:
        Tuple of (CrackDiagnosticsResult, AnalysisMode)

    Raises:
        ConnectionError: If network connectivity to Gemini API fails.
        ValueError: If JSON extraction or response parsing fails.
    """
    if is_demo_mode() or ai_service is None:
        return get_demo_crack_result(), AnalysisMode.DEMONSTRATION

    try:
        # Get AI analysis
        response_text = ai_service.analyze_image(image, CRACK_DIAGNOSTICS_PROMPT)

        # Extract JSON
        json_data = extract_json_from_response(response_text)
        if json_data is None:
            raise ValueError("Could not extract valid JSON from AI response")

        # Parse defect type
        defect_type_val = json_data.get("defect_type", "Unknown / Insufficient Evidence")
        try:
            defect_type = DefectType(defect_type_val)
        except ValueError:
            found_dt = None
            for dt in DefectType:
                if dt.value.lower() == str(defect_type_val).strip().lower():
                    found_dt = dt
                    break
            defect_type = found_dt if found_dt is not None else DefectType.UNKNOWN

        # Parse severity
        severity_val = json_data.get("severity", "Medium")
        try:
            severity = SeverityLevel(severity_val)
        except ValueError:
            found_sev = None
            for s in SeverityLevel:
                if s.value.lower() == str(severity_val).strip().lower():
                    found_sev = s
                    break
            severity = found_sev if found_sev is not None else SeverityLevel.MEDIUM

        # Parse urgency
        urgency_val = json_data.get("urgency", "Routine Inspection")
        try:
            urgency = UrgencyLevel(urgency_val)
        except ValueError:
            found_urg = None
            for u in UrgencyLevel:
                if u.value.lower() == str(urgency_val).strip().lower():
                    found_urg = u
                    break
            urgency = found_urg if found_urg is not None else UrgencyLevel.ROUTINE

        # Parse estimated width - must be null if no scale reference
        estimated_width = json_data.get("estimated_width_mm")
        if estimated_width is not None:
            try:
                estimated_width = float(estimated_width)
                if estimated_width < 0:
                    estimated_width = None
            except (TypeError, ValueError):
                estimated_width = None

        possible_causes = json_data.get("possible_causes", [])
        if not isinstance(possible_causes, list):
            possible_causes = []

        evidence = json_data.get("evidence", [])
        if not isinstance(evidence, list):
            evidence = []

        recommended_actions = json_data.get("recommended_actions", [])
        if not isinstance(recommended_actions, list):
            recommended_actions = []

        professional_review = json_data.get("professional_review_required", True)
        if not isinstance(professional_review, bool):
            professional_review = True

        limitations = json_data.get("limitations")
        if not isinstance(limitations, list) or not limitations:
            limitations = [
                "A photograph alone cannot reliably establish actual crack width."
            ]

        result = CrackDiagnosticsResult(
            analysis_type="crack_diagnostics",
            defect_type=defect_type,
            estimated_width_mm=estimated_width,
            severity=severity,
            possible_causes=possible_causes,
            evidence=evidence,
            recommended_actions=recommended_actions,
            urgency=urgency,
            professional_review_required=professional_review,
            limitations=limitations,
        )

        return result, AnalysisMode.LIVE_AI

    except ConnectionError as e:
        raise e
    except Exception as e:
        raise ValueError(f"Failed to process crack analysis: {e}")

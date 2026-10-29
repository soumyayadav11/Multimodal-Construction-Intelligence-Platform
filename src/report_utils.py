"""Report generation and download utilities."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from src.schemas import ReportEnvelope, AnalysisMode


def create_report_envelope(
    data: dict[str, Any],
    analysis_mode: AnalysisMode = AnalysisMode.DEMONSTRATION,
) -> ReportEnvelope:
    """Create a standardized report envelope wrapping analysis results.

    Args:
        data: The analysis result dictionary
        analysis_mode: Whether this was live AI or demonstration

    Returns:
        ReportEnvelope with metadata and the analysis data
    """
    return ReportEnvelope(
        report_id=str(uuid.uuid4())[:8],
        generated_at=datetime.now().isoformat(),
        analysis_mode=analysis_mode,
        data=data,
    )


def generate_json_report(
    data: dict[str, Any],
    analysis_mode: AnalysisMode = AnalysisMode.DEMONSTRATION,
) -> str:
    """Generate a downloadable JSON report string.

    Args:
        data: The analysis result dictionary
        analysis_mode: Whether this was live AI or demonstration

    Returns:
        Pretty-printed JSON string
    """
    envelope = create_report_envelope(data, analysis_mode)
    return envelope.model_dump_json(indent=2)


def get_report_filename(analysis_type: str) -> str:
    """Generate a timestamped filename for a report.

    Args:
        analysis_type: Type of analysis (e.g., 'safety_audit', 'crack_diagnostics')

    Returns:
        Filename string like 'safety_audit_20261029_143022.json'
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{analysis_type}_{timestamp}.json"

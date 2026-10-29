"""Tests for report generation and JSON export utilities."""
from __future__ import annotations

import json
import pytest

from src.schemas import AnalysisMode
from src.report_utils import (
    create_report_envelope,
    generate_json_report,
    get_report_filename,
)


class TestReportEnvelope:
    """Tests for report envelope creation."""

    def test_envelope_structure(self):
        data = {"analysis_type": "test", "score": 85}
        envelope = create_report_envelope(data, AnalysisMode.DEMONSTRATION)
        assert envelope.platform == "Multimodal Construction Intelligence Platform"
        assert envelope.analysis_mode == AnalysisMode.DEMONSTRATION
        assert envelope.data == data
        assert envelope.generated_at is not None
        assert len(envelope.report_id) > 0

    def test_envelope_live_mode(self):
        envelope = create_report_envelope({"test": True}, AnalysisMode.LIVE_AI)
        assert envelope.analysis_mode == AnalysisMode.LIVE_AI

    def test_envelope_has_disclaimer(self):
        envelope = create_report_envelope({})
        assert "decision-support" in envelope.disclaimer.lower() or \
               "educational" in envelope.disclaimer.lower()


class TestJSONReport:
    """Tests for JSON report generation."""

    def test_valid_json_output(self):
        data = {"analysis_type": "safety_audit", "safety_score": 75}
        report = generate_json_report(data, AnalysisMode.DEMONSTRATION)
        
        # Must be valid JSON
        parsed = json.loads(report)
        assert isinstance(parsed, dict)

    def test_report_contains_data(self):
        data = {"analysis_type": "crack_diagnostics", "defect_type": "Hairline"}
        report = generate_json_report(data, AnalysisMode.LIVE_AI)
        parsed = json.loads(report)
        
        assert parsed["data"]["analysis_type"] == "crack_diagnostics"
        assert parsed["data"]["defect_type"] == "Hairline"
        assert parsed["analysis_mode"] == "Live AI"

    def test_report_has_timestamp(self):
        report = generate_json_report({"test": True})
        parsed = json.loads(report)
        assert "generated_at" in parsed
        assert len(parsed["generated_at"]) > 0

    def test_report_has_platform_name(self):
        report = generate_json_report({})
        parsed = json.loads(report)
        assert "platform" in parsed
        assert "Construction" in parsed["platform"]

    def test_empty_data_report(self):
        report = generate_json_report({})
        parsed = json.loads(report)
        assert parsed["data"] == {}

    def test_nested_data_serialization(self):
        data = {
            "analysis_type": "safety_audit",
            "ppe_detection": {
                "helmet": {"status": "Observed", "confidence": 0.9}
            },
            "hazards": [
                {"hazard": "Edge", "severity": "High"}
            ]
        }
        report = generate_json_report(data)
        parsed = json.loads(report)
        assert parsed["data"]["ppe_detection"]["helmet"]["confidence"] == 0.9


class TestReportFilename:
    """Tests for report filename generation."""

    def test_filename_format(self):
        filename = get_report_filename("safety_audit")
        assert filename.startswith("safety_audit_")
        assert filename.endswith(".json")

    def test_filename_different_types(self):
        f1 = get_report_filename("safety_audit")
        f2 = get_report_filename("crack_diagnostics")
        assert f1.startswith("safety_audit")
        assert f2.startswith("crack_diagnostics")

    def test_filename_has_timestamp(self):
        filename = get_report_filename("test")
        # Should be like test_20261029_143022.json
        parts = filename.replace(".json", "").split("_")
        assert len(parts) >= 3  # type_date_time

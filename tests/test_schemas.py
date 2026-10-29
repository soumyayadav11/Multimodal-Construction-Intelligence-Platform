"""Tests for Pydantic schemas validation."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.schemas import (
    PPEItem, PPEStatus, HazardItem, SeverityLevel, SafetyAuditResult,
    OverallStatus, CrackDiagnosticsResult, DefectType, UrgencyLevel,
    MaterialEstimate, ConstructionPlan, StructureType, LocationTier,
    QualityLevel, ValuationResult, WeatherAdvisory, WeatherCondition,
    RiskLevel, WeatherAlert, ChecklistItem, ReportEnvelope, AnalysisMode,
)


class TestPPEItem:
    """Tests for PPE item schema."""

    def test_valid_ppe_item(self):
        item = PPEItem(status=PPEStatus.OBSERVED, confidence=0.85, notes="Helmet visible")
        assert item.status == PPEStatus.OBSERVED
        assert item.confidence == 0.85

    def test_ppe_item_null_confidence(self):
        item = PPEItem(status=PPEStatus.UNKNOWN, confidence=None, notes="Cannot determine")
        assert item.confidence is None

    def test_ppe_item_invalid_confidence_high(self):
        with pytest.raises(ValidationError):
            PPEItem(status=PPEStatus.OBSERVED, confidence=1.5, notes="Invalid")

    def test_ppe_item_invalid_confidence_negative(self):
        with pytest.raises(ValidationError):
            PPEItem(status=PPEStatus.OBSERVED, confidence=-0.1, notes="Invalid")

    def test_ppe_status_values(self):
        for status in PPEStatus:
            item = PPEItem(status=status)
            assert item.status == status


class TestHazardItem:
    """Tests for hazard item schema."""

    def test_valid_hazard(self):
        hazard = HazardItem(
            hazard="Unprotected edge",
            severity=SeverityLevel.HIGH,
            evidence="Edge visible",
            corrective_action="Install barriers"
        )
        assert hazard.severity == SeverityLevel.HIGH

    def test_hazard_severity_values(self):
        for severity in SeverityLevel:
            hazard = HazardItem(hazard="Test", severity=severity)
            assert hazard.severity == severity


class TestSafetyAuditResult:
    """Tests for safety audit result schema."""

    def test_valid_safety_result(self):
        result = SafetyAuditResult(
            safety_score=75,
            overall_status=OverallStatus.NEEDS_ATTENTION,
            ppe_detection={
                "helmet": PPEItem(status=PPEStatus.OBSERVED, confidence=0.9, notes="Visible"),
            },
            hazards=[],
            limitations=["Test limitation"],
        )
        assert result.safety_score == 75
        assert result.overall_status == OverallStatus.NEEDS_ATTENTION

    def test_safety_score_too_high(self):
        with pytest.raises(ValidationError):
            SafetyAuditResult(
                safety_score=150,
                overall_status=OverallStatus.SAFE,
                ppe_detection={},
            )

    def test_safety_score_too_low(self):
        with pytest.raises(ValidationError):
            SafetyAuditResult(
                safety_score=-10,
                overall_status=OverallStatus.SAFE,
                ppe_detection={},
            )

    def test_safety_score_boundary_zero(self):
        result = SafetyAuditResult(
            safety_score=0,
            overall_status=OverallStatus.UNSAFE,
            ppe_detection={},
        )
        assert result.safety_score == 0

    def test_safety_score_boundary_hundred(self):
        result = SafetyAuditResult(
            safety_score=100,
            overall_status=OverallStatus.SAFE,
            ppe_detection={},
        )
        assert result.safety_score == 100

    def test_invalid_overall_status(self):
        with pytest.raises(ValidationError):
            SafetyAuditResult(
                safety_score=50,
                overall_status="Invalid Status",
                ppe_detection={},
            )


class TestCrackDiagnosticsResult:
    """Tests for crack diagnostics result schema."""

    def test_valid_crack_result(self):
        result = CrackDiagnosticsResult(
            defect_type=DefectType.HAIRLINE,
            estimated_width_mm=None,
            severity=SeverityLevel.LOW,
            possible_causes=["Shrinkage"],
            urgency=UrgencyLevel.ROUTINE,
            professional_review_required=True,
        )
        assert result.defect_type == DefectType.HAIRLINE
        assert result.estimated_width_mm is None

    def test_crack_width_null_handling(self):
        result = CrackDiagnosticsResult(
            defect_type=DefectType.UNKNOWN,
            estimated_width_mm=None,
            severity=SeverityLevel.MEDIUM,
            urgency=UrgencyLevel.SOON,
        )
        assert result.estimated_width_mm is None

    def test_crack_width_valid_value(self):
        result = CrackDiagnosticsResult(
            defect_type=DefectType.SETTLEMENT,
            estimated_width_mm=2.5,
            severity=SeverityLevel.HIGH,
            urgency=UrgencyLevel.URGENT,
        )
        assert result.estimated_width_mm == 2.5

    def test_crack_width_negative_rejected(self):
        with pytest.raises(ValidationError):
            CrackDiagnosticsResult(
                defect_type=DefectType.STRUCTURAL_SHEAR,
                estimated_width_mm=-1.0,
                severity=SeverityLevel.CRITICAL,
                urgency=UrgencyLevel.IMMEDIATE,
            )

    def test_all_defect_types(self):
        for defect in DefectType:
            result = CrackDiagnosticsResult(
                defect_type=defect,
                severity=SeverityLevel.LOW,
                urgency=UrgencyLevel.ROUTINE,
            )
            assert result.defect_type == defect

    def test_all_urgency_levels(self):
        for urgency in UrgencyLevel:
            result = CrackDiagnosticsResult(
                defect_type=DefectType.UNKNOWN,
                severity=SeverityLevel.LOW,
                urgency=urgency,
            )
            assert result.urgency == urgency


class TestMaterialEstimate:
    """Tests for material estimate schema."""

    def test_valid_material(self):
        mat = MaterialEstimate(
            material="Steel",
            estimated_quantity=6000.0,
            unit="kg",
            assumption="4 kg per sq ft",
        )
        assert mat.estimated_quantity == 6000.0

    def test_negative_quantity_rejected(self):
        with pytest.raises(ValidationError):
            MaterialEstimate(
                material="Cement",
                estimated_quantity=-100.0,
                unit="bags",
            )


class TestValuationResult:
    """Tests for valuation result schema."""

    def test_valid_valuation(self):
        val = ValuationResult(
            construction_cost_inr=5_000_000.0,
            land_cost_inr=10_000_000.0,
            market_rate_per_sqft=5000.0,
            estimated_property_value_inr=7_500_000.0,
            total_asset_value_inr=17_500_000.0,
            valuation_method="Market comparison",
        )
        assert val.construction_cost_inr == 5_000_000.0

    def test_valuation_without_optional_fields(self):
        val = ValuationResult(construction_cost_inr=3_000_000.0)
        assert val.land_cost_inr is None
        assert val.market_rate_per_sqft is None
        assert val.estimated_property_value_inr is None


class TestReportEnvelope:
    """Tests for report envelope schema."""

    def test_valid_envelope(self):
        envelope = ReportEnvelope(
            data={"analysis_type": "test", "result": "ok"},
            analysis_mode=AnalysisMode.DEMONSTRATION,
        )
        assert envelope.platform == "Multimodal Construction Intelligence Platform"
        assert envelope.analysis_mode == AnalysisMode.DEMONSTRATION
        assert "test" in str(envelope.data)

    def test_envelope_has_timestamp(self):
        envelope = ReportEnvelope(data={"test": True})
        assert envelope.generated_at is not None
        assert len(envelope.generated_at) > 0

    def test_envelope_modes(self):
        for mode in AnalysisMode:
            envelope = ReportEnvelope(data={}, analysis_mode=mode)
            assert envelope.analysis_mode == mode

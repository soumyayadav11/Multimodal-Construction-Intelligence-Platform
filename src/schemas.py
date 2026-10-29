"""Pydantic v2 schemas for all analysis modules.

This module defines the standardized data contracts, enumerations,
and response envelopes used across site safety audits, crack diagnostics,
cost estimation, valuation, and weather advisory services.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# Enums
# ============================================================================

class PPEStatus(str, Enum):
    """Observation status of Personal Protective Equipment (PPE)."""

    OBSERVED = "Observed"
    NOT_OBSERVED = "Not Observed"
    UNKNOWN = "Unknown"
    NOT_APPLICABLE = "Not Applicable"


class SeverityLevel(str, Enum):
    """Standardized severity rating for hazards, defects, and weather alerts."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class OverallStatus(str, Enum):
    """High-level safety compliance or condition status."""

    SAFE = "Safe"
    NEEDS_ATTENTION = "Needs Attention"
    CRITICAL = "Critical"
    UNSAFE = "Unsafe"


class DefectType(str, Enum):
    """Classification of concrete, masonry, or structural defects."""

    HAIRLINE = "Hairline"
    SETTLEMENT = "Settlement"
    STRUCTURAL_SHEAR = "Structural Shear"
    THERMAL_EXPANSION = "Thermal Expansion"
    SPALLING = "Spalling"
    UNKNOWN = "Unknown / Insufficient Evidence"


class UrgencyLevel(str, Enum):
    """Recommended urgency for inspection and remedial action."""

    ROUTINE = "Routine Inspection"
    SOON = "Inspect Soon"
    URGENT = "Urgent"
    IMMEDIATE = "Immediate Action Required"


class WeatherCondition(str, Enum):
    """Dominant on-site weather condition."""

    HIGH_WIND = "High Wind"
    HEAVY_RAIN = "Heavy Rain"
    EXTREME_HEAT = "Extreme Heat"
    NORMAL = "Normal"


class RiskLevel(str, Enum):
    """Overall environmental or site operational risk level."""

    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    EXTREME = "Extreme"


class StructureType(str, Enum):
    """Type of building or civil structure."""

    RESIDENTIAL = "Residential"
    COMMERCIAL = "Commercial"
    MIXED_USE = "Mixed-Use"


class LocationTier(str, Enum):
    """Geographic market tier governing material and labor rates."""

    TIER_1 = "Tier 1"
    TIER_2 = "Tier 2"
    TIER_3 = "Tier 3"


class QualityLevel(str, Enum):
    """Construction finish and material specification grade."""

    BASIC = "Basic"
    STANDARD = "Standard"
    PREMIUM = "Premium"
    LUXURY = "Luxury"


class AnalysisMode(str, Enum):
    """Execution mode of the intelligence engine."""

    LIVE_AI = "Live AI"
    DEMONSTRATION = "Demonstration"


# ============================================================================
# PPE & Safety Audit Models
# ============================================================================

class PPEItem(BaseModel):
    """Status and detection confidence for a single PPE category."""

    model_config = ConfigDict(str_strip_whitespace=True)

    status: PPEStatus
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    notes: str = ""


class HazardItem(BaseModel):
    """Details of an identified safety hazard on site."""

    model_config = ConfigDict(str_strip_whitespace=True)

    hazard: str
    severity: SeverityLevel
    evidence: str = ""
    corrective_action: str = ""


class SafetyAuditResult(BaseModel):
    """Structured report outcome for a multimodal site safety audit."""

    model_config = ConfigDict(str_strip_whitespace=True)

    analysis_type: str = "site_safety_audit"
    safety_score: int = Field(ge=0, le=100)
    overall_status: OverallStatus
    ppe_detection: dict[str, PPEItem]
    hazards: list[HazardItem] = []
    limitations: list[str] = []

    @field_validator("safety_score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        """Ensure safety score is bounded within 0 to 100."""
        if not 0 <= v <= 100:
            raise ValueError("Safety score must be between 0 and 100")
        return v


# ============================================================================
# Crack & Structural Defect Diagnostics Models
# ============================================================================

class CrackDiagnosticsResult(BaseModel):
    """Diagnostic evaluation for structural and surface cracks."""

    model_config = ConfigDict(str_strip_whitespace=True)

    analysis_type: str = "crack_diagnostics"
    defect_type: DefectType
    estimated_width_mm: Optional[float] = Field(default=None, ge=0.0)
    severity: SeverityLevel
    possible_causes: list[str] = []
    evidence: list[str] = []
    recommended_actions: list[str] = []
    urgency: UrgencyLevel
    professional_review_required: bool = True
    limitations: list[str] = []


# ============================================================================
# Planning, Cost Estimation & Valuation Models
# ============================================================================

class MaterialEstimate(BaseModel):
    """Estimated bill of quantities item for key construction materials."""

    model_config = ConfigDict(str_strip_whitespace=True)

    material: str
    estimated_quantity: float = Field(ge=0.0)
    unit: str
    assumption: str = ""


class MilestoneStage(BaseModel):
    """Construction milestone stage and percentage range."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    percentage_range: tuple[int, int]  # (start%, end%)
    description: str = ""


class ConstructionPlan(BaseModel):
    """Comprehensive budget, progress, and material breakdown."""

    model_config = ConfigDict(str_strip_whitespace=True)

    structure_type: StructureType
    area_sqft: float = Field(gt=0)
    location_tier: LocationTier
    quality_level: QualityLevel
    rate_per_sqft: float = Field(gt=0)
    completion_percentage: float = Field(ge=0, le=100)
    estimated_budget_inr: float = Field(ge=0)
    expenditure_incurred_inr: float = Field(ge=0)
    remaining_budget_inr: float = Field(ge=0)
    materials: list[MaterialEstimate] = []
    current_milestone: str = ""


class ValuationResult(BaseModel):
    """Valuation assessment incorporating structure, land, and market rates."""

    model_config = ConfigDict(str_strip_whitespace=True)

    construction_cost_inr: float = Field(ge=0)
    land_cost_inr: Optional[float] = Field(default=None, ge=0)
    market_rate_per_sqft: Optional[float] = Field(default=None, ge=0)
    estimated_property_value_inr: Optional[float] = Field(default=None, ge=0)
    total_asset_value_inr: Optional[float] = Field(default=None, ge=0)
    valuation_method: str = ""
    assumptions: list[str] = []


# ============================================================================
# Weather Advisory Models
# ============================================================================

class WeatherAlert(BaseModel):
    """Advisory alert for specific weather risks."""

    model_config = ConfigDict(str_strip_whitespace=True)

    category: str
    message: str
    priority: SeverityLevel = SeverityLevel.MEDIUM


class ChecklistItem(BaseModel):
    """Actionable safety or preparation checklist item."""

    model_config = ConfigDict(str_strip_whitespace=True)

    item: str
    checked: bool = False


class WeatherAdvisory(BaseModel):
    """Weather condition assessment and construction site protocol advisory."""

    model_config = ConfigDict(str_strip_whitespace=True)

    condition: WeatherCondition
    risk_level: RiskLevel
    alerts: list[WeatherAlert] = []
    preventive_actions: list[str] = []
    checklist: list[ChecklistItem] = []
    general_notes: list[str] = []


# ============================================================================
# Generic Report Envelope
# ============================================================================

class ReportEnvelope(BaseModel):
    """Standardized metadata envelope enclosing intelligence report outputs."""

    model_config = ConfigDict(str_strip_whitespace=True)

    report_id: str = ""
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    platform: str = "Multimodal Construction Intelligence Platform"
    analysis_mode: AnalysisMode = AnalysisMode.DEMONSTRATION
    data: dict[str, Any] = Field(default_factory=dict)
    disclaimer: str = (
        "This report is for decision-support and educational purposes only. "
        "It does not replace professional engineering assessment."
    )

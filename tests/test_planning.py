"""Tests for construction planning and cost calculation module."""
from __future__ import annotations

import pytest

from src.schemas import StructureType, LocationTier, QualityLevel
from src.planning import (
    calculate_construction_plan, format_inr, get_default_rate,
    get_current_milestone, get_milestones,
    DEFAULT_RATES, TIER_MULTIPLIERS, STEEL_KG_PER_SQFT, CEMENT_BAGS_PER_SQFT,
)


class TestConstructionBudget:
    """Tests for construction budget calculations."""

    def test_basic_budget_calculation(self):
        plan = calculate_construction_plan(
            structure_type=StructureType.RESIDENTIAL,
            area_sqft=1000.0,
            location_tier=LocationTier.TIER_2,
            quality_level=QualityLevel.STANDARD,
            rate_per_sqft=2000.0,
            completion_percentage=50.0,
        )
        assert plan.estimated_budget_inr == 2_000_000.0  # 1000 * 2000
        assert plan.expenditure_incurred_inr == 1_000_000.0  # 2M * 50%
        assert plan.remaining_budget_inr == 1_000_000.0  # 2M - 1M

    def test_zero_completion(self):
        plan = calculate_construction_plan(
            structure_type=StructureType.RESIDENTIAL,
            area_sqft=1500.0,
            location_tier=LocationTier.TIER_1,
            quality_level=QualityLevel.BASIC,
            rate_per_sqft=1500.0,
            completion_percentage=0.0,
        )
        assert plan.expenditure_incurred_inr == 0.0
        assert plan.remaining_budget_inr == plan.estimated_budget_inr

    def test_full_completion(self):
        plan = calculate_construction_plan(
            structure_type=StructureType.COMMERCIAL,
            area_sqft=2000.0,
            location_tier=LocationTier.TIER_2,
            quality_level=QualityLevel.PREMIUM,
            rate_per_sqft=3000.0,
            completion_percentage=100.0,
        )
        assert plan.expenditure_incurred_inr == plan.estimated_budget_inr
        assert plan.remaining_budget_inr == 0.0

    def test_budget_formula_correctness(self):
        """Verify: budget = area * rate, expenditure = budget * completion/100"""
        area = 1234.0
        rate = 1750.0
        completion = 35.0
        plan = calculate_construction_plan(
            structure_type=StructureType.MIXED_USE,
            area_sqft=area,
            location_tier=LocationTier.TIER_3,
            quality_level=QualityLevel.STANDARD,
            rate_per_sqft=rate,
            completion_percentage=completion,
        )
        expected_budget = round(area * rate, 2)
        expected_expenditure = round(expected_budget * completion / 100, 2)
        expected_remaining = round(expected_budget - expected_expenditure, 2)

        assert plan.estimated_budget_inr == expected_budget
        assert plan.expenditure_incurred_inr == expected_expenditure
        assert plan.remaining_budget_inr == expected_remaining


class TestMaterialEstimates:
    """Tests for material estimation calculations."""

    def test_steel_estimate_residential(self):
        plan = calculate_construction_plan(
            structure_type=StructureType.RESIDENTIAL,
            area_sqft=1000.0,
            location_tier=LocationTier.TIER_2,
            quality_level=QualityLevel.STANDARD,
            rate_per_sqft=2000.0,
            completion_percentage=0.0,
        )
        steel = next(m for m in plan.materials if m.material == "Steel")
        expected = 1000.0 * STEEL_KG_PER_SQFT[StructureType.RESIDENTIAL]
        assert steel.estimated_quantity == expected
        assert steel.unit == "kg"

    def test_cement_estimate_commercial(self):
        plan = calculate_construction_plan(
            structure_type=StructureType.COMMERCIAL,
            area_sqft=2000.0,
            location_tier=LocationTier.TIER_1,
            quality_level=QualityLevel.PREMIUM,
            rate_per_sqft=3000.0,
            completion_percentage=50.0,
        )
        cement = next(m for m in plan.materials if m.material == "Cement")
        expected = 2000.0 * CEMENT_BAGS_PER_SQFT[StructureType.COMMERCIAL]
        assert cement.estimated_quantity == expected

    def test_materials_have_assumptions(self):
        plan = calculate_construction_plan(
            structure_type=StructureType.RESIDENTIAL,
            area_sqft=500.0,
            location_tier=LocationTier.TIER_2,
            quality_level=QualityLevel.BASIC,
            rate_per_sqft=1200.0,
            completion_percentage=10.0,
        )
        for mat in plan.materials:
            assert mat.assumption != "", f"Material {mat.material} missing assumption"


class TestINRFormatting:
    """Tests for Indian Rupee formatting."""

    def test_crore_formatting(self):
        result = format_inr(1_50_00_000)  # 1.5 crore
        assert "Crore" in result
        assert "₹" in result

    def test_lakh_formatting(self):
        result = format_inr(5_00_000)  # 5 lakhs
        assert "Lakh" in result
        assert "₹" in result

    def test_thousand_formatting(self):
        result = format_inr(50_000)
        assert "₹" in result

    def test_small_amount(self):
        result = format_inr(500)
        assert "₹" in result
        assert "500" in result

    def test_zero_amount(self):
        result = format_inr(0)
        assert "₹" in result

    def test_negative_amount(self):
        result = format_inr(-5_00_000)
        assert "-" in result

    def test_large_amount(self):
        result = format_inr(10_00_00_000)  # 10 crores
        assert "Crore" in result


class TestDefaultRates:
    """Tests for default construction rates."""

    def test_tier_1_multiplier(self):
        rate = get_default_rate(QualityLevel.STANDARD, LocationTier.TIER_1)
        base = DEFAULT_RATES[QualityLevel.STANDARD]
        expected = round(base * TIER_MULTIPLIERS[LocationTier.TIER_1], 2)
        assert rate == expected

    def test_tier_3_multiplier(self):
        rate = get_default_rate(QualityLevel.BASIC, LocationTier.TIER_3)
        base = DEFAULT_RATES[QualityLevel.BASIC]
        expected = round(base * TIER_MULTIPLIERS[LocationTier.TIER_3], 2)
        assert rate == expected

    def test_all_quality_levels(self):
        for quality in QualityLevel:
            rate = get_default_rate(quality, LocationTier.TIER_2)
            assert rate > 0


class TestMilestones:
    """Tests for construction milestone tracking."""

    def test_planning_milestone(self):
        assert get_current_milestone(0) == "Planning & Approvals"

    def test_foundation_milestone(self):
        assert get_current_milestone(10) == "Foundation"

    def test_completion_milestone(self):
        assert get_current_milestone(100) == "Completion & Handover"

    def test_mid_construction(self):
        milestone = get_current_milestone(50)
        assert milestone in ["Brickwork & Masonry", "Structural Frame"]

    def test_milestones_list(self):
        milestones = get_milestones()
        assert len(milestones) >= 5
        for m in milestones:
            assert m.name
            assert m.percentage_range[0] < m.percentage_range[1]

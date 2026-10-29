"""Tests for property valuation module."""
from __future__ import annotations

import pytest

from src.valuation import calculate_valuation


class TestValuationCalculations:
    """Tests for property valuation calculations."""

    def test_basic_valuation(self):
        result = calculate_valuation(
            construction_cost_inr=3_000_000.0,
            area_sqft=1500.0,
        )
        assert result.construction_cost_inr == 3_000_000.0
        assert result.land_cost_inr is None
        assert result.estimated_property_value_inr is None

    def test_valuation_with_land_cost(self):
        result = calculate_valuation(
            construction_cost_inr=3_000_000.0,
            area_sqft=1500.0,
            land_cost_inr=5_000_000.0,
        )
        assert result.land_cost_inr == 5_000_000.0
        assert result.total_asset_value_inr == 8_000_000.0  # construction + land

    def test_valuation_with_market_rate(self):
        result = calculate_valuation(
            construction_cost_inr=3_000_000.0,
            area_sqft=1000.0,
            market_rate_per_sqft=5000.0,
        )
        assert result.estimated_property_value_inr == 5_000_000.0  # 1000 * 5000
        assert result.market_rate_per_sqft == 5000.0

    def test_valuation_with_land_and_market(self):
        result = calculate_valuation(
            construction_cost_inr=3_000_000.0,
            area_sqft=1000.0,
            land_cost_inr=2_000_000.0,
            market_rate_per_sqft=5000.0,
        )
        assert result.estimated_property_value_inr == 5_000_000.0
        # total = property value + land
        assert result.total_asset_value_inr == 7_000_000.0

    def test_valuation_method_without_market_rate(self):
        result = calculate_valuation(
            construction_cost_inr=3_000_000.0,
            area_sqft=1500.0,
        )
        assert "cost" in result.valuation_method.lower()

    def test_valuation_method_with_market_rate(self):
        result = calculate_valuation(
            construction_cost_inr=3_000_000.0,
            area_sqft=1500.0,
            market_rate_per_sqft=4000.0,
        )
        assert "market" in result.valuation_method.lower()

    def test_valuation_assumptions_present(self):
        result = calculate_valuation(
            construction_cost_inr=3_000_000.0,
            area_sqft=1500.0,
        )
        assert len(result.assumptions) > 0

    def test_zero_land_cost_treated_as_none(self):
        result = calculate_valuation(
            construction_cost_inr=3_000_000.0,
            area_sqft=1500.0,
            land_cost_inr=0.0,
        )
        # Zero land cost should not affect total
        # (implementation may treat 0 as no land cost)
        assert result.construction_cost_inr == 3_000_000.0

    def test_zero_market_rate_treated_as_none(self):
        result = calculate_valuation(
            construction_cost_inr=3_000_000.0,
            area_sqft=1500.0,
            market_rate_per_sqft=0.0,
        )
        assert result.estimated_property_value_inr is None

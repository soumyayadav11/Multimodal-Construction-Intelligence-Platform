"""Real estate valuation module for Indian property market."""
from __future__ import annotations

from typing import Optional

from src.schemas import ValuationResult


def calculate_valuation(
    construction_cost_inr: float,
    area_sqft: float,
    land_cost_inr: Optional[float] = None,
    market_rate_per_sqft: Optional[float] = None,
) -> ValuationResult:
    """Calculate preliminary property valuation.

    This provides a simplified estimate based on user-supplied inputs.
    It does not constitute an official property valuation.

    Args:
        construction_cost_inr: Total estimated construction cost
        area_sqft: Built-up area in square feet
        land_cost_inr: Optional land acquisition cost
        market_rate_per_sqft: Optional market rate per sq ft for property value estimation

    Returns:
        ValuationResult with calculated values and documented assumptions
    """
    assumptions = [
        "Construction cost is based on user-supplied rate per sq ft and area.",
        "This is a preliminary estimate, not a certified property valuation.",
        "Actual property value depends on location, amenities, market conditions, and other factors.",
    ]

    estimated_property_value = None
    total_asset_value = None
    valuation_method = "Cost-based estimate using user-supplied construction rate"

    if market_rate_per_sqft and market_rate_per_sqft > 0:
        estimated_property_value = area_sqft * market_rate_per_sqft
        valuation_method = "Market comparison using user-supplied market rate per sq ft"
        assumptions.append(
            f"Market rate of ₹{market_rate_per_sqft:,.0f}/sq ft is user-supplied and may not reflect current market conditions."
        )

    # Calculate total asset value
    if estimated_property_value is not None:
        total_asset_value = estimated_property_value
        if land_cost_inr and land_cost_inr > 0:
            total_asset_value = estimated_property_value + land_cost_inr
            assumptions.append("Total asset value includes land cost and estimated property value.")
    elif land_cost_inr and land_cost_inr > 0:
        total_asset_value = construction_cost_inr + land_cost_inr
        assumptions.append("Total asset value is sum of construction cost and land cost (no market rate provided).")

    if land_cost_inr and land_cost_inr > 0:
        assumptions.append("Land cost is user-supplied and treated separately from construction cost.")

    return ValuationResult(
        construction_cost_inr=round(construction_cost_inr, 2),
        land_cost_inr=round(land_cost_inr, 2) if land_cost_inr else None,
        market_rate_per_sqft=round(market_rate_per_sqft, 2) if market_rate_per_sqft else None,
        estimated_property_value_inr=round(estimated_property_value, 2) if estimated_property_value else None,
        total_asset_value_inr=round(total_asset_value, 2) if total_asset_value else None,
        valuation_method=valuation_method,
        assumptions=assumptions,
    )

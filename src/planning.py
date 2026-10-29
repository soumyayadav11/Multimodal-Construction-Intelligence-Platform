"""Construction planning, cost calculation, and material estimation module."""
from __future__ import annotations

from src.schemas import (
    StructureType,
    LocationTier,
    QualityLevel,
    ConstructionPlan,
    MaterialEstimate,
    MilestoneStage,
)


# Default construction rates per sq ft (INR) - configurable assumptions
DEFAULT_RATES: dict[QualityLevel, float] = {
    QualityLevel.BASIC: 1200.0,
    QualityLevel.STANDARD: 1800.0,
    QualityLevel.PREMIUM: 2800.0,
    QualityLevel.LUXURY: 4500.0,
}

# Location tier multipliers
TIER_MULTIPLIERS: dict[LocationTier, float] = {
    LocationTier.TIER_1: 1.3,
    LocationTier.TIER_2: 1.0,
    LocationTier.TIER_3: 0.8,
}

# Material estimation assumptions per sq ft
STEEL_KG_PER_SQFT: dict[StructureType, float] = {
    StructureType.RESIDENTIAL: 4.0,
    StructureType.COMMERCIAL: 5.5,
    StructureType.MIXED_USE: 4.8,
}

CEMENT_BAGS_PER_SQFT: dict[StructureType, float] = {
    StructureType.RESIDENTIAL: 0.4,
    StructureType.COMMERCIAL: 0.5,
    StructureType.MIXED_USE: 0.45,
}

# Construction milestones
MILESTONES: list[MilestoneStage] = [
    MilestoneStage(
        name="Planning & Approvals",
        percentage_range=(0, 5),
        description="Design, permits, and regulatory approvals",
    ),
    MilestoneStage(
        name="Foundation",
        percentage_range=(5, 20),
        description="Site preparation, excavation, and foundation work",
    ),
    MilestoneStage(
        name="Structural Frame",
        percentage_range=(20, 45),
        description="Column, beam, and slab construction",
    ),
    MilestoneStage(
        name="Brickwork & Masonry",
        percentage_range=(45, 60),
        description="Wall construction and masonry work",
    ),
    MilestoneStage(
        name="MEP Services",
        percentage_range=(60, 75),
        description="Mechanical, electrical, and plumbing installations",
    ),
    MilestoneStage(
        name="Finishing",
        percentage_range=(75, 95),
        description="Plastering, painting, flooring, and fixtures",
    ),
    MilestoneStage(
        name="Completion & Handover",
        percentage_range=(95, 100),
        description="Final inspection, testing, and handover",
    ),
]


def get_default_rate(quality: QualityLevel, tier: LocationTier) -> float:
    """Get the default construction rate per sq ft based on quality and location tier.

    Args:
        quality: Construction quality level
        tier: City tier classification

    Returns:
        Default rate per sq ft in INR
    """
    base_rate = DEFAULT_RATES.get(quality, DEFAULT_RATES[QualityLevel.STANDARD])
    multiplier = TIER_MULTIPLIERS.get(tier, 1.0)
    return round(base_rate * multiplier, 2)


def calculate_construction_plan(
    structure_type: StructureType,
    area_sqft: float,
    location_tier: LocationTier,
    quality_level: QualityLevel,
    rate_per_sqft: float,
    completion_percentage: float,
) -> ConstructionPlan:
    """Calculate construction budget, expenditure, and material estimates.

    Args:
        structure_type: Type of structure
        area_sqft: Built-up area in square feet
        location_tier: City tier for cost adjustment
        quality_level: Construction quality/finish level
        rate_per_sqft: Construction rate per sq ft in INR
        completion_percentage: Current project completion (0-100)

    Returns:
        ConstructionPlan with all calculated values
    """
    # Core calculations
    estimated_budget = area_sqft * rate_per_sqft
    expenditure_incurred = estimated_budget * (completion_percentage / 100)
    remaining_budget = estimated_budget - expenditure_incurred

    # Material estimates
    steel_rate = STEEL_KG_PER_SQFT.get(structure_type, 4.0)
    cement_rate = CEMENT_BAGS_PER_SQFT.get(structure_type, 0.4)

    materials = [
        MaterialEstimate(
            material="Steel",
            estimated_quantity=round(area_sqft * steel_rate, 2),
            unit="kg",
            assumption=f"{steel_rate} kg per sq ft for {structure_type.value} construction",
        ),
        MaterialEstimate(
            material="Cement",
            estimated_quantity=round(area_sqft * cement_rate, 2),
            unit="bags (50 kg)",
            assumption=f"{cement_rate} bags per sq ft for {structure_type.value} construction",
        ),
    ]

    # Determine current milestone
    current_milestone = get_current_milestone(completion_percentage)

    return ConstructionPlan(
        structure_type=structure_type,
        area_sqft=area_sqft,
        location_tier=location_tier,
        quality_level=quality_level,
        rate_per_sqft=rate_per_sqft,
        completion_percentage=completion_percentage,
        estimated_budget_inr=round(estimated_budget, 2),
        expenditure_incurred_inr=round(expenditure_incurred, 2),
        remaining_budget_inr=round(remaining_budget, 2),
        materials=materials,
        current_milestone=current_milestone,
    )


def get_current_milestone(completion_percentage: float) -> str:
    """Determine the current construction milestone based on completion percentage."""
    for milestone in MILESTONES:
        start, end = milestone.percentage_range
        if start <= completion_percentage <= end:
            return milestone.name
    return MILESTONES[-1].name


def format_inr(amount: float) -> str:
    """Format amount in Indian Rupee notation with lakhs and crores.

    Args:
        amount: Amount in INR

    Returns:
        Formatted string like '₹12.50 Lakhs' or '₹1.25 Crores'
    """
    if amount < 0:
        return f"-{format_inr(abs(amount))}"

    if amount >= 1_00_00_000:  # 1 crore
        return f"₹{amount / 1_00_00_000:.2f} Crores"
    elif amount >= 1_00_000:  # 1 lakh
        return f"₹{amount / 1_00_000:.2f} Lakhs"
    elif amount >= 1_000:
        return f"₹{amount:,.0f}"
    else:
        return f"₹{amount:.2f}"


def get_milestones() -> list[MilestoneStage]:
    """Return the list of construction milestones."""
    return MILESTONES

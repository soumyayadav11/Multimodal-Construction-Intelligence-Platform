"""Weather-aware construction safety advisory module.

Uses deterministic, testable rules rather than generative AI.
"""
from __future__ import annotations

from src.schemas import (
    WeatherCondition,
    RiskLevel,
    SeverityLevel,
    WeatherAdvisory,
    WeatherAlert,
    ChecklistItem,
)


def get_weather_advisory(condition: WeatherCondition) -> WeatherAdvisory:
    """Generate weather-specific safety advisory using rule-based logic.

    Args:
        condition: Current weather condition

    Returns:
        WeatherAdvisory with alerts, preventive actions, and checklists
    """
    if condition == WeatherCondition.HIGH_WIND:
        return _high_wind_advisory()
    elif condition == WeatherCondition.HEAVY_RAIN:
        return _heavy_rain_advisory()
    elif condition == WeatherCondition.EXTREME_HEAT:
        return _extreme_heat_advisory()
    else:
        return _normal_advisory()


def _high_wind_advisory() -> WeatherAdvisory:
    return WeatherAdvisory(
        condition=WeatherCondition.HIGH_WIND,
        risk_level=RiskLevel.HIGH,
        alerts=[
            WeatherAlert(
                category="Crane Operations",
                message="Check site-specific wind thresholds and equipment manufacturer instructions. Suspend crane lifting if applicable thresholds are exceeded.",
                priority=SeverityLevel.CRITICAL,
            ),
            WeatherAlert(
                category="Work at Height",
                message="Suspend work at height when wind speeds exceed safe limits per site safety plan.",
                priority=SeverityLevel.HIGH,
            ),
            WeatherAlert(
                category="Loose Materials",
                message="Secure all loose materials, temporary structures, scaffolding nets, and signage.",
                priority=SeverityLevel.HIGH,
            ),
        ],
        preventive_actions=[
            "Verify wind speed using on-site anemometer or local weather station data.",
            "Suspend crane operations when manufacturer-specified wind limits are exceeded.",
            "Suspend work at height when wind creates unsafe conditions.",
            "Secure loose materials and temporary structures.",
            "Ensure scaffolding is properly anchored and toe-boards are in place.",
            "Brief all workers on wind-related hazards before shift starts.",
            "Keep emergency contact numbers readily available.",
        ],
        checklist=[
            ChecklistItem(item="Wind speed checked against site thresholds"),
            ChecklistItem(item="Crane operations status reviewed with operator"),
            ChecklistItem(item="Loose materials and debris secured"),
            ChecklistItem(item="Scaffolding and temporary structures inspected"),
            ChecklistItem(item="Work at height activities reviewed"),
            ChecklistItem(item="Workers briefed on wind hazards"),
        ],
        general_notes=[
            "Wind conditions can change rapidly. Monitor throughout the shift.",
            "This advisory uses a manually selected weather scenario, not live weather data.",
        ],
    )


def _heavy_rain_advisory() -> WeatherAdvisory:
    return WeatherAdvisory(
        condition=WeatherCondition.HEAVY_RAIN,
        risk_level=RiskLevel.HIGH,
        alerts=[
            WeatherAlert(
                category="Slip & Fall Hazards",
                message="All surfaces may be extremely slippery. Ensure proper footwear and anti-slip measures.",
                priority=SeverityLevel.HIGH,
            ),
            WeatherAlert(
                category="Excavation Safety",
                message="Water accumulation may destabilize excavation walls. Inspect excavations before entry.",
                priority=SeverityLevel.CRITICAL,
            ),
            WeatherAlert(
                category="Electrical Hazards",
                message="Protect electrical equipment and connections from water exposure. Inspect for ground faults.",
                priority=SeverityLevel.HIGH,
            ),
        ],
        preventive_actions=[
            "Deploy anti-slip walkways and warning signs on wet surfaces.",
            "Inspect excavations for water accumulation and wall stability before entry.",
            "Protect electrical connections and equipment from water exposure.",
            "Ensure proper drainage and dewatering systems are operational.",
            "Cover and protect stored materials, especially cement and reinforcement steel.",
            "Review site access routes for safe passage.",
            "Follow project specifications for concrete protection and curing during rain.",
        ],
        checklist=[
            ChecklistItem(item="Slip hazard warnings posted"),
            ChecklistItem(item="Excavation walls inspected"),
            ChecklistItem(item="Electrical equipment protected"),
            ChecklistItem(item="Drainage systems checked"),
            ChecklistItem(item="Materials properly covered"),
            ChecklistItem(item="Site access routes safe"),
            ChecklistItem(item="Concrete work assessed per project specs"),
        ],
        general_notes=[
            "Heavy rain significantly increases the risk of ground instability and electrical hazards.",
            "This advisory uses a manually selected weather scenario, not live weather data.",
        ],
    )


def _extreme_heat_advisory() -> WeatherAdvisory:
    return WeatherAdvisory(
        condition=WeatherCondition.EXTREME_HEAT,
        risk_level=RiskLevel.HIGH,
        alerts=[
            WeatherAlert(
                category="Heat Illness",
                message="Workers are at risk of heat exhaustion and heatstroke. Ensure hydration and rest breaks.",
                priority=SeverityLevel.CRITICAL,
            ),
            WeatherAlert(
                category="Work Scheduling",
                message="Schedule strenuous work during cooler periods (early morning or late afternoon) where feasible.",
                priority=SeverityLevel.HIGH,
            ),
            WeatherAlert(
                category="Concrete Work",
                message="Concrete placement and curing should follow the applicable mix design, specifications, and professional guidance for hot weather conditions.",
                priority=SeverityLevel.MEDIUM,
            ),
        ],
        preventive_actions=[
            "Ensure adequate drinking water supply is accessible at all work areas.",
            "Schedule mandatory rest breaks in shaded areas every 30-45 minutes.",
            "Monitor workers for signs of heat exhaustion: dizziness, nausea, excessive sweating.",
            "Schedule physically demanding tasks during cooler hours where feasible.",
            "Provide shaded rest areas with adequate ventilation.",
            "Follow project specifications for hot-weather concrete practices.",
            "Keep first-aid supplies readily available with heat illness treatment capability.",
        ],
        checklist=[
            ChecklistItem(item="Drinking water supply adequate and accessible"),
            ChecklistItem(item="Rest break schedule communicated"),
            ChecklistItem(item="Shaded rest areas available"),
            ChecklistItem(item="Workers briefed on heat illness symptoms"),
            ChecklistItem(item="Heavy work rescheduled to cooler hours"),
            ChecklistItem(item="First-aid supplies checked"),
            ChecklistItem(item="Concrete work plan reviewed for hot weather"),
        ],
        general_notes=[
            "Heat illness can be life-threatening. Take all symptoms seriously.",
            "This advisory uses a manually selected weather scenario, not live weather data.",
        ],
    )


def _normal_advisory() -> WeatherAdvisory:
    return WeatherAdvisory(
        condition=WeatherCondition.NORMAL,
        risk_level=RiskLevel.LOW,
        alerts=[
            WeatherAlert(
                category="Routine Operations",
                message="Normal weather conditions. Maintain standard safety procedures.",
                priority=SeverityLevel.LOW,
            ),
        ],
        preventive_actions=[
            "Conduct routine safety inspections at the start of each shift.",
            "Verify all workers have appropriate PPE for their assigned tasks.",
            "Inspect access routes and work areas for housekeeping.",
            "Check equipment and machinery for proper functioning.",
            "Review daily work permits and method statements.",
            "Ensure emergency exits and assembly points are clear.",
        ],
        checklist=[
            ChecklistItem(item="PPE inspection completed for all workers"),
            ChecklistItem(item="Site housekeeping and access routes checked"),
            ChecklistItem(item="Equipment and machinery pre-use checks done"),
            ChecklistItem(item="Daily work permits issued and briefed"),
            ChecklistItem(item="Emergency routes and assembly points clear"),
            ChecklistItem(item="First-aid and fire safety equipment checked"),
            ChecklistItem(item="Toolbox talk / safety briefing conducted"),
        ],
        general_notes=[
            "Good weather is an opportunity to catch up on maintenance and safety improvements.",
            "This advisory uses a manually selected weather scenario, not live weather data.",
        ],
    )

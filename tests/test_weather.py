"""Tests for weather advisory rule-based engine."""
from __future__ import annotations

import pytest

from src.schemas import WeatherCondition, RiskLevel, SeverityLevel
from src.weather_advisory import get_weather_advisory


class TestWeatherAdvisory:
    """Tests for deterministic weather advisory rules."""

    def test_high_wind_advisory(self):
        advisory = get_weather_advisory(WeatherCondition.HIGH_WIND)
        assert advisory.condition == WeatherCondition.HIGH_WIND
        assert advisory.risk_level == RiskLevel.HIGH
        assert len(advisory.alerts) > 0
        assert len(advisory.preventive_actions) > 0
        assert len(advisory.checklist) > 0

    def test_heavy_rain_advisory(self):
        advisory = get_weather_advisory(WeatherCondition.HEAVY_RAIN)
        assert advisory.condition == WeatherCondition.HEAVY_RAIN
        assert advisory.risk_level == RiskLevel.HIGH
        assert len(advisory.alerts) > 0

    def test_extreme_heat_advisory(self):
        advisory = get_weather_advisory(WeatherCondition.EXTREME_HEAT)
        assert advisory.condition == WeatherCondition.EXTREME_HEAT
        assert advisory.risk_level == RiskLevel.HIGH
        assert len(advisory.alerts) > 0

    def test_normal_advisory(self):
        advisory = get_weather_advisory(WeatherCondition.NORMAL)
        assert advisory.condition == WeatherCondition.NORMAL
        assert advisory.risk_level == RiskLevel.LOW
        assert len(advisory.checklist) > 0

    def test_all_conditions_produce_results(self):
        for condition in WeatherCondition:
            advisory = get_weather_advisory(condition)
            assert advisory.condition == condition
            assert advisory.risk_level is not None
            assert len(advisory.preventive_actions) > 0

    def test_high_wind_has_crane_alert(self):
        advisory = get_weather_advisory(WeatherCondition.HIGH_WIND)
        alert_texts = " ".join(a.message.lower() for a in advisory.alerts)
        assert "crane" in alert_texts

    def test_heavy_rain_has_slip_warning(self):
        advisory = get_weather_advisory(WeatherCondition.HEAVY_RAIN)
        alert_texts = " ".join(a.message.lower() for a in advisory.alerts)
        assert "slip" in alert_texts

    def test_extreme_heat_has_hydration(self):
        advisory = get_weather_advisory(WeatherCondition.EXTREME_HEAT)
        all_text = " ".join(advisory.preventive_actions).lower()
        assert "water" in all_text or "hydrat" in all_text

    def test_normal_has_ppe_check(self):
        advisory = get_weather_advisory(WeatherCondition.NORMAL)
        checklist_text = " ".join(item.item.lower() for item in advisory.checklist)
        assert "ppe" in checklist_text

    def test_alert_priorities_valid(self):
        for condition in WeatherCondition:
            advisory = get_weather_advisory(condition)
            for alert in advisory.alerts:
                assert alert.priority in SeverityLevel

    def test_advisory_has_general_notes(self):
        for condition in WeatherCondition:
            advisory = get_weather_advisory(condition)
            assert len(advisory.general_notes) > 0

    def test_demo_note_present(self):
        """All advisories should note they use manually selected scenarios."""
        for condition in WeatherCondition:
            advisory = get_weather_advisory(condition)
            notes_text = " ".join(advisory.general_notes).lower()
            assert "manually selected" in notes_text or "not live" in notes_text

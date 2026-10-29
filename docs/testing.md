# Testing Documentation

## Multimodal Construction Intelligence Platform

### Test Strategy

All tests use **pytest** and run without requiring a real Gemini API key or network access.

### Test Files

| File | Module Tested | Coverage |
|------|---------------|----------|
| `test_schemas.py` | `src/schemas.py` | Pydantic validation, enums, boundary conditions |
| `test_planning.py` | `src/planning.py` | Budget calculations, material estimates, INR formatting, milestones |
| `test_valuation.py` | `src/valuation.py` | Property valuation with various inputs |
| `test_weather.py` | `src/weather_advisory.py` | All 4 weather conditions, alerts, checklists |
| `test_reports.py` | `src/report_utils.py` | JSON generation, envelope structure, filenames |

### Running Tests

```powershell
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_schemas.py -v

# Run with short traceback
python -m pytest tests/ -v --tb=short

# Run a specific test class
python -m pytest tests/test_planning.py::TestINRFormatting -v
```

### Test Categories

#### Schema Validation Tests (`test_schemas.py`)
- Valid and invalid safety scores (0-100 boundary)
- PPE status enum values (Observed, Not Observed, Unknown, Not Applicable)
- Confidence value ranges (0.0 to 1.0, null handling)
- Crack width null handling (no scale reference)
- Negative width rejection
- All defect type and urgency level enums
- Report envelope structure and timestamp presence

#### Planning Calculation Tests (`test_planning.py`)
- Budget formula: `area × rate = budget`
- Expenditure formula: `budget × completion% / 100`
- Zero and 100% completion edge cases
- Steel and cement material estimates
- INR formatting (lakhs, crores, thousands)
- Default rate calculations with tier multipliers
- Milestone progression tracking

#### Valuation Tests (`test_valuation.py`)
- Basic valuation (construction cost only)
- Valuation with land cost
- Valuation with market rate
- Combined land + market rate
- Zero values treated as "not provided"
- Valuation method labeling

#### Weather Advisory Tests (`test_weather.py`)
- All 4 weather conditions produce valid results
- Correct risk levels assigned
- Specific content checks (crane for wind, slip for rain, hydration for heat)
- PPE checklist for normal conditions
- Alert priorities are valid severity levels
- Demo/manual-selection notes present

#### Report Tests (`test_reports.py`)
- Valid JSON serialization
- Report envelope structure
- Timestamp presence
- Platform name inclusion
- Nested data serialization
- Filename format and timestamp

### What Is NOT Tested Automatically

- Live Gemini API calls (requires API key and network)
- Streamlit UI rendering (requires browser)
- Pollinations image generation (requires network)
- File upload via Streamlit widget (requires runtime)

These are verified through manual testing during development.

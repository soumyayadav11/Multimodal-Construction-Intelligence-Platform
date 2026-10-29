# Architecture Overview

## Multimodal Construction Intelligence Platform

### System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     STREAMLIT WEB INTERFACE                       │
│                          (app.py)                                 │
│  ┌──────────┬────────────┬──────────────┬──────────────────────┐  │
│  │  Tab 1   │   Tab 2    │    Tab 3     │       Tab 4          │  │
│  │ Safety   │  Crack     │  Planning &  │  Assistant &         │  │
│  │ Audit    │  Diag.     │  Valuation   │  Weather Advisory    │  │
│  └────┬─────┴─────┬──────┴──────┬───────┴──────────┬───────────┘  │
│       │           │             │                  │              │
├───────┴───────────┴─────────────┴──────────────────┴──────────────┤
│                       MODULE LAYER (src/)                         │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────┐ ┌─────────────┐  │
│  │safety_audit │ │crack_diag    │ │planning   │ │weather_adv  │  │
│  │.py          │ │.py           │ │.py        │ │.py          │  │
│  └──────┬──────┘ └──────┬───────┘ └───────────┘ └─────────────┘  │
│         │               │                                        │
│  ┌──────┴───────────────┴───────┐  ┌──────────┐ ┌────────────┐  │
│  │      ai_service.py           │  │valuation │ │assistant   │  │
│  │  (Google Gemini SDK Client)  │  │.py       │ │.py         │  │
│  └──────────────────────────────┘  └──────────┘ └────────────┘  │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                    VALIDATION LAYER                               │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                  schemas.py (Pydantic v2)                    │ │
│  │   PPEItem, HazardItem, SafetyAuditResult,                   │ │
│  │   CrackDiagnosticsResult, ConstructionPlan,                  │ │
│  │   ValuationResult, WeatherAdvisory, ReportEnvelope           │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                    UTILITY LAYER                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐    │
│  │ image_utils.py │  │ report_utils.py│  │ visualization.py │    │
│  │ (PIL / Pillow) │  │ (JSON export)  │  │ (UI components)  │    │
│  └────────────────┘  └────────────────┘  └──────────────────┘    │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                    CONFIGURATION                                  │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │   config.py — API keys, model settings, app constants       │ │
│  │   Streamlit Secrets → Env Vars → Session State              │ │
│  └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → Streamlit UI captures images, form data, or chat messages.
2. **Validation** → `image_utils.py` validates uploads; Pydantic schemas validate data.
3. **Processing** →
   - Image analysis: `ai_service.py` sends to Gemini, response parsed via `extract_json_from_response`.
   - Calculations: `planning.py` and `valuation.py` run deterministic math.
   - Weather: `weather_advisory.py` applies rule-based logic.
   - Chat: `assistant.py` uses Gemini or returns demo responses.
4. **Validation** → All AI responses validated against Pydantic schemas.
5. **Display** → `visualization.py` renders metric cards, tables, progress bars.
6. **Export** → `report_utils.py` wraps results in `ReportEnvelope` for JSON download.

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Pydantic v2 for all schemas | Type safety, validation, JSON serialization |
| Deterministic calculations | Planning/valuation/weather work without AI |
| Demo mode fallback | App usable without API key for demonstrations |
| Modular source structure | Each module testable independently |
| Custom CSS injection | Professional UI without external CSS frameworks |
| No persistent storage | Privacy-first: nothing stored between sessions |

### External Dependencies

| Service | Usage | Required? |
|---------|-------|-----------|
| Google Gemini API | Image analysis, chatbot | No (demo mode available) |
| Pollinations API | Conceptual image generation | No (optional feature) |

# 🏗️ Multimodal Construction Intelligence Platform

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45%2B-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **SkillWallet Capstone Project 1** | Platform ID: `6ac4c98d1dcde6d7857c1642`

An intelligent construction decision-support platform that combines multimodal AI, deterministic financial calculations, and rule-based safety advisory. Built with Streamlit and Google Gemini.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Problem Statement](#-problem-statement)
3. [Objectives](#-objectives)
4. [Main Features](#-main-features)
5. [Technology Stack](#-technology-stack)
6. [Architecture Overview](#-architecture-overview)
7. [Project Structure](#-project-structure)
8. [Prerequisites](#-prerequisites)
9. [Local Setup](#-local-setup)
10. [API Key Configuration](#-api-key-configuration)
11. [Running the App](#-running-the-app)
12. [Running Tests](#-running-tests)
13. [Demonstration Mode](#-demonstration-mode)
14. [JSON Contracts](#-json-contracts)
15. [Limitations & Disclaimer](#-limitations--disclaimer)
16. [Deployment](#-deployment)
17. [Screenshots](#-screenshots)
18. [Future Enhancements](#-future-enhancements)
19. [Repository Info](#-repository-info)

---

## 🎯 Project Overview

The **Multimodal Construction Intelligence Platform** is a decision-support and educational application designed for construction industry professionals and engineering students. It provides:

- **Image-based PPE safety audits** using AI vision
- **Concrete crack diagnostics** with defect classification
- **Construction budget calculations** and material estimates in Indian Rupees
- **Weather-aware safety advisories** using rule-based logic
- **Multi-turn AI chatbot** for construction industry queries

> ⚠️ **This application does not replace qualified structural engineers, professional safety inspections, certified valuations, or applicable local regulations.**

---

## 🔍 Problem Statement

Construction sites face persistent challenges with safety compliance, structural defect detection, cost estimation, and weather-related risk management. Manual inspections are time-consuming and subjective. This platform leverages multimodal AI to provide rapid, preliminary assessments that complement — but never replace — professional expertise.

---

## 🎯 Objectives

1. Analyze construction site images for PPE compliance and hazard identification
2. Classify concrete defects from surface photographs
3. Calculate construction budgets with transparent formulas
4. Provide deterministic weather-based safety recommendations
5. Deliver an interactive construction assistant chatbot
6. Ensure all outputs follow validated JSON schemas

---

## ✨ Main Features

### 🦺 Tab 1: Site Safety & PPE Audit
- Upload construction site photos (JPG/JPEG/PNG)
- AI-powered PPE detection (helmets, vests, footwear, harnesses)
- Hazard identification with severity ratings
- Safety score (0-100) with corrective actions
- Downloadable JSON reports

### 🔍 Tab 2: Crack Diagnostics & Structural Integrity
- Upload concrete/wall surface images
- Defect classification: Hairline, Settlement, Structural Shear, Thermal, Spalling
- Width estimation (only with scale reference)
- Urgency assessment and professional review recommendations

### 📐 Tab 3: Planning & Real Estate Valuation
- Construction cost calculator (₹ INR with lakhs/crores)
- Material estimates (steel kg, cement bags)
- Milestone progress tracking (7 stages)
- Property valuation with user-supplied market rates
- Optional AI-generated conceptual architectural images

### 🌤️ Tab 4: Daily Site Assistant & Weather Advisory
- Rule-based weather safety advisories (4 conditions)
- Interactive safety checklists
- Multi-turn AI chatbot for construction queries
- Demo-mode responses without API key

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend & UI | Streamlit |
| AI/ML | Google Gemini (gemini-3.8-flash) via `google-genai` SDK |
| Image Processing | Pillow (PIL) |
| Data Validation | Pydantic v2 |
| Image Generation | Pollinations API (optional) |
| Environment Config | python-dotenv, Streamlit Secrets |
| Testing | pytest |
| Language | Python 3.9+ |
| Version Control | Git & GitHub |

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────┐
│           Streamlit Web Interface            │
│  (Tab 1 | Tab 2 | Tab 3 | Tab 4)           │
├─────────────────────────────────────────────┤
│  Module Layer                               │
│  safety_audit │ crack_diag │ planning │ ... │
├─────────────────────────────────────────────┤
│  AI Service (Gemini SDK)                    │
├─────────────────────────────────────────────┤
│  Validation Layer (Pydantic v2 Schemas)     │
├─────────────────────────────────────────────┤
│  Report Generator (JSON Export)             │
└─────────────────────────────────────────────┘
```

See [docs/architecture.md](docs/architecture.md) for detailed diagrams.

---

## 📁 Project Structure

```
Multimodal-Construction-Intelligence-Platform/
├── app.py                          # Main Streamlit entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git exclusions
├── .env.example                    # Environment variable template
├── LICENSE                         # MIT License
├── packages.txt                    # System packages (Streamlit Cloud)
├── .streamlit/
│   └── config.toml                 # Streamlit theme & server config
├── src/
│   ├── __init__.py                 # Package initialization
│   ├── config.py                   # App configuration & API key management
│   ├── schemas.py                  # Pydantic v2 data models & enums
│   ├── ai_service.py              # Gemini API client & prompt templates
│   ├── image_utils.py             # Image validation & processing
│   ├── safety_audit.py            # PPE & hazard analysis module
│   ├── crack_diagnostics.py       # Crack classification module
│   ├── planning.py                # Construction cost & material calculator
│   ├── valuation.py               # Property valuation module
│   ├── weather_advisory.py        # Rule-based weather safety engine
│   ├── assistant.py               # Multi-turn chatbot module
│   ├── visualization.py           # Streamlit UI components & CSS
│   └── report_utils.py            # JSON report generation & export
├── tests/
│   ├── test_schemas.py            # Schema validation tests
│   ├── test_planning.py           # Budget & material calculation tests
│   ├── test_valuation.py          # Valuation calculation tests
│   ├── test_weather.py            # Weather advisory rule tests
│   └── test_reports.py            # Report generation tests
└── docs/
    ├── architecture.md            # System architecture documentation
    └── testing.md                 # Test strategy documentation
```

---

## 📦 Prerequisites

- **Python 3.9+** (tested with Python 3.13)
- **pip** (Python package manager)
- **Git** (for version control)
- **Google Gemini API key** (free tier available at [aistudio.google.com](https://aistudio.google.com))

---

## 🚀 Local Setup

### 1. Clone the Repository

```powershell
git clone https://github.com/soumyayadav11/Multimodal-Construction-Intelligence-Platform.git
cd Multimodal-Construction-Intelligence-Platform
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment

```powershell
# Copy the example env file
Copy-Item .env.example .env

# Edit .env and add your API key
notepad .env
```

---

## 🔑 API Key Configuration

### Option 1: `.env` File (Local Development)

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

> ⚠️ **Never commit `.env` to Git.** It is listed in `.gitignore`.

### Option 2: Streamlit Secrets (Cloud Deployment)

In Streamlit Community Cloud, go to **Settings → Secrets** and add:
```toml
GEMINI_API_KEY = "your_actual_api_key_here"
GEMINI_MODEL = "gemini-3.8-flash"
```

### Option 3: Session Input

Enter the API key directly in the app sidebar. It is used only for the current session and never stored.

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com)
2. Sign in with your Google account
3. Click "Get API Key" → "Create API key"
4. Copy the key and configure it as shown above

---

## ▶️ Running the App

```powershell
# From the project root directory
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🧪 Running Tests

```powershell
# Run all tests
python -m pytest tests/ -v

# Run with short traceback
python -m pytest tests/ -v --tb=short

# Run a specific test file
python -m pytest tests/test_schemas.py -v

# Run a specific test class
python -m pytest tests/test_planning.py::TestINRFormatting -v
```

Tests do **not** require a Gemini API key or network access.

See [docs/testing.md](docs/testing.md) for full test documentation.

---

## 🏷️ Demonstration Mode

The app works **without an API key** in demonstration mode:

- ✅ All four tabs are accessible
- ✅ Construction planning calculations work fully
- ✅ Weather advisories use rule-based logic (no AI needed)
- ✅ Sample safety and crack results are available
- ✅ The chatbot provides pre-written educational responses
- ✅ JSON reports can be downloaded

All demonstration results are **clearly labeled** and never presented as findings from uploaded images.

---

## 📄 JSON Contracts

### Safety Audit Result

```json
{
  "analysis_type": "site_safety_audit",
  "safety_score": 75,
  "overall_status": "Needs Attention",
  "ppe_detection": {
    "helmet": {
      "status": "Observed",
      "confidence": 0.85,
      "notes": "A hard hat appears visible."
    }
  },
  "hazards": [
    {
      "hazard": "Unprotected edge",
      "severity": "High",
      "evidence": "An edge appears exposed.",
      "corrective_action": "Install edge protection."
    }
  ],
  "limitations": ["Image-based analysis limitation."]
}
```

### Crack Diagnostics Result

```json
{
  "analysis_type": "crack_diagnostics",
  "defect_type": "Hairline",
  "estimated_width_mm": null,
  "severity": "Low",
  "possible_causes": ["Surface shrinkage"],
  "recommended_actions": ["Monitor for changes"],
  "urgency": "Routine Inspection",
  "professional_review_required": true,
  "limitations": ["No scale reference for width measurement."]
}
```

---

## ⚠️ Limitations & Disclaimer

This application is for **decision-support and educational purposes only**.

- It does **not** replace qualified structural engineers
- It does **not** replace professional safety inspections
- It does **not** provide certified property valuations
- It does **not** override applicable local regulations
- Image-based analysis **cannot** detect all hazards
- Crack width **cannot** be reliably measured from uncalibrated photos
- Material estimates are **approximate** based on configurable assumptions
- Construction cost calculations use **user-supplied or default rates**

Always consult qualified professionals for critical safety, structural, and valuation decisions.

---

## ☁️ Deployment

### Streamlit Community Cloud

1. **Push code to GitHub** (ensure no secrets are committed)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Select:
   - **Repository:** `soumyayadav11/Multimodal-Construction-Intelligence-Platform`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Deploy"**
6. Go to **Settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   GEMINI_MODEL = "gemini-3.8-flash"
   ```

### Deployment Checklist

- [x] `requirements.txt` at project root
- [x] `app.py` as main entry point
- [x] `.streamlit/config.toml` for theme
- [x] `packages.txt` for system dependencies
- [x] No secrets in source code
- [x] `.gitignore` excludes `.env`

---

## 📸 Screenshots

> *Screenshots will be added after deployment.*

| Module | Screenshot |
|--------|------------|
| Site Safety Audit | *Coming soon* |
| Crack Diagnostics | *Coming soon* |
| Planning & Valuation | *Coming soon* |
| Weather Advisory | *Coming soon* |
| Construction Assistant | *Coming soon* |

---

## 🚀 Future Enhancements

- [ ] Live weather API integration (OpenWeatherMap)
- [ ] PDF report generation
- [ ] Historical analysis tracking
- [ ] Multi-language support (Hindi, regional languages)
- [ ] Batch image processing
- [ ] Integration with BIM models
- [ ] Mobile-responsive enhancements
- [ ] User authentication and role-based access

---

## 📂 Repository Info

- **Author:** Soumya Yadav
- **GitHub:** [@soumyayadav11](https://github.com/soumyayadav11)
- **Repository:** [Multimodal-Construction-Intelligence-Platform](https://github.com/soumyayadav11/Multimodal-Construction-Intelligence-Platform)
- **License:** MIT
- **Category:** Generative AI, Real Estate Decision Support
- **Platform ID:** `6ac4c98d1dcde6d7857c1642`

---

<p align="center">
  Built with ❤️ for SkillWallet Capstone Project 1
</p>

"""
Multimodal Construction Intelligence Platform
==============================================
Main Streamlit application entry point.

A decision-support and educational platform for construction site safety,
crack diagnostics, project planning, and weather-aware advisory.

This application does not replace qualified structural engineers, professional
safety inspections, certified valuations, or applicable local regulations.
"""
from __future__ import annotations

import streamlit as st
import json
from PIL import Image

# Source modules
from src.config import AppConfig, get_api_key, is_demo_mode, get_model_name
from src.schemas import (
    AnalysisMode, WeatherCondition, StructureType,
    LocationTier, QualityLevel,
)
from src.image_utils import validate_image_file, load_image
from src.ai_service import GeminiService
from src.safety_audit import analyze_site_safety
from src.crack_diagnostics import analyze_crack
from src.planning import calculate_construction_plan, format_inr, get_default_rate, get_milestones
from src.valuation import calculate_valuation
from src.weather_advisory import get_weather_advisory
from src.assistant import get_ai_response, get_demo_response
from src.report_utils import generate_json_report, get_report_filename
from src.visualization import (
    inject_custom_css, render_demo_banner, render_mode_indicator,
    render_safety_score, render_ppe_checklist, render_hazard_table,
    render_crack_results, render_construction_plan, render_valuation,
    render_milestone_progress, render_weather_advisory,
    render_architecture_diagram, render_metric_card,
)


# ── Page Configuration ──────────────────────────────────────────────────────

st.set_page_config(
    page_title=AppConfig.APP_TITLE,
    page_icon=AppConfig.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()


# ── Sidebar ─────────────────────────────────────────────────────────────────

def render_sidebar():
    """Render the application sidebar with configuration and info."""
    with st.sidebar:
        st.image(
            "https://img.icons8.com/3d-fluency/94/building.png",
            width=60,
        )
        st.title("🏗️ Config & Info")
        st.markdown("---")

        # AI Configuration
        st.subheader("🔑 AI Configuration")

        # Check for existing key
        api_key = get_api_key()

        if api_key:
            st.success("✅ API key configured")
            st.caption(f"Model: `{get_model_name()}`")
        else:
            st.warning("⚠️ No API key found")
            user_key = st.text_input(
                "Enter Gemini API Key",
                type="password",
                help="Your key is used only for this session and is never stored or logged.",
                placeholder="Enter your API key...",
            )
            if user_key:
                st.session_state["gemini_api_key"] = user_key
                st.success("✅ API key set for this session")
                st.rerun()

        # Mode indicator
        if is_demo_mode():
            st.info("🏷️ **Demo Mode** — No API key. Using sample results.")
        else:
            st.success("🤖 **Live AI Mode** — Connected to Gemini.")

        st.markdown("---")

        # Architecture overview
        with st.expander("📐 Architecture Overview"):
            render_architecture_diagram()

        st.markdown("---")

        # About
        with st.expander("ℹ️ About This Platform"):
            st.markdown("""
            **Multimodal Construction Intelligence Platform**

            A decision-support and educational application for construction
            industry professionals and students.

            **Modules:**
            - 🦺 Site Safety & PPE Audit
            - 🔍 Crack Diagnostics
            - 📐 Planning & Valuation
            - 🌤️ Daily Assistant & Weather Advisory

            **⚠️ Disclaimer:**
            This application does not replace qualified structural engineers,
            professional safety inspections, certified valuations, or
            applicable local regulations.

            **Platform ID:** `6ac4c98d1dcde6d7857c1642`
            """)

        st.caption("Built for SkillWallet Capstone Project 1")


# ── Tab 1: Site Safety & PPE Audit ──────────────────────────────────────────

def render_safety_tab():
    """Render the Site Safety & PPE Audit tab."""
    st.header("🦺 Site Safety & PPE Audit")
    st.markdown(
        "Upload a construction site photo for preliminary safety assessment. "
        "This tool identifies visible PPE and potential hazards from images."
    )

    # Instructions
    with st.expander("📖 How to Use", expanded=False):
        st.markdown("""
        1. **Upload** a clear photo of a construction site (JPG, JPEG, or PNG, max 10 MB).
        2. Click **🔍 Analyze Image** to run the assessment.
        3. Review the safety score, PPE checklist, and identified hazards.
        4. **Download** the JSON report for documentation.

        **Tips for better results:**
        - Use well-lit, clear photos
        - Include workers and their surroundings
        - Capture the full work area where possible

        **Limitations:**
        - Image-based analysis cannot replace on-site inspection
        - Steel-toe protection in footwear cannot be confirmed from photos
        - Hazards outside the camera view will be missed
        """)

    # Image upload
    uploaded_file = st.file_uploader(
        "Upload Construction Site Photo",
        type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG, JPEG, PNG. Maximum size: 10 MB.",
        key="safety_upload",
    )

    if uploaded_file is not None:
        # Validate
        is_valid, error_msg = validate_image_file(uploaded_file)
        if not is_valid:
            st.error(f"❌ {error_msg}")
            return

        # Display image
        image = load_image(uploaded_file)
        if image is None:
            st.error("❌ Could not load the image. Please try a different file.")
            return

        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image, caption="Uploaded Construction Site Photo", use_container_width=True)

        # Analyze button
        with col2:
            if st.button("🔍 Analyze Image", key="analyze_safety", type="primary", use_container_width=True):
                with st.spinner("Analyzing construction site safety..."):
                    try:
                        ai_service = None if is_demo_mode() else GeminiService()
                        result, mode = analyze_site_safety(image, ai_service)

                        # Store in session
                        st.session_state["safety_result"] = result
                        st.session_state["safety_mode"] = mode
                    except ConnectionError as e:
                        st.error(f"🔌 Connection Error: {e}")
                        return
                    except Exception as e:
                        st.error(f"❌ Analysis Error: {e}")
                        return

    # Display results if available
    if "safety_result" in st.session_state:
        result = st.session_state["safety_result"]
        mode = st.session_state.get("safety_mode", AnalysisMode.DEMONSTRATION)

        st.markdown("---")
        render_mode_indicator(mode)
        render_safety_score(result.safety_score, result.overall_status)
        render_ppe_checklist(result.ppe_detection)
        render_hazard_table(result.hazards)

        # Limitations
        if result.limitations:
            with st.expander("⚠️ Analysis Limitations"):
                for lim in result.limitations:
                    st.markdown(f"- {lim}")

        # Regulatory note
        with st.expander("📜 Regulatory References"):
            st.markdown("""
            **Relevant standards and regulations may include:**
            - OSHA Construction Safety Standards (29 CFR 1926)
            - Building and Other Construction Workers Act (India)
            - IS 3696 — Safety Code for Scaffolds and Ladders
            - Site-specific safety plans and method statements

            ⚠️ *Always verify applicable regulations for your specific jurisdiction and project.*
            """)

        # JSON report
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("📋 Raw JSON Result"):
                st.json(result.model_dump())
        with col2:
            report_json = generate_json_report(result.model_dump(), mode)
            st.download_button(
                label="📥 Download JSON Report",
                data=report_json,
                file_name=get_report_filename("safety_audit"),
                mime="application/json",
                use_container_width=True,
            )
    elif uploaded_file is None:
        # Empty state
        st.markdown("---")
        st.markdown(
            '<div class="info-card">'
            '📸 <strong>Upload a construction site photo</strong> to begin the safety assessment. '
            'The analysis will check for PPE compliance and identify potential hazards.'
            '</div>',
            unsafe_allow_html=True,
        )


# ── Tab 2: Crack Diagnostics ────────────────────────────────────────────────

def render_crack_tab():
    """Render the Crack Diagnostics & Structural Integrity tab."""
    st.header("🔍 Crack Diagnostics & Structural Integrity")
    st.markdown(
        "Upload an image of a concrete or wall surface to get a preliminary defect assessment. "
        "This tool classifies visible cracks and suggests next steps."
    )

    with st.expander("📖 How to Use", expanded=False):
        st.markdown("""
        1. **Upload** a clear, well-lit photo focused on the crack or defect (JPG, JPEG, or PNG).
        2. Click **🔍 Analyze Crack** to run the diagnostic.
        3. Review the defect classification, severity, and recommended actions.
        4. **Download** the JSON report for records.

        **Tips for better results:**
        - Photograph the crack from directly in front
        - Include a ruler or scale reference if possible for width estimation
        - Ensure good lighting and focus
        - Include surrounding context (wall, floor, column)

        **⚠️ Important:**
        A photograph alone cannot reliably determine if a crack is structural.
        Always consult a qualified structural engineer for definitive assessment.
        """)

    uploaded_file = st.file_uploader(
        "Upload Crack / Surface Photo",
        type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG, JPEG, PNG. Maximum size: 10 MB.",
        key="crack_upload",
    )

    if uploaded_file is not None:
        is_valid, error_msg = validate_image_file(uploaded_file)
        if not is_valid:
            st.error(f"❌ {error_msg}")
            return

        image = load_image(uploaded_file)
        if image is None:
            st.error("❌ Could not load the image. Please try a different file.")
            return

        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image, caption="Uploaded Surface Photo", use_container_width=True)

        with col2:
            if st.button("🔍 Analyze Crack", key="analyze_crack", type="primary", use_container_width=True):
                with st.spinner("Analyzing surface defect..."):
                    try:
                        ai_service = None if is_demo_mode() else GeminiService()
                        result, mode = analyze_crack(image, ai_service)
                        st.session_state["crack_result"] = result
                        st.session_state["crack_mode"] = mode
                    except ConnectionError as e:
                        st.error(f"🔌 Connection Error: {e}")
                        return
                    except Exception as e:
                        st.error(f"❌ Analysis Error: {e}")
                        return

    if "crack_result" in st.session_state:
        result = st.session_state["crack_result"]
        mode = st.session_state.get("crack_mode", AnalysisMode.DEMONSTRATION)

        st.markdown("---")
        render_mode_indicator(mode)
        render_crack_results(result)

        # Limitations
        if result.limitations:
            with st.expander("⚠️ Analysis Limitations"):
                for lim in result.limitations:
                    st.markdown(f"- {lim}")

        # JSON report
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("📋 Raw JSON Result"):
                st.json(result.model_dump())
        with col2:
            report_json = generate_json_report(result.model_dump(), mode)
            st.download_button(
                label="📥 Download JSON Report",
                data=report_json,
                file_name=get_report_filename("crack_diagnostics"),
                mime="application/json",
                use_container_width=True,
            )
    elif uploaded_file is None:
        st.markdown("---")
        st.markdown(
            '<div class="info-card">'
            '🔍 <strong>Upload a photo of a concrete or wall surface</strong> to begin crack diagnostics. '
            'Use a clear, well-lit image focused on the defect area.'
            '</div>',
            unsafe_allow_html=True,
        )


# ── Tab 3: Planning & Valuation ─────────────────────────────────────────────

def render_planning_tab():
    """Render the Planning & Real Estate Valuation tab."""
    st.header("📐 Planning & Real Estate Valuation")
    st.markdown(
        "Calculate construction budgets, estimate material requirements, and get preliminary "
        "property valuations. All values are in Indian Rupees (INR)."
    )

    with st.expander("📖 About This Module", expanded=False):
        st.markdown("""
        This module uses **deterministic calculations** — no AI is required.

        - **Construction budget** = Built-up Area × Rate per Sq Ft
        - **Expenditure incurred** = Budget × Completion %
        - **Material estimates** use configurable industry assumptions
        - **Valuation** uses user-supplied market rates

        ⚠️ All calculations use configurable assumptions. They do not constitute
        professional cost estimates or certified property valuations.
        """)

    # Input form
    st.subheader("📝 Project Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        structure_type = st.selectbox(
            "Structure Type",
            options=[e.value for e in StructureType],
            help="Type of construction project",
        )
        area_sqft = st.number_input(
            "Built-up Area (sq ft)",
            min_value=100.0,
            max_value=1_000_000.0,
            value=1500.0,
            step=100.0,
            help="Total built-up area in square feet",
        )
        city_name = st.text_input(
            "City / Location (optional)",
            placeholder="e.g., Mumbai, Bangalore, Jaipur",
        )

    with col2:
        location_tier = st.selectbox(
            "Location Tier",
            options=[e.value for e in LocationTier],
            help="Tier 1: Metro cities, Tier 2: Large cities, Tier 3: Smaller cities/towns",
        )
        quality_level = st.selectbox(
            "Construction Quality",
            options=[e.value for e in QualityLevel],
            index=1,
            help="Basic, Standard, Premium, or Luxury finish level",
        )

    with col3:
        # Calculate default rate
        selected_quality = QualityLevel(quality_level)
        selected_tier = LocationTier(location_tier)
        default_rate = get_default_rate(selected_quality, selected_tier)

        rate_per_sqft = st.number_input(
            "Rate per Sq Ft (₹)",
            min_value=500.0,
            max_value=50_000.0,
            value=default_rate,
            step=100.0,
            help=f"Default for {quality_level} in {location_tier}: ₹{default_rate:,.0f}/sq ft. Adjust as needed.",
        )

        completion_pct = st.slider(
            "Completion %",
            min_value=0,
            max_value=100,
            value=30,
            help="Current project completion percentage",
        )

    # Optional inputs
    with st.expander("🏠 Optional: Land Cost & Market Rate"):
        ocol1, ocol2 = st.columns(2)
        with ocol1:
            land_cost = st.number_input(
                "Estimated Land Cost (₹)",
                min_value=0.0,
                value=0.0,
                step=100_000.0,
                help="Optional: Estimated cost of land acquisition",
            )
        with ocol2:
            market_rate = st.number_input(
                "Market Rate per Sq Ft (₹)",
                min_value=0.0,
                value=0.0,
                step=500.0,
                help="Optional: Current market rate for comparable properties in the area",
            )

    # Calculate
    if st.button("📊 Calculate", type="primary", use_container_width=True):
        selected_structure = StructureType(structure_type)

        plan = calculate_construction_plan(
            structure_type=selected_structure,
            area_sqft=area_sqft,
            location_tier=selected_tier,
            quality_level=selected_quality,
            rate_per_sqft=rate_per_sqft,
            completion_percentage=float(completion_pct),
        )

        st.session_state["planning_result"] = plan

        # Valuation
        valuation = calculate_valuation(
            construction_cost_inr=plan.estimated_budget_inr,
            area_sqft=area_sqft,
            land_cost_inr=land_cost if land_cost > 0 else None,
            market_rate_per_sqft=market_rate if market_rate > 0 else None,
        )
        st.session_state["valuation_result"] = valuation

    # Display results
    if "planning_result" in st.session_state:
        plan = st.session_state["planning_result"]
        st.markdown("---")
        render_construction_plan(plan)
        render_milestone_progress(plan.completion_percentage)

        if "valuation_result" in st.session_state:
            st.markdown("---")
            render_valuation(st.session_state["valuation_result"])

        # Conceptual image generation
        st.markdown("---")
        st.subheader("🎨 Conceptual Architectural Visualization")
        st.caption("⚠️ Generated images are conceptual illustrations, NOT approved construction drawings.")

        if st.button("🖼️ Generate Conceptual Image", key="gen_image"):
            prompt = (
                f"Architectural rendering of a modern {structure_type.lower()} building, "
                f"Indian architectural style, {quality_level.lower()} finish, "
                f"professional architectural visualization, clear sky background"
            )
            try:
                import requests
                image_url = f"{AppConfig.POLLINATIONS_URL}/{requests.utils.quote(prompt)}?width=768&height=512"
                with st.spinner("Generating conceptual visualization..."):
                    response = requests.get(image_url, timeout=30)
                    if response.status_code == 200:
                        st.image(response.content, caption="🎨 Conceptual Illustration (AI-Generated — Not a Construction Drawing)")
                    else:
                        st.warning("⚠️ Image generation service is currently unavailable. This is an optional feature.")
            except Exception:
                st.warning("⚠️ Conceptual image generation is unavailable. This optional feature requires an internet connection.")

        # Download
        st.markdown("---")
        plan_data = plan.model_dump()
        plan_data["analysis_type"] = "construction_planning"
        if "valuation_result" in st.session_state:
            plan_data["valuation"] = st.session_state["valuation_result"].model_dump()

        col1, col2 = st.columns(2)
        with col1:
            with st.expander("📋 Raw JSON Result"):
                st.json(plan_data)
        with col2:
            report_json = generate_json_report(plan_data, AnalysisMode.LIVE_AI)
            st.download_button(
                label="📥 Download Planning Report",
                data=report_json,
                file_name=get_report_filename("construction_planning"),
                mime="application/json",
                use_container_width=True,
            )


# ── Tab 4: Daily Assistant & Weather Advisory ───────────────────────────────

def render_assistant_tab():
    """Render the Daily Site Assistant & Weather Advisory tab."""
    st.header("🌤️ Daily Site Assistant & Weather Advisory")

    # Split into two sub-sections
    weather_section, chat_section = st.tabs(["☁️ Weather Advisory", "💬 Construction Assistant"])

    # ── Weather Advisory ──
    with weather_section:
        st.subheader("☁️ Weather-Aware Safety Advisory")
        st.caption(
            "Select a weather condition to get rule-based safety recommendations. "
            "This uses deterministic logic — no AI required."
        )

        weather_col1, weather_col2 = st.columns([1, 2])
        with weather_col1:
            condition_options = {
                "☀️ Normal": WeatherCondition.NORMAL,
                "💨 High Wind": WeatherCondition.HIGH_WIND,
                "🌧️ Heavy Rain": WeatherCondition.HEAVY_RAIN,
                "🔥 Extreme Heat": WeatherCondition.EXTREME_HEAT,
            }
            selected = st.radio(
                "Select Weather Condition",
                options=list(condition_options.keys()),
                help="Select the current or expected weather condition for your site.",
            )
            condition = condition_options[selected]

            st.caption("ℹ️ This is a manually selected scenario, not live weather data.")

        with weather_col2:
            advisory = get_weather_advisory(condition)
            render_weather_advisory(advisory)

            # Download
            advisory_data = advisory.model_dump()
            advisory_data["analysis_type"] = "weather_advisory"
            report_json = generate_json_report(advisory_data, AnalysisMode.LIVE_AI)
            st.download_button(
                label="📥 Download Advisory Report",
                data=report_json,
                file_name=get_report_filename("weather_advisory"),
                mime="application/json",
            )

    # ── Construction Assistant Chatbot ──
    with chat_section:
        st.subheader("💬 Construction Assistant")

        if is_demo_mode():
            st.info(
                "🏷️ **Demo Mode** — Responses are pre-written examples. "
                "Configure an API key for AI-powered answers."
            )
        else:
            st.success("🤖 **AI Mode** — Powered by Google Gemini.")

        st.caption(
            "Ask questions about construction planning, site safety, PPE, "
            "concrete defects, budgets, materials, weather precautions, or daily checklists."
        )

        # Initialize chat history
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = []

        # Display chat history
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input("Ask about construction, safety, or planning..."):
            # Add user message
            st.session_state["chat_messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        ai_service = None if is_demo_mode() else GeminiService()
                        response = get_ai_response(
                            st.session_state["chat_messages"],
                            ai_service,
                        )
                    except Exception as e:
                        response = f"⚠️ Error: {e}\n\nSwitching to demo response:\n\n{get_demo_response(prompt)}"

                st.markdown(response)

            st.session_state["chat_messages"].append({"role": "assistant", "content": response})

        # Clear chat button
        if st.session_state.get("chat_messages"):
            if st.button("🗑️ Clear Chat History", key="clear_chat"):
                st.session_state["chat_messages"] = []
                st.rerun()


# ── Main Application ────────────────────────────────────────────────────────

def main():
    """Main application entry point."""
    render_sidebar()

    # App header
    st.markdown(
        f"<h1 style='text-align:center;'>{AppConfig.APP_ICON} {AppConfig.APP_TITLE}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#666; font-size:1.1rem;'>"
        "An intelligent decision-support platform for construction site safety, "
        "structural diagnostics, project planning, and weather-aware advisory."
        "</p>",
        unsafe_allow_html=True,
    )

    if is_demo_mode():
        render_demo_banner()

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🦺 Site Safety & PPE Audit",
        "🔍 Crack Diagnostics",
        "📐 Planning & Valuation",
        "🌤️ Assistant & Weather",
    ])

    with tab1:
        render_safety_tab()

    with tab2:
        render_crack_tab()

    with tab3:
        render_planning_tab()

    with tab4:
        render_assistant_tab()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#888; font-size:0.8rem;'>"
        "⚠️ <strong>Disclaimer:</strong> This platform is for decision-support and educational "
        "purposes only. It does not replace qualified structural engineers, professional safety "
        "inspections, certified valuations, or applicable local regulations.<br>"
        "Platform ID: <code>6ac4c98d1dcde6d7857c1642</code> | SkillWallet Capstone Project 1"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

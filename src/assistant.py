"""Construction assistant chatbot with multi-turn conversation support."""
from __future__ import annotations

from typing import Optional

from src.ai_service import ASSISTANT_SYSTEM_PROMPT, GeminiService
from src.config import is_demo_mode


# Demo mode responses for common topics
DEMO_RESPONSES: dict[str, str] = {
    "safety": """**Construction Site Safety Best Practices:**

1. **PPE Requirements**: All workers must wear appropriate PPE including hard hats, high-visibility vests, safety boots, and task-specific protection (gloves, goggles, harnesses).
2. **Site Induction**: Every worker should receive a safety induction before starting work.
3. **Daily Briefings**: Conduct toolbox talks at the start of each shift covering the day's hazards.
4. **Housekeeping**: Maintain clean, organized work areas to prevent trips and falls.
5. **Emergency Procedures**: Ensure all workers know emergency exits, assembly points, and first-aid locations.

⚠️ *This is general educational information. Always follow your site-specific safety plan and applicable regulations.*

🏷️ *[Demonstration Mode Response]*""",

    "ppe": """**Personal Protective Equipment (PPE) Guide:**

| PPE Item | Purpose | When Required |
|----------|---------|---------------|
| Hard Hat | Head protection from falling objects | Always on site |
| Hi-Vis Vest | Visibility for vehicle/equipment awareness | Always on site |
| Safety Boots | Foot protection, ankle support | Always on site |
| Safety Goggles | Eye protection from dust, debris | Cutting, grinding, demolition |
| Gloves | Hand protection | Material handling, concrete work |
| Harness | Fall protection | Work at height (typically >2m) |
| Ear Protection | Hearing protection | Near loud machinery |

⚠️ *PPE requirements vary by task and jurisdiction. Consult your site safety plan.*

🏷️ *[Demonstration Mode Response]*""",

    "concrete": """**Common Concrete Defects:**

1. **Hairline Cracks**: Very fine surface cracks, often from shrinkage during curing. Usually cosmetic.
2. **Settlement Cracks**: Caused by uneven foundation settlement. May indicate soil issues.
3. **Structural Shear Cracks**: Diagonal cracks, often near supports. May indicate overloading.
4. **Thermal Cracks**: From temperature changes causing expansion/contraction.
5. **Spalling**: Surface flaking or peeling, often from moisture ingress or rebar corrosion.

🔍 **Key Rule**: Any crack that is widening, associated with displacement, or appears in a structural element should be inspected by a qualified structural engineer.

🏷️ *[Demonstration Mode Response]*""",

    "budget": """**Construction Budget Planning Tips:**

1. **Rate Per Sq Ft**: Varies significantly by location, quality, and structure type:
   - Basic residential: ₹1,000–1,500/sq ft
   - Standard residential: ₹1,500–2,500/sq ft
   - Premium residential: ₹2,500–4,000/sq ft
   - Commercial: Often 20-40% higher than residential

2. **Key Cost Components**:
   - Foundation: ~15% of total cost
   - Structure (frame): ~25%
   - Brickwork & masonry: ~10%
   - MEP services: ~15%
   - Finishing: ~25%
   - Contingency: ~10%

3. **Material Estimates** (approximate per sq ft for residential):
   - Steel: 3.5–5 kg
   - Cement: 0.35–0.45 bags (50 kg each)

⚠️ *These are approximate ranges. Actual costs depend on local rates, design, and specifications.*

🏷️ *[Demonstration Mode Response]*""",

    "weather": """**Weather Precautions for Construction:**

🌧️ **Rain**: Protect materials, check drainage, avoid concrete pouring without protection, inspect excavations for instability.

🌪️ **High Wind**: Suspend crane operations above threshold, secure loose materials, avoid work at height.

☀️ **Extreme Heat**: Ensure hydration, schedule rest breaks, reschedule heavy work, follow hot-weather concrete practices.

❄️ **Cold Weather**: Protect freshly placed concrete from freezing, warm materials if needed, check for ice on surfaces.

🏷️ *[Demonstration Mode Response]*""",

    "default": """I can help with questions about:

- 🦺 **Site Safety** — PPE, hazards, safety procedures
- 🔍 **Concrete & Cracks** — Defect types, causes, repair options
- 📐 **Construction Planning** — Budgets, materials, milestones
- 🌤️ **Weather Precautions** — Safety in different weather conditions
- 📋 **Daily Checklists** — Site inspection procedures
- 📚 **Construction Terms** — Industry terminology explained

Try asking about any of these topics!

🏷️ *[Demonstration Mode — No AI key configured. Responses are pre-written examples.]*"""
}


def get_demo_response(user_message: str) -> str:
    """Get a demonstration mode response based on keyword matching.

    Args:
        user_message: The user's question

    Returns:
        A relevant demo response
    """
    message_lower = user_message.lower()

    if any(word in message_lower for word in ['safety', 'safe', 'hazard', 'accident', 'incident']):
        return DEMO_RESPONSES['safety']
    elif any(word in message_lower for word in ['ppe', 'helmet', 'vest', 'boot', 'harness', 'protective']):
        return DEMO_RESPONSES['ppe']
    elif any(word in message_lower for word in ['crack', 'concrete', 'defect', 'spalling', 'structural']):
        return DEMO_RESPONSES['concrete']
    elif any(word in message_lower for word in ['budget', 'cost', 'rate', 'price', 'estimate', 'material', 'steel', 'cement']):
        return DEMO_RESPONSES['budget']
    elif any(word in message_lower for word in ['weather', 'rain', 'wind', 'heat', 'cold', 'temperature']):
        return DEMO_RESPONSES['weather']
    else:
        return DEMO_RESPONSES['default']


def get_ai_response(
    messages: list[dict[str, str]],
    ai_service: Optional[GeminiService] = None
) -> str:
    """Get a response from the AI assistant.

    Args:
        messages: Conversation history as list of {role, content} dicts
        ai_service: Optional GeminiService instance

    Returns:
        Assistant response text
    """
    if is_demo_mode() or ai_service is None:
        # Use demo response for the latest user message
        latest_message = messages[-1]['content'] if messages else ''
        return get_demo_response(latest_message)

    try:
        return ai_service.chat(messages, system_prompt=ASSISTANT_SYSTEM_PROMPT)
    except Exception as e:
        return f"⚠️ AI service error: {str(e)}\n\nSwitching to demonstration mode for this response.\n\n{get_demo_response(messages[-1]['content'] if messages else '')}"

"""Nexus Core — The Meta-Coordinator Agent.

Handles natural language organizer requests, plans multi-agent workflows,
and provides the chat interface for the Command Bar.
Falls back to keyword-based routing if LLM is unavailable.
"""
from ..models.schemas import ChatResponse
from .llm_helper import call_llm_json


async def handle_chat_message(message: str) -> ChatResponse:
    """Process an organizer's natural language request.
    
    Args:
        message: The organizer's message from the Command Bar.
    
    Returns:
        ChatResponse with reply, execution plan, and involved agents.
    """
    prompt = f"""You are Nexus Core, the meta-coordinator for TechSummit 2026's AI agent swarm.

You coordinate 5 specialist agents:
- Chronos (Scheduler): Schedule management, conflict resolution
- Hermes (Mailer): Email communications, CSV processing, audience segmentation
- Apollo (Content): Social media content, promotional campaigns
- Athena (Analytics): Registration analytics, capacity planning, risk detection
- Fortuna (Budget): Budget tracking, cost estimation, financial alerts

The organizer says: "{message}"

Analyze the request and create an execution plan. Respond in JSON:
{{
    "reply": "Natural language response to the organizer (2-3 sentences, friendly and specific)",
    "plan": [
        "Step 1: → Agent Name: specific action",
        "Step 2: → Agent Name: specific action"
    ],
    "agents_involved": ["agent_name_1", "agent_name_2"]
}}

Be specific about what each agent will do. If the request is unclear, ask for clarification in the reply."""

    # Fallback: keyword-based routing
    msg_lower = message.lower()
    
    if any(word in msg_lower for word in ["schedule", "time", "move", "conflict", "session", "keynote"]):
        fallback = {
            "reply": "I'll coordinate the schedule change. Chronos will handle the rescheduling, and I'll loop in Hermes and Apollo for any downstream notifications.",
            "plan": [
                "→ Chronos: Analyze the schedule change and detect any conflicts",
                "→ Chronos: Resolve conflicts using priority heuristics",
                "→ Hermes: Draft notification emails for affected participants",
                "→ Apollo: Update any queued social posts mentioning old timing"
            ],
            "agents_involved": ["Chronos", "Hermes", "Apollo"]
        }
    elif any(word in msg_lower for word in ["email", "send", "mail", "notify", "csv", "upload"]):
        fallback = {
            "reply": "I'll get Hermes on it right away. The email workflow will include validation, personalization, and a preview before sending.",
            "plan": [
                "→ Hermes: Process and validate the participant data",
                "→ Hermes: Generate personalized email previews",
                "→ Hermes: Queue the batch for your approval"
            ],
            "agents_involved": ["Hermes"]
        }
    elif any(word in msg_lower for word in ["content", "post", "social", "promote", "campaign", "marketing"]):
        fallback = {
            "reply": "Apollo will craft some compelling content for you. I'll make sure it aligns with the latest schedule and audience data from Athena.",
            "plan": [
                "→ Athena: Pull latest audience demographics for targeting",
                "→ Apollo: Generate multi-platform content variants",
                "→ Apollo: Create a publishing timeline"
            ],
            "agents_involved": ["Apollo", "Athena"]
        }
    elif any(word in msg_lower for word in ["budget", "cost", "spend", "money", "expense", "revenue"]):
        fallback = {
            "reply": "I'll have Fortuna run a budget analysis for you. This includes current spending, revenue tracking, and any alerts on overruns.",
            "plan": [
                "→ Fortuna: Generate current budget snapshot",
                "→ Fortuna: Check for any line items approaching limits",
                "→ Fortuna: Provide recommendations for cost optimization"
            ],
            "agents_involved": ["Fortuna"]
        }
    elif any(word in msg_lower for word in ["analytics", "data", "registr", "capacity", "insight", "report"]):
        fallback = {
            "reply": "Athena will analyze the latest data and generate insights. I'll compile them on the dashboard for you.",
            "plan": [
                "→ Athena: Analyze current registration trends",
                "→ Athena: Check venue capacity against registrations",
                "→ Athena: Generate a risk assessment report"
            ],
            "agents_involved": ["Athena"]
        }
    else:
        fallback = {
            "reply": f"Got it! I'll analyze your request and coordinate the right agents. Based on \"{message[:100]}\", here's what I'm planning.",
            "plan": [
                "→ Nexus Core: Analyze request and identify required agents",
                "→ Relevant agents: Execute specific tasks based on request",
                "→ Nexus Core: Compile results and report back"
            ],
            "agents_involved": ["Nexus Core", "Chronos", "Hermes"]
        }

    result = await call_llm_json(prompt, fallback)

    return ChatResponse(
        reply=result.get("reply", fallback["reply"]),
        plan=result.get("plan", fallback["plan"]),
        agents_involved=result.get("agents_involved", fallback["agents_involved"])
    )

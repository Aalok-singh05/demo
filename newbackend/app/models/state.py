# LangGraph NexusState TypedDict — the shared state across all agents

from typing import TypedDict, List, Optional


class NexusState(TypedDict, total=False):
    # User request
    user_input: str
    request_type: str  # schedule, mail, content, analytics, general

    # Event context (shared read)
    event: dict
    participants: list
    schedule: list
    content_queue: list

    # Agent outputs
    scheduler_output: dict
    mailer_output: dict
    content_output: dict
    analytics_output: dict

    # Coordination
    pending_tasks: list
    messages: list
    activity_log: list

    # Human-in-the-loop
    requires_approval: bool
    approval_items: list

    # Control flow
    next_agent: str
    iteration_count: int
    error: str

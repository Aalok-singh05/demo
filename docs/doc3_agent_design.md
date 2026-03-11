# Document 3 — Autonomous Agent / Component Design

---

## 3.1 Agent Design Philosophy

Every agent in the system follows a consistent design contract:

```
┌─────────────────────────────────────────┐
│              AGENT ANATOMY              │
├─────────────────────────────────────────┤
│ Identity     │ Name, role, system prompt │
│ Capabilities │ LLM tools it can invoke  │
│ Inputs       │ What triggers it          │
│ Outputs      │ Structured Pydantic model │
│ Side Effects │ State mutations, events   │
│ Escalation   │ When it asks for human    │
│              │ approval                  │
└─────────────────────────────────────────┘
```

**Key principle:** An agent is NOT a wrapper around a single LLM call. An agent is a **stateful process** that may make multiple LLM calls, use tools, read/write shared state, and emit events — all within a single activation.

---

## 3.2 Baseline Agents (Required by Problem Statement)

---

### AGENT 1: The Scheduler — "Chronos"

**Role:** Master timeline builder and conflict resolver

**System Prompt Essence:**
> You are Chronos, the scheduling intelligence for a large-scale technical event. You build optimal schedules from rough constraints, detect conflicts, and resolve them autonomously. You always explain your reasoning.

**Capabilities:**

| Capability | Implementation |
|---|---|
| Build schedule from constraints | Takes natural language constraints + structured inputs, generates a complete timeline |
| Conflict detection | Checks for room overlaps, speaker double-bookings, time violations |
| Autonomous resolution | Applies heuristic rules: prioritize keynotes > workshops > breaks; minimize attendee disruption |
| Cascade notification | Emits events to trigger Mailing Agent when schedule changes |
| What-if analysis | "What happens if we move this session?" — simulates before committing |

**Input Schema:**
```python
class ScheduleRequest(BaseModel):
    event_name: str
    days: int
    venues: list[Venue]          # rooms with capacity
    sessions: list[Session]       # talks, workshops, breaks
    constraints: list[str]        # natural language: "Dr. Smith only available after 2 PM"
    fixed_slots: list[FixedSlot]  # immovable items (opening ceremony, etc.)
```

**Output Schema:**
```python
class ScheduleResult(BaseModel):
    timeline: list[ScheduledSession]  # each session with assigned room, time, speaker
    conflicts_found: list[Conflict]
    conflicts_resolved: list[Resolution]
    warnings: list[str]               # "Room A may be at 95% capacity"
    reasoning: str                    # why the agent made these choices
```

**Conflict Resolution Strategy:**
1. Detect all conflicts in proposed schedule
2. Classify by severity: HARD (same room, same time) vs SOFT (speaker preference violated)
3. Resolve HARD conflicts first using constraint relaxation
4. For SOFT conflicts, propose alternatives and escalate to organizer if ambiguous
5. After resolution, diff the old and new schedules to identify affected participants

**Inter-Agent Interactions:**
- **→ Mail Agent**: "These 87 participants are affected by schedule changes. Here are the details."
- **→ Content Agent**: "The keynote time changed. Update any queued social posts."
- **← Orchestrator**: Triggered by `SCHEDULE_CONSTRAINT_CHANGED` or `NEW_SESSION_ADDED` events

---

### AGENT 2: The Mailer — "Hermes"

**Role:** Communications and targeted mailing specialist

**System Prompt Essence:**
> You are Hermes, the communications specialist. You handle participant data, personalize emails, segment audiences, and manage bulk outreach. You validate data meticulously and never send without approval.

**Capabilities:**

| Capability | Implementation |
|---|---|
| CSV/Excel parsing | Extract participant data, validate emails, flag errors |
| Email personalization | Use participant data fields to customize a base template dynamically |
| Audience segmentation | Group participants by track, role, registration date, etc. |
| Bulk distribution | Send personalized emails via SMTP or simulated queue |
| Template management | Store and retrieve reusable email templates |

**Input Schema:**
```python
class MailRequest(BaseModel):
    action: Literal["parse_data", "personalize", "segment", "send"]
    data_file: Optional[str]       # path to uploaded CSV/Excel
    base_template: Optional[str]    # raw email draft with {{placeholders}}
    segment_criteria: Optional[str] # "all speakers", "day 2 attendees"
    recipients: Optional[list[Participant]]
```

**Output Schema:**
```python
class MailResult(BaseModel):
    action_completed: str
    participants_processed: int
    invalid_emails: list[InvalidEmail]
    segments_created: list[Segment]
    preview_emails: list[EmailPreview]   # first 3 personalized emails for approval
    ready_to_send: bool
    reasoning: str
```

**Personalization Engine:**
- Parses the base template for `{{field_name}}` placeholders
- Maps to CSV columns intelligently (handles "First Name", "first_name", "firstName" variants)
- Generates a preview batch for organizer review
- Supports conditional content: "If attendee.role == 'speaker', include speaker-specific instructions"

**Data Validation:**
- Email format validation (regex + MX record check if online)
- Duplicate detection
- Missing field warnings
- Encoding issue handling (common in Indian names with special characters)

**Inter-Agent Interactions:**
- **← Scheduler**: Receives notification requests when schedule changes
- **← Orchestrator**: Triggered by `PARTICIPANT_DATA_UPLOADED` or `SEND_NOTIFICATION` events
- **→ Frontend**: Streams progress ("Processing row 142/347...")

---

### AGENT 3: The Content Strategist — "Apollo"

**Role:** Marketing content creator and social media strategist

**System Prompt Essence:**
> You are Apollo, the creative marketing mind. You generate compelling promotional content, plan social media campaigns, and optimize posting schedules based on engagement analysis. You always provide multiple variants for the organizer to choose from.

**Capabilities:**

| Capability | Implementation |
|---|---|
| Content generation | Create promotional copy, social posts, email headers from raw prompts |
| Campaign planning | Suggest a multi-post series to build event hype over days/weeks |
| Engagement analysis | Analyze provided historical data to recommend optimal posting times |
| Content variants | Always generate 2-3 variants with different tones (professional, casual, hype) |
| Content queue | Maintain a queue of scheduled posts with status tracking |

**Input Schema:**
```python
class ContentRequest(BaseModel):
    action: Literal["generate", "plan_campaign", "analyze_timing", "update_content"]
    event_description: str
    target_audience: Optional[str]
    tone: Optional[str]           # "professional", "casual", "hype", "auto"
    platform: Optional[str]       # "twitter", "linkedin", "instagram", "email"
    historical_data: Optional[str] # engagement CSV for timing analysis
    existing_content_id: Optional[str]  # for updates after schedule changes
```

**Output Schema:**
```python
class ContentResult(BaseModel):
    content_pieces: list[ContentPiece]  # each with text, platform, suggested_time
    campaign_timeline: Optional[CampaignPlan]
    engagement_insights: Optional[EngagementAnalysis]
    reasoning: str
```

**Content Generation Strategy:**
- Takes raw event info and generates platform-specific content
- Each piece includes: main text, hashtags, emoji suggestions, image prompt (for generate_image tool)
- For campaigns: builds a narrative arc (Teaser → Reveal → Countdown → D-Day → Recap)
- Tone adaptation based on platform: LinkedIn (professional), Twitter/X (punchy), Instagram (visual)

**Engagement Analysis:**
- If historical data is provided, analyzes:
  - Day-of-week patterns
  - Time-of-day patterns
  - Content type performance (text vs image vs video mentions)
- Uses LLM to interpret patterns and recommend posting schedule
- If no historical data: uses general best practices by platform

**Inter-Agent Interactions:**
- **← Scheduler**: "Keynote time changed" → updates any queued posts mentioning the old time
- **← Orchestrator**: Triggered by `CONTENT_REQUESTED` or `EVENT_DETAILS_CHANGED` events
- **→ Frontend**: Delivers content to Content Studio for organizer preview and editing

---

## 3.3 Innovation Agents (Open Innovation — 20 Points)

These agents go beyond the baseline to create genuine "wow" moments.

---

### AGENT 4: The Analyst — "Athena"

**Role:** Real-time event intelligence and analytics

**Why This Wins Points:**
- Provides data-driven insights that no other team is likely to implement
- Makes the dashboard feel alive with real metrics
- Demonstrates practical value beyond content generation

**Capabilities:**

| Capability | Description |
|---|---|
| Registration analytics | Track signups over time, predict final attendance |
| Capacity planning | Warn when sessions approach room capacity limits |
| Engagement scoring | Score participants by involvement (sessions registered, emails opened) |
| Risk detection | Flag potential issues: "Speaker X hasn't confirmed", "Room B has no backup" |
| Post-event summary | Auto-generate event report with key metrics |

**Example Outputs:**
- "📊 Registration velocity is 23% slower than last week. Consider a reminder push."
- "⚠️ Workshop C has 45 registrants but Room 2 only seats 40. Recommend moving to Room 1."
- "🎯 42% of your registrants are students. Consider adding student-specific networking events."

**Inter-Agent Interactions:**
- **→ Content Agent**: "Registration is slowing. Generate a urgency-based promotional push."
- **→ Scheduler**: "Room capacity mismatch detected. Suggest room swap."
- **→ Mail Agent**: "These 15 speakers haven't confirmed. Draft follow-up emails."

---

### AGENT 5: The Meta-Coordinator — "Nexus Core"

**Role:** Orchestrator's intelligent assistant — handles complex multi-agent workflows

**Why This Wins Points:**
- Demonstrates a **higher-order agent** that coordinates other agents
- This is the most architecturally impressive component
- Shows that the system can handle complex, multi-step workflows autonomously

**Capabilities:**

| Capability | Description |
|---|---|
| Workflow planning | Breaks complex organizer requests into multi-agent task plans |
| Priority management | Decides which agent tasks are urgent vs can wait |
| Conflict mediation | When two agents have conflicting needs (e.g., Scheduler wants to cancel a session but Content already promoted it) |
| Summary generation | Provides the organizer with a daily/hourly briefing of all agent activities |
| Chat interface | Natural language interface for the organizer to give ad-hoc instructions |

**Example Interaction:**
```
Organizer: "We just confirmed a surprise keynote by the CEO. Add it to Day 2 afternoon
            and make sure everyone knows."

Meta-Coordinator's plan:
  1. → Scheduler: Add "CEO Keynote" to Day 2, 3:00-4:00 PM, Main Hall
  2. → Scheduler: Check for conflicts and resolve
  3. → Mail Agent: Draft and send "Exciting Update!" email to all registrants
  4. → Content Agent: Create social media hype post about surprise keynote
  5. → Analytics Agent: Update capacity projections for Main Hall

All steps execute in parallel where possible, with dependencies respected.
```

---

### AGENT 6: The Budget Tracker — "Fortuna" (Bonus Innovation)

**Role:** Financial oversight for the event

**Why This Wins Points:**
- No other team will think of this
- Adds practical viability (judges criterion: "ready to manage an actual event")
- Simple to implement but very impressive in a demo

**Capabilities:**
- Track vendor costs, venue fees, sponsorship revenue
- Estimate costs for schedule changes ("Moving to a bigger room costs $X more")
- Generate a budget dashboard
- Alert when spending approaches limits

---

## 3.4 Agent Communication Protocol

All inter-agent communication follows a structured protocol:

```python
class AgentMessage(BaseModel):
    from_agent: str           # "chronos", "hermes", "apollo", etc.
    to_agent: str             # target agent or "broadcast"
    message_type: str         # "request", "notification", "data_share"
    priority: str             # "critical", "normal", "low"
    payload: dict             # structured data relevant to the message
    requires_response: bool   # whether the sender is waiting for a reply
    timestamp: datetime
    trace_id: str             # for linking related messages in the activity log
```

This protocol ensures:
1. Every inter-agent interaction is logged and visible on the frontend
2. Messages are typed and validated
3. The orchestrator can prioritize and route messages
4. The activity panel can show a clear communication trail

---

## 3.5 Agent Memory Architecture

Each agent has two types of memory:

### Short-Term Memory (Within a Session)
- The current LangGraph state
- Conversation history with the organizer
- Pending tasks and their status

### Long-Term Memory (Across Sessions)
- Event configuration and preferences
- Past decisions and their outcomes
- Organizer's communication style preferences (learned over interactions)
- Stored in SQLite, loaded on agent activation

**Shared Memory (Cross-Agent):**
- The event schedule (single source of truth)
- Participant registry
- Content queue
- Action log (who did what, when, why)

All agents read from and write to the **same shared state object** managed by LangGraph. This prevents data inconsistencies and enables true coordination.

---

## 3.6 Agent Tool Definitions

Each agent has specific tools (functions) it can call:

### Chronos (Scheduler) Tools:
- `get_current_schedule()` → returns full timeline
- `add_session(session)` → adds a new session
- `detect_conflicts()` → scans for overlaps
- `resolve_conflict(conflict, strategy)` → applies resolution
- `notify_affected_participants(changes)` → emits event to Mail Agent

### Hermes (Mailer) Tools:
- `parse_csv(file_path)` → extracts participant data
- `validate_emails(participants)` → checks email validity
- `personalize_template(template, participant)` → fills placeholders
- `create_segment(criteria)` → groups participants
- `queue_emails(emails)` → stages for sending
- `send_emails(batch_id)` → executes send (requires approval flag)

### Apollo (Content) Tools:
- `generate_content(prompt, platform, tone)` → creates content pieces
- `plan_campaign(event_info, duration)` → creates multi-post timeline
- `analyze_engagement(historical_data)` → extracts timing insights
- `update_content(content_id, changes)` → modifies queued content
- `queue_post(content, scheduled_time)` → adds to publication queue

### Athena (Analytics) Tools:
- `analyze_registrations(data)` → trends and predictions
- `check_capacity(schedule, venues)` → capacity analysis
- `generate_risk_report()` → identifies potential issues
- `create_summary(time_period)` → generates briefing

---

*The next document explains how these agents actually coordinate and communicate with each other through the orchestration layer.*

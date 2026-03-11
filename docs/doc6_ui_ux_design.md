# Document 6 — User Interface and Product Experience

---

## 6.1 Design Philosophy

The UI has one job: **make the invisible visible.**

Multi-agent systems are powerful but abstract. If judges can't *see* the agents working, collaborating, and reasoning, they'll assume it's just a fancy wrapper around ChatGPT. The UI must:

1. **Show agency** — Agents are characters with names, avatars, and visible activity
2. **Show coordination** — Inter-agent handoffs are displayed as real-time events
3. **Show intelligence** — Reasoning chains, not just outputs
4. **Enable control** — The organizer approves, edits, or overrides anything

---

## 6.2 Visual Design System

### Color Palette (Dark Mode)

The dashboard should use a **dark, professional theme** — think mission control, not pastel SaaS.

| Element | Color | Hex |
|---|---|---|
| Background | Deep Navy | `#0a0f1e` |
| Card Background | Dark Slate | `#111827` |
| Primary Accent | Electric Blue | `#3b82f6` |
| Success | Emerald | `#10b981` |
| Warning | Amber | `#f59e0b` |
| Error | Red | `#ef4444` |
| Text Primary | White | `#f9fafb` |
| Text Secondary | Gray | `#9ca3af` |
| Agent Chronos | Blue | `#60a5fa` |
| Agent Hermes | Green | `#34d399` |
| Agent Apollo | Purple | `#a78bfa` |
| Agent Athena | Orange | `#fb923c` |

### Typography
- **Headlines:** Inter (bold, clean)
- **Body:** Inter (regular)
- **Code/Data:** JetBrains Mono

### Agent Identity System

Each agent has:
- A distinct color (see above)
- An icon/emoji (📅 Chronos, 📧 Hermes, 📱 Apollo, 📊 Athena)
- A persona name displayed in the activity feed
- Status indicator (idle/working/done/error)

---

## 6.3 Page Layout — The Dashboard

The main dashboard is a **command center** layout with 4 key zones:

```
┌─────────────────────────────────────────────────────────────────────┐
│  NEXUS   [🔍 Command Bar: "What if we move the keynote to 3 PM?"]  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
├──────────────────────┬──────────────────────────────────────────────┤
│                      │                                              │
│  📊 EVENT OVERVIEW   │  📋 AGENT ACTIVITY FEED                      │
│                      │                                              │
│  Event: TechSummit   │  ┌─────────────────────────────────────┐    │
│  Days: 3             │  │ 12:34 📅 Chronos is working...     │    │
│  Attendees: 347      │  │ "Checking for conflicts in         │    │
│  Sessions: 24        │  │  Day 2 schedule"                   │    │
│  Speakers: 18        │  ├─────────────────────────────────────┤    │
│                      │  │ 12:33 📧 Hermes completed          │    │
│  ┌────────────────┐  │  │ "Processed 347 participants        │    │
│  │ Agent Status   │  │  │  from CSV (12 invalid emails)"     │    │
│  │                │  │  ├─────────────────────────────────────┤    │
│  │ 📅 Working...  │  │  │ 12:32 📊 Athena insight            │    │
│  │ 📧 Idle        │  │  │ "Registration velocity is 23%      │    │
│  │ 📱 Idle        │  │  │  below target"                     │    │
│  │ 📊 Observing   │  │  ├─────────────────────────────────────┤    │
│  └────────────────┘  │  │ 12:31 📱 Apollo completed          │    │
│                      │  │ "Generated 3 promotional post       │    │
│  ┌────────────────┐  │  │  variants for LinkedIn"            │    │
│  │ Quick Stats    │  │  └─────────────────────────────────────┘    │
│  │ Emails Sent: 0 │  │                                              │
│  │ Posts Queued: 5 │  │                                              │
│  │ Conflicts: 0   │  │                                              │
│  └────────────────┘  │                                              │
│                      │                                              │
├──────────────────────┴──────────────────────────────────────────────┤
│                                                                     │
│  ⚡ PENDING APPROVALS                                               │
│                                                                     │
│  ┌──────────────────────┐  ┌──────────────────────┐                │
│  │ 📧 Email Batch       │  │ 📱 Social Post       │                │
│  │ "Schedule update"   │  │ "Keynote announce"  │                │
│  │ 87 recipients       │  │ LinkedIn + Twitter   │                │
│  │                     │  │                      │                │
│  │ [Approve] [Edit]    │  │ [Approve] [Edit]     │                │
│  └──────────────────────┘  └──────────────────────┘                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6.4 Key UI Pages

### Page 1: Dashboard (Home)
- **Event overview card** with key metrics
- **Agent status indicators** (working/idle/error)
- **Live activity feed** streaming via WebSocket
- **Pending approvals** section
- **Quick insights** from Athena
- **Command bar** at the top for natural language input

### Page 2: Schedule View
- **Interactive timeline** showing all sessions across days and rooms
- **Visual conflict highlights** (red overlay on conflicting blocks)
- **Drag-and-drop** session rearrangement (triggers Scheduler Agent on drop)
- **Session detail panel** (click a session → see speaker, attendees, room)
- **"What-If" button** — simulate changes before committing
- **Color-coded sessions** by type (keynote, workshop, break, networking)

```
┌─────────────────────────────────────────────────────┐
│  SCHEDULE — Day 2                                    │
│  ┌─────────┬──────────┬──────────┬──────────┐       │
│  │  Time   │  Room A  │  Room B  │  Room C  │       │
│  ├─────────┼──────────┼──────────┼──────────┤       │
│  │ 9:00 AM │ ████████ │          │ ████████ │       │
│  │         │ Keynote  │          │ Workshop │       │
│  │         │ (Dr.Chen)│          │ (AI 101) │       │
│  ├─────────┼──────────┼──────────┼──────────┤       │
│  │ 10:30AM │          │ ████████ │ ████████ │       │
│  │         │  BREAK   │ Panel    │ Workshop │       │
│  │         │          │ (Ethics) │ (ML Ops) │       │
│  ├─────────┼──────────┼──────────┼──────────┤       │
│  │ 1:00 PM │ ████████ │ ██🔴██  │          │       │
│  │         │ Workshop │ CONFLICT │          │       │
│  │         │ (Web3)   │ 2 events │          │       │
│  └─────────┴──────────┴──────────┴──────────┘       │
│                                                      │
│  🔴 1 Conflict Detected                              │
│  [🤖 Auto-Resolve]  [✍️ Manual Fix]  [🔮 Simulate] │
└─────────────────────────────────────────────────────┘
```

### Page 3: Content Studio
- **Content generation panel** — input prompt, select platform, choose tone
- **Content variants** displayed as cards (2-3 options per generation)
- **Campaign timeline** — visual view of planned post schedule
- **Preview mode** — see posts as they'd appear on each platform
- **Engagement insights** (if historical data provided)
- **One-click approve → queue** workflow

### Page 4: Mail Center
- **CSV upload zone** (drag-and-drop)
- **Data preview table** — see parsed participants with validation status
- **Segment creator** — filter participants by criteria
- **Email composer** with template placeholders
- **Preview carousel** — swipe through personalized emails
- **Send progress** — real-time progress bar during batch send

### Page 5: Agent Activity (Detailed View)
- **Full chronological log** of all agent actions
- **Reasoning chain visualizer** — expand any action to see why
- **Inter-agent message timeline** — see how agents communicated
- **Filter by agent** — show only Chronos actions, only Hermes, etc.
- **Export log** — download activity history

---

## 6.5 Real-Time UI Behaviors

### Agent Working Animation
When an agent is active, its card in the sidebar should:
- Pulse with its signature color
- Show a brief text of what it's doing: "Resolving conflict in Day 2..."
- Display a subtle animated indicator (spinner or progress dots)

### Activity Feed Streaming
- New items slide in from the top with a smooth animation
- Color-coded left border matching the agent's color
- Expandable: click to see full reasoning and details
- Auto-scroll to latest, but pause scrolling if user is reading older items

### Approval Card Interactions
- Cards slide in when approval is needed
- "Approve" triggers a satisfying checkmark animation + green flash
- "Edit" opens an inline editor with the agent's draft pre-filled
- "Reject" shows a brief "Why?" textarea for the agent to learn from

### Cascading Event Visualization
When a cascade happens (Scheduler → Mailer → Content):
- The activity feed shows a **connected chain** with arrows between entries
- A "cascade" badge appears: "⚡ Cascade: 3 agents activated"
- The agent status indicators all light up in sequence (Chronos → Hermes → Apollo)

---

## 6.6 Mobile Responsiveness

For a hackathon, full mobile responsiveness isn't required, but:
- The dashboard should work on a laptop screen (1366×768 minimum)
- Side panels should be collapsible
- Tables should be horizontally scrollable
- Font sizes should be readable without zooming

---

## 6.7 Component Library Recommendation

**Shadcn/UI + Tailwind CSS** (if team is comfortable with Tailwind):
- Beautiful, accessible components out of the box
- Dark mode support built-in
- Easy to customize
- Widely used, well-documented

**OR Ant Design** (if team prefers conventional component libraries):
- Rich component set (tables, forms, modals, timelines)
- Built-in dark theme
- More opinionated, but faster to build with

For charts: **Recharts** (simple, React-native) or **Nivo** (more beautiful but more complex).

For the timeline/Gantt view: Custom implementation using CSS Grid or a lightweight library like `react-big-calendar`.

---

## 6.8 Key UI/UX Principles for Judges

1. **Every screen should show agent activity** — even if it's just a small indicator in the corner
2. **Labels and explanations everywhere** — judges need to understand what they're looking at in seconds
3. **Smooth animations** — they signal quality. Use `framer-motion` for React animations
4. **Professional color scheme** — dark mode with accent colors feels more "mission control" than "toy project"
5. **Loading states** — when agents are processing, show meaningful loading states (not just spinners — show what the agent is doing)
6. **Error states** — if something fails, show a clear error with a "Retry" button

---

## 6.9 The "Judge Walk-Through" Path

Design the UI so that a judge can understand the system in 60 seconds:

```
1. Land on Dashboard → See event overview, active agents, recent activity
2. See a pending approval → Click "Approve" → Watch the cascade happen
3. Navigate to Schedule → See the interactive timeline → Trigger a conflict
4. Watch auto-resolution → See the reasoning chain → See notification sent
5. Open Mail Center → See parsed CSV data → Preview personalized emails
6. Open Content Studio → See generated posts → Approve and queue
```

This flow should be seamless, with no dead ends or confusing navigation.

---

*The next document covers how the team should divide this work efficiently.*

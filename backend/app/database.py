"""SQLite database layer with async support and demo data seeding."""
import aiosqlite
import os
import json
from pathlib import Path
from datetime import datetime

DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/nexus.db")


def _get_db_path():
    """Resolve DB path relative to backend directory."""
    backend_dir = Path(__file__).resolve().parent.parent
    db_path = backend_dir / DATABASE_PATH.lstrip("./")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return str(db_path)


DB_PATH = _get_db_path()


async def get_db():
    """Get an async database connection."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Create all tables and seed with demo data."""
    db = await get_db()
    try:
        # ── Create Tables ──────────────────────────────────
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                venue TEXT NOT NULL,
                days INTEGER DEFAULT 3,
                attendees INTEGER DEFAULT 0,
                sessions_count INTEGER DEFAULT 0,
                speakers INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                time TEXT NOT NULL,
                room TEXT NOT NULL,
                speaker TEXT DEFAULT '',
                type TEXT DEFAULT 'workshop',
                has_conflict INTEGER DEFAULT 0,
                conflict_with INTEGER DEFAULT NULL,
                day INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT DEFAULT 'attendee',
                status TEXT DEFAULT 'valid',
                segment TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT NOT NULL,
                agent TEXT NOT NULL,
                text TEXT NOT NULL,
                status TEXT DEFAULT 'done',
                details TEXT DEFAULT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                agent TEXT NOT NULL,
                desc TEXT NOT NULL,
                impact TEXT NOT NULL,
                preview TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                desc TEXT NOT NULL,
                action TEXT DEFAULT '',
                source_agent TEXT DEFAULT 'athena',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS content_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                tone TEXT NOT NULL,
                text TEXT NOT NULL,
                image_prompt TEXT DEFAULT '',
                scheduled_time TEXT DEFAULT '',
                status TEXT DEFAULT 'draft',
                is_recommended INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent TEXT NOT NULL,
                action TEXT NOT NULL,
                reasoning TEXT NOT NULL,
                cascaded_to TEXT DEFAULT '[]',
                status TEXT DEFAULT 'completed',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS agent_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                state_json TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS budget_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ── Seed Demo Data (only if tables are empty) ──────
        row = await db.execute_fetchall("SELECT COUNT(*) as cnt FROM events")
        if row[0][0] == 0:
            await _seed_demo_data(db)

        await db.commit()
    finally:
        await db.close()


async def _seed_demo_data(db: aiosqlite.Connection):
    """Seed database with demo data matching frontend's hardcoded values."""

    # Event
    await db.execute(
        "INSERT INTO events (name, venue, days, attendees, sessions_count, speakers, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("TechSummit 2026", "Main Campus, Building A", 3, 347, 24, 18, "active")
    )

    # Sessions
    sessions = [
        ("Opening Keynote: AI in 2026", "09:00 AM - 10:30 AM", "Main Hall", "Dr. Sarah Chen", "keynote", 0, None, 1),
        ("Workshop: Multi-Agent Systems", "11:00 AM - 12:30 PM", "Room A", "James Wilson", "workshop", 0, None, 1),
        ("Panel: Ethics in Automation", "11:00 AM - 12:30 PM", "Room B", "Mixed Panel", "panel", 0, None, 1),
        ("Networking Lunch", "12:30 PM - 02:00 PM", "Dining Pavilion", "", "break", 0, None, 1),
        ("Workshop: LangGraph Deep Dive", "02:00 PM - 03:30 PM", "Room A", "Elena Rostova", "workshop", 1, 6, 1),
        ("Founder AMA Session", "02:00 PM - 03:00 PM", "Room A", "Startup Hub", "panel", 1, 5, 1),
        ("Cloud Infrastructure Talk", "09:00 AM - 10:00 AM", "Room B", "Raj Patel", "workshop", 0, None, 2),
        ("Design Systems Workshop", "10:30 AM - 12:00 PM", "Room A", "Maya Lin", "workshop", 0, None, 2),
        ("Closing Keynote: Future of Tech", "03:00 PM - 04:30 PM", "Main Hall", "Dr. Sarah Chen", "keynote", 0, None, 3),
    ]
    await db.executemany(
        "INSERT INTO sessions (title, time, room, speaker, type, has_conflict, conflict_with, day) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        sessions
    )

    # Participants (sample set)
    participants = [
        ("Dr. Sarah Chen", "sarah.chen@university.edu", "speaker", "valid"),
        ("Alex Johnson", "alex.j@startup.io", "attendee", "valid"),
        ("Priya Sharma", "priya.s@techcorp.com", "attendee", "valid"),
        ("James Wilson", "j.wilson@research.org", "speaker", "valid"),
        ("Elena Rostova", "elena.r@ailab.eu", "speaker", "valid"),
        ("Raj Patel", "raj.patel@cloud.dev", "speaker", "valid"),
        ("Maya Lin", "maya.lin@design.co", "speaker", "valid"),
        ("Unknown User", "john.doe@missingdomain.com", "attendee", "invalid"),
        ("Ananya Gupta", "ananya@devtools.in", "attendee", "valid"),
        ("Tom Baker", "tom.b@startuphub.com", "attendee", "valid"),
        ("Fatima Al-Rashid", "fatima@mlresearch.ae", "attendee", "valid"),
        ("Carlos Mendez", "carlos.m@data.mx", "attendee", "valid"),
    ]
    await db.executemany(
        "INSERT INTO participants (name, email, role, status) VALUES (?, ?, ?, ?)",
        participants
    )

    # Activity Log
    activities = [
        ("12:34 PM", "Chronos", "Detected 2 schedule conflicts in Day 2. Resolving...", "working", None),
        ("12:33 PM", "Hermes", "Processed 347 participants from CSV. 12 invalid emails flagged.", "done", None),
        ("12:31 PM", "Apollo", "Generated 3 promotional post variants for LinkedIn.", "done", "Based on historical data, recommended posting at 2 PM."),
        ("12:28 PM", "Athena", "Registration velocity analysis complete. 23% slowdown detected.", "done", "Recommended promotional push to meet target of 500."),
        ("12:25 PM", "Fortuna", "Budget snapshot updated. Current spend: ₹4.2L of ₹6L budget.", "done", "Venue costs are 15% over initial estimate."),
        ("12:20 PM", "System", "Registration CSV uploaded by Organizer", "done", None),
    ]
    await db.executemany(
        "INSERT INTO activity_log (time, agent, text, status, details) VALUES (?, ?, ?, ?, ?)",
        activities
    )

    # Pending Approvals
    approvals = [
        ("Email Batch", "Hermes", '"Schedule update"', "87 recipients", "Dear {{name}}, the workshop you registered for has moved to..."),
        ("Social Post", "Apollo", '"Keynote announce"', "LinkedIn + Twitter", "🚨 Update! The keynote by Dr. Chen will now start at 10 AM in..."),
        ("Budget Alert", "Fortuna", '"Venue cost overrun"', "₹30K over budget", "Venue rental for Day 3 exceeds allocated budget by 15%. Suggest renegotiation."),
    ]
    await db.executemany(
        "INSERT INTO approvals (title, agent, desc, impact, preview) VALUES (?, ?, ?, ?, ?)",
        approvals
    )

    # Insights
    insights = [
        ("warning", "Capacity Warning", "Workshop C has 45 registrants but Room 2 only seats 40.", "Suggest Swap"),
        ("info", "Registration Velocity", "Velocity is 23% slower than last week. Target is 500.", "Push Promo"),
        ("success", "Audience Insight", "42% of registrants are students. Highly engaged.", ""),
    ]
    await db.executemany(
        "INSERT INTO insights (type, title, desc, action) VALUES (?, ?, ?, ?)",
        insights
    )

    # Agent State
    state = {
        "iteration_count": 4,
        "next_agent": "apollo",
        "requires_approval": True,
        "pending_tasks": [
            {"target": "hermes", "task": "send_batch", "status": "APPROVED"},
            {"target": "fortuna", "task": "budget_review", "status": "PENDING"}
        ],
        "event_config": {"name": "TechSummit 2026", "days": 3, "venues": 4},
        "conflicts_resolved": 2,
        "latest_trigger": "SCHEDULE_CONSTRAINT_CHANGED"
    }
    await db.execute(
        "INSERT OR REPLACE INTO agent_state (id, state_json, updated_at) VALUES (1, ?, ?)",
        (json.dumps(state), datetime.now().isoformat())
    )

    # Agent Reasoning Logs
    logs = [
        ("10:45 AM", "System", "Organizer Input", "Modified Keynote Time: 10:00 AM → 2:00 PM", "[]"),
        ("10:45 AM", "Chronos", "Conflict Resolution",
         '> Detected overlap: Room A double-booked at 2:00 PM.\n> "LangGraph Deep Dive" vs "Opening Keynote".\n> Applying heuristic: Keynote priority > Workshop priority.\n> Moving "LangGraph Deep Dive" to newly freed 10:00 AM slot.',
         '["hermes", "apollo"]'),
        ("10:46 AM", "Hermes", "Notification Gen",
         '> Received SCHEDULE_MODIFIED event.\n> Queried DB for participants registered to "LangGraph Deep Dive" (87 attendees) and "Keynote" (320 attendees).\n> Generating 407 targeted notification emails.\n> Halted on user approval requirement.',
         '[]'),
        ("10:46 AM", "Nexus Core", "Workflow Planning",
         '> Analyzing cascading impact of schedule change.\n> Identified 3 downstream tasks: notification emails, social post update, budget impact check.\n> Dispatching tasks to Hermes, Apollo, and Fortuna in parallel.',
         '["hermes", "apollo", "fortuna"]'),
        ("10:47 AM", "Fortuna", "Budget Impact",
         '> Schedule change requires extending Room A booking by 30 mins.\n> Additional cost: ₹5,000.\n> Current budget utilization: 70%. Within safe limits.',
         '[]'),
    ]
    await db.executemany(
        "INSERT INTO agent_logs (timestamp, agent, action, reasoning, cascaded_to) VALUES (?, ?, ?, ?, ?)",
        logs
    )

    # Budget Items
    budget_items = [
        ("Venue", "Main Hall rental (3 days)", 150000.0, "expense"),
        ("Venue", "Room A rental (3 days)", 45000.0, "expense"),
        ("Venue", "Room B rental (3 days)", 40000.0, "expense"),
        ("Catering", "Lunch buffet (3 days × 400 pax)", 120000.0, "expense"),
        ("Marketing", "Social media ads", 25000.0, "expense"),
        ("Speakers", "Honorarium & travel", 80000.0, "expense"),
        ("Sponsorship", "TechCorp Gold Sponsor", 300000.0, "revenue"),
        ("Sponsorship", "StartupHub Silver Sponsor", 150000.0, "revenue"),
        ("Tickets", "Early bird registrations (200 × ₹500)", 100000.0, "revenue"),
        ("Tickets", "Regular registrations (147 × ₹750)", 110250.0, "revenue"),
    ]
    await db.executemany(
        "INSERT INTO budget_items (category, description, amount, type) VALUES (?, ?, ?, ?)",
        budget_items
    )

    # Content Queue
    content_items = [
        ("linkedin", "professional",
         "We are thrilled to announce Dr. Sarah Chen as our opening keynote speaker for TechSummit 2026.\n\nJoin us as she explores the paradigm-shifting impacts of autonomous AI over the next 5 years.\n\n#TechSummit2026 #AI #Innovation",
         "A professional banner showing Dr. Sarah Chen speaking at a tech conference with futuristic holographic displays", "", "draft", 1),
        ("twitter", "hype",
         "🚨 BIG NEWS! 🚨\n\nDr. Sarah Chen is officially opening TechSummit 2026! 🤯 You don't want to miss her breakdown of how autonomous AI is rebuilding our world in the next 5 years.\n\nSecure your spot now! 👇\n#TechSummit2026",
         "Tech_Summit_Banner_v2.webp", "", "draft", 0),
    ]
    await db.executemany(
        "INSERT INTO content_queue (platform, tone, text, image_prompt, scheduled_time, status, is_recommended) VALUES (?, ?, ?, ?, ?, ?, ?)",
        content_items
    )

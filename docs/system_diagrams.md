# Nexus Event Intelligence Platform — System Diagrams

This document contains visual diagrams outlining the core architecture, orchestration flows, and database structures of the Nexus backend.

## 1. High-Level System Architecture

This diagram shows how the React Frontend interacts with the FastAPI backend, and how the backend manages the SQLite database, real-time WebSocket streams, and the LangGraph orchestration engine.

```mermaid
graph TD
    classDef frontend fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff;
    classDef backend fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;
    classDef db fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff;
    classDef ai fill:#8b5cf6,stroke:#4c1d95,stroke-width:2px,color:#fff;

    UI[React Frontend Dashboard]:::frontend

    subgraph Backend Infrastructure [FastAPI Backend]
        API[REST HTTP APIs]:::backend
        WS[WebSocket Manager]:::backend
        StateManager[In-Memory State Manager]:::backend
        EventDispatcher[Event Dispatcher]:::backend
    end

    subgraph LangGraph Orchestration [Multi-Agent Orchestrator]
        Router[Router Node]:::ai
        Evaluator[Evaluator Node]:::ai
        Agents[(Chronos, Hermes, Apollo, Athena)]:::ai
    end

    DB[(SQLite Database)]:::db

    %% Connections
    UI <-->|HTTP Requests| API
    UI <-->|Real-time Events| WS
    API --> DB

    API -->|Triggers| EventDispatcher
    EventDispatcher -->|Invokes| Router

    Router --> Agents
    Agents -->|Results/Drafts| Evaluator
    Evaluator -.->|Cascading Tasks| Router
    
    Evaluator -->|Saves Approvals| DB
    Evaluator -->|Streams Activity| WS
    Agents -->|Streams Status| WS
```

---

## 2. LangGraph Orchestrator Flow

This flow illustrates the underlying state machine that powers the `NexusState` inside `app/agents/orchestrator.py`. It shows how requests are routed and how agents are evaluated for cascading tasks or human approvals.

```mermaid
stateDiagram-v2
    [*] --> Router : API Request or Internal Event

    state Router {
        [*] --> ClassifyRequest
        ClassifyRequest --> PickAgent
    }

    Router --> chronos : type = schedule
    Router --> hermes : type = mail
    Router --> apollo : type = content
    Router --> athena : type = analytics

    chronos --> Evaluator
    hermes --> Evaluator
    apollo --> Evaluator
    athena --> Evaluator

    state Evaluator {
        [*] --> CheckCascading
        CheckCascading --> CheckApprovalNeeded
    }

    Evaluator --> Router : Has Pending Tasks (Loop)
    Evaluator --> [*] : Requires Approval (Pause)
    Evaluator --> [*] : Done (No tasks/Empty Queue)
```

---

## 3. Autonomous Workflow: CSV Upload Event

This sequence diagram details exactly what happens across the system when an organizer uploads a participant CSV file.

```mermaid
sequenceDiagram
    participant UI as Organizer (Frontend)
    participant API as /api/upload
    participant DB as SQLite DB
    participant Dispatcher as Event Dispatcher
    participant Athena as Athena (Analytics)
    participant Hermes as Hermes (Mail)
    participant WS as WebSocket

    UI->>API: POST /api/upload/participants (CSV)
    API->>API: Parse CSV & Validate Emails
    API->>DB: Bulk insert participants
    API->>Dispatcher: dispatch(PARTICIPANT_DATA_UPLOADED)
    
    par Parallel Agent Execution
        Dispatcher->>Athena: run_orchestrator(Analyze Data)
        Dispatcher->>Hermes: run_orchestrator(Draft Welcome Emails)
    end
    
    Athena-->>DB: Save capacity/registration insights
    Athena-->>WS: Stream [Done] Status
    
    Hermes-->>Hermes: Personalize templates based on CSV
    Hermes->>DB: Save target segment & email drafts
    Hermes-->>WS: Stream [APPROVAL_REQUIRED]
    
    Note over UI,WS: Organizer sees metrics and pending approval card
    
    UI->>API: POST /api/approval/{id} (Approve)
    API->>DB: Update approval status
    API->>Dispatcher: dispatch(EMAIL_APPROVED)
    Dispatcher->>Hermes: Execute SMTP Send
    Hermes-->>WS: Stream [Emails Sent] Success
```

---

## 4. Automatic Conflict Resolution & Cascading

This sequence demonstrates how a single manual request triggers a chain reaction between multiple agents via the `Evaluator` node.

```mermaid
sequenceDiagram
    participant UI as Organizer
    participant Router as Orchestrator Router
    participant Chronos as Chronos (Scheduler)
    participant Evaluator as Orchestrator Evaluator
    participant Apollo as Apollo (Content)
    participant Hermes as Hermes (Mail)

    UI->>Router: "Move Keynote to 2:00 PM Thursday"
    
    Router->>Chronos: Route Request (Schedule)
    Chronos->>Chronos: Detects double-booking at 2:00 PM
    Chronos->>Chronos: Moves conflicting session to Room B
    Chronos->>Evaluator: Return successful schedule update + 2 Cascade Tasks
    
    Note over Evaluator: Emits Cascade Tasks to queue
    Evaluator->>Router: Loop -> Next Task (Content)
    
    Router->>Apollo: Task: Publish schedule change
    Apollo->>Evaluator: Return drafted Tweets (Requires Approval)
    
    Evaluator->>Router: Loop -> Next Task (Mail)
    
    Router->>Hermes: Task: Email attendees about room change
    Hermes->>Evaluator: Return drafted Emails (Requires Approval)
    
    Evaluator-->>UI: End Graph & Request 2 Approvals via WebSocket
```

---

## 5. Database Entity Relationship Diagram (ERD)

How the core SQLite tables relate to one another to store event memory and logs.

```mermaid
erDiagram
    EVENTS ||--o{ PARTICIPANTS : "has many"
    EVENTS ||--o{ SESSIONS : "has many"
    EVENTS ||--o{ CONTENT_QUEUE : "has many"
    EVENTS ||--o{ APPROVALS : "has many"
    EVENTS ||--o{ AGENT_LOGS : "has many"

    EVENTS {
        string id PK
        string name
        string status
        string start_date
        string end_date
    }

    PARTICIPANTS {
        string id PK
        string event_id FK
        string name
        string email
        string role
        boolean is_valid_email
    }

    SESSIONS {
        string id PK
        string event_id FK
        string title
        string speaker
        string start_time
        string venue
    }

    CONTENT_QUEUE {
        string id PK
        string event_id FK
        string content_type
        string body
        string platform
        string status
    }

    APPROVALS {
        string id PK
        string event_id FK
        string agent
        string action
        string status
    }

    AGENT_LOGS {
        string id PK
        string event_id FK
        string agent
        string action
        string details
    }
```

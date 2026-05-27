# Production-Grade AI Systems Architecture & Expansion Plan

## Goal Description
Transform the existing functional AI-powered restaurant recommender into a **Production-Grade AI Recommendation and Decision-Support System**. This upgrade elevates the project from a standard LLM wrapper to a mature portfolio piece demonstrating operational AI readiness, multi-agent orchestration, advanced telemetry, reliability engineering, and AI product management (PM) thinking.

No executable code has been implemented yet. This document serves as the formal architectural specification and PM tradeoff analysis for stakeholder review and approval.

---

## User Review Required

> [!IMPORTANT]
> **1. Data Persistence Choice:** For the Human Feedback, Memory, and Analytics layers, we propose using a lightweight local `SQLite` database rather than just flat files. This provides realistic query capabilities for telemetry dashboards while remaining fully local and easy to set up.
>
> **2. Multi-Agent Latency Tradeoff:** Introducing a Critic/Validation agent will increase the end-to-end latency. We propose mitigating this by routing the Critic Agent to an ultra-fast model (e.g., `Llama3-8b` via Groq) while the Semantic Ranker uses a heavier model.
>
> **3. Scope of Analytics:** The proposed telemetry and analytics layers will generate significant local log data. We will implement log rotation and TTL (Time-To-Live) constraints to ensure the application footprint remains lightweight.

## Open Questions

> [!NOTE]
> **Q1:** Do we want to build a lightweight internal "Admin/Ops Dashboard" in the frontend to visualize the Telemetry and Evaluation data, or simply log it to structured files for portfolio demonstration purposes?
>
> **Q2:** For Cost-Aware Orchestration, do you have a preference for mixing API providers (e.g., Groq for fast cheap routing, OpenAI/Gemini for complex synthesis), or should we stick exclusively to Groq models to simplify API key management?

---

## Phase 1 Execution Plan: Foundation & Observability

We will execute **Phase 1** of the recommended roadmap. This phase introduces the foundational tracking, routing, and caching mechanisms necessary before building the complex multi-agent layers.

### 1. Telemetry & Observability Logger
*   **[NEW] `backend/src/observability/logger.py`**: Create a `TelemetryLogger` class to structure and append JSON logs into `backend/data/logs/telemetry.jsonl`.
*   **[MODIFY] `backend/src/api.py`**:
    *   Generate a unique `trace_id` for every request using the `uuid` module.
    *   Fire `AI_REQUEST_START` and `AI_REQUEST_COMPLETE` telemetry events.
    *   Capture and log `latency_seconds`.

### 2. Prompt Caching
*   **[NEW] `backend/src/observability/cache.py`** (or embedded in `recommender.py`): Implement a SHA-256 hash generator that creates a unique key from `(location, cuisine, budget, min_rating, qualitative)`.
*   **[MODIFY] `backend/src/recommender.py`**:
    *   Before invoking the LLM, check if the hash exists in a local `backend/data/cache.json` file.
    *   If it exists, return the cached JSON instantly (latency < 50ms, cost = $0).
    *   If it misses, call the LLM and save the response to the cache file.

### 3. Cost-Aware Routing
*   **[MODIFY] `backend/src/config.py`**: Define `FAST_MODEL` (`llama3-8b-8192`) and `REASONING_MODEL` (`llama3-70b-8192` or `llama-3.3-70b-versatile`).
*   **[MODIFY] `backend/src/recommender.py`**:
    *   Add routing logic: If the `qualitative` input is empty or very short (<10 chars), use the `FAST_MODEL` to save costs, as it primarily just formats the deterministic outputs.
    *   If the user provides a detailed qualitative query, route to the `REASONING_MODEL` for deep semantic reasoning.

---

## Phase 2 Execution Plan: Multi-Agent Pipeline & Reliability

We will execute **Phase 2** to transition from a monolithic script to a robust, self-correcting agentic pipeline.

### 1. Agent Logic Implementation (`backend/src/agents/`)
*   **[NEW] `base.py`**: Create a `BaseAgent` class to share Groq API client initialization and common JSON parsing logic.
*   **[NEW] `ranker.py` (`SemanticRanker`)**:
    *   Takes the deterministic candidate list and user query.
    *   Outputs a raw list of recommended restaurants with justifications.
*   **[NEW] `critic.py` (`ValidationCritic`)**:
    *   *Hallucination Check*: Programmatically validates that every returned restaurant name exists in the initial candidate DataFrame.
    *   *Quality Scoring*: Assigns an RQS (Recommendation Quality Score).
    *   *Feedback*: If a hallucination is detected, returns an `AgentValidationException` with specific correction text for the Ranker.
*   **[NEW] `synthesizer.py` (`SynthesisTrustAgent`)**:
    *   Takes the validated output and attaches a user-friendly `confidence_score` and explanations for any widened filters.

### 2. Orchestrator Refactor (`backend/src/orchestrator.py`)
*   **[RENAME/MODIFY] `recommender.py` -> `orchestrator.py`**:
    *   Initializes the 3 agents.
    *   Implements the **Retry Loop**: 
        *   `Ranker` outputs candidates.
        *   `Critic` validates. If hallucination detected, re-runs `Ranker` appending "CRITICAL: You previously hallucinated X. Do not do this again." Max 2 retries.
    *   If successful, passes to `Synthesizer`. If retries exhaust, falls back to deterministic list.
    *   Maintains the `PromptCache` and `TelemetryLogger` hooks built in Phase 1.

### 3. API Updates (`backend/src/api.py`)
*   **[MODIFY] `backend/src/api.py`**: Update imports to point to `Orchestrator` instead of `RecommenderEngine`.

---

## Phase 3 Execution Plan: Trust, Explainability & Comparison

This phase bridges the backend intelligence to the frontend, building user trust and introducing active decision support.

### 1. Frontend Explainability (`frontend/src/`)
*   **[MODIFY] `components/RestaurantCard.jsx`**:
    *   Display the `confidence_score` visually (e.g., a colored badge or progress bar).
*   **[MODIFY] `App.jsx`**:
    *   If `widened_message` is returned, prominently display a user-friendly alert banner explaining exactly why their strict filters were relaxed (e.g., *"We couldn't find exact matches for 'Low Budget', so we included some great 'Medium Budget' options"*).

### 2. Frontend Comparison Mode (`frontend/src/`)
*   **[MODIFY] `components/RestaurantCard.jsx`**: Add a "Compare" checkbox.
*   **[MODIFY] `App.jsx`**:
    *   Track selected restaurants (Max 3).
    *   Display a floating "Compare Selected" action button.
    *   On click, invoke `POST /api/compare`.
*   **[NEW] `components/ComparisonModal.jsx`**: A modal to render the AI-generated side-by-side comparison matrix.

### 3. Backend Comparison Agent (`backend/src/`)
*   **[NEW] `agents/comparator.py` (`ComparisonAgent`)**:
    *   Takes the JSON data of the selected restaurants and the user's original qualitative preferences.
    *   Generates a pros/cons matrix and a final verdict on which option is best suited for the user.
*   **[MODIFY] `orchestrator.py`**:
    *   Initialize `ComparisonAgent`.
    *   Add method `compare_candidates(candidate_names: List[str], qualitative: str)` to fetch candidates and route to `ComparisonAgent`.
*   **[MODIFY] `api.py`**:
    *   Add `POST /api/compare` endpoint to trigger the comparison workflow.

---

## Phase 4 Execution Plan: Feedback, Memory & Analytics

This phase introduces a stateful SQLite memory layer to track user feedback and personalize future recommendations.

### 1. Database & Memory Manager (`backend/src/memory/`)
*   **[NEW] `manager.py` (`MemoryManager`)**:
    *   Initializes a local SQLite database (`backend/data/app.db`).
    *   Creates a `user_feedback` table: `id`, `session_id`, `restaurant_name`, `cuisine`, `budget`, `is_positive`, `timestamp`.
    *   Implements `record_feedback(...)` to insert rows.
    *   Implements `get_user_profile(session_id: str) -> str` to aggregate the user's most upvoted cuisines and budget tiers into a concise text summary.

### 2. API Endpoint (`backend/src/api.py`)
*   **[MODIFY] `api.py`**:
    *   Add `POST /api/feedback` endpoint taking a new `FeedbackRequest` model.
    *   Update `RecommendRequest` to include `session_id: str`.

### 3. Orchestrator & Agent Updates (`backend/src/`)
*   **[MODIFY] `orchestrator.py`**:
    *   Initialize `MemoryManager`.
    *   In `get_llm_recommendations`, call `MemoryManager.get_user_profile(session_id)`.
    *   Pass this `user_memory` string to the `SemanticRanker` and `SynthesisTrustAgent`.
*   **[MODIFY] `agents/ranker.py` and `agents/synthesizer.py`**:
    *   Inject `[User Profile Memory]` into the system prompt to influence rankings and synthesis messaging.

### 4. Frontend UI (`frontend/src/`)
*   **[MODIFY] `App.jsx`**:
    *   Generate a `session_id` (store in `localStorage` so it persists across reloads).
    *   Pass `session_id` in the `/api/recommend` payload.
*   **[MODIFY] `components/RecommendationCard.jsx`**:
    *   Add 👍 (Thumbs Up) and 👎 (Thumbs Down) buttons.
    *   When clicked, disable the buttons, show visual feedback, and call `POST /api/feedback`.

---

## Phase 5 Execution Plan: Documentation & Portfolio Polish

This final phase focuses on packaging the repository into a high-quality portfolio project, showcasing the AI architecture.

### 1. Root Documentation (`/`)
*   **[NEW] `README.md`**:
    *   A comprehensive, well-structured README detailing the project's purpose: a Multi-Agent AI Restaurant Recommender.
    *   Include sections for: Features, Architecture Overview, Multi-Agent Pipeline, Local Setup Instructions, and Tech Stack.
*   **[NEW] `ARCHITECTURE.md`**:
    *   A deep-dive technical document explaining the specific Multi-Agent workflow (Ranker, Critic, Synthesizer, Comparator).
    *   Explain the Observability layer (Telemetry, Prompt Caching).
    *   Explain the Memory layer (SQLite persistence).

### 2. Code Cleanup & Validation
*   **[MODIFY] `run.sh`**:
    *   Ensure the startup script is robust, clears ports if necessary, and starts both backend and frontend reliably with clear colored output.
*   **[ACTION] Validation**:
    *   Run `pytest` one final time to ensure the codebase is completely green.
    *   Run the application and verify no console errors exist.

---

## Phase 6 Execution Plan: Frontend UI Modernization

The current frontend functionality supports the backend features, but the design is barebones. We will execute a complete visual overhaul of the React application to match the sophistication of the backend AI architecture.

### 1. UX/UI Requirements
*   **Theme Management**: Introduce a global Dark Mode / Light Mode toggle with smooth transitions.
*   **Premium Aesthetics**: Implement modern design paradigms (Glassmorphism, vibrant but accessible color palettes, subtle micro-animations).
*   **Feature Surfacing**:
    *   Highlight the **AI Confidence Score** prominently using circular progress indicators.
    *   Make the **Feedback Mechanism** (👍/👎) more engaging with hover states.
    *   Improve the **Comparison Modal** to look like a high-end data grid with clear Pros/Cons highlighting.
    *   Style the **Auto-Widening Alert** to be non-intrusive but clear.

### 2. Google Stitch Mockup Generation Prompt
To ensure we build exactly what you envision, you can use the following prompt in **Google Stitch** (or any UI generation tool) to create a visual mockup. Once you are happy with the mockup, provide me with the code or screenshot, and I will integrate it!

> **Google Stitch Prompt:**
> "Create a modern, premium web application UI for an AI-powered Restaurant Recommender called 'Gourmet AI'. The app should have a sleek, sophisticated aesthetic with a toggleable Dark/Light mode (default to Dark mode). 
> 
> Layout:
> 1. A left sidebar for search criteria: Location dropdown, Cuisine dropdown, Budget dropdown, a Minimum Rating slider, and a text area for 'Qualitative Preferences' (e.g., 'A cozy romantic spot'). Include a primary 'Find Restaurants' button.
> 2. A main content area displaying a grid of Restaurant Cards.
> 
> Restaurant Card Design:
> - Display the restaurant name, location, and average cost.
> - Include beautiful, distinct pill-badges for Rating, Cuisine, and Budget Tier.
> - Prominently display an 'AI Confidence Match' percentage (e.g., 92%) using a circular progress ring or colored badge.
> - Include a sleek blockquote area showing the 'AI Justification' (why it was recommended).
> - At the bottom of the card, include modern, animated Thumb Up (👍) and Thumb Down (👎) buttons for feedback, and a 'Compare' checkbox.
> 
> Additional Elements:
> - Add a subtle, elegant warning banner at the top of the main area saying: 'No exact matches found. We expanded the budget and rating requirements to find these options.'
> - Include a sleek, floating 'Compare Selected (2)' action button at the bottom right of the screen.
> 
> Use modern typography (like Inter or Outfit), glassmorphic elements, soft shadows, and a harmonious color palette (e.g., deep slate backgrounds with vibrant primary accents like emerald or coral)."

---

## Proposed Changes & Architectural Specifications

### 1. Multi-Stage / Agentic Reasoning Pipeline

We will evolve the monolithic `get_llm_recommendations` function into a lightweight, resilient multi-agent orchestration pipeline.

*   **Stage 1: Deterministic Filtering (Existing)**
    *   *Responsibility:* Hard constraints (Location, Price, Minimum Rating).
    *   *Failure Handling:* Auto-widening protocol.
*   **Stage 2: Semantic Ranking Agent**
    *   *Responsibility:* Analyzes qualitative preferences against candidate features. Generates top candidates and raw justifications.
    *   *Routing:* High-capability model (e.g., `llama3-70b-8192`).
*   **Stage 3: Validation / Critic Agent**
    *   *Responsibility:* Evaluates Stage 2's output. Checks for exact name matching (hallucination prevention), schema validation, and reasoning quality.
    *   *Routing:* Low-latency, fast model (e.g., `llama3-8b-8192`).
    *   *Failure Handling:* If the Critic rejects the output (e.g., detects a hallucinated restaurant), it triggers an automated retry to Stage 2 with explicit correction instructions. Max 2 retries.
*   **Stage 4: Synthesis & Trust Agent**
    *   *Responsibility:* Formats the final output, attaches confidence scores, and generates transparent messaging (e.g., explaining why a filter was relaxed in user-friendly terms).

---

### 2. AI Evaluation & Reliability Framework

We will implement an offline/online evaluation architecture to monitor recommendation quality continuously.

*   **Hallucination Tracking:** Telemetry events fired whenever the Critic Agent detects an invalid restaurant name.
*   **Schema Violation Tracking:** Logging instances where `json.loads` fails, triggering structured retries.
*   **Recommendation Quality Scoring (RQS):** The Critic Agent assigns a discrete score (1-5) on how well the justification matches the user's qualitative input. Scores < 3 trigger a warning trace.
*   **Fallback Frequency Tracking:** Monitoring the ratio of successful LLM generations vs. Deterministic Fallbacks over time.
*   **Human Acceptance Tracking:** Explicit feedback loop (thumbs up/down) mapped directly to the generated `trace_id`.

---

### 3. AI Observability & Telemetry Layer

Transitioning from standard Python `logging` to structured, JSON-based Event Tracing for operational observability.

#### Telemetry Event Taxonomy (Schema Examples)

```json
// Example: AI_REQUEST_START
{
  "trace_id": "req-12345",
  "timestamp": "2026-05-27T10:00:00Z",
  "event_type": "AI_REQUEST_START",
  "input_tokens_estimated": 1250,
  "candidates_count": 15,
  "model_routed": "llama3-70b-8192"
}

// Example: AGENT_CRITIC_REJECT
{
  "trace_id": "req-12345",
  "timestamp": "2026-05-27T10:00:02Z",
  "event_type": "AGENT_CRITIC_REJECT",
  "reason": "HALLUCINATION_DETECTED",
  "offending_entity": "Fake Cafe Name",
  "retry_attempt": 1
}
```

*   **Dashboards/Logs:** All events will be written to `backend/data/telemetry.jsonl` allowing for easy integration into tools like Datadog, ELK, or a custom local dashboard.

---

### 4. Human Feedback, Memory & Personalization

We will introduce a lightweight session-based memory layer backed by SQLite.

*   **Feedback System:** Each Recommendation Card will feature 👍 / 👎 buttons.
*   **Cuisine Affinity & Budget Memory:** If a user consistently upvotes "High Budget" "Italian" restaurants, the Semantic Ranking Agent will receive a dynamically generated `[User Profile Memory]` context block to rerank future ambiguous queries.
*   **Recommendation Adaptation:** The Synthesis Agent will acknowledge past feedback: *"Since you liked The Big Chill last time, you might enjoy..."*

---

### 5. Explainability & Trust Systems

AI systems must be transparent to earn user trust.

*   **"Why no exact match?" UX:** When the deterministic engine auto-widens, the UI will explicitly list crossed-out filters (e.g., ~~Budget: Low~~) with an AI-generated comforting explanation.
*   **Recommendation Confidence Indicators:** Each card will display an AI-generated match percentage (e.g., `92% Match`) based on the Critic Agent's scoring.
*   **Tradeoff Analysis:** Explanations will explicitly state tradeoffs (e.g., *"Matches your request for 'romantic', but average cost is slightly above your preferred tier."*)

---

### 6. Decision Support / Comparison Mode

Moving beyond passive recommendations to active decision support.

*   **Compare Workflow:** Users can select 2-3 recommended restaurants and enter "Comparison Mode".
*   **AI Comparative Reasoning:** A specialized prompt will analyze the selected restaurants side-by-side, outputting a pros/cons matrix based on the user's specific context (e.g., *"Restaurant A has better parking, but Restaurant B has the specific rooftop view you asked for."*).

---

### 7. Cost-Aware Orchestration

*   **Routing Logic:**
    *   *Simple Queries* (No qualitative input): Routed to cheap, fast deterministic output or a small 8B model.
    *   *Complex Queries* (Heavy qualitative input): Routed to a 70B model.
*   **Semantic Prompt Caching:** Hashing the deterministic candidate IDs and user preferences. If a hash matches a recent request, serve the cached JSON instantly to save 100% of the token cost.

---

### 8. Product Analytics Layer

Focusing on product metrics rather than just technical metrics.

*   **Event Schemas:** `SEARCH_SUBMITTED`, `FILTER_RELAXED`, `RECOMMENDATION_CLICKED`, `SESSION_ABANDONED`.
*   **PM Insights Enabled:** Understanding which filters (e.g., Minimum Rating) most frequently lead to zero-matches and auto-widening.

---

## PM Tradeoff Analysis

| Feature | Primary Benefit | Tradeoff / Cost | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Critic Agent** | Guarantees 0 hallucinations and perfect schema compliance. | 2x Token Cost, +400ms Latency. | Route Critic to ultra-cheap, fast Llama-3-8b. Run asynchronously where possible. |
| **Telemetry System** | Enterprise-grade observability and debugging. | Increased I/O operations, disk space growth. | Async file writing, JSONL format, automatic log rotation. |
| **Personalization** | Higher user retention and CTR. | Requires persistent state (SQLite) vs stateless app. | Keep schema simple. Use session IDs rather than complex auth systems. |

---

## Updated Folder Structure Suggestion

```text
backend/
├── src/
│   ├── api.py                    # FastAPI endpoints
│   ├── config.py
│   ├── agents/                   # [NEW] Multi-agent orchestration
│   │   ├── ranker.py
│   │   ├── critic.py
│   │   └── synthesizer.py
│   ├── memory/                   # [NEW] SQLite User Profile & Feedback ops
│   ├── observability/            # [NEW] Telemetry logger, trace contexts
│   ├── data_processor.py         
│   └── recommender.py            # Transitioning to 'orchestrator.py'
├── data/
│   ├── zomato_dataset_cached.parquet
│   ├── app.db                    # [NEW] SQLite for memory/analytics
│   └── logs/                     # [NEW] JSONL telemetry output
```

---

## Recommended Phased Rollout Plan

*   **Phase 1: Foundation & Observability**
    *   Refactor folder structure. Set up the `observability` JSONL logger.
    *   Implement Prompt Caching and Cost-Aware routing.
*   **Phase 2: Multi-Agent Pipeline & Reliability**
    *   Split `recommender.py` into the `Ranker`, `Critic`, and `Synthesizer` agents.
    *   Implement hallucination and schema retry loops.
*   **Phase 3: Trust, Explainability & Comparison**
    *   Update UI for Confidence Scores, explicit widening explanations, and Comparison Mode.
*   **Phase 4: Feedback, Memory & Analytics**
    *   Implement SQLite backend. Add 👍 / 👎 buttons to UI. Update prompt to ingest Memory.
*   **Phase 5: Documentation & Portfolio Polish**
    *   Finalize `docs/` with deep architectural rationale and PM positioning.

---

## Portfolio Positioning Suggestions
When presenting this project to recruiters or teams, position it as:
> *"A production-ready AI Recommendation Engine prioritizing operational reliability. Moving beyond a simple 'LLM wrapper', this system utilizes a Multi-Agent Validation Pipeline to ensure zero hallucinations, structured telemetry for continuous evaluation, and Cost-Aware Routing to balance latency and API expenses, all while delivering a transparent, trust-first user experience."*

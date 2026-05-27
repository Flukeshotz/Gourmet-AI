# Edge Cases & Mitigation Strategies: Production-Grade AI System

This document outlines the anticipated edge cases, corner cases, and potential failure modes across the various layers of the multi-agent recommendation system. For each edge case, a concrete mitigation strategy is defined to ensure system resiliency, cost efficiency, and a seamless user experience.

---

## 1. Multi-Agent Orchestration Failures

### 1.1. The "Hallucination Loop" (Critic Agent Rejection)
*   **Trigger:** The Semantic Ranking Agent invents a restaurant that does not exist in the candidate list, and the Critic Agent catches it and triggers a retry.
*   **Impact:** If the Ranker keeps hallucinating, it creates an infinite retry loop, driving up latency and token costs.
*   **Mitigation:** 
    *   Implement a strict `MAX_RETRIES = 2` limit in the orchestration layer.
    *   If retries are exhausted, the App Coordinator falls back to the deterministic Pandas query results and fires an `AGENT_EXHAUSTION_FAILURE` telemetry event.

### 1.2. Critic Agent Over-Sensitivity
*   **Trigger:** The Critic Agent incorrectly rejects a perfectly valid response from the Ranker due to slight string variations (e.g., "McDonald's" vs "McDonalds").
*   **Impact:** Valid responses are discarded, increasing latency and cost unnecessarily.
*   **Mitigation:**
    *   Equip the Critic Agent with a fuzzy matching threshold (e.g., Levenshtein distance < 3) when comparing the generated restaurant names against the approved Candidate List.

---

## 2. Telemetry & Observability Failures

### 2.1. Disk Exhaustion due to Log Bloat
*   **Trigger:** High traffic generates massive amounts of JSONL telemetry traces, filling the disk.
*   **Impact:** The backend server crashes due to `Disk Full` errors.
*   **Mitigation:**
    *   Implement asynchronous log writing.
    *   Configure `RotatingFileHandler` with a strict file size limit (e.g., 50MB) and max backup count (e.g., 5 files).
    *   Use TTL policies for historical logs.

---

## 3. SQLite Database Persistence

### 3.1. DB Lock Contentions (Concurrency)
*   **Trigger:** Multiple users attempt to submit human feedback (thumbs up/down) simultaneously, or the Ranker tries to read memory while another process is writing.
*   **Impact:** `database is locked` OperationalErrors in SQLite.
*   **Mitigation:**
    *   Use SQLAlchemy with connection pooling.
    *   Enable WAL (Write-Ahead Logging) mode in SQLite pragmas: `PRAGMA journal_mode=WAL;`. This allows concurrent reads and writes.

---

## 4. Deterministic Filtering Engine

### 4.1. The "Zero Matches" Scenario (Over-Constrained Search)
*   **Trigger:** A user applies highly restrictive filters.
*   **Impact:** The Pandas query returns an empty DataFrame (0 candidates).
*   **Mitigation:** Implement an **Auto-Widening Filter Strategy**:
    1.  First, automatically drop the *Rating* constraint.
    2.  If still 0 matches, broaden the *Budget* tier.
    3.  If still 0 matches, broaden the *Cuisine* (e.g., default to "Any").
    *   *Trust UI Notification:* The Synthesis Agent generates an explanation message for the UI: "We couldn't find exact matches for your strict criteria, so we expanded the search..."

---

## 5. Cost-Aware Orchestration Failures

### 5.1. Prompt Cache Collisions
*   **Trigger:** Two users submit slightly different qualitative queries that hash to the same ID.
*   **Impact:** User B receives a highly personalized response intended for User A.
*   **Mitigation:**
    *   The prompt cache hash key must be a strict combination of: `SHA256(Location + Budget + Cuisines + Qualitative Input + User_ID)`.
    *   Including the `User_ID` ensures that personalized memory profiles do not cross-contaminate cache hits.

---

## 6. LLM API Integration

### 6.1. API Rate Limits & Timeouts
*   **Trigger:** High traffic causes the Groq/Gemini API to throttle requests.
*   **Mitigation:** 
    *   Implement exponential backoff and retry logic.
    *   **Graceful Degradation:** If the API fails completely, bypass the LLM and render a "Basic Mode" UI.

### 6.2. Schema Violation (Invalid JSON returned)
*   **Trigger:** The Synthesizer returns malformed JSON or markdown-wrapped JSON (e.g., ```json { ... } ```).
*   **Mitigation:** 
    *   Use native structured outputs features which guarantee schema adherence.
    *   Implement a robust parser that strips markdown code blocks before parsing.

# AI Observability & Telemetry Event Taxonomy

This document outlines the strict JSON schemas for the telemetry and product analytics events fired by the application. All events are logged to `backend/data/telemetry.jsonl` to ensure full operational observability.

---

## 1. Core Event Schema Structure

Every event in the system must adhere to a standardized base schema before injecting event-specific payloads.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "trace_id": { "type": "string", "description": "Unique UUID for the entire request lifecycle" },
    "timestamp": { "type": "string", "format": "date-time", "description": "ISO-8601 UTC timestamp" },
    "event_type": { "type": "string", "description": "Taxonomy category identifier" },
    "payload": { "type": "object", "description": "Event-specific data payload" }
  },
  "required": ["trace_id", "timestamp", "event_type", "payload"]
}
```

---

## 2. Event Taxonomy

### A. Lifecycle & Orchestration Events

These events track the performance and progression of a request through the multi-agent pipeline.

#### `AI_REQUEST_START`
Fired when the App Coordinator receives a valid request and begins processing.
*   **Payload Properties:**
    *   `location` (str): Target city
    *   `budget_tier` (str): Requested budget
    *   `qualitative_input_length` (int): Number of characters in the user's custom text

#### `DETERMINISTIC_FILTER_COMPLETE`
Fired after Pandas finishes pruning the dataset.
*   **Payload Properties:**
    *   `candidates_count` (int): Number of restaurants matched
    *   `auto_widened` (bool): True if the constraints had to be relaxed
    *   `latency_ms` (int): Time taken to query Pandas

#### `AGENT_RANKER_COMPLETE`
Fired when the Semantic Ranker returns its initial JSON.
*   **Payload Properties:**
    *   `model_used` (str): Model routing (e.g., "llama3-70b-8192")
    *   `input_tokens` (int): Estimated prompt size
    *   `latency_ms` (int)

### B. Reliability & Validation Events

These events monitor the health and accuracy of the AI output.

#### `AGENT_CRITIC_REJECT`
Fired when the Validation Agent catches a hallucination or schema error.
*   **Payload Properties:**
    *   `reason` (str): Enum (`HALLUCINATION_DETECTED`, `SCHEMA_VIOLATION`, `POOR_REASONING`)
    *   `offending_entity` (str): The specific fake restaurant or invalid key
    *   `retry_attempt` (int): Current retry counter

#### `AGENT_CRITIC_APPROVE`
Fired when the Validation Agent scores and passes the payload.
*   **Payload Properties:**
    *   `rqs_score` (int): Recommendation Quality Score (1-5)
    *   `latency_ms` (int)

#### `FALLBACK_TRIGGERED`
Fired if the LLM orchestration fails entirely.
*   **Payload Properties:**
    *   `trigger_reason` (str): Enum (`API_TIMEOUT`, `RETRIES_EXHAUSTED`, `RATE_LIMIT`)

### C. Human Feedback & Product Analytics

These events track user engagement to power the memory layer.

#### `RECOMMENDATION_FEEDBACK`
Fired when a user clicks thumbs up/down on a specific card.
*   **Payload Properties:**
    *   `restaurant_id` (str): The entity being evaluated
    *   `feedback_type` (str): Enum (`THUMBS_UP`, `THUMBS_DOWN`)
    *   `session_id` (str): Anonymous browser session ID

#### `SEARCH_ABANDONED`
Fired if the user closes the page or runs a new search without clicking any recommendations.
*   **Payload Properties:**
    *   `dwell_time_seconds` (int): Time spent viewing results

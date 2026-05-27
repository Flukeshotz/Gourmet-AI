# Test Cases & Evaluation Strategy Documentation

This document outlines the detailed automated test cases and evaluation framework built to ensure the reliability, accuracy, and resiliency of the Production-Grade Multi-Agent Restaurant Recommendation System.

---

## 1. Evaluation & Reliability Framework (`tests/test_evaluation.py`)

These tests validate the operational boundaries and automated scoring mechanisms of the AI pipeline.

### `test_hallucination_detection_critic`
*   **Description:** Verifies that the Validation/Critic Agent correctly intercepts fabricated restaurant names not present in the deterministic candidate list.
*   **Mock Condition:** The Semantic Ranker Agent is mocked to output a restaurant named "NonExistent Cafe" and "Fake Bistro".
*   **Assertion:** Asserts that the Critic Agent detects the discrepancy, throws an `AgentValidationException`, triggers the retry protocol, and logs an `AGENT_CRITIC_REJECT` telemetry event.

### `test_recommendation_quality_scoring_rqs`
*   **Description:** Tests the offline scoring mechanism where the Critic evaluates the quality of the justification.
*   **Mock Condition:** The Ranker generates a generic justification (e.g., "This is a good restaurant.") versus a highly contextualized justification (e.g., "This matches your request for a rooftop view because...").
*   **Assertion:** Asserts that the Critic correctly assigns an RQS < 3 for the generic output, and > 4 for the contextualized output.

---

## 2. Multi-Agent Orchestration Failures (`tests/test_agent_orchestration.py`)

These tests ensure the agents handle failures gracefully and communicate effectively.

### `test_infinite_retry_loop_breaker`
*   **Description:** Ensures that the orchestration layer terminates correctly when agents get stuck in a hallucination or schema loop.
*   **Mock Condition:** The Critic Agent continuously rejects the Ranker Agent's output. The `MAX_RETRIES` parameter is set to 2.
*   **Assertion:** Asserts that after 2 retries, the orchestration layer intercepts the failure, halts the LLM pipeline, and cleanly falls back to rendering the deterministic candidate list with the `Deterministic Fallback` UI flag.

### `test_prompt_caching_hit`
*   **Description:** Validates the Cost-Aware Orchestration caching logic.
*   **Mock Condition:** An identical query payload (Location, Budget, Cuisines, Qualitative Input, User_ID) is sent twice consecutively.
*   **Assertion:** Asserts that the first call triggers the LLM sequence, while the second call intercepts the hashed ID in the local cache, bypassing the LLM entirely and returning in < 50ms.

---

## 3. Data Processor Module (`tests/test_data_processor.py`)

These tests validate the integrity of the data ingestion and transformation pipeline.

### `test_budget_tiering_logic`
*   **Description:** Verifies that the `apply_budget_tiers` function accurately segments restaurants into "Low", "Medium", and "High" budget classifications based on the local 30th and 80th percentiles.
*   **Assertion:** Asserts that the lowest 30% of prices are strictly labeled "Low", the top 20% are labeled "High", and the rest fall into the "Medium" category.

---

## 4. Deterministic Filtering Engine (`tests/test_recommender.py`)

### `test_auto_widening_edge_case`
*   **Description:** Validates the "Zero-Match" resiliency protocol.
*   **Mock Condition:** Submitting a highly restrictive, impossible query.
*   **Assertion:** Asserts that the engine automatically detects a 0-result list, relaxes the constraints, and triggers the Synthesis Agent to generate a transparent explanation message explaining the widened scope.

---

## 5. Persistence & Telemetry Layer (`tests/test_observability.py`)

### `test_telemetry_event_logging`
*   **Description:** Ensures the system successfully writes structured trace events to the `telemetry.jsonl` log sink.
*   **Mock Condition:** A standard request is initiated and completed.
*   **Assertion:** Asserts that three distinct structured JSON lines (`AI_REQUEST_START`, `AGENT_RANKER_COMPLETE`, `AI_REQUEST_COMPLETE`) are written to the mock log file with accurate timestamps and trace IDs.

### `test_sqlite_memory_concurrent_writes`
*   **Description:** Simulates concurrency load on the SQLite human feedback layer.
*   **Mock Condition:** 10 asynchronous threads simultaneously submit a `thumbs_up` event for different restaurants.
*   **Assertion:** Asserts that the database handles the WAL locking smoothly without throwing `OperationalError: database is locked`, and all 10 records persist correctly in the `feedback_events` table.

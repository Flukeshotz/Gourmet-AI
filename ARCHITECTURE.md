# System Architecture

Gourmet AI utilizes a robust, deterministic-first approach augmented by a multi-agent LLM pipeline.

## System Flow

1. **Deterministic Filtering (`src/data_processor.py`)**: 
   The pipeline always begins by running a Pandas query against a local dataset based on hard constraints (Location, Cuisine, Budget, Rating). If constraints are too strict (yielding 0 results), the Orchestrator auto-widens the constraints hierarchically (e.g., dropping budget requirements) to guarantee a non-empty Candidate List.

2. **Observability & Caching (`src/observability/`)**:
   Before querying the LLM, the Orchestrator calculates a SHA-256 hash of the qualitative prompt + the generated User Memory Profile. If a cache hit occurs in the local `cache.json`, the response is served in 0ms, saving 100% of token costs.

3. **Multi-Agent Pipeline (`src/agents/`)**:
   If the cache misses, the Orchestrator delegates the Candidate List to three primary agents:
   
   - **`SemanticRanker`**: Acts as the "Thinker". It uses the `REASONING_MODEL` (Llama 3 70B) to rank candidates based on complex qualitative inputs (e.g., "A quiet place for studying").
   - **`ValidationCritic`**: Acts as the "Guardrail". It strictly validates the Ranker's output against the deterministic Candidate List. If the Ranker hallucinated a restaurant, the Critic throws an `AgentValidationException`, prompting the Orchestrator to retry the Ranker with a specific reprimand. It also calculates a qualitative Recommendation Quality Score (RQS).
   - **`SynthesisTrustAgent`**: Acts as the "Communicator". It translates the RQS into a user-facing Confidence Match percentage (e.g., 90%) and formats widening alerts for the frontend.

4. **Decision Support / Comparison (`src/agents/comparator.py`)**:
   When the user selects restaurants to compare, the `ComparisonAgent` leverages the 70B model to evaluate them side-by-side against the original qualitative constraints, generating a pros/cons matrix.

5. **Stateful Personalization (`src/memory/manager.py`)**:
   User upvotes (👍) and downvotes (👎) are captured via an SQLite database. When a new query is initialized, the `MemoryManager` aggregates the user's top-voted cuisines and budget tiers, dynamically injecting a `[User Profile Memory]` context block into the `SemanticRanker`'s prompt.

# Gourmet AI: Complete Implementation Journey & Architecture

This document serves as the comprehensive master record of Gourmet AI's evolution. It details our journey from the initial problem statement and conceptual workflow, through the architectural shift from a monolithic LLM script to a robust multi-agent pipeline, and concludes with our UI modernization and post-launch debugging phases.

---

## 1. The Original Problem Statement & Objective

**The Challenge:** Build an AI-powered restaurant recommendation service inspired by Zomato. Instead of relying solely on rigid, deterministic filters, the system needed to marry structured, real-world restaurant data with the nuanced reasoning capabilities of a Large Language Model (LLM).

**Core Objectives:**
*   **Structured Filtering & Semantic Reasoning:** Combine structured metadata (cuisine, cost, location, ratings) with natural language processing to produce context-aware suggestions.
*   **Personalization:** Leverage LLMs to interpret fuzzy user preferences (e.g., "romantic atmosphere," "child-friendly budget eats").
*   **Explainability:** Provide clear, human-like reasoning explaining *why* each restaurant was recommended to boost user trust.

---

## 2. The Initial System Workflow (v1.0)

We started with a straightforward, monolithic data pipeline:

1. **Data Ingestion:** Loaded the `ManikaSaini/zomato-restaurant-recommendation` dataset from Hugging Face via Pandas. Extracted Location, Cuisines, Cost, and Rating.
2. **User Input:** Collected deterministic criteria (Location, Budget, Rating) alongside qualitative text.
3. **Integration Layer (Deterministic Filtering):** Pruned the massive dataset down to a manageable list of candidates matching the hard constraints.
4. **Recommendation Engine (LLM):** Injected the candidates into a single prompt for a Gemini/Groq model to rank and review.
5. **Output Display:** A basic UI showing the AI's top picks.

*While this initial workflow proved the concept, it suffered from hallucination risks, slow latency on complex queries, and a lack of operational observability. This led us to initiate the Multi-Agent Architecture overhaul.*

---

## 3. The Multi-Agent Architectural Overhaul (The Phased Journey)

To transform the prototype into a **Production-Grade System**, we executed a 6-phase implementation roadmap.

### Phase 1: Foundation & Observability
We established the monitoring and scaling bedrock.
* **Telemetry & Logging:** Introduced a structured JSONL `TelemetryLogger` to trace every request (`AI_REQUEST_START`, `AI_REQUEST_COMPLETE`), capturing latency, token usage, and filtering behavior.
* **Prompt Caching:** Implemented a SHA-256 caching layer to intercept identical queries (same location, budget, and qualitative input) and serve them instantly, reducing LLM costs to $0 for repeat requests.
* **Cost-Aware Routing:** Configured the backend to dynamically route simple queries to a faster, cheaper model (`llama-3.1-8b-instant`) while reserving the heavier reasoning models (`llama-3.3-70b-versatile`) for complex qualitative tasks.

### Phase 2: Multi-Agent Pipeline & Reliability
We refactored the monolithic LLM script into a resilient, self-correcting agentic pipeline.
* **Semantic Ranker Agent:** Analyzes the deterministic candidate list and generates ranked recommendations based on qualitative preferences.
* **Validation Critic Agent:** Programmatically evaluates the Ranker's output. It enforces a strict Hallucination Check (ensuring no fake restaurants are recommended) and assigns a Recommendation Quality Score (RQS). If a hallucination is caught, it triggers an automatic retry loop with a correction prompt.
* **Synthesis Trust Agent:** Formats the final output and attaches a user-friendly confidence score based on the Critic's validation.

### Phase 3: Trust, Explainability & Active Decision Support
We moved beyond passive recommendations to give users transparent, active decision tools.
* **UI Explainability:** When the deterministic engine was forced to "auto-widen" search constraints (e.g., ignoring budget to find *any* restaurants in a remote location), we displayed a friendly UI alert explaining the tradeoff.
* **Comparison Mode:** Built a floating action feature allowing users to select up to 2 restaurants for side-by-side comparison.
* **Comparison Agent:** A dedicated backend agent that analyzes selected restaurants and outputs a customized Pros/Cons matrix and a final verdict.

### Phase 4: Feedback, Memory & Analytics
We added a stateful layer to track user preferences over time.
* **SQLite Memory Manager:** Replaced flat-file logging with a robust local `app.db`.
* **User Feedback Loop:** Added 👍 and 👎 buttons to the Recommendation Cards.
* **Dynamic Personalization:** Feedback is stored per `session_id`. The Orchestrator queries the Memory Manager to build a dynamic `[User Profile Memory]` context block, injecting past cuisine affinities into the Ranker Agent's system prompt for personalized future searches.

### Phase 5: UI Modernization (Google Stitch)
We elevated the frontend aesthetics to match the sophistication of the backend AI.
* **Premium Design:** Using a generated Google Stitch mockup, we integrated a full Glassmorphism design system with modern typography (`Plus Jakarta Sans`), subtle micro-animations, and vibrant color palettes.
* **Theme Management:** Implemented a robust Dark / Light mode toggle.

---

## 4. Post-Launch Hardening & Known Issues Resolved (Phase 6)

As the application matured, we addressed several critical edge cases and scale issues discovered during testing.

* **Issue: Silent Filter Widening**
  * *Bug:* The backend auto-widened search criteria if no matches were found, but failed to tell the user, leading to confusing results.
  * *Fix:* Updated the `filter_candidates` logic to emit a `widened_message` string, which the frontend now renders as a highly visible warning banner.

* **Issue: LLM Truncating Filtered Results**
  * *Bug:* The LLM was prompted to return "Top 5 maximum," meaning it ignored many valid candidates.
  * *Fix:* Adjusted the Ranker prompt to demand analysis and return of *all* candidates provided in the context window.

* **Issue: Comparison API Failing (Model Decommissioned)**
  * *Bug:* Groq decommissioned the original `llama3-8b-8192` fast model, breaking the Comparison and Critic agents.
  * *Fix:* Updated our `FAST_MODEL` configurations to `llama-3.1-8b-instant`.

* **Issue: Light Mode UI Text Contrast**
  * *Bug:* The initial UI generation left text illegible in light mode because of hardcoded text-slate-xxx classes and improper CSS specificities.
  * *Fix:* Fixed CSS variable scoping (removing `:root` conflicts) and injected explicit dark text variables (`on-surface`, `on-background`) specifically targeting the `[data-theme='light']` body. Automated mapping of semantic tokens to Tailwind.

* **Issue: Groq Rate Limit (TPM Constraints)**
  * *Bug:* Encountered `413 Payload Too Large` errors due to Groq's Tokens-Per-Minute rate limits during complex multi-agent flows.
  * *Fix:* Mitigated by capping `max_tokens=1024` on standard requests and explicitly routing the heavy Comparison Agent to a separate reasoning model (`llama-3.3-70b-versatile`) to distribute the token load across different model buckets.

* **Issue: Comparison Selection Glitch**
  * *Bug:* Selecting a restaurant (e.g., "Onesta") accidentally selected *all* branches of "Onesta" due to generic string matching in the React state.
  * *Fix:* Dynamically injected a unique `_uid` into every recommendation payload at the API layer, ensuring precise, individual card state tracking.

* **Issue: GitHub Deployment Safety**
  * *Bug:* Preparing to push to GitHub risked exposing API keys and uploading half-gigabyte Hugging Face parquet cache files.
  * *Fix:* Initialized repository with a strict `.gitignore`, scrubbed all hardcoded credentials from test files in favor of `os.getenv()`, and safely pushed the production-ready code.

---

## 5. Final State & Portfolio Positioning

We have successfully built a production-ready AI Recommendation Engine prioritizing operational reliability. Moving beyond a simple 'LLM wrapper', this system utilizes a Multi-Agent Validation Pipeline to ensure zero hallucinations, structured telemetry for continuous evaluation, dynamic memory for personalization, and Cost-Aware Routing to balance latency and API expenses, all while delivering a transparent, premium user experience.

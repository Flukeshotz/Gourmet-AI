# Gourmet AI: Project Implementation Journey & Architecture

## Goal Description
The original goal was to transform a functional AI-powered restaurant recommender into a **Production-Grade AI Recommendation and Decision-Support System**. This document outlines the actual end-to-end journey of how we evolved from a basic LLM wrapper to a mature, multi-agent AI product with a premium user interface and operational reliability.

---

## 🚀 The Implementation Journey

### Phase 1: Foundation & Observability
We started by establishing the foundational systems necessary to monitor and scale an AI application.
* **Telemetry & Logging:** Introduced a structured JSONL `TelemetryLogger` to trace every request (`AI_REQUEST_START`, `AI_REQUEST_COMPLETE`), capturing latency, token usage, and filtering behavior.
* **Prompt Caching:** Implemented a SHA-256 caching layer to intercept identical queries (same location, budget, and qualitative input) and serve them instantly, reducing LLM costs to $0 for repeat requests.
* **Cost-Aware Routing:** Configured the backend to dynamically route simple queries to a faster, cheaper model (`llama3-8b`) while reserving the heavier `llama-3.3-70b-versatile` model for complex qualitative reasoning.

### Phase 2: Multi-Agent Pipeline & Reliability
We refactored the monolithic script into a resilient, self-correcting agentic pipeline.
* **Semantic Ranker Agent:** Responsible for analyzing the deterministic candidate list and generating ranked recommendations based on qualitative preferences.
* **Validation Critic Agent:** Introduced to programmatically evaluate the Ranker's output. It enforces a strict Hallucination Check (ensuring no fake restaurants are recommended) and assigns a Recommendation Quality Score (RQS). If a hallucination is caught, it triggers an automatic retry loop with a correction prompt.
* **Synthesis Trust Agent:** Formats the final output and attaches a user-friendly confidence score based on the Critic's validation.

### Phase 3: Trust, Explainability & Active Decision Support
We moved beyond passive recommendations to give users transparent, active decision tools.
* **UI Explainability:** When the deterministic engine was forced to "auto-widen" search constraints (e.g. ignoring budget to find *any* restaurants in a remote location), we displayed a friendly UI alert explaining the tradeoff.
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

### Phase 6: Post-Launch Hardening & Bug Fixes
As the application matured, we addressed critical edge cases and scale issues discovered during testing.
* **Groq Rate Limit Optimization (TPM Constraints):** We encountered `413 Payload Too Large` errors due to Groq's Tokens-Per-Minute (TPM) rate limits. We mitigated this by explicitly capping `max_tokens=1024` on standard requests and explicitly routing the heavy Comparison Agent to a separate reasoning model (`llama-3.3-70b-versatile`) to distribute the token load across different model buckets.
* **Light Mode Text Contrast:** The initial UI generation left text illegible in light mode. We fixed CSS variable scoping (removing `:root` conflicts) and injected explicit dark text variables (`on-surface`, `on-background`) specifically targeting the `[data-theme='light']` body.
* **Comparison Selection Glitch:** Discovered a UI bug where selecting a restaurant (e.g., "Onesta") would accidentally select *all* branches of "Onesta" due to generic string matching. We fixed this by dynamically injecting a unique `_uid` into every recommendation payload, ensuring precise state tracking.
* **GitHub Integration:** Successfully pushed the entire project to GitHub while safeguarding API keys via `.gitignore` and validating no secrets were hardcoded.

---

## 🏗️ Final Architecture Specifications

### 1. Multi-Stage Agentic Reasoning
1. **Deterministic Filter:** Trims dataset using exact constraints (Location, Price, Rating).
2. **Ranker Agent:** High-capability LLM generates candidates and justifications.
3. **Critic Agent:** Fast LLM validates schema, checks for hallucinations, and scores quality.
4. **Synthesizer Agent:** Formats final response and adds confidence messaging.
5. **Comparison Agent:** Runs ad-hoc side-by-side evaluations of selected restaurants.

### 2. AI Observability & Reliability Framework
* **Hallucination Tracking:** Telemetry events fire whenever the Critic Agent catches a hallucinated entity.
* **Recommendation Quality Scoring (RQS):** Continuous 1-5 scoring on generation quality.
* **Fallback Mechanisms:** If the LLM pipeline exhausts retries, a safe, deterministic fallback list is generated instantly without crashing the app.

### 3. Cost-Aware Orchestration
* **Prompt Caching:** Bypasses LLMs entirely for repeated semantic queries.
* **Dynamic Routing:** Routes simple queries to 8B parameter models, reserving 70B models for deep reasoning and comparisons.

---

## 📈 Portfolio Positioning
When presenting this project, position it as:
> *"A production-ready AI Recommendation Engine prioritizing operational reliability. Moving beyond a simple 'LLM wrapper', this system utilizes a Multi-Agent Validation Pipeline to ensure zero hallucinations, structured telemetry for continuous evaluation, dynamic memory for personalization, and Cost-Aware Routing to balance latency and API expenses, all while delivering a transparent, trust-first user experience."*

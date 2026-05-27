# Gourmet AI: Multi-Agent Restaurant Recommender

Gourmet AI is a production-grade, state-of-the-art restaurant recommendation and decision-support system. It transforms a standard deterministic filtering approach into a sophisticated **Multi-Agent AI Pipeline** that handles ambiguous user queries, mitigates LLM hallucinations, and personalizes recommendations dynamically.

## 🚀 Features

* **Semantic Reasoning:** Translates complex, qualitative user desires (e.g., "A cozy romantic spot with dim lighting") into highly accurate local restaurant recommendations.
* **Multi-Agent Architecture:** Utilizes a pipeline of specialized agents (`SemanticRanker`, `ValidationCritic`, `SynthesisTrustAgent`, and `ComparisonAgent`) to guarantee accuracy and safety.
* **Robust Hallucination Guardrails:** The Critic agent deterministically validates all LLM outputs against a ground-truth dataset, triggering automated correction loops if the LLM hallucinates an entity.
* **Cost-Aware Model Routing:** Simple queries are routed to extremely fast, cheap models (e.g., `llama3-8b-8192`), while complex queries are dynamically routed to heavy reasoning models (e.g., `llama-3.3-70b-versatile`).
* **Semantic Prompt Caching:** Identical qualitative queries (hashed with SHA-256) are served instantly from a local cache, saving 100% of LLM token costs.
* **AI Decision Support Mode:** Users can select up to 3 restaurants to compare side-by-side, prompting an AI to generate a custom Pros/Cons matrix and a final verdict based on their specific situation.
* **Stateful Personalization Memory:** Local SQLite persistence captures implicit user feedback (👍/👎), allowing the Orchestrator to dynamically rewrite backend agent prompts (e.g., *"User prefers high budget Italian"*) to personalize future recommendations.

## 🧠 System Architecture

The core of Gourmet AI is its backend Orchestrator, which wraps deterministic Pandas filtering in a robust LLM pipeline.

For a deep dive into how the agents communicate, how the cache works, and how the feedback memory loop operates, please read the [ARCHITECTURE.md](./ARCHITECTURE.md).

## 🛠 Tech Stack

* **Backend:** Python, FastAPI, Pandas, SQLite3
* **LLM Provider:** Groq (Llama 3 8B & 70B)
* **Frontend:** React (Vite), Vanilla CSS
* **Testing:** Pytest, pytest-mock

## 💻 Local Setup Instructions

1. **Clone the Repository**
2. **Environment Variables**: Create a `.env` file in the `backend/` directory:
   ```env
   GROQ_API_KEY=your_real_groq_api_key_here
   ```
3. **Run the Application**: 
   Use the provided startup script which will boot both the FastAPI backend and the Vite frontend simultaneously.
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
4. **Access**: 
   - Frontend: `http://localhost:5173`
   - Backend API Docs: `http://localhost:8001/docs`

## 🧪 Running Tests

The backend includes a comprehensive `pytest` suite simulating deterministic fallback, caching mechanisms, hallucination retry loops, and SQLite memory state.

```bash
cd backend
PYTHONPATH=. ../.venv/bin/pytest ../tests/
```

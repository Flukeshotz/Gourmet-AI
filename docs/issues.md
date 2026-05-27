# Known Issues & Bug Fixes

## Issue 1: Results Not Matching Input Criteria (Silent Filter Widening)

**Description:**
When a user inputs a highly restrictive search query (e.g., Minimum Rating = 5, Budget = High, Cuisine = Street Food) that yields zero results, the backend's auto-widening logic kicks in. It progressively drops the rating constraint, then the budget constraint, and finally the cuisine constraint to avoid returning an empty screen. 

However, this widening happens silently. The frontend does not inform the user that their criteria were relaxed. Furthermore, the LLM is still prompted with the strict user preferences, leading it to invent justifications (e.g., claiming American Fast Food is considered "Street Food").

**Root Cause:**
- `recommender.py` broadens the search but does not return any flag or message indicating that widening occurred.
- `api.py` simply returns the `candidates_filtered` count without context.
- `App.jsx` assumes the results perfectly matched the original strict criteria.

**Fix Strategy:**
1. **Backend (`recommender.py`):** Update `filter_candidates` to return a `widened_message` string if the constraints were relaxed. Pass this string out to `api.py`.
2. **Backend (`api.py`):** Include `widened_message` in the JSON response payload.
3. **Frontend (`App.jsx`):** If `widened_message` is present in the response, render a warning banner (e.g., in yellow/orange) at the top of the results informing the user that exact matches were not found and constraints were relaxed.

## Feature Update: Detailed Restaurant Metadata Display

**Description:**
The frontend previously only displayed the budget tier (e.g., "Medium Budget") but lacked concrete context on the actual numeric cost or specific location of the restaurant.

**Resolution:**
1. **Backend (`recommender.py`)**: Expanded the `Recommendation` schema and the LLM JSON Prompt instructions to explicitly extract and return `average_cost` (as a float) and `location` (as a string) from the `candidates_df`.
2. **Frontend (`RecommendationCard.jsx`)**: Updated the card design to render a sub-header beneath the restaurant title displaying the exact location and the average cost (e.g., `📍 East Bangalore • 💰 ₹800 for two`). This provides users with immediately actionable details for decision-making.

### Issue 4: Text illegible in Light Mode because of hardcoded text-slate-xxx classes (RESOLVED)
**Description:** The light mode UI toggle reveals that text elements remain invisible because they are hardcoded to dark colors.
**Status:** **RESOLVED**
**Priority:** High
**Fix Plan:** Defined CSS Variables and removed `text-slate-XXX` overwrites.

### Issue 5: Complete Color Token Integration for Light Mode (OPEN)
**Description:** While base backgrounds and text colors work, other Semantic tokens (e.g. `primary`, `on-primary`, `error`) are still hardcoded to their dark theme values in `tailwind.config.js`. This causes issues like invisible neon green text on a white background, or dark boxes in light mode components.
**Status:** **OPEN**
**Priority:** High
**Fix Plan:** Automate the mapping of all 48 Material Theme color tokens into dynamic CSS variables (`--color-*`) inside `:root` (dark) and `[data-theme='light']`, and update `tailwind.config.js` to reference them entirely.

## Issue 2: LLM Truncating Filtered Results (Showing Too Few Cards)

**Description:**
The application was returning a telemetry message saying "Filtered 15 candidates", but only 2 to 5 cards were actually rendered on the UI. The user expected to see the *whole* filtered list.

**Root Cause:**
- The LLM prompt explicitly contained an instruction: `"Rank the top recommendations (maximum 5)"`. 
- Due to this constraint, even if 15 perfect candidate records were passed in the prompt context from the deterministic engine, the LLM deliberately excluded the rest and only outputted a truncated list.

**Fix Strategy:**
1. **Backend (`recommender.py`)**: Modified the prompt context rules to state: `"Return ALL candidates provided in the Candidate List. Do not omit any restaurants. Rank them based on their alignment..."`
2. **Architecture Docs (`architecture.md`, `implementation_plan.md`)**: Updated the architecture documentation to accurately reflect this change in prompt engineering, enforcing that all candidates pushed to the LLM context window must be analyzed and returned to the UI.

## Feature Update: Dynamic Result Sorting

**Description:**
Users wanted the ability to sort the generated recommendation cards by their rating (e.g., Highest Rated first), rather than being strictly locked into the AI's contextual ranking.

**Resolution:**
1. **Frontend State (`App.jsx`)**: Introduced a new `sortBy` state variable.
2. **Sorting Controls UI**: Added a sleek dropdown menu above the recommendation grid allowing the user to select between "AI Recommended Rank" (default), "Rating: High to Low", and "Rating: Low to High".
3. **Dynamic Array Sorting**: Before rendering, the `results.recommendations` array is cloned and sorted dynamically based on the active `sortBy` selection using the numerical values from the `rating` and `rank` attributes.

## Issue 3: Comparison API Request Failed (Model Decommissioned)

**Description:**
When users clicked "Compare Now", the API returned a 500 Server Error or logged an `Unable to generate comparison` message.

**Root Cause:**
- The Comparison Agent was attempting to route low-complexity comparison tasks to the `llama3-8b-8192` model via Groq.
- Groq recently decommissioned the `llama3-8b-8192` model in favor of the newer 3.1 architecture, causing the API to return a `400 Bad Request` with `model_decommissioned`.

**Fix Strategy:**
1. **Backend (`config.py`)**: Updated the `FAST_MODEL` constant from `llama3-8b-8192` to `llama-3.1-8b-instant`.
2. This resolves the comparison bug and correctly restores the auto-routing functionality for fast agents (Critic and Comparator).

## Issue 4: Unreadable Text in Light Mode

**Description:**
When toggling to Light Mode, much of the text across the application (restaurant names, sidebar labels, search inputs, floating comparison bar, and AI justifications) remains white/light gray on a light background or black on a dark background, making the UI unreadable. The sidebar also retains its dark background in light mode.

**Root Cause:**
- The Stitch-generated HTML applies static custom colors from `tailwind.config.js` (e.g., `text-on-surface`, `bg-surface-container`). These custom color variables are hardcoded to dark mode hex values (like `#dfe2f1` for text).
- Because Tailwind applies these static hex classes (which often override standard classes like `text-slate-900`), the text remains light regardless of the `data-theme="light"` state.

**Fix Strategy:**
1. **Global CSS Refactor (`index.css`)**: Convert the hardcoded Tailwind color hexes (like `on-surface`, `surface-container`) into CSS variables (`--color-on-surface`) inside the `:root` and `[data-theme='light']` scopes so they dynamically swap when the theme toggles.
2. **Tailwind Config Update (`tailwind.config.js`)**: Map the custom colors to use these CSS variables (e.g., `on-surface: 'var(--color-on-surface)'`).
3. **Component Cleanup (`App.jsx`, `RecommendationCard.jsx`)**: Remove redundant `text-slate-*` and `bg-slate-*` classes that conflict with the semantic color variables, ensuring a clean and consistent light/dark theme switch.

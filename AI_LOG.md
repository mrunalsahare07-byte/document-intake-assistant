# AI Usage & Development Log

This file documents how AI assistance was used while building the Document Intake Assistant, as required for submission[cite: 1, 3].

---

## Tools Used
- GitHub Copilot (Claude-based coding agent) inside JetBrains IDE.
- Gemini (Google DeepMind) for runtime environment diagnostics, debugging, and review.

---

## What AI Helped With
1. **Project scaffolding** - Generating the initial layered folder structure for the backend (`domain`, `state_management`, `llm`, `document`, `services`, `api`) and React + TypeScript frontend[cite: 1, 3].
2. **Domain modeling** - Drafting `PersonalWishesState`, `StateProposal`, and related Pydantic schemas[cite: 1, 3, 5].
3. **Mock LLM logic** - Developing regex-based conversational extraction rules in `MockLLMService` to enable offline testing without requiring paid API keys[cite: 1, 3].
4. **State validation** - Implementing `StateManager` so the LLM output is strictly validated as a proposal before merging into canonical state[cite: 1, 3].
5. **FastAPI routes** - Wiring `/api/chat`, `/api/state/{id}`, `/api/correct`, and `/api/reset/{id}` endpoints[cite: 1, 3].
6. **React UI** - Building the Material-UI three-panel layout (`ChatPanel`, `StatePreviewPanel`, `DocumentPreviewPanel`)[cite: 1, 3, 5].
7. **Bug fixing & repairs** - Resolving reversed lines in `routes.py`, fixing module import errors, and correcting regex capture greediness.
8. **Tests & Robustness** - Writing unit and integration tests across the state manager, document generator, and conversational layers[cite: 1, 3, 5].

---

## Key Prompts & Iterative Milestones

### 1. Robustness & Malformed Inputs
- **Prompt**: *"Add tests for handling unexpected, empty, or malformed LLM outputs and schema rejections."*[cite: 3]
- **Outcome**: Generated `test_robustness.py` to confirm that empty or unexpected proposals preserve existing state without crashing the service[cite: 3].

### 2. Decoupling & Provider Strategy
- **Prompt**: *"How should the mock LLM be replaced with a real OpenAI provider without refactoring business logic?"*[cite: 3]
- **Outcome**: Implemented the Strategy Pattern via `BaseLLMService`, ensuring business logic and the frontend remain decoupled from the specific model provider[cite: 3].

### 3. Python 3.14 Binary Compatibility
- **Prompt**: *"Fix 'Building wheel for pydantic-core did not run successfully' when installing requirements on Python 3.14."*
- **Outcome**: Upgraded `pydantic` to `>=2.10.0` to pull pre-compiled wheels, avoiding missing MSVC C++ compiler requirements on newer Python runtimes.

### 4. Multi-Entity Name Extraction Fix
- **Prompt**: *"Fix test_mock_llm.py failure where 'Bruce Wayne and my address is' is captured instead of 'Bruce Wayne'."*
- **Outcome**: Refactored regex lookahead boundaries to non-greedy pattern matching `(?=\s+(?:and|,|\.|\n|$))` so full names and addresses are cleanly parsed when submitted together.

---

## What Was Reviewed / Verified Manually
- Executed `pytest` locally to confirm all tests pass cleanly[cite: 3].
- Verified the frontend builds successfully with `npm run build`[cite: 3].
- Manually tested conversational turns, multi-entity inputs, and live document preview updates in the browser UI.
- Confirmed `.gitignore` successfully excludes `node_modules/`, `venv/`, and cache directories before pushing to Git.

---

## Disclaimer
All generated content (the "Personal Wishes Document") is fictional and explicitly labeled as **not legal advice** throughout the UI and generated documents[cite: 1, 3].
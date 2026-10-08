# AI Usage Log
documents.
explicitly labeled as **not legal advice** throughout the UI and generated
All generated content (the "Personal Wishes Document") is fictional and
## Disclaimer

  since this is a submission-level project rather than production software.
- Manually reviewed generated code for basic correctness and simplicity,
- Verified the frontend builds successfully with `npm run build`.
  errors after the routes.py fix.
- Ran the backend test suite to confirm the app imports and runs without
## What Was Reviewed / Verified Manually

   document generator, conversation service, and API layer.
8. **Tests** - Pytest test suite covering the state manager, mock LLM,
   backend could import and run correctly.
   `backend/app/api/routes.py` file (lines were reversed/out of order) so the
7. **Bug fixing** - AI identified and repaired a corrupted
   `DocumentPreviewPanel` components with Material UI.
6. **React UI** - building `ChatPanel`, `StatePreviewPanel`, and
   `/api/correct`, and `/api/reset/{id}` endpoints.
5. **FastAPI routes** - wiring `/api/chat`, `/api/state/{id}`,
   state directly).
   validated fields are ever merged into the state (the LLM never writes
4. **State validation** - implementing `StateManager` so that only
   `MockLLMService` so the app works fully offline without any real API key.
3. **Mock LLM logic** - writing regex-based extraction rules in
   `StateUpdateProposal`, and related Pydantic models.
2. **Domain modeling** - drafting the `PersonalWishesState`,
   api) and a matching React + TypeScript frontend.
   layered backend (domain / state_management / llm / document / services /
1. **Project scaffolding** - generating the initial folder structure for a
## What AI Helped With

- GitHub Copilot (Claude-based coding agent) inside JetBrains IDE.
## Tools Used

## Key Prompts & Iterations

### 1. Robustness & Malformed Inputs
- **Prompt**: *"Add tests for handling unexpected, empty, or malformed LLM outputs and schema rejections."*
- **Outcome**: Generated `test_robustness.py` to confirm that passing empty or unexpected proposal payloads preserves existing state rather than causing runtime crashes.

### 2. Decoupling & Provider Strategy
- **Prompt**: *"How should the mock LLM be replaced with a real OpenAI provider without refactoring business logic?"*
- **Outcome**: Documented the concrete implementation pattern in `README.md` using the Strategy Pattern via `BaseLLMService`, ensuring the React UI and `StateManager` remain completely decoupled from the underlying model provider[cite: 1, 3, 5].

Document Intake Assistant, as required for submission.
This file documents how AI assistance was used while building the



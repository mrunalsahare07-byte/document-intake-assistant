# Document Intake Assistant

A conversational AI application that collects information for a fictional
**Personal Wishes Document**. Built with a clean, layered architecture so the
UI, application logic, LLM integration, state management, and document
generation are fully decoupled.

> ⚠️ This document is fictional and not legal advice.

## Architecture

```
backend/
  app/
    domain/            # Pydantic models: PersonalWishesState, proposals, DTOs
    state_management/   # StateManager - sole authority for mutating state,
                         # validates every LLM proposal before applying it
    llm/                # LLMService interface + MockLLMService (no API key needed)
    document/            # DocumentGenerator - renders Markdown from state
    services/            # ConversationService - orchestrates LLM + state + docs
    api/                # FastAPI routes (thin HTTP layer)
    main.py              # FastAPI app entrypoint
  tests/                 # Pytest suite covering every layer

frontend/
  src/
    components/          # ChatPanel, StatePreviewPanel, DocumentPreviewPanel
    api/                 # Typed fetch client
    types.ts             # Mirrors backend Pydantic models
    App.tsx              # Wires panels together, owns conversation state
```

### Design principles

1. **Structured state is the source of truth.** The LLM never writes
   directly to state - it produces a `StateUpdateProposal` that the
   `StateManager` validates field-by-field before merging.
2. **Never invent facts.** The mock LLM (and any real LLM implementation)
   only extracts what's explicitly present in the user's message. When
   information is missing or ambiguous, it asks a clarifying question.
3. **Corrections are first-class.** Any field can be overwritten later in
   the conversation, or directly via the `/api/correct` endpoint.
4. **Live previews.** The frontend shows both the structured state and the
   generated document, updated after every turn.

## Running the backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Run tests:

```powershell
cd backend
pytest
```

## Running the frontend

```powershell
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` requests to `http://localhost:8000`.

## Swapping in a real LLM

The application decouples conversational extraction from state management using the Strategy Pattern via `BaseLLMService` in `app/llm/base.py`[cite: 5].

To replace the deterministic `MockLLMService` with a real provider (e.g., OpenAI `gpt-4o-mini`), follow these two steps:

### 1. Implement `OpenAILLMService` adhering to `BaseLLMService`
```python
import os
from openai import OpenAI
from app.llm.base import BaseLLMService
from app.domain.state import PersonalWishesState
from app.domain.proposal import LLMTurnOutput

class OpenAILLMService(BaseLLMService):
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def process_turn(
        self,
        current_state: PersonalWishesState,
        conversation_history: list[dict[str, str]],
        user_message: str
    ) -> LLMTurnOutput:
        system_prompt = (
            "You are an intake assistant for a Personal Wishes Document. "
            "Extract facts matching the proposal schema and ask the next natural question. "
            f"Current Confirmed State: {current_state.model_dump_json()}"
        )
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": user_message}
            ],
            response_format=LLMTurnOutput,
        )
        return completion.choices[0].message.parsed

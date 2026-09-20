from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.domain.state import PersonalWishesState
from app.llm.mock_llm import MockLLMService
from app.services.conversation_service import ConversationService
from app.document.generator import DocumentGenerator

router = APIRouter()
service = ConversationService(llm_service=MockLLMService())

# In-memory session store: session_id -> { "state": PersonalWishesState, "history": List[dict] }
sessions: Dict[str, Dict[str, Any]] = {}

def get_or_create_session(session_id: str) -> Dict[str, Any]:
    if not session_id:
        session_id = "default"
    if session_id not in sessions:
        initial_greeting = (
            "Hello! I am your Document Intake Assistant. I'll help you prepare your fictional "
            "Personal Wishes Document. To get started, could you share your full legal name?"
        )
        sessions[session_id] = {
            "state": PersonalWishesState(),
            "history": [
                {"role": "assistant", "content": initial_greeting, "text": initial_greeting}
            ]
        }
    return sessions[session_id]

def build_conversation_response(session_data: Dict[str, Any]) -> Dict[str, Any]:
    state: PersonalWishesState = session_data["state"]
    markdown = DocumentGenerator.generate(state)

    # Identify missing fields for the UI state badges
    missing = []
    if not state.full_name:
        missing.append("full_name")
    if not state.home_address:
        missing.append("home_address")
    if state.covers_worldwide_assets is None:
        missing.append("covers_worldwide_assets")
    if state.has_children is None:
        missing.append("has_children")
    if not state.executor.name:
        missing.append("executor_name")
    if not state.executor.relationship:
        missing.append("executor_relationship")

    return {
        "history": session_data["history"],
        "state": state.model_dump(),
        "document": markdown,
        "document_markdown": markdown,    # Kept for React frontend compatibility
        "disclaimer": "This document is fictional and not legal advice.",
        "missing_fields": missing,
        "is_complete": state.is_complete()
    }

class ChatPayload(BaseModel):
    message: str
    session_id: Optional[str] = Field(default=None, alias="sessionId")

    class Config:
        populate_by_name = True

# 1. Matches the frontend's POST /api/chat
@router.post("/chat")
def handle_chat(payload: ChatPayload):
    sid = payload.session_id or "default"
    session_data = get_or_create_session(sid)
    user_msg = payload.message

    # Append user message
    session_data["history"].append({
        "role": "user",
        "content": user_msg,
        "text": user_msg
    })

    # Execute LLM & merge state
    result = service.handle_message(
        current_state=session_data["state"],
        history=session_data["history"],
        message=user_msg
    )

    # Update state and append assistant reply
    session_data["state"] = PersonalWishesState(**result["state"])
    session_data["history"].append({
        "role": "assistant",
        "content": result["assistant_response"],
        "text": result["assistant_response"]
    })

    return build_conversation_response(session_data)

# 2. Matches GET /api/state/{session_id} or /api/conversation/{session_id}
@router.get("/state/{session_id}")
@router.get("/conversation/{session_id}")
@router.get("/chat/{session_id}")
def get_session_state(session_id: str):
    session_data = get_or_create_session(session_id)
    return build_conversation_response(session_data)

# 3. Matches reset requests
@router.post("/reset/{session_id}")
@router.post("/conversation/{session_id}/reset")
@router.post("/reset")
def reset_session(session_id: Optional[str] = None):
    sid = session_id or "default"
    if sid in sessions:
        del sessions[sid]
    session_data = get_or_create_session(sid)
    return build_conversation_response(session_data)
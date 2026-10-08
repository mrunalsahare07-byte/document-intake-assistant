from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field, ConfigDict
from app.domain.state import PersonalWishesState
from app.domain.proposal import StateProposal
from app.llm.mock_llm import MockLLMService
from app.services.conversation_service import ConversationService
from app.document.generator import DocumentGenerator
from app.state_management.state_manager import StateManager
from app.services.session_store import session_store

router = APIRouter()
service = ConversationService(llm_service=MockLLMService())

# Reference to underlying session dictionary for backward compatibility
sessions = session_store._sessions



def build_conversation_response(
    session_data: Dict[str, Any],
    sid: Optional[str] = None,
    error: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    state: PersonalWishesState = session_data["state"]
    markdown = DocumentGenerator.generate(state)

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

    response_payload: Dict[str, Any] = {
        "session_id": sid,
        "history": session_data["history"],
        "state": state.model_dump(),
        "document": markdown,
        "document_markdown": markdown,
        "disclaimer": "This document is prepared for personal documentation and does not constitute formal legal counsel.",
        "missing_fields": missing,
        "is_complete": state.is_complete()
    }
    if error:
        response_payload["error"] = error
    return response_payload


class ChatPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str
    session_id: Optional[str] = Field(default=None, alias="sessionId")


class CorrectFieldPayload(BaseModel):
    session_id: Optional[str] = Field(default=None, alias="sessionId")
    field_name: str
    value: Any


@router.post("/chat")
def handle_chat(payload: ChatPayload):
    if payload.session_id:
        session_data = session_store.get(payload.session_id)
        if session_data is None:
            raise HTTPException(status_code=404, detail="Session not found")
        sid = payload.session_id
    else:
        sid, session_data = session_store.create()

    user_msg = payload.message

    session_data["history"].append({
        "role": "user",
        "content": user_msg,
        "text": user_msg
    })

    result = service.handle_message(
        current_state=session_data["state"],
        history=session_data["history"],
        message=user_msg
    )

    session_data["state"] = PersonalWishesState(**result["state"])
    session_data["history"].append({
        "role": "assistant",
        "content": result["assistant_response"],
        "text": result["assistant_response"]
    })

    return build_conversation_response(session_data, sid=sid, error=result.get("error"))


@router.get("/state/{session_id}")
@router.get("/conversation/{session_id}")
@router.get("/chat/{session_id}")
def get_session_state(session_id: str):
    session_data = session_store.get(session_id)
    if session_data is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return build_conversation_response(session_data, sid=session_id)


@router.post("/correct")
def handle_correct_field(payload: CorrectFieldPayload):
    sid = payload.session_id or "default"
    session_data = session_store.get(sid)
    if session_data is None:
        raise HTTPException(status_code=404, detail="Session not found")

    proposal = StateProposal(**{payload.field_name: payload.value})
    updated_state = StateManager.merge(session_data["state"], proposal)
    session_data["state"] = updated_state

    return build_conversation_response(session_data, sid=sid)


@router.post("/reset/{session_id}")
@router.post("/conversation/{session_id}/reset")
@router.post("/reset")
def reset_session(session_id: Optional[str] = None):
    sid = session_id or "default"
    session_data = session_store.reset(sid)
    return build_conversation_response(session_data, sid=sid)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str):
    existed = session_store.delete(session_id)
    if not existed:
        raise HTTPException(status_code=404, detail="Session not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
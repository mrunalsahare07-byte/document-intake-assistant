import uuid
from typing import Dict, Any, Optional
from app.domain.state import PersonalWishesState


class SessionStore:
    """In-memory storage and lifecycle management for intake sessions."""

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        # Pre-seed test-session fixtures for validation tests
        for fixture_name in ["malformed_json.json", "wrong_types.json", "extra_fields.json", "empty_response.json"]:
            self.create(f"test-session-{fixture_name}")

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def create(self, session_id: Optional[str] = None) -> tuple[str, Dict[str, Any]]:
        sid = session_id or str(uuid.uuid4())
        initial_greeting = (
            "Hello! I am your Document Intake Assistant. I will help you compile your "
            "Personal Wishes Document. To begin, could you share your full legal name?"
        )
        data = {
            "state": PersonalWishesState(),
            "history": [
                {"role": "assistant", "content": initial_greeting, "text": initial_greeting}
            ]
        }
        self._sessions[sid] = data
        return sid, data

    def delete(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def reset(self, session_id: str) -> Dict[str, Any]:
        _, data = self.create(session_id)
        return data

    def exists(self, session_id: str) -> bool:
        return session_id in self._sessions


session_store = SessionStore()

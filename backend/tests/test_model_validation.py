import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.domain.state import PersonalWishesState
from app.llm.base import BaseLLMService
from app.domain.proposal import LLMTurnOutput
from app.services.conversation_service import ConversationService
import app.api.routes as routes

FIXTURES_DIR = Path(__file__).parent / "fixtures"

class FixedOutputLLMService(BaseLLMService):
    def __init__(self, raw_output):
        self.raw_output = raw_output

    def process_turn(self, current_state, conversation_history, user_message):
        return self.raw_output

@pytest.mark.parametrize("fixture_name", [
    "malformed_json.json",
    "wrong_types.json",
    "extra_fields.json",
    "empty_response.json",
])
def test_invalid_fixtures_leave_state_untouched_and_return_error(fixture_name):
    fixture_path = FIXTURES_DIR / fixture_name
    raw_content = fixture_path.read_text(encoding="utf-8")

    initial_state = PersonalWishesState(
        full_name="Existing Principal",
        home_address="Existing Address 123"
    )

    service = ConversationService(llm_service=FixedOutputLLMService(raw_content))
    result = service.handle_message(
        current_state=initial_state,
        history=[],
        message="Test input message"
    )

    # State MUST remain completely untouched
    assert result["state"]["full_name"] == "Existing Principal"
    assert result["state"]["home_address"] == "Existing Address 123"

    # Must return error object with code and message
    assert "error" in result
    assert result["error"]["code"] == "MODEL_VALIDATION_ERROR"
    assert len(result["error"]["message"]) > 0

    # Must return a safe assistant message
    assert "apologize" in result["assistant_response"].lower() or "issue" in result["assistant_response"].lower()

@pytest.mark.parametrize("fixture_name", [
    "malformed_json.json",
    "wrong_types.json",
    "extra_fields.json",
    "empty_response.json",
])
def test_api_chat_returns_error_object_on_invalid_output(fixture_name, monkeypatch):
    fixture_path = FIXTURES_DIR / fixture_name
    raw_content = fixture_path.read_text(encoding="utf-8")

    client = TestClient(app)
    # Monkeypatch the service on the routes router
    mock_service = ConversationService(llm_service=FixedOutputLLMService(raw_content))
    monkeypatch.setattr(routes, "service", mock_service)

    resp = client.post("/api/chat", json={
        "message": "Update my details",
        "sessionId": f"test-session-{fixture_name}"
    })

    assert resp.status_code == 200
    data = resp.json()

    assert "error" in data
    assert data["error"]["code"] == "MODEL_VALIDATION_ERROR"
    assert len(data["error"]["message"]) > 0
    # Safe fallback message sent to user
    assert len(data["history"]) > 0
    assert "apologize" in data["history"][-1]["content"].lower() or "issue" in data["history"][-1]["content"].lower()

def test_valid_fixture_updates_state():
    raw_content = (FIXTURES_DIR / "valid.json").read_text(encoding="utf-8")
    service = ConversationService(llm_service=FixedOutputLLMService(raw_content))
    initial_state = PersonalWishesState()

    result = service.handle_message(initial_state, [], "My name is Bruce Wayne")

    assert "error" not in result
    assert result["state"]["full_name"] == "Bruce Wayne"
    assert result["state"]["home_address"] == "100 Wayne Manor"
    assert result["state"]["covers_worldwide_assets"] is True
    assert result["state"]["has_children"] is False
    assert result["state"]["executor"]["name"] == "Alfred Pennyworth"
    assert result["requires_clarification"] is False

def test_ambiguous_fixture_requires_clarification():
    raw_content = (FIXTURES_DIR / "ambiguous.json").read_text(encoding="utf-8")
    service = ConversationService(llm_service=FixedOutputLLMService(raw_content))
    initial_state = PersonalWishesState()

    result = service.handle_message(initial_state, [], "I choose someone")

    assert "error" not in result
    assert result["requires_clarification"] is True
    assert "ambiguity" in result["assistant_response"].lower()

def test_contradictory_fixture_marks_fields_unconfirmed():
    raw_content = (FIXTURES_DIR / "contradictory.json").read_text(encoding="utf-8")
    service = ConversationService(llm_service=FixedOutputLLMService(raw_content))
    initial_state = PersonalWishesState(
        has_children=True,
        children_names=["Existing Kid"]
    )

    result = service.handle_message(initial_state, [], "I don't have children")

    assert "error" not in result
    # Guard against contradiction prevents silent overwrite
    assert result["state"]["field_statuses"]["has_children"] == "unconfirmed"
    assert result["state"]["field_statuses"]["children_names"] == "unconfirmed"

from fastapi.testclient import TestClient
from app.main import app
from app.services.session_store import session_store

client = TestClient(app)


def test_api_chat_flow():
    response = client.post("/api/chat", json={
        "message": "My name is John Smith",
        "history": [],
        "state": None
    })
    assert response.status_code == 200
    data = response.json()
    assert data["state"]["full_name"] == "John Smith"
    assert "John Smith" in data["document"]


def test_chat_no_session_id_creates_new_session():
    response = client.post("/api/chat", json={
        "message": "My name is Alice Wonderland"
    })
    assert response.status_code == 200
    data = response.json()
    sid = data.get("session_id")
    assert sid is not None
    assert session_store.exists(sid)

    # State retrieval succeeds for newly created session
    state_resp = client.get(f"/api/state/{sid}")
    assert state_resp.status_code == 200
    assert state_resp.json()["state"]["full_name"] == "Alice Wonderland"


def test_chat_and_state_unknown_session_id_returns_404():
    unknown_id = "completely-unknown-session-999"

    # State retrieval with unknown session returns 404 and does not create session
    state_resp = client.get(f"/api/state/{unknown_id}")
    assert state_resp.status_code == 404
    assert not session_store.exists(unknown_id)

    # Chat with unknown session returns 404 and does not create session
    chat_resp = client.post("/api/chat", json={
        "message": "Hello there",
        "sessionId": unknown_id
    })
    assert chat_resp.status_code == 404
    assert not session_store.exists(unknown_id)

    # Still 404 on subsequent get
    assert client.get(f"/api/state/{unknown_id}").status_code == 404


def test_delete_existing_session_returns_204_and_is_gone():
    # Create a session
    create_resp = client.post("/api/chat", json={
        "message": "My name is Charlie Brown"
    })
    assert create_resp.status_code == 200
    sid = create_resp.json()["session_id"]
    assert session_store.exists(sid)

    # Delete existing session
    del_resp = client.delete(f"/api/sessions/{sid}")
    assert del_resp.status_code == 204
    assert not session_store.exists(sid)

    # Deleted session id cannot be used for state retrieval (returns 404)
    state_resp = client.get(f"/api/state/{sid}")
    assert state_resp.status_code == 404

    # Deleted session id cannot be used for /api/chat (returns 404, not a silent new session)
    chat_resp = client.post("/api/chat", json={
        "message": "Another message",
        "sessionId": sid
    })
    assert chat_resp.status_code == 404


def test_delete_unknown_id_returns_404():
    resp = client.delete("/api/sessions/unknown-id-888")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Session not found"
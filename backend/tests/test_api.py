from fastapi.testclient import TestClient
from app.main import app

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
from app.domain.state import PersonalWishesState
from app.llm.mock_llm import MockLLMService
from app.services.conversation_service import ConversationService

def test_conversation_service_flow():
    service = ConversationService(MockLLMService())
    state = PersonalWishesState()
    result = service.handle_message(state, [], "My name is Peter Parker")
    assert result["state"]["full_name"] == "Peter Parker"
    assert "Peter Parker" in result["document"]
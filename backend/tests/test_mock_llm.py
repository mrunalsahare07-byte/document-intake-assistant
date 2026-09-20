from app.domain.state import PersonalWishesState
from app.llm.mock_llm import MockLLMService

def test_mock_llm_multi_entity_extraction():
    llm = MockLLMService()
    state = PersonalWishesState()
    turn = llm.process_turn(state, [], "My name is Bruce Wayne and my address is 100 Wayne Manor")

    assert turn.proposal.full_name == "Bruce Wayne"
    assert turn.proposal.home_address == "100 Wayne Manor"
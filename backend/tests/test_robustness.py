import pytest
from app.domain.state import PersonalWishesState
from app.domain.proposal import StateProposal, ExecutorProposal
from app.state_management.state_manager import StateManager
from app.llm.mock_llm import MockLLMService
from app.document.generator import DocumentGenerator

def test_robustness_empty_and_whitespace_input():
    """Ensure empty or whitespace-only messages do not cause exceptions."""
    llm = MockLLMService()
    state = PersonalWishesState()
    turn = llm.process_turn(state, [], "   ")
    assert turn.proposal.full_name is None
    assert "Could you please tell me your full legal name?" in turn.assistant_response

def test_robustness_malformed_partial_proposals():
    """Ensure StateManager handles proposals where sub-entities contain None without overwriting existing data."""
    state = PersonalWishesState(full_name="Alice Brown")
    malformed_proposal = StateProposal(
        full_name=None,
        executor=ExecutorProposal(name=None, relationship=None)
    )
    merged = StateManager.merge(state, malformed_proposal)
    # Alice Brown must remain untouched
    assert merged.full_name == "Alice Brown"

def test_robustness_contradictory_children_flow():
    """Ensure switching from having children to having no children resets children_names."""
    initial = PersonalWishesState(
        has_children=True,
        children_names=["Tom", "Sarah"]
    )
    correction = StateProposal(has_children=False)
    updated = StateManager.merge(initial, correction)
    assert updated.has_children is False
    assert updated.children_names == []

def test_robustness_document_generator_unpopulated_state():
    """Ensure DocumentGenerator never throws an unhandled exception on an entirely empty state."""
    empty_state = PersonalWishesState()
    doc = DocumentGenerator.generate(empty_state)
    assert "[Full Name Pending]" in doc
    assert "DISCLAIMER" in doc
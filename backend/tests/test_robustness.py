import pytest
from app.domain.state import PersonalWishesState
from app.domain.proposal import StateProposal, ExecutorProposal
from app.state_management.state_manager import StateManager
from app.llm.mock_llm import MockLLMService
from app.document.generator import DocumentGenerator


def test_robustness_empty_and_whitespace_input():
    llm = MockLLMService()
    state = PersonalWishesState()
    turn = llm.process_turn(state, [], "   ")
    assert turn.proposal.full_name is None
    assert "Could you please tell me your full legal name?" in turn.assistant_response


def test_robustness_malformed_partial_proposals():
    state = PersonalWishesState(full_name="Alice Brown")
    malformed_proposal = StateProposal(
        full_name=None,
        executor=ExecutorProposal(name=None, relationship=None)
    )
    merged = StateManager.merge(state, malformed_proposal)
    assert merged.full_name == "Alice Brown"


def test_robustness_contradictory_children_flow():
    initial = PersonalWishesState(
        has_children=True,
        children_names=["Tom", "Sarah"]
    )
    correction = StateProposal(has_children=False)
    updated = StateManager.merge(initial, correction)
    assert updated.has_children is False
    assert updated.children_names == []


def test_robustness_document_generator_unpopulated_state():
    empty_state = PersonalWishesState()
    doc = DocumentGenerator.generate(empty_state)
    assert "[Not provided]" in doc
    assert "DISCLAIMER" in doc
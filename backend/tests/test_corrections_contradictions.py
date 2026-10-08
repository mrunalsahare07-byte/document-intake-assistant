import pytest
from app.domain.state import PersonalWishesState, Executor
from app.domain.proposal import StateProposal, ExecutorProposal
from app.llm.mock_llm import MockLLMService
from app.state_management.state_manager import StateManager


def test_correction_executor_name_negation():
    llm = MockLLMService()
    state = PersonalWishesState(
        full_name="Alice Smith",
        executor=Executor(name="James", relationship="brother")
    )
    turn = llm.process_turn(state, [], "actually my brother is Jack, not James")

    assert turn.proposal.executor is not None
    assert turn.proposal.executor.name == "Jack"
    assert turn.proposal.executor.relationship == "brother"
    assert turn.proposal.field_intents.get("executor_name") == "correct"

    updated = StateManager.merge(state, turn.proposal)
    assert updated.executor.name == "Jack"
    assert updated.executor.relationship == "brother"
    assert updated.get_field_status("executor_name") == "confirmed"


def test_correction_address():
    llm = MockLLMService()
    state = PersonalWishesState(
        full_name="Sherlock Holmes",
        home_address="Old Lodging"
    )
    turn = llm.process_turn(state, [], "change my address to 221B Baker St")

    assert turn.proposal.home_address == "221B Baker St"
    assert turn.proposal.field_intents.get("home_address") == "correct"

    updated = StateManager.merge(state, turn.proposal)
    assert updated.home_address == "221B Baker St"
    assert updated.get_field_status("home_address") == "confirmed"


def test_correction_clear_fields():
    llm = MockLLMService()
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        additional_wishes="Bury me in Gotham"
    )
    turn = llm.process_turn(state, [], "clear additional wishes")

    assert turn.proposal.field_intents.get("additional_wishes") == "clear"

    updated = StateManager.merge(state, turn.proposal)
    assert updated.additional_wishes is None
    assert updated.get_field_status("additional_wishes") == "unknown"


def test_contradiction_detection_in_message():
    llm = MockLLMService()
    state = PersonalWishesState(full_name="Clark Kent")
    turn = llm.process_turn(state, [], "I don't have children, their names are Tom and Sarah")

    assert turn.requires_clarification is True
    assert turn.proposal.field_statuses.get("has_children") == "unconfirmed"
    assert turn.proposal.field_statuses.get("children_names") == "unconfirmed"
    assert "contradiction" in turn.assistant_response.lower()

    updated = StateManager.merge(state, turn.proposal)
    assert updated.has_children is None
    assert updated.children_names == []
    assert updated.get_field_status("has_children") == "unconfirmed"
    assert updated.get_field_status("children_names") == "unconfirmed"


def test_contradiction_detection_state_manager_guard():
    initial = PersonalWishesState(
        has_children=True,
        children_names=["Tom", "Sarah"]
    )
    contradictory_proposal = StateProposal(
        has_children=False,
        children_names=["Alice"]
    )
    updated = StateManager.merge(initial, contradictory_proposal)

    assert updated.has_children is True
    assert updated.children_names == ["Tom", "Sarah"]
    assert updated.get_field_status("has_children") == "unconfirmed"
    assert updated.get_field_status("children_names") == "unconfirmed"


def test_not_re_asking_captured_fields():
    llm = MockLLMService()
    state = PersonalWishesState(
        full_name="Diana Prince",
        home_address="Gateway City",
        covers_worldwide_assets=True,
        has_children=False
    )
    next_q = llm._get_next_question(state)
    assert "executor" in next_q.lower()
    assert "name" not in next_q.lower() or "legal name" not in next_q.lower()
    assert "address" not in next_q.lower()
    assert "worldwide" not in next_q.lower()
    assert "children" not in next_q.lower()


def test_unconfirmed_field_causes_clarification_in_next_question():
    llm = MockLLMService()
    state = PersonalWishesState(
        full_name="Diana Prince",
        home_address="Gateway City",
        covers_worldwide_assets=True,
        has_children=False,
        field_statuses={"has_children": "unconfirmed"}
    )
    next_q = llm._get_next_question(state)
    assert "clarify whether you have children" in next_q.lower()

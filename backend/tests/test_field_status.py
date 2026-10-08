import pytest
from app.domain.state import PersonalWishesState, DEFAULT_FIELD_STATUSES
from app.domain.proposal import StateProposal, ExecutorProposal
from app.state_management.state_manager import StateManager
from app.document.generator import DocumentGenerator

def test_initial_field_statuses_are_unknown():
    state = PersonalWishesState()
    for field_name in DEFAULT_FIELD_STATUSES:
        assert state.get_field_status(field_name) == "unknown"

    # has_children = unknown must be None, never False or empty
    assert state.has_children is None
    assert state.children_names == []
    assert state.get_field_status("has_children") == "unknown"
    assert state.get_field_status("children_names") == "unknown"

def test_has_children_false_distinct_from_unknown():
    unknown_state = PersonalWishesState()
    assert unknown_state.has_children is None
    assert unknown_state.get_field_status("has_children") == "unknown"

    no_children_state = PersonalWishesState(has_children=False)
    assert no_children_state.has_children is False
    assert no_children_state.get_field_status("has_children") == "confirmed"

    # Explicit check that unknown does not evaluate to False
    assert (unknown_state.has_children is False) is False

def test_state_manager_merges_to_confirmed_by_default():
    state = PersonalWishesState()
    proposal = StateProposal(
        full_name="Bruce Wayne",
        home_address="100 Wayne Manor",
        covers_worldwide_assets=True,
        has_children=False,
        executor=ExecutorProposal(name="Alfred Pennyworth", relationship="butler")
    )
    updated = StateManager.merge(state, proposal)

    assert updated.full_name == "Bruce Wayne"
    assert updated.get_field_status("full_name") == "confirmed"
    assert updated.get_field_status("home_address") == "confirmed"
    assert updated.get_field_status("covers_worldwide_assets") == "confirmed"
    assert updated.get_field_status("has_children") == "confirmed"
    assert updated.get_field_status("children_names") == "confirmed"
    assert updated.get_field_status("executor_name") == "confirmed"
    assert updated.get_field_status("executor_relationship") == "confirmed"

def test_state_manager_preserves_explicit_unconfirmed_status():
    state = PersonalWishesState(full_name="Bruce Wayne")
    proposal = StateProposal(
        home_address="Gotham City",
        field_statuses={"home_address": "unconfirmed"}
    )
    updated = StateManager.merge(state, proposal)

    assert updated.home_address == "Gotham City"
    assert updated.get_field_status("home_address") == "unconfirmed"
    assert updated.get_field_status("full_name") == "confirmed"

def test_is_complete_rejects_unconfirmed_and_unknown_fields():
    state = PersonalWishesState(
        full_name="Clark Kent",
        home_address="344 Clinton St",
        covers_worldwide_assets=True,
        has_children=False,
    )
    state.executor.name = "Martha Kent"
    state.executor.relationship = "mother"

    assert state.is_complete() is True

    # Marking any required field as unconfirmed should cause is_complete to return False
    state.set_field_status("executor_name", "unconfirmed")
    assert state.is_complete() is False

    # Restoring to confirmed makes it complete again
    state.set_field_status("executor_name", "confirmed")
    assert state.is_complete() is True

def test_document_generator_placeholders_unknown_vs_unconfirmed():
    # 1. Empty/unknown state renders [Not provided]
    empty_state = PersonalWishesState()
    doc_empty = DocumentGenerator.generate(empty_state)
    assert "**Principal:** [Not provided]" in doc_empty
    assert "**Address:** [Not provided]" in doc_empty
    assert "[Not provided]" in doc_empty

    # 2. Unconfirmed state renders [Unconfirmed]
    unconfirmed_state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="100 Wayne Manor",
        field_statuses={
            "full_name": "unconfirmed",
            "home_address": "unconfirmed",
            "covers_worldwide_assets": "unconfirmed"
        }
    )
    doc_unconfirmed = DocumentGenerator.generate(unconfirmed_state)
    assert "Bruce Wayne [Unconfirmed]" in doc_unconfirmed
    assert "100 Wayne Manor [Unconfirmed]" in doc_unconfirmed

import pytest
from app.llm.mock_llm import MockLLMService
from app.domain.state import PersonalWishesState
from app.state_management.state_manager import StateManager


@pytest.fixture
def mock_llm():
    return MockLLMService()


def test_multifield_extraction_in_single_message(mock_llm):
    state = PersonalWishesState()
    msg = "My name is Bruce Wayne, I live at 100 Wayne Manor, worldwide assets, and my executor is my friend Alfred"
    turn_output = mock_llm.process_turn(state, [], msg)
    proposal = turn_output.proposal

    assert proposal.full_name == "Bruce Wayne"
    assert proposal.home_address == "100 Wayne Manor"
    assert proposal.covers_worldwide_assets is True
    assert proposal.executor is not None
    assert proposal.executor.name == "Alfred"
    assert proposal.executor.relationship == "friend"

    merged = StateManager.merge(state, proposal)
    assert merged.full_name == "Bruce Wayne"
    assert merged.home_address == "100 Wayne Manor"
    assert merged.covers_worldwide_assets is True
    assert merged.executor.name == "Alfred"
    assert merged.executor.relationship == "friend"
    assert merged.get_field_status("full_name") == "confirmed"
    assert merged.get_field_status("home_address") == "confirmed"
    assert merged.get_field_status("covers_worldwide_assets") == "confirmed"
    assert merged.get_field_status("executor_name") == "confirmed"
    assert merged.get_field_status("executor_relationship") == "confirmed"


def test_any_order_extraction(mock_llm):
    state = PersonalWishesState()
    msg = "Worldwide assets, I live at 100 Wayne Manor, my name is Bruce Wayne"
    turn_output = mock_llm.process_turn(state, [], msg)
    proposal = turn_output.proposal

    assert proposal.full_name == "Bruce Wayne"
    assert proposal.home_address == "100 Wayne Manor"
    assert proposal.covers_worldwide_assets is True

    state2 = PersonalWishesState()
    msg2 = "My executor is my sister Diana, covers domestic assets, I live at 42 Wallaby Way, my name is Clark Kent"
    turn_output2 = mock_llm.process_turn(state2, [], msg2)
    prop2 = turn_output2.proposal

    assert prop2.full_name == "Clark Kent"
    assert prop2.home_address == "42 Wallaby Way"
    assert prop2.covers_worldwide_assets is False
    assert prop2.executor is not None
    assert prop2.executor.name == "Diana"
    assert prop2.executor.relationship == "sister"


def test_short_followup_answer_executor(mock_llm):
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="100 Wayne Manor",
        covers_worldwide_assets=True,
    )
    history = [
        {"role": "assistant", "content": "Who would you like to appoint as the executor of your wishes?"}
    ]

    turn_output = mock_llm.process_turn(state, history, "Alfred")
    assert turn_output.proposal.executor is not None
    assert turn_output.proposal.executor.name == "Alfred"

    turn_output_full = mock_llm.process_turn(state, history, "Alfred Pennyworth")
    assert turn_output_full.proposal.executor is not None
    assert turn_output_full.proposal.executor.name == "Alfred Pennyworth"


def test_short_followup_answer_relationship(mock_llm):
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="100 Wayne Manor",
        covers_worldwide_assets=True,
    )
    state.executor.name = "Alfred"
    history = [
        {"role": "assistant", "content": "What is your legal or personal relationship to Alfred (e.g., brother, friend, solicitor)?"}
    ]

    turn_output = mock_llm.process_turn(state, history, "friend")
    assert turn_output.proposal.executor is not None
    assert turn_output.proposal.executor.name == "Alfred"
    assert turn_output.proposal.executor.relationship == "friend"


def test_regression_greedy_name_capture(mock_llm):
    state = PersonalWishesState()

    out1 = mock_llm.process_turn(state, [], "My name is Bruce Wayne living at Wayne Manor")
    assert out1.proposal.full_name == "Bruce Wayne"

    out2 = mock_llm.process_turn(state, [], "My name is Bruce Wayne I live at 100 Wayne Manor")
    assert out2.proposal.full_name == "Bruce Wayne"

    out3 = mock_llm.process_turn(state, [], "My name is Bruce Wayne and my executor is Alfred")
    assert out3.proposal.full_name == "Bruce Wayne"

    out4 = mock_llm.process_turn(state, [], "My name is Bruce Wayne worldwide assets")
    assert out4.proposal.full_name == "Bruce Wayne"


def test_regression_trailing_words_in_address(mock_llm):
    state = PersonalWishesState()

    out1 = mock_llm.process_turn(state, [], "I live at 100 Wayne Manor, worldwide assets")
    assert out1.proposal.home_address == "100 Wayne Manor"
    assert out1.proposal.covers_worldwide_assets is True

    out2 = mock_llm.process_turn(state, [], "I live at 100 Wayne Manor, worldwide assets, and my executor is Alfred")
    assert out2.proposal.home_address == "100 Wayne Manor"
    assert out2.proposal.covers_worldwide_assets is True
    assert out2.proposal.executor.name == "Alfred"

    out3 = mock_llm.process_turn(state, [], "I live at 100 Wayne Manor, no children")
    assert out3.proposal.home_address == "100 Wayne Manor"
    assert out3.proposal.has_children is False

    out4 = mock_llm.process_turn(state, [], "I live at 100 Wayne Manor, my name is Bruce Wayne")
    assert out4.proposal.home_address == "100 Wayne Manor"
    assert out4.proposal.full_name == "Bruce Wayne"


def test_executor_name_does_not_corrupt_principal_name(mock_llm):
    state = PersonalWishesState(
        full_name="Mrunal",
        home_address="Pune",
        covers_worldwide_assets=True,
    )
    state.executor.relationship = "brother"
    history = [
        {"role": "assistant", "content": "What is your brother's full legal name?"}
    ]

    turn_output = mock_llm.process_turn(state, history, "My executors name is Raj")
    assert turn_output.proposal.full_name is None
    assert turn_output.proposal.executor is not None
    assert turn_output.proposal.executor.name == "Raj"

    merged = StateManager.merge(state, turn_output.proposal)
    assert merged.full_name == "Mrunal"
    assert merged.executor.name == "Raj"
    assert merged.executor.relationship == "brother"


def test_executor_not_overwritten_in_gifts_and_wishes_sections(mock_llm):
    state = PersonalWishesState(
        full_name="Mrunal",
        home_address="Pune",
        covers_worldwide_assets=True,
        has_children=False,
    )
    state.executor.name = "Raj"
    state.executor.relationship = "brother"
    state.set_field_status("executor_name", "confirmed")
    state.set_field_status("executor_relationship", "confirmed")

    gifts_history = [
        {"role": "assistant", "content": "Understood, I've recorded executor's name as Raj. Do you have any specific gifts you'd like to leave, or would you like to skip this?"}
    ]
    out_gifts = mock_llm.process_turn(state, gifts_history, "no")
    assert out_gifts.proposal.executor is None
    assert out_gifts.proposal.has_specific_gifts is False

    merged_gifts = StateManager.merge(state, out_gifts.proposal)
    assert merged_gifts.executor.name == "Raj"
    assert merged_gifts.executor.relationship == "brother"

    wishes_history = [
        {"role": "assistant", "content": "Understood, I've noted no specific gifts. Do you have any additional wishes, such as funeral instructions or personal notes?"}
    ]
    out_wishes = mock_llm.process_turn(merged_gifts, wishes_history, "cremation")
    assert out_wishes.proposal.executor is None
    assert out_wishes.proposal.additional_wishes == "cremation"

    merged_wishes = StateManager.merge(merged_gifts, out_wishes.proposal)
    assert merged_wishes.executor.name == "Raj"
    assert merged_wishes.executor.relationship == "brother"
    assert merged_wishes.additional_wishes == "cremation"

    out_wishes_rel = mock_llm.process_turn(merged_gifts, wishes_history, "my brother should handle funeral")
    assert out_wishes_rel.proposal.executor is None
    assert "funeral" in out_wishes_rel.proposal.additional_wishes

    merged_rel = StateManager.merge(merged_gifts, out_wishes_rel.proposal)
    assert merged_rel.executor.name == "Raj"
    assert merged_rel.executor.relationship == "brother"


def test_correction_at_wishes_step_leaves_additional_wishes_unchanged(mock_llm):
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="Wayne Manor",
        covers_worldwide_assets=True,
        has_children=False,
        additional_wishes="no flowers"
    )
    state.executor.name = "Alfred"
    state.executor.relationship = "friend"
    state.set_field_status("additional_wishes", "confirmed")
    history = [
        {"role": "assistant", "content": "Understood, I've noted no specific gifts. Do you have any additional wishes, such as funeral instructions or personal notes?"}
    ]

    turn_output = mock_llm.process_turn(state, history, "change my address to 12 Park Road")
    assert turn_output.proposal.home_address == "12 Park Road"
    assert turn_output.proposal.field_intents.get("home_address") == "correct"
    assert turn_output.proposal.additional_wishes is None
    assert "additional_wishes" not in turn_output.proposal.field_intents

    merged = StateManager.merge(state, turn_output.proposal)
    assert merged.home_address == "12 Park Road"
    assert merged.additional_wishes == "no flowers"
    assert merged.get_field_status("home_address") == "confirmed"
    assert merged.get_field_status("additional_wishes") == "confirmed"


def test_correction_executor_leaves_additional_wishes_unchanged(mock_llm):
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="Wayne Manor",
        covers_worldwide_assets=True,
        has_children=False,
        additional_wishes="no flowers"
    )
    state.executor.name = "Alfred"
    state.executor.relationship = "friend"
    state.set_field_status("additional_wishes", "confirmed")
    history = [
        {"role": "assistant", "content": "Understood, I've noted no specific gifts. Do you have any additional wishes, such as funeral instructions or personal notes?"}
    ]

    turn_output = mock_llm.process_turn(state, history, "Actually my executor is Jack")
    assert turn_output.proposal.executor is not None
    assert turn_output.proposal.executor.name == "Jack"
    assert turn_output.proposal.field_intents.get("executor_name") == "correct"
    assert turn_output.proposal.additional_wishes is None
    assert "additional_wishes" not in turn_output.proposal.field_intents

    merged = StateManager.merge(state, turn_output.proposal)
    assert merged.executor.name == "Jack"
    assert merged.executor.relationship == "friend"
    assert merged.additional_wishes == "no flowers"


def test_wishes_step_saves_to_additional_wishes_only(mock_llm):
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="Wayne Manor",
        covers_worldwide_assets=True,
        has_children=False,
    )
    state.executor.name = "Alfred"
    state.executor.relationship = "friend"
    history = [
        {"role": "assistant", "content": "Do you have any additional wishes, such as funeral instructions or personal notes?"}
    ]

    turn_output = mock_llm.process_turn(state, history, "Please keep the funeral simple")
    assert turn_output.proposal.additional_wishes == "Please keep the funeral simple"
    assert turn_output.proposal.home_address is None
    assert turn_output.proposal.executor is None
    assert turn_output.proposal.full_name is None

    merged = StateManager.merge(state, turn_output.proposal)
    assert merged.additional_wishes == "Please keep the funeral simple"
    assert merged.home_address == "Wayne Manor"
    assert merged.full_name == "Bruce Wayne"
    assert merged.executor.name == "Alfred"


def test_correction_full_name_only_changes_name(mock_llm):
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="Wayne Manor",
        covers_worldwide_assets=True,
        has_children=False,
        additional_wishes="no flowers"
    )
    state.executor.name = "Alfred"
    state.executor.relationship = "friend"

    turn_output = mock_llm.process_turn(state, [], "Change my name to Jane Smith")
    assert turn_output.proposal.full_name == "Jane Smith"
    assert turn_output.proposal.field_intents.get("full_name") == "correct"
    assert turn_output.proposal.home_address is None
    assert turn_output.proposal.additional_wishes is None

    merged = StateManager.merge(state, turn_output.proposal)
    assert merged.full_name == "Jane Smith"
    assert merged.home_address == "Wayne Manor"
    assert merged.additional_wishes == "no flowers"
    assert merged.executor.name == "Alfred"


def test_explicit_change_additional_wishes_replaces_field(mock_llm):
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="Wayne Manor",
        covers_worldwide_assets=True,
        has_children=False,
        additional_wishes="simple funeral"
    )
    state.executor.name = "Alfred"
    state.executor.relationship = "friend"

    turn_output = mock_llm.process_turn(state, [], "Change my additional wishes to: no flowers")
    assert turn_output.proposal.additional_wishes == "no flowers"
    assert turn_output.proposal.field_intents.get("additional_wishes") == "correct"
    assert turn_output.proposal.full_name is None
    assert turn_output.proposal.home_address is None

    merged = StateManager.merge(state, turn_output.proposal)
    assert merged.additional_wishes == "no flowers"
    assert merged.full_name == "Bruce Wayne"
    assert merged.home_address == "Wayne Manor"
    assert merged.executor.name == "Alfred"


def test_correction_and_extra_wish_in_single_message(mock_llm):
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="Wayne Manor",
        covers_worldwide_assets=True,
        has_children=False,
        additional_wishes="no flowers"
    )
    state.executor.name = "Alfred"
    state.executor.relationship = "friend"

    turn_output = mock_llm.process_turn(state, [], "change my address to 12 Park Road, and also I want a simple funeral")
    assert turn_output.proposal.home_address == "12 Park Road"
    assert turn_output.proposal.field_intents.get("home_address") == "correct"
    assert "simple funeral" in turn_output.proposal.additional_wishes
    assert turn_output.proposal.field_intents.get("additional_wishes") == "append"

    merged = StateManager.merge(state, turn_output.proposal)
    assert merged.home_address == "12 Park Road"
    assert "no flowers" in merged.additional_wishes
    assert "simple funeral" in merged.additional_wishes
    assert merged.additional_wishes == "no flowers. a simple funeral"
    assert merged.full_name == "Bruce Wayne"
    assert merged.executor.name == "Alfred"


def test_correction_during_executor_question_leaves_wishes_empty(mock_llm):
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="Wayne Manor",
        covers_worldwide_assets=True,
        has_children=False,
    )
    history = [
        {"role": "assistant", "content": "Who would you like to appoint as the executor of your wishes?"}
    ]

    turn_output = mock_llm.process_turn(state, history, "change my address to 12 Park Road")
    assert turn_output.proposal.home_address == "12 Park Road"
    assert turn_output.proposal.additional_wishes is None
    assert "additional_wishes" not in turn_output.proposal.field_intents

    merged = StateManager.merge(state, turn_output.proposal)
    assert merged.home_address == "12 Park Road"
    assert merged.additional_wishes is None


def test_charity_instead_of_flowers_saved_as_wish_not_correction(mock_llm):
    state = PersonalWishesState(
        full_name="Bruce Wayne",
        home_address="Wayne Manor",
        covers_worldwide_assets=True,
        has_children=False,
    )
    state.executor.name = "Alfred"
    state.executor.relationship = "friend"
    history = [
        {"role": "assistant", "content": "Do you have any additional wishes, such as funeral instructions or personal notes?"}
    ]

    turn_output = mock_llm.process_turn(state, history, "I want charity donations instead of flowers")
    assert turn_output.proposal.additional_wishes == "I want charity donations instead of flowers"
    assert turn_output.proposal.field_intents.get("additional_wishes") == "set"
    assert turn_output.proposal.home_address is None
    assert turn_output.proposal.executor is None

    merged = StateManager.merge(state, turn_output.proposal)
    assert merged.additional_wishes == "I want charity donations instead of flowers"
    assert merged.home_address == "Wayne Manor"
    assert merged.executor.name == "Alfred"

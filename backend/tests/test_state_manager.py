from app.domain.state import PersonalWishesState
from app.domain.proposal import StateProposal, ExecutorProposal
from app.state_management.state_manager import StateManager

def test_state_merge_and_corrections():
    initial = PersonalWishesState(full_name="Jane Doe", home_address="Old Address")
    proposal = StateProposal(
        home_address="42 Elm St, London",
        executor=ExecutorProposal(name="Sarah Connor", relationship="sister")
    )
    updated = StateManager.merge(initial, proposal)

    assert updated.full_name == "Jane Doe"
    assert updated.home_address == "42 Elm St, London"
    assert updated.executor.name == "Sarah Connor"
    assert updated.executor.relationship == "sister"
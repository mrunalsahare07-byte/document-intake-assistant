from app.domain.state import PersonalWishesState

def test_initial_state_defaults():
    state = PersonalWishesState()
    assert state.full_name is None
    assert state.has_children is None
    assert state.children_names == []
    assert state.is_complete() is False

def test_is_complete_validation():
    state = PersonalWishesState(
        full_name="Jane Doe",
        home_address="12 High St",
        covers_worldwide_assets=True,
        has_children=False,
    )
    state.executor.name = "James Doe"
    state.executor.relationship = "brother"
    if hasattr(state, "has_specific_gifts"):
        state.has_specific_gifts = False
    assert state.is_complete() is True
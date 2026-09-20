from typing import Optional
from app.domain.state import PersonalWishesState
from app.domain.proposal import StateProposal

class StateManager:
    @staticmethod
    def merge(current_state: PersonalWishesState, proposal: Optional[StateProposal]) -> PersonalWishesState:
        if not proposal:
            return current_state

        updated = current_state.model_copy(deep=True)

        if proposal.full_name is not None:
            updated.full_name = proposal.full_name.strip()
        if proposal.home_address is not None:
            updated.home_address = proposal.home_address.strip()
        if proposal.covers_worldwide_assets is not None:
            updated.covers_worldwide_assets = proposal.covers_worldwide_assets
        if proposal.has_children is not None:
            updated.has_children = proposal.has_children
            if not proposal.has_children:
                updated.children_names = []
        if proposal.children_names is not None:
            updated.children_names = [c.strip() for c in proposal.children_names if c.strip()]

        if proposal.executor is not None:
            if proposal.executor.name is not None:
                updated.executor.name = proposal.executor.name.strip()
            if proposal.executor.relationship is not None:
                updated.executor.relationship = proposal.executor.relationship.strip()

        if proposal.has_specific_gifts is not None:
            updated.has_specific_gifts = proposal.has_specific_gifts
        if proposal.specific_gifts is not None:
            updated.specific_gifts = [g.strip() for g in proposal.specific_gifts if g.strip()]

        if proposal.additional_wishes is not None:
            updated.additional_wishes = proposal.additional_wishes.strip()

        return updated
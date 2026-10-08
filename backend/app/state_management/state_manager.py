from typing import Optional
from app.domain.state import PersonalWishesState
from app.domain.proposal import StateProposal


class StateManager:
    """Central authority for validated state transitions and contradiction handling."""

    @staticmethod
    def merge(current_state: PersonalWishesState, proposal: Optional[StateProposal]) -> PersonalWishesState:
        if not proposal:
            return current_state

        updated = current_state.model_copy(deep=True)
        prop_statuses = proposal.field_statuses or {}
        prop_intents = proposal.field_intents or {}

        # Principal name
        if prop_intents.get("full_name") == "clear":
            updated.full_name = None
            updated.field_statuses["full_name"] = "unknown"
        elif proposal.full_name is not None:
            updated.full_name = proposal.full_name.strip()
            updated.field_statuses["full_name"] = prop_statuses.get("full_name", "confirmed")

        # Home address
        if prop_intents.get("home_address") == "clear":
            updated.home_address = None
            updated.field_statuses["home_address"] = "unknown"
        elif proposal.home_address is not None:
            updated.home_address = proposal.home_address.strip()
            updated.field_statuses["home_address"] = prop_statuses.get("home_address", "confirmed")

        # Asset scope
        if prop_intents.get("covers_worldwide_assets") == "clear":
            updated.covers_worldwide_assets = None
            updated.field_statuses["covers_worldwide_assets"] = "unknown"
        elif proposal.covers_worldwide_assets is not None:
            updated.covers_worldwide_assets = proposal.covers_worldwide_assets
            updated.field_statuses["covers_worldwide_assets"] = prop_statuses.get("covers_worldwide_assets", "confirmed")

        # Family & dependents (with contradiction guard)
        has_contradiction = (
            proposal.has_children is False and bool(proposal.children_names)
        )
        if has_contradiction:
            updated.field_statuses["has_children"] = "unconfirmed"
            updated.field_statuses["children_names"] = "unconfirmed"
        else:
            if prop_intents.get("has_children") == "clear":
                updated.has_children = None
                updated.children_names = []
                updated.field_statuses["has_children"] = "unknown"
                updated.field_statuses["children_names"] = "unknown"
            elif proposal.has_children is not None:
                updated.has_children = proposal.has_children
                updated.field_statuses["has_children"] = prop_statuses.get("has_children", "confirmed")
                if not proposal.has_children:
                    updated.children_names = []
                    updated.field_statuses["children_names"] = prop_statuses.get("children_names", "confirmed")

            if prop_intents.get("children_names") == "clear":
                updated.children_names = []
                updated.field_statuses["children_names"] = "unknown"
            elif proposal.children_names is not None and not has_contradiction:
                updated.children_names = [c.strip() for c in proposal.children_names if c.strip()]
                updated.field_statuses["children_names"] = prop_statuses.get("children_names", "confirmed")

        # Executor appointment
        if prop_intents.get("executor") == "clear" or prop_intents.get("executor_name") == "clear":
            updated.executor.name = None
            updated.field_statuses["executor_name"] = "unknown"
        if prop_intents.get("executor_relationship") == "clear":
            updated.executor.relationship = None
            updated.field_statuses["executor_relationship"] = "unknown"

        if proposal.executor is not None:
            is_self_executor = (
                proposal.executor.name is not None
                and updated.full_name is not None
                and proposal.executor.name.strip().lower() == updated.full_name.strip().lower()
            )
            if is_self_executor:
                updated.field_statuses["executor_name"] = "unconfirmed"
            else:
                if proposal.executor.name is not None:
                    updated.executor.name = proposal.executor.name.strip()
                    updated.field_statuses["executor_name"] = prop_statuses.get("executor_name", "confirmed")
                if proposal.executor.relationship is not None:
                    updated.executor.relationship = proposal.executor.relationship.strip()
                    updated.field_statuses["executor_relationship"] = prop_statuses.get("executor_relationship", "confirmed")

        # Specific gifts & bequests
        if prop_intents.get("has_specific_gifts") == "clear" or prop_intents.get("specific_gifts") == "clear":
            updated.has_specific_gifts = None
            updated.specific_gifts = []
            updated.field_statuses["has_specific_gifts"] = "unknown"
            updated.field_statuses["specific_gifts"] = "unknown"
        else:
            if proposal.has_specific_gifts is not None:
                updated.has_specific_gifts = proposal.has_specific_gifts
                updated.field_statuses["has_specific_gifts"] = prop_statuses.get("has_specific_gifts", "confirmed")
            if proposal.specific_gifts is not None:
                updated.specific_gifts = [g.strip() for g in proposal.specific_gifts if g.strip()]
                updated.field_statuses["specific_gifts"] = prop_statuses.get("specific_gifts", "confirmed")

        # Additional wishes & instructions
        if prop_intents.get("additional_wishes") == "clear":
            updated.additional_wishes = None
            updated.field_statuses["additional_wishes"] = "unknown"
        elif proposal.additional_wishes is not None:
            wish_val = proposal.additional_wishes.strip()
            if (
                prop_intents.get("additional_wishes") == "append"
                and updated.additional_wishes
                and updated.additional_wishes.strip().lower() != "none"
            ):
                sep = ". " if not updated.additional_wishes.rstrip().endswith((".", ";")) else " "
                updated.additional_wishes = f"{updated.additional_wishes.rstrip()}{sep}{wish_val}"
            else:
                updated.additional_wishes = wish_val
            updated.field_statuses["additional_wishes"] = prop_statuses.get("additional_wishes", "confirmed")

        # Explicit status overrides
        for field, st in prop_statuses.items():
            updated.field_statuses[field] = st

        return updated
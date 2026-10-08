from typing import Optional, List, Dict, Literal, Any
from pydantic import BaseModel, Field

FieldStatus = Literal["unknown", "unconfirmed", "confirmed"]

DEFAULT_FIELD_STATUSES: Dict[str, FieldStatus] = {
    "full_name": "unknown",
    "home_address": "unknown",
    "covers_worldwide_assets": "unknown",
    "has_children": "unknown",
    "children_names": "unknown",
    "executor_name": "unknown",
    "executor_relationship": "unknown",
    "has_specific_gifts": "unknown",
    "specific_gifts": "unknown",
    "additional_wishes": "unknown",
}

class Executor(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None

class PersonalWishesState(BaseModel):
    full_name: Optional[str] = None
    home_address: Optional[str] = None
    covers_worldwide_assets: Optional[bool] = None
    has_children: Optional[bool] = None
    children_names: List[str] = Field(default_factory=list)
    executor: Executor = Field(default_factory=Executor)
    has_specific_gifts: Optional[bool] = None
    specific_gifts: List[str] = Field(default_factory=list)
    additional_wishes: Optional[str] = None
    field_statuses: Dict[str, str] = Field(default_factory=lambda: dict(DEFAULT_FIELD_STATUSES))

    def model_post_init(self, __context: Any) -> None:
        for field, default_st in DEFAULT_FIELD_STATUSES.items():
            if field not in self.field_statuses:
                self.field_statuses[field] = default_st

        # If values were passed at initialization without explicit status, infer confirmed
        if self.full_name is not None and self.field_statuses.get("full_name") == "unknown":
            self.field_statuses["full_name"] = "confirmed"
        if self.home_address is not None and self.field_statuses.get("home_address") == "unknown":
            self.field_statuses["home_address"] = "confirmed"
        if self.covers_worldwide_assets is not None and self.field_statuses.get("covers_worldwide_assets") == "unknown":
            self.field_statuses["covers_worldwide_assets"] = "confirmed"
        if self.has_children is not None and self.field_statuses.get("has_children") == "unknown":
            self.field_statuses["has_children"] = "confirmed"
        if self.children_names and self.field_statuses.get("children_names") == "unknown":
            self.field_statuses["children_names"] = "confirmed"
        if self.executor.name is not None and self.field_statuses.get("executor_name") == "unknown":
            self.field_statuses["executor_name"] = "confirmed"
        if self.executor.relationship is not None and self.field_statuses.get("executor_relationship") == "unknown":
            self.field_statuses["executor_relationship"] = "confirmed"
        if self.has_specific_gifts is not None and self.field_statuses.get("has_specific_gifts") == "unknown":
            self.field_statuses["has_specific_gifts"] = "confirmed"
        if self.specific_gifts and self.field_statuses.get("specific_gifts") == "unknown":
            self.field_statuses["specific_gifts"] = "confirmed"
        if self.additional_wishes is not None and self.field_statuses.get("additional_wishes") == "unknown":
            self.field_statuses["additional_wishes"] = "confirmed"

    def get_field_status(self, field_name: str) -> str:
        status = self.field_statuses.get(field_name, "unknown")
        if status == "unconfirmed":
            return "unconfirmed"

        val = getattr(self, field_name, None)
        if field_name == "executor_name":
            val = self.executor.name
        elif field_name == "executor_relationship":
            val = self.executor.relationship

        if val is not None:
            if isinstance(val, list) and not val:
                return status
            return "confirmed"
        return status

    def set_field_status(self, field_name: str, status: str) -> None:
        self.field_statuses[field_name] = status

    def is_complete(self) -> bool:
        basic_filled = (
            self.full_name is not None
            and self.home_address is not None
            and self.covers_worldwide_assets is not None
            and self.has_children is not None
            and self.executor.name is not None
            and self.executor.relationship is not None
        )
        if not basic_filled:
            return False
        if self.has_children and not self.children_names:
            return False

        required = [
            "full_name",
            "home_address",
            "covers_worldwide_assets",
            "has_children",
            "executor_name",
            "executor_relationship",
        ]
        if self.has_children:
            required.append("children_names")

        for f in required:
            if self.get_field_status(f) != "confirmed":
                return False
        return True
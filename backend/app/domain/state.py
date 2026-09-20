from typing import Optional, List
from pydantic import BaseModel, Field

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
        return True
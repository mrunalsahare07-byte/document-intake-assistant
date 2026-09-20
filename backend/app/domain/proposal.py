from typing import Optional, List
from pydantic import BaseModel, Field

class ExecutorProposal(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None

class StateProposal(BaseModel):
    full_name: Optional[str] = None
    home_address: Optional[str] = None
    covers_worldwide_assets: Optional[bool] = None
    has_children: Optional[bool] = None
    children_names: Optional[List[str]] = None
    executor: Optional[ExecutorProposal] = None
    has_specific_gifts: Optional[bool] = None
    specific_gifts: Optional[List[str]] = None
    additional_wishes: Optional[str] = None

class LLMTurnOutput(BaseModel):
    proposal: StateProposal = Field(default_factory=StateProposal)
    assistant_response: str
    requires_clarification: bool = False
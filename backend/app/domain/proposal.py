from typing import Optional, List, Dict, Literal
from pydantic import BaseModel, Field, ConfigDict

FieldIntent = Literal["set", "correct", "clear", "append"]

class ExecutorProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, max_length=200)
    relationship: Optional[str] = Field(default=None, max_length=100)

class StateProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: Optional[str] = Field(default=None, max_length=200)
    home_address: Optional[str] = Field(default=None, max_length=500)
    covers_worldwide_assets: Optional[bool] = None
    has_children: Optional[bool] = None
    children_names: Optional[List[str]] = Field(default=None, max_length=50)
    executor: Optional[ExecutorProposal] = None
    has_specific_gifts: Optional[bool] = None
    specific_gifts: Optional[List[str]] = Field(default=None, max_length=50)
    additional_wishes: Optional[str] = Field(default=None, max_length=2000)
    field_statuses: Optional[dict[str, str]] = None
    field_intents: dict[str, str] = Field(default_factory=dict)

class LLMTurnOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal: StateProposal = Field(default_factory=StateProposal)
    assistant_response: str = Field(..., min_length=1, max_length=5000)
    requires_clarification: bool = False
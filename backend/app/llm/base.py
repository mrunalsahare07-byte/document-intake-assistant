from abc import ABC, abstractmethod
from typing import List, Dict
from app.domain.state import PersonalWishesState
from app.domain.proposal import LLMTurnOutput

class BaseLLMService(ABC):
    @abstractmethod
    def process_turn(
        self,
        current_state: PersonalWishesState,
        conversation_history: List[Dict[str, str]],
        user_message: str
    ) -> LLMTurnOutput:
        pass
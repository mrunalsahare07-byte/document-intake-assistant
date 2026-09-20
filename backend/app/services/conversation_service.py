from typing import Dict, Any, List
from app.domain.state import PersonalWishesState
from app.llm.base import BaseLLMService
from app.state_management.state_manager import StateManager
from app.document.generator import DocumentGenerator

class ConversationService:
    def __init__(self, llm_service: BaseLLMService):
        self.llm = llm_service

    def handle_message(
        self,
        current_state: PersonalWishesState,
        history: List[Dict[str, str]],
        message: str
    ) -> Dict[str, Any]:
        llm_output = self.llm.process_turn(current_state, history, message)
        new_state = StateManager.merge(current_state, llm_output.proposal)
        document_md = DocumentGenerator.generate(new_state)

        return {
            "assistant_response": llm_output.assistant_response,
            "state": new_state.model_dump(),
            "document": document_md
        }
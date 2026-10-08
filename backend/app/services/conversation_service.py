import json
from typing import Dict, Any, List
from pydantic import ValidationError
from app.domain.state import PersonalWishesState
from app.domain.proposal import LLMTurnOutput
from app.llm.base import BaseLLMService
from app.state_management.state_manager import StateManager
from app.document.generator import DocumentGenerator


class ConversationService:
    """Coordinates turn-based dialogue flow, payload validation, and state persistence."""

    def __init__(self, llm_service: BaseLLMService):
        self.llm = llm_service

    def handle_message(
        self,
        current_state: PersonalWishesState,
        history: List[Dict[str, str]],
        message: str
    ) -> Dict[str, Any]:
        try:
            raw_output = self.llm.process_turn(current_state, history, message)

            if isinstance(raw_output, LLMTurnOutput):
                validated_output = LLMTurnOutput.model_validate(raw_output.model_dump())
            elif isinstance(raw_output, dict):
                validated_output = LLMTurnOutput.model_validate(raw_output)
            elif isinstance(raw_output, str):
                parsed = json.loads(raw_output)
                validated_output = LLMTurnOutput.model_validate(parsed)
            else:
                raise TypeError(f"Unsupported model output type: {type(raw_output)}")

            new_state = StateManager.merge(current_state, validated_output.proposal)
            document_md = DocumentGenerator.generate(new_state)

            return {
                "assistant_response": validated_output.assistant_response,
                "state": new_state.model_dump(),
                "document": document_md,
                "requires_clarification": validated_output.requires_clarification
            }
        except (ValidationError, json.JSONDecodeError, TypeError, ValueError) as err:
            safe_message = (
                "I apologize, but I encountered an issue processing that response safely. "
                "Your existing document information remains saved. Could you please rephrase or repeat your answer?"
            )
            return {
                "assistant_response": safe_message,
                "state": current_state.model_dump(),
                "document": DocumentGenerator.generate(current_state),
                "error": {
                    "code": "MODEL_VALIDATION_ERROR",
                    "message": str(err)
                }
            }
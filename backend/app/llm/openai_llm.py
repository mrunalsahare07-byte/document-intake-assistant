import os
from openai import OpenAI
from app.llm.base import BaseLLMService
from app.domain.state import PersonalWishesState
from app.domain.proposal import LLMTurnOutput


class OpenAILLMService(BaseLLMService):
    """Production provider integrating OpenAI chat models via structured output parsing."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("LLM_MODEL", "gpt-4o")

    def process_turn(
        self,
        current_state: PersonalWishesState,
        conversation_history: list,
        user_message: str
    ) -> LLMTurnOutput:
        system_prompt = (
            "You are an intake assistant conducting a structured interview for a Personal "
            "Wishes Document. Extract confirmed details into the state proposal and guide the "
            "user through the remaining intake steps."
        )

        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": user_message},
            ],
            response_format=LLMTurnOutput,
        )
        return completion.choices[0].message.parsed
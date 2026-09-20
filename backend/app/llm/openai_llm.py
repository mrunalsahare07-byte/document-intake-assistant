import os
from openai import OpenAI
from app.llm.base import BaseLLMService
from app.domain.state import PersonalWishesState
from app.domain.proposal import LLMTurnOutput

class OpenAILLMService(BaseLLMService):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("LLM_MODEL", "gpt-4o")

    def process_turn(
            self,
            current_state: PersonalWishesState,
            conversation_history: list,
            user_message: str
    ) -> LLMTurnOutput:
        # Call model using Structured Outputs enforcing the LLMTurnOutput Pydantic schema
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Document Intake Assistant conducting an intake interview "
                        "for a Personal Wishes Document. Extract confirmed fields into the proposal "
                        "and output your next response."
                    ),
                },
                *conversation_history,
                {"role": "user", "content": user_message},
            ],
            response_format=LLMTurnOutput,
        )
        return completion.choices[0].message.parsed
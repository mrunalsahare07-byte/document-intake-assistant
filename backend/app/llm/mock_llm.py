import re
from typing import List, Dict
from app.domain.state import PersonalWishesState
from app.domain.proposal import LLMTurnOutput, StateProposal, ExecutorProposal
from app.llm.base import BaseLLMService

class MockLLMService(BaseLLMService):
    def process_turn(
            self,
            current_state: PersonalWishesState,
            conversation_history: List[Dict[str, str]],
            user_message: str
    ) -> LLMTurnOutput:
        text = user_message.strip()
        lower = text.lower()
        proposal = StateProposal()
        notes = []

        # Find the last assistant prompt
        last_bot_prompt = ""
        for msg in reversed(conversation_history):
            role = msg.get("role") or msg.get("sender")
            if role == "assistant":
                last_bot_prompt = (msg.get("content") or msg.get("text") or "").lower()
                break

        # ---------------- 1. FULL NAME ----------------
        name_match = re.search(r"(?:my name is|i am|call me|name:?)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*?)(?:\s+(?:and|,|\.|\n|$))", text + " ", re.IGNORECASE)
        if name_match:
            proposal.full_name = name_match.group(1).strip()
            notes.append(f"recorded your name as {proposal.full_name}")
        elif current_state.full_name is None:
            clean_text = re.sub(r"[^\w\s]", "", text).strip()
            words = clean_text.split()
            blocked = {"yes", "no", "sure", "ok", "hello", "hi", "worldwide", "domestic"}
            if 1 <= len(words) <= 4 and clean_text.lower() not in blocked:
                proposal.full_name = clean_text
                notes.append(f"recorded your name as {clean_text}")

        # ---------------- 2. HOME ADDRESS ----------------
        addr_match = re.search(
            r"\b(?:i live (?:at|in)|live (?:at|in)|living (?:at|in)|based in|located in|address is|address:?)\s+([^,.\n]+(?:,\s*[^,.\n]+)*)",
            text,
            re.IGNORECASE
        )
        if addr_match:
            raw_address = addr_match.group(1).strip()
            raw_address = re.split(r"\b(?:and my executor|my executor|and i appoint)\b", raw_address, flags=re.IGNORECASE)[0].strip()
            proposal.home_address = re.sub(r"[.\s]+$", "", raw_address)
            notes.append("updated your address")
        elif (
                current_state.full_name is not None
                and current_state.home_address is None
                and not proposal.full_name
                and not any(k in lower for k in ["yes", "no", "executor", "worldwide", "children", "gift"])
        ):
            clean_addr = text.strip(" .,")
            if 2 <= len(clean_addr) <= 100:
                proposal.home_address = clean_addr
                notes.append(f"updated your address to {clean_addr}")

        # ---------------- 3. WORLDWIDE ASSET COVERAGE ----------------
        if "worldwide" in lower or "global" in lower or "all assets" in lower:
            if "not worldwide" in lower or "no worldwide" in lower:
                proposal.covers_worldwide_assets = False
                notes.append("recorded coverage as domestic only")
            else:
                proposal.covers_worldwide_assets = True
                notes.append("confirmed worldwide asset coverage")
        elif "domestic" in lower or "local" in lower or "uk only" in lower or "india only" in lower:
            proposal.covers_worldwide_assets = False
            notes.append("recorded coverage as domestic only")
        elif "worldwide" in last_bot_prompt and current_state.covers_worldwide_assets is None:
            if re.search(r"\b(yes|yeah|yep|sure|worldwide|all)\b", lower):
                proposal.covers_worldwide_assets = True
                notes.append("confirmed worldwide asset coverage")
            elif re.search(r"\b(no|nope|domestic|local|only domestic)\b", lower):
                proposal.covers_worldwide_assets = False
                notes.append("recorded coverage as domestic only")

        # ---------------- 4. CHILDREN & DEPENDENTS ----------------
        is_asking_children = "children" in last_bot_prompt or "dependents" in last_bot_prompt or "kids" in last_bot_prompt
        is_asking_child_names = "names of your children" in last_bot_prompt or "list the names" in last_bot_prompt

        if re.search(r"\b(no children|don't have children|do not have kids|no kids|no child)\b", lower):
            proposal.has_children = False
            proposal.children_names = []
            notes.append("noted that you do not have children")
        elif is_asking_child_names and not proposal.full_name:
            # Direct response when prompted to list children's names (e.g., "A and B", "A B", "Alex, Bob")
            raw_names_str = text.strip(" .")
            raw_names_str = re.split(r"\b(?:and my|my executor|and i|i live)\b", raw_names_str, flags=re.IGNORECASE)[0].strip()
            # Split by comma, '&', 'and', or whitespace if separated by spaces
            if "," in raw_names_str or re.search(r"\b(and|&)\b", raw_names_str, re.IGNORECASE):
                raw_names = re.split(r",|\band\b|&", raw_names_str, flags=re.IGNORECASE)
            else:
                raw_names = raw_names_str.split()

            cleaned_names = [n.strip(" .\"'") for n in raw_names if n.strip(" .\"'") and n.strip(" .\"'").lower() not in {"and", "&"}]
            if cleaned_names:
                proposal.has_children = True
                proposal.children_names = cleaned_names
                notes.append(f"recorded children: {', '.join(cleaned_names)}")
        else:
            kids_match = re.search(
                r"(?:children are|kids are|have\s+(?:a|\d+|one|two|three|four|five|several)?\s*(?:children|kids|child)?\s*(?:named|called))\s+([A-Za-z,\s&]+)",
                text,
                re.IGNORECASE
            )
            if kids_match:
                proposal.has_children = True
                raw_names_str = kids_match.group(1).strip()
                raw_names_str = re.split(r"\b(?:and my|my executor|and i|i live)\b", raw_names_str, flags=re.IGNORECASE)[0].strip()
                raw_names = re.split(r",|\band\b|&", raw_names_str, flags=re.IGNORECASE)
                cleaned_names = [n.strip(" .\"'") for n in raw_names if n.strip(" .\"'") and n.strip(" .\"'").lower() not in {"and", "&"}]
                if cleaned_names:
                    proposal.children_names = cleaned_names
                    notes.append(f"recorded children: {', '.join(cleaned_names)}")
            elif is_asking_children and current_state.has_children is None:
                if re.search(r"\b(no|none|dont|do not|zero)\b", lower):
                    proposal.has_children = False
                    proposal.children_names = []
                    notes.append("noted that you do not have children")
                elif re.search(r"\b(yes|yeah|yep|i do|i have)\b", lower):
                    proposal.has_children = True
                    notes.append("noted that you have children")

        # ---------------- 5. APPOINTED EXECUTOR ----------------
        # Only execute executor logic if we have cleared the personal name/address steps or executor is explicitly mentioned
        RELATIONSHIPS = [
            "brother", "sister", "father", "mother", "son", "daughter",
            "friend", "partner", "spouse", "wife", "husband", "lawyer",
            "solicitor", "cousin", "uncle", "aunt"
        ]
        rel_pattern = r"\b(" + "|".join(RELATIONSHIPS) + r")\b"

        can_process_executor = (
                "executor" in lower
                or any(r in lower for r in RELATIONSHIPS)
                or ("executor" in last_bot_prompt)
                or ("relationship to" in last_bot_prompt)
                or ("full legal name" in last_bot_prompt and current_state.executor.relationship is not None)
        )

        if can_process_executor and not proposal.full_name:
            if re.search(r"\b(either\b.*\bor\b|\bor\b)", text, re.IGNORECASE) and ("executor" in lower or any(r in lower for r in RELATIONSHIPS)):
                proposal.executor = None
                notes.append("detected ambiguity between multiple candidates; please choose one executor")
            elif re.search(r"\b(be my own executor|appoint myself|myself as executor)\b", lower) or (
                    current_state.full_name and current_state.full_name.lower() in lower and "executor" in lower
            ):
                proposal.executor = None
                notes.append("you cannot appoint yourself as executor; please name a third party")
            elif ("relationship to" in last_bot_prompt) and current_state.executor.relationship is None:
                rel_search = re.search(rel_pattern, text, re.IGNORECASE)
                if rel_search:
                    found_rel = rel_search.group(1).lower()
                    proposal.executor = ExecutorProposal(name=current_state.executor.name, relationship=found_rel)
                    notes.append(f"recorded relationship as {found_rel}")
            elif ("full legal name" in last_bot_prompt and current_state.executor.relationship is not None and current_state.executor.name is None):
                clean_name = text.strip(" .")
                proposal.executor = ExecutorProposal(name=clean_name, relationship=current_state.executor.relationship)
                notes.append(f"recorded executor's name as {clean_name}")
            elif "executor" in lower or any(r in lower for r in RELATIONSHIPS):
                found_rel = None
                rel_search = re.search(rel_pattern, text, re.IGNORECASE)
                if rel_search:
                    found_rel = rel_search.group(1).lower()

                STOPWORDS = {
                    "my", "the", "executor", "should", "be", "is", "and", "or",
                    "either", "to", "i", "want", "appoint", "as", "named", "called",
                    "would", "like"
                }
                words = [w.strip(".,!?") for w in text.split()]
                name_candidates = [
                    w for w in words
                    if w and w[0].isupper() and w.lower() not in STOPWORDS and w.lower() not in RELATIONSHIPS
                ]
                found_name = " ".join(name_candidates) if name_candidates else None

                if found_name or found_rel:
                    proposal.executor = ExecutorProposal(name=found_name, relationship=found_rel)
                    if found_name and found_rel:
                        notes.append(f"appointed {found_name} ({found_rel}) as executor")
                    elif found_name:
                        notes.append(f"recorded executor name {found_name} (relationship pending)")
                    elif found_rel:
                        notes.append(f"recorded executor as {found_rel} (name pending)")

        # ---------------- 6. SPECIFIC GIFTS ----------------
        is_asking_gifts = ("gift" in last_bot_prompt or "bequest" in last_bot_prompt or "skip this" in last_bot_prompt)
        is_asking_wishes = ("additional wishes" in last_bot_prompt or "funeral" in last_bot_prompt or "personal notes" in last_bot_prompt)

        # Only process gifts if we are currently being asked about gifts OR the user explicitly mentions 'gift' / 'bequeath'
        if is_asking_gifts and not is_asking_wishes:
            if re.search(r"\b(no|none|skip|nope|nothing|no gifts?)\b", lower):
                proposal.has_specific_gifts = False
                proposal.specific_gifts = []
                notes.append("noted no specific gifts")
            else:
                clean_gift = text.strip(" .\"'")
                proposal.has_specific_gifts = True
                proposal.specific_gifts = [clean_gift]
                notes.append(f"recorded specific gift: {clean_gift}")
        elif ("gift" in lower or "leave my" in lower or "bequeath" in lower) and not is_asking_wishes:
            gift_match = re.search(r"(?:leave|gift|bequeath)\s+(.*)", text, re.IGNORECASE)
            if gift_match:
                clean_gift = gift_match.group(1).strip(" .\"'")
                proposal.has_specific_gifts = True
                proposal.specific_gifts = [clean_gift]
                notes.append(f"recorded specific gift: {clean_gift}")

        # ---------------- 7. ADDITIONAL WISHES ----------------
        # Only process wishes if we are being asked about wishes OR user mentions funeral / cremation / wishes
        if is_asking_wishes:
            if re.search(r"\b(no|none|skip|nothing|no wishes|nope)\b", lower):
                proposal.additional_wishes = "None"
                notes.append("noted no additional wishes")
            else:
                proposal.additional_wishes = text.strip(" .\"'")
                notes.append("recorded additional wishes")
        elif any(k in lower for k in ["cremat", "burial", "funeral", "scatter", "ashes", "additional wish"]) and not is_asking_gifts:
            proposal.additional_wishes = text.strip(" .\"'")
            notes.append("recorded additional wishes")

        # ---------------- MERGE & NEXT PROMPT ----------------
        temp_state = current_state.model_copy(deep=True)
        from app.state_management.state_manager import StateManager
        preview_state = StateManager.merge(temp_state, proposal)

        next_question = self._get_next_question(preview_state)
        ack = f"Understood, I've {', and '.join(notes)}. " if notes else ""
        response_text = f"{ack}{next_question}".strip()

        return LLMTurnOutput(
            proposal=proposal,
            assistant_response=response_text,
            requires_clarification=False
        )

    def _get_next_question(self, state: PersonalWishesState) -> str:
        if not state.full_name:
            return "Could you please tell me your full legal name?"
        if not state.home_address:
            return f"Thank you, {state.full_name}. What is your current residential address?"
        if state.covers_worldwide_assets is None:
            return "Should this document cover assets worldwide, or only domestic assets?"
        if state.has_children is None:
            return "Do you have any children?"
        if state.has_children and not state.children_names:
            return "Could you list the names of your children?"
        if not state.executor.name and not state.executor.relationship:
            return "Who would you like to appoint as the executor of your wishes?"
        if state.executor.name and not state.executor.relationship:
            return f"What is your legal or personal relationship to {state.executor.name} (e.g., brother, friend, solicitor)?"
        if state.executor.relationship and not state.executor.name:
            return f"What is your {state.executor.relationship}'s full legal name?"
        if state.has_specific_gifts is None:
            return "Do you have any specific gifts you'd like to leave (e.g. heirloom, car), or would you like to skip this?"
        if state.additional_wishes is None:
            return "Do you have any additional wishes, such as funeral instructions or personal notes?"

        return "Your draft Personal Wishes Document is complete! Feel free to review the preview or make any corrections."
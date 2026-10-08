import re
from typing import List, Dict, Optional, Set
from app.domain.state import PersonalWishesState
from app.domain.proposal import LLMTurnOutput, StateProposal, ExecutorProposal
from app.llm.base import BaseLLMService
from app.state_management.state_manager import StateManager

RELATIONSHIP_TERMS = [
    "brother", "sister", "father", "mother", "son", "daughter",
    "friend", "partner", "spouse", "wife", "husband", "lawyer",
    "solicitor", "cousin", "uncle", "aunt"
]

RELATIONSHIP_PATTERN = r"\b(" + "|".join(RELATIONSHIP_TERMS) + r")\b"

STOPWORDS = {
    "my", "the", "executor", "executors", "should", "be", "is", "and", "or",
    "either", "to", "i", "want", "appoint", "as", "named", "called",
    "would", "like", "actually", "not", "instead", "of", "please",
    "change", "update", "correct", "now", "but",
    "who", "for", "with", "worldwide", "domestic", "assets", "asset",
    "covers", "cover", "live", "living", "address", "name", "him", "her",
    "no", "none", "skip", "nope", "nothing", "yes", "yeah", "yep", "sure", "ok", "okay"
}


class MockLLMService(BaseLLMService):
    """Deterministic intake dialogue engine using rule-based entity extraction.

    Extracts intake fields from natural conversational responses, tracks
    modification intents (set, correct, clear, append), guards against contradictions,
    and guides the interview sequence until all required estate details are captured.
    """

    def process_turn(
        self,
        current_state: PersonalWishesState,
        conversation_history: List[Dict[str, str]],
        user_message: str
    ) -> LLMTurnOutput:
        text = user_message.strip()
        lower = text.lower()
        proposal = StateProposal()
        notes: List[str] = []

        last_bot_prompt = self._extract_last_bot_prompt(conversation_history)
        bot_question = self._extract_bot_question(last_bot_prompt)

        is_asking_gifts = bool("gift" in bot_question or "bequest" in bot_question or "skip this" in bot_question)
        is_asking_wishes = bool("additional wishes" in bot_question or "funeral" in bot_question or "personal notes" in bot_question)
        is_asking_children = bool("children" in bot_question or "dependents" in bot_question or "kids" in bot_question)
        is_asking_child_names = bool("names of your children" in bot_question or "list the names" in bot_question)

        # Detect correction intents and field scopes
        target_fields = self._detect_target_fields(lower)
        has_correction_keyword = bool(
            re.search(r"\b(change|update|actually|correct|instead\s+of|is\s+now|not\s+\w+\s+but)\b", lower)
        )
        is_correction_turn = has_correction_keyword and len(target_fields) > 0
        is_correction_for_other_field = is_correction_turn and "additional_wishes" not in target_fields

        # Check explicit clear commands
        self._handle_clear_commands(lower, proposal, notes)

        # Check for contradictions
        contradiction_turn = self._check_contradictions(text, lower, current_state)
        if contradiction_turn:
            return contradiction_turn

        # Field extractions
        self._extract_name(text, lower, current_state, proposal, notes)
        self._extract_address(text, lower, current_state, proposal, notes)
        self._extract_worldwide_assets(text, lower, last_bot_prompt, current_state, proposal, notes)
        self._extract_children(text, lower, bot_question, is_asking_children, is_asking_child_names, current_state, proposal, notes)
        self._extract_executor(text, lower, bot_question, is_asking_gifts, is_asking_wishes, is_asking_children, current_state, proposal, notes)
        self._extract_gifts(text, lower, bot_question, is_asking_wishes, current_state, proposal, notes)
        self._extract_additional_wishes(text, lower, bot_question, is_asking_gifts, is_asking_wishes, is_correction_for_other_field, current_state, proposal, notes)

        # Determine next prompt based on merged preview state
        preview_state = StateManager.merge(current_state.model_copy(deep=True), proposal)
        next_question = self._get_next_question(preview_state)

        ack = f"Understood, I've {', and '.join(notes)}. " if notes else ""
        response_text = f"{ack}{next_question}".strip()

        return LLMTurnOutput(
            proposal=proposal,
            assistant_response=response_text,
            requires_clarification=False
        )

    def _extract_last_bot_prompt(self, history: List[Dict[str, str]]) -> str:
        for msg in reversed(history):
            role = msg.get("role") or msg.get("sender")
            if role == "assistant":
                return (msg.get("content") or msg.get("text") or "").lower()
        return ""

    def _extract_bot_question(self, last_prompt: str) -> str:
        question = re.sub(r"^understood,.*?\.\s*", "", last_prompt, flags=re.IGNORECASE).strip()
        return question or last_prompt

    def _detect_target_fields(self, lower: str) -> Set[str]:
        targets = set()
        if re.search(r"\b(?:address|residential\s+address|live|living)\b", lower):
            targets.add("home_address")
        if re.search(r"\b(?:worldwide|domestic|assets|coverage)\b", lower):
            targets.add("covers_worldwide_assets")
        if re.search(r"\b(?:children|kids|child|dependents)\b", lower):
            targets.add("children")
        if re.search(r"\b(?:executor|executors|brother|sister|father|mother|son|daughter|friend|partner|spouse|wife|husband|lawyer|solicitor|cousin|uncle|aunt|appoint)\b", lower):
            targets.add("executor")
        if re.search(r"\b(?:gift|gifts|bequest|bequeath)\b", lower):
            targets.add("specific_gifts")
        if re.search(r"\b(?:additional\s+wishes|wishes)\b", lower):
            targets.add("additional_wishes")

        is_subordinate_name = bool(re.search(r"\b(?:executor'?s?\s+name|name\s+of\s+(?:my\s+)?executor|children'?s?\s+name|child'?s?\s+name)\b", lower))
        if not is_subordinate_name and re.search(r"\b(?:my\s+name|full\s+name|^name:?)\b", lower):
            targets.add("full_name")
        return targets

    def _handle_clear_commands(self, lower: str, proposal: StateProposal, notes: List[str]) -> None:
        if re.search(r"\b(clear|remove|delete)\s+(?:my\s+)?(?:additional\s+)?wishes\b", lower):
            proposal.additional_wishes = None
            proposal.field_intents["additional_wishes"] = "clear"
            notes.append("cleared your additional wishes")
        if re.search(r"\b(clear|remove|delete)\s+(?:my\s+)?(?:specific\s+)?gifts\b", lower):
            proposal.has_specific_gifts = None
            proposal.specific_gifts = []
            proposal.field_intents["has_specific_gifts"] = "clear"
            proposal.field_intents["specific_gifts"] = "clear"
            notes.append("cleared your specific gifts")
        if re.search(r"\b(clear|remove|delete)\s+(?:my\s+)?address\b", lower):
            proposal.home_address = None
            proposal.field_intents["home_address"] = "clear"
            notes.append("cleared your address")
        if re.search(r"\b(clear|remove|delete)\s+(?:my\s+)?executor\b", lower):
            proposal.executor = None
            proposal.field_intents["executor"] = "clear"
            notes.append("cleared your executor appointment")

    def _check_contradictions(
        self,
        text: str,
        lower: str,
        current_state: PersonalWishesState
    ) -> Optional[LLMTurnOutput]:
        has_no_children_phrase = bool(re.search(r"\b(no children|don't have children|do not have kids|no kids|no child)\b", lower))
        child_names_explicit = re.search(
            r"(?:their names are|names are|names:?|children are|kids are|have\s+(?:a|\d+|one|two|three|four|five|several)?\s*(?:children|kids|child)?\s*(?:named|called))\s+([A-Za-z,\s&]+)",
            text,
            re.IGNORECASE
        )

        if has_no_children_phrase and child_names_explicit:
            proposal = StateProposal(
                field_statuses={"has_children": "unconfirmed", "children_names": "unconfirmed"},
                field_intents={"has_children": "correct", "children_names": "correct"}
            )
            return LLMTurnOutput(
                proposal=proposal,
                assistant_response="I noticed a contradiction: you mentioned having no children, but child names were also mentioned. Could you please clarify if you have children, and if so, their names?",
                requires_clarification=True
            )

        if (
            current_state.has_children is False
            and child_names_explicit
            and not any(k in lower for k in ["actually", "change", "correction", "update", "i do have", "i have"])
        ):
            proposal = StateProposal(
                field_statuses={"has_children": "unconfirmed", "children_names": "unconfirmed"},
                field_intents={"has_children": "correct", "children_names": "correct"}
            )
            return LLMTurnOutput(
                proposal=proposal,
                assistant_response="You previously indicated having no children, but now mentioned child names. Could you please clarify whether you have children?",
                requires_clarification=True
            )

        return None

    def _extract_name(
        self,
        text: str,
        lower: str,
        current_state: PersonalWishesState,
        proposal: StateProposal,
        notes: List[str]
    ) -> None:
        is_subordinate = bool(re.search(r"\b(?:executor'?s?\s+name|name\s+of\s+(?:my\s+)?executor|children'?s?\s+name|child'?s?\s+name)\b", text, re.IGNORECASE))
        name_delim = r"(?=[,.;!?]|\s+(?:and\b|i\s+live\b|live\b|living\b|lives\b|my\s+address\b|address\b|executor\b|my\s+executor\b|worldwide\b|domestic\b|no\s+children\b|children\b|and\s+also\s+i\s+want|also\s+i\s+want|and\s+my\s+wish\s+is|my\s+wish\s+is|and\s+please\s+note|please\s+note)|$)"

        name_match = None
        if not is_subordinate:
            name_match = re.search(
                r"(?:change\s+(?:my\s+)?name\s+to|update\s+(?:my\s+)?name\s+to|correct\s+(?:my\s+)?name\s+to|actually\s+my\s+name\s+is|my\s+name\s+is\s+now|my\s+name\s+is|i\s+am\s+called|call\s+me|^(?:full\s+)?name:\s*)\s+"
                r"(?!is\b)"
                r"([A-Za-z]+(?:\s+[A-Za-z]+)*?)" + name_delim,
                text,
                re.IGNORECASE
            )

        if name_match:
            proposal.full_name = name_match.group(1).strip()
            proposal.field_intents["full_name"] = "correct" if current_state.full_name else "set"
            notes.append(f"updated your name to {proposal.full_name}" if current_state.full_name else f"recorded your name as {proposal.full_name}")
        elif current_state.full_name is None:
            clean_text = re.sub(r"[^\w\s]", "", text).strip()
            words = clean_text.split()
            blocked = {"yes", "no", "sure", "ok", "hello", "hi", "worldwide", "domestic"}
            is_address_like = bool(re.search(r"^\d+\s+[A-Za-z]+", clean_text) or any(k in lower for k in ["street", "st", "road", "rd", "avenue", "ave", "lane", "way", "drive", "manor"]))
            has_other_intent = any(k in lower for k in ["executor", "worldwide", "domestic", "live", "address", "children", "kids", "gift"])
            if 1 <= len(words) <= 4 and clean_text.lower() not in blocked and not is_address_like and not has_other_intent and not is_subordinate:
                proposal.full_name = clean_text
                proposal.field_intents["full_name"] = "set"
                notes.append(f"recorded your name as {clean_text}")

    def _extract_address(
        self,
        text: str,
        lower: str,
        current_state: PersonalWishesState,
        proposal: StateProposal,
        notes: List[str]
    ) -> None:
        addr_match = re.search(
            r"\b(?:change\s+(?:my\s+)?address\s+to|update\s+(?:my\s+)?address\s+to|correct\s+(?:my\s+)?address\s+to|actually\s+my\s+address\s+is|my\s+address\s+is\s+now|my\s+address\s+is|i\s+live\s+(?:at|in)|live\s+(?:at|in)|living\s+(?:at|in)|based\s+in|located\s+in|address\s+is|address:?)\s+(.+)",
            text,
            re.IGNORECASE
        )
        addr_delim = r"\b(?:and\s+my\s+executor|my\s+executor|and\s+i\s+appoint|appoint\s+my|executor\s+is|and\s+worldwide|worldwide\s+assets?|and\s+covers\s+worldwide|covers\s+worldwide|worldwide|domestic|and\s+my\s+name|my\s+name\s+is|my\s+name|and\s+i\s+have|and\s+no\s+children|no\s+children|no\s+kids|and\s+i\s+am|i\s+am|and\s+also\s+i\s+want|also\s+i\s+want|and\s+my\s+wish\s+is|my\s+wish\s+is|and\s+please\s+note|please\s+note)\b"

        if addr_match:
            raw_address = addr_match.group(1).strip()
            raw_address = re.split(addr_delim, raw_address, flags=re.IGNORECASE)[0].strip(" ,.")
            proposal.home_address = re.sub(r"[.\s]+$", "", raw_address)
            proposal.field_intents["home_address"] = "correct" if current_state.home_address else "set"
            notes.append(f"updated your address to {proposal.home_address}")
        elif (
            current_state.full_name is not None
            and current_state.home_address is None
            and not proposal.full_name
            and not any(k in lower for k in ["yes", "no", "executor", "worldwide", "children", "gift"])
        ):
            clean_addr = text.strip(" .,")
            if 2 <= len(clean_addr) <= 100:
                proposal.home_address = clean_addr
                proposal.field_intents["home_address"] = "set"
                notes.append(f"updated your address to {clean_addr}")

    def _extract_worldwide_assets(
        self,
        text: str,
        lower: str,
        last_bot_prompt: str,
        current_state: PersonalWishesState,
        proposal: StateProposal,
        notes: List[str]
    ) -> None:
        if "worldwide" in lower or "global" in lower or "all assets" in lower:
            if "not worldwide" in lower or "no worldwide" in lower:
                proposal.covers_worldwide_assets = False
                proposal.field_intents["covers_worldwide_assets"] = "correct" if current_state.covers_worldwide_assets is not None else "set"
                notes.append("recorded coverage as domestic only")
            else:
                proposal.covers_worldwide_assets = True
                proposal.field_intents["covers_worldwide_assets"] = "correct" if current_state.covers_worldwide_assets is not None else "set"
                notes.append("confirmed worldwide asset coverage")
        elif "domestic" in lower or "local" in lower or "uk only" in lower or "india only" in lower:
            proposal.covers_worldwide_assets = False
            proposal.field_intents["covers_worldwide_assets"] = "correct" if current_state.covers_worldwide_assets is not None else "set"
            notes.append("recorded coverage as domestic only")
        elif "worldwide" in last_bot_prompt and current_state.covers_worldwide_assets is None:
            if re.search(r"\b(yes|yeah|yep|sure|worldwide|all)\b", lower):
                proposal.covers_worldwide_assets = True
                proposal.field_intents["covers_worldwide_assets"] = "set"
                notes.append("confirmed worldwide asset coverage")
            elif re.search(r"\b(no|nope|domestic|local|only domestic)\b", lower):
                proposal.covers_worldwide_assets = False
                proposal.field_intents["covers_worldwide_assets"] = "set"
                notes.append("recorded coverage as domestic only")

    def _extract_children(
        self,
        text: str,
        lower: str,
        bot_question: str,
        is_asking_children: bool,
        is_asking_child_names: bool,
        current_state: PersonalWishesState,
        proposal: StateProposal,
        notes: List[str]
    ) -> None:
        has_no_children_phrase = bool(re.search(r"\b(no children|don't have children|do not have kids|no kids|no child)\b", lower))

        if has_no_children_phrase:
            proposal.has_children = False
            proposal.children_names = []
            proposal.field_intents["has_children"] = "correct" if current_state.has_children is not None else "set"
            proposal.field_intents["children_names"] = "correct" if current_state.children_names else "set"
            notes.append("noted that you do not have children")
        elif is_asking_child_names and not proposal.full_name:
            raw_names_str = text.strip(" .")
            raw_names_str = re.split(r"\b(?:and my|my executor|and i|i live)\b", raw_names_str, flags=re.IGNORECASE)[0].strip()
            if "," in raw_names_str or re.search(r"\b(and|&)\b", raw_names_str, re.IGNORECASE):
                raw_names = re.split(r",|\band\b|&", raw_names_str, flags=re.IGNORECASE)
            else:
                raw_names = raw_names_str.split()

            cleaned_names = [n.strip(" .\"'") for n in raw_names if n.strip(" .\"'") and n.strip(" .\"'").lower() not in {"and", "&"}]
            if cleaned_names:
                proposal.has_children = True
                proposal.children_names = cleaned_names
                proposal.field_intents["has_children"] = "correct" if current_state.has_children is not None else "set"
                proposal.field_intents["children_names"] = "correct" if current_state.children_names else "set"
                notes.append(f"recorded children: {', '.join(cleaned_names)}")
        else:
            kids_match = re.search(
                r"(?:their names are|names are|names:?|children are|kids are|have\s+(?:a|\d+|one|two|three|four|five|several)?\s*(?:children|kids|child)?\s*(?:named|called))\s+([A-Za-z,\s&]+)",
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
                    proposal.field_intents["has_children"] = "correct" if current_state.has_children is not None else "set"
                    proposal.field_intents["children_names"] = "correct" if current_state.children_names else "set"
                    notes.append(f"recorded children: {', '.join(cleaned_names)}")
            elif is_asking_children and current_state.has_children is None:
                if re.search(r"\b(no|none|dont|do not|zero)\b", lower):
                    proposal.has_children = False
                    proposal.children_names = []
                    proposal.field_intents["has_children"] = "set"
                    proposal.field_intents["children_names"] = "set"
                    notes.append("noted that you do not have children")
                elif re.search(r"\b(yes|yeah|yep|i do|i have)\b", lower):
                    proposal.has_children = True
                    proposal.field_intents["has_children"] = "set"
                    notes.append("noted that you have children")

    def _extract_executor(
        self,
        text: str,
        lower: str,
        bot_question: str,
        is_asking_gifts: bool,
        is_asking_wishes: bool,
        is_asking_children: bool,
        current_state: PersonalWishesState,
        proposal: StateProposal,
        notes: List[str]
    ) -> None:
        is_asking_executor = (
            ("executor" in bot_question or "relationship to" in bot_question or "who would you like to appoint" in bot_question or ("full legal name" in bot_question and current_state.executor.relationship is not None))
            and not is_asking_gifts
            and not is_asking_wishes
            and (current_state.executor.name is None or current_state.executor.relationship is None or current_state.get_field_status("executor_name") != "confirmed" or current_state.get_field_status("executor_relationship") != "confirmed")
        )
        has_explicit_executor = bool(
            re.search(r"\b(?:executor|appoint(?:ing|ed|s)?)\b", lower)
            or (any(r in lower for r in RELATIONSHIP_TERMS) and not is_asking_gifts and not is_asking_wishes and not is_asking_children)
        )
        can_process_executor = has_explicit_executor or (is_asking_executor and not proposal.full_name)

        if not can_process_executor:
            return

        if re.search(r"\b(either\b.*\bor\b|\bor\b)", text, re.IGNORECASE) and ("executor" in lower or any(r in lower for r in RELATIONSHIP_TERMS)):
            proposal.executor = None
            notes.append("detected ambiguity between multiple candidates; please choose one executor")
            return

        if re.search(r"\b(be my own executor|appoint myself|myself as executor)\b", lower) or (
            (current_state.full_name and current_state.full_name.lower() in lower and "executor" in lower)
            or (proposal.full_name and proposal.full_name.lower() in lower and "executor" in lower and any(k in lower for k in ["myself", "own"]))
        ):
            proposal.executor = None
            proposal.field_statuses = {"executor_name": "unconfirmed"}
            notes.append("you cannot appoint yourself as executor; please name a third party")
            return

        if ("relationship to" in bot_question) and current_state.executor.relationship is None:
            rel_search = re.search(RELATIONSHIP_PATTERN, text, re.IGNORECASE)
            if rel_search:
                found_rel = rel_search.group(1).lower()
                proposal.executor = ExecutorProposal(name=current_state.executor.name, relationship=found_rel)
                proposal.field_intents["executor_relationship"] = "set"
                notes.append(f"recorded relationship as {found_rel}")
            return

        if (
            ("full legal name" in bot_question and current_state.executor.relationship is not None and current_state.executor.name is None)
            or (re.search(r"\b(?:executor'?s?\s+name|his\s+name|her\s+name)\b", lower))
        ):
            name_clause_match = re.search(
                r"\b(?:(?:executor|brother|sister|friend|lawyer|solicitor|partner|spouse|he|him|his|she|her)'?s?\s+name\s+is|name\s+is|named|is|called)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
                text,
                re.IGNORECASE
            )
            if name_clause_match:
                clean_name = name_clause_match.group(1).strip(" .")
            else:
                words = [w for w in text.split() if w.lower() not in STOPWORDS and w.lower() not in RELATIONSHIP_TERMS]
                clean_name = " ".join(words).strip(" .") if words else text.strip(" .")

            rel_to_use = current_state.executor.relationship
            proposal.executor = ExecutorProposal(name=clean_name, relationship=rel_to_use)
            proposal.field_intents["executor_name"] = "correct" if current_state.executor.name else "set"
            notes.append(f"updated executor's name to {clean_name}" if current_state.executor.name else f"recorded executor's name as {clean_name}")
            return

        found_rel = None
        rel_search = re.search(RELATIONSHIP_PATTERN, text, re.IGNORECASE)
        if rel_search:
            found_rel = rel_search.group(1).lower()

        negated_name = None
        neg_match = re.search(r"\b(?:not|instead of)\s+([A-Za-z]+)\b", text, re.IGNORECASE)
        if neg_match:
            negated_name = neg_match.group(1).lower()

        exclude_words: Set[str] = set()
        active_name = proposal.full_name or current_state.full_name
        if active_name:
            exclude_words.update(re.findall(r"\b\w+\b", active_name.lower()))
        active_address = proposal.home_address or current_state.home_address
        if active_address:
            exclude_words.update(re.findall(r"\b\w+\b", active_address.lower()))

        exec_target_text = text
        exec_match = re.search(r"\b(?:executor|appoint|appointing)\b.*", text, re.IGNORECASE)
        if exec_match:
            exec_clause = exec_match.group(0)
            clause_delim = r"\b(?:and\s+i\s+live|i\s+live|and\s+my\s+address|my\s+address|and\s+my\s+name|my\s+name|and\s+covers|covers|cover|and\s+worldwide|worldwide|domestic|and\s+no\s+children|no\s+children|children|and\s+also\s+i\s+want|also\s+i\s+want|and\s+my\s+wish\s+is|my\s+wish\s+is|and\s+please\s+note|please\s+note)\b"
            exec_target_text = re.split(clause_delim, exec_clause, flags=re.IGNORECASE)[0]

        raw_tokens = [re.sub(r"[^\w]", "", w) for w in exec_target_text.split()]
        name_candidates = [
            w for w in raw_tokens
            if w and w.lower() not in STOPWORDS
            and w.lower() not in RELATIONSHIP_TERMS
            and w.lower() not in exclude_words
            and (not negated_name or w.lower() != negated_name)
        ]

        found_name = " ".join(name_candidates) if name_candidates else None
        if not found_name and is_asking_executor and not has_explicit_executor:
            clean_short = text.strip(" .,'\"")
            if 1 <= len(clean_short.split()) <= 4 and clean_short.lower() not in STOPWORDS:
                found_name = clean_short.title()

        if found_name or found_rel:
            rel_to_use = found_rel if found_rel else current_state.executor.relationship
            proposal.executor = ExecutorProposal(name=found_name, relationship=rel_to_use)
            if found_name:
                proposal.field_intents["executor_name"] = "correct" if current_state.executor.name else "set"
            if found_rel:
                proposal.field_intents["executor_relationship"] = "correct" if current_state.executor.relationship else "set"

            if found_name and found_rel:
                notes.append(f"updated executor to {found_name} ({found_rel})" if current_state.executor.name else f"appointed {found_name} ({found_rel}) as executor")
            elif found_name:
                notes.append(f"updated executor's name to {found_name}" if current_state.executor.name else f"recorded executor name {found_name} (relationship pending)")
            elif found_rel:
                notes.append(f"updated executor relationship to {found_rel}" if current_state.executor.relationship else f"recorded executor as {found_rel} (name pending)")

    def _extract_gifts(
        self,
        text: str,
        lower: str,
        bot_question: str,
        is_asking_wishes: bool,
        current_state: PersonalWishesState,
        proposal: StateProposal,
        notes: List[str]
    ) -> None:
        is_asking_gifts = bool("gift" in bot_question or "bequest" in bot_question or "skip this" in bot_question)

        if is_asking_gifts and not is_asking_wishes and "has_specific_gifts" not in proposal.field_intents:
            if re.search(r"\b(no|none|skip|nope|nothing|no gifts?)\b", lower):
                proposal.has_specific_gifts = False
                proposal.specific_gifts = []
                proposal.field_intents["has_specific_gifts"] = "correct" if current_state.has_specific_gifts is not None else "set"
                notes.append("noted no specific gifts")
            else:
                clean_gift = text.strip(" .\"'")
                proposal.has_specific_gifts = True
                proposal.specific_gifts = [clean_gift]
                proposal.field_intents["has_specific_gifts"] = "correct" if current_state.has_specific_gifts is not None else "set"
                proposal.field_intents["specific_gifts"] = "correct" if current_state.specific_gifts else "set"
                notes.append(f"recorded specific gift: {clean_gift}")
        elif ("gift" in lower or "leave my" in lower or "bequeath" in lower) and not is_asking_wishes and "has_specific_gifts" not in proposal.field_intents:
            gift_match = re.search(r"(?:leave|gift|bequeath)\s+(.*)", text, re.IGNORECASE)
            if gift_match:
                clean_gift = gift_match.group(1).strip(" .\"'")
                proposal.has_specific_gifts = True
                proposal.specific_gifts = [clean_gift]
                proposal.field_intents["has_specific_gifts"] = "correct" if current_state.has_specific_gifts is not None else "set"
                proposal.field_intents["specific_gifts"] = "correct" if current_state.specific_gifts else "set"
                notes.append(f"recorded specific gift: {clean_gift}")

    def _extract_additional_wishes(
        self,
        text: str,
        lower: str,
        bot_question: str,
        is_asking_gifts: bool,
        is_asking_wishes: bool,
        is_correction_for_other_field: bool,
        current_state: PersonalWishesState,
        proposal: StateProposal,
        notes: List[str]
    ) -> None:
        other_fields = [k for k in proposal.field_intents if k != "additional_wishes"]

        change_wishes_match = re.search(
            r"\b(?:change|update|correct)\s+(?:my\s+)?(?:additional\s+)?wishes\s+to:?\s*(.+)",
            text,
            re.IGNORECASE
        )
        extra_wish_match = re.search(
            r"\b(?:and\s+also\s+i\s+want|also\s+i\s+want|and\s+my\s+wish\s+is|my\s+wish\s+is|and\s+please\s+note|please\s+note)\s+(.+)",
            text,
            re.IGNORECASE
        )

        if change_wishes_match:
            clean_wish = change_wishes_match.group(1).strip(" .\"'")
            proposal.additional_wishes = clean_wish
            proposal.field_intents["additional_wishes"] = "correct"
            notes.append("updated your additional wishes")
        elif extra_wish_match:
            clean_wish = extra_wish_match.group(1).strip(" .\"'")
            proposal.additional_wishes = clean_wish
            proposal.field_intents["additional_wishes"] = "append"
            notes.append("recorded additional wishes")
        elif len(other_fields) == 0 and not is_correction_for_other_field:
            if is_asking_wishes and "additional_wishes" not in proposal.field_intents:
                if re.search(r"\b(no|none|skip|nothing|no wishes|nope)\b", lower):
                    proposal.additional_wishes = "None"
                    proposal.field_intents["additional_wishes"] = "correct" if current_state.additional_wishes is not None else "set"
                    notes.append("noted no additional wishes")
                else:
                    proposal.additional_wishes = text.strip(" .\"'")
                    proposal.field_intents["additional_wishes"] = "correct" if current_state.additional_wishes is not None else "set"
                    notes.append("recorded additional wishes")
            elif any(k in lower for k in ["cremat", "burial", "funeral", "scatter", "ashes", "charity donation", "charity", "additional wish"]) and not is_asking_gifts and "additional_wishes" not in proposal.field_intents:
                proposal.additional_wishes = text.strip(" .\"'")
                proposal.field_intents["additional_wishes"] = "correct" if current_state.additional_wishes is not None else "set"
                notes.append("recorded additional wishes")

    def _get_next_question(self, state: PersonalWishesState) -> str:
        # Prompt for clarifications on unconfirmed items first
        if state.get_field_status("has_children") == "unconfirmed" or state.get_field_status("children_names") == "unconfirmed":
            return "Could you please clarify whether you have children, and if so, what their names are?"
        if state.get_field_status("executor_name") == "unconfirmed" or state.get_field_status("executor_relationship") == "unconfirmed":
            return "Could you please clarify the full legal name and relationship of your appointed executor?"
        if state.get_field_status("home_address") == "unconfirmed":
            return "Could you please clarify your residential address?"
        if state.get_field_status("full_name") == "unconfirmed":
            return "Could you please clarify your full legal name?"
        if state.get_field_status("covers_worldwide_assets") == "unconfirmed":
            return "Could you please clarify if this document covers assets worldwide or domestic only?"

        # Advance to uncollected intake fields in structured interview sequence
        if not state.full_name or state.get_field_status("full_name") != "confirmed":
            return "Could you please tell me your full legal name?"
        if not state.home_address or state.get_field_status("home_address") != "confirmed":
            return f"Thank you, {state.full_name}. What is your current residential address?"
        if state.covers_worldwide_assets is None or state.get_field_status("covers_worldwide_assets") != "confirmed":
            return "Should this document cover assets worldwide, or only domestic assets?"
        if state.has_children is None or state.get_field_status("has_children") != "confirmed":
            return "Do you have any children?"
        if state.has_children and (not state.children_names or state.get_field_status("children_names") != "confirmed"):
            return "Could you list the names of your children?"
        if not state.executor.name and not state.executor.relationship:
            return "Who would you like to appoint as the executor of your wishes?"
        if state.executor.name and not state.executor.relationship:
            return f"What is your legal or personal relationship to {state.executor.name} (e.g., brother, friend, solicitor)?"
        if state.executor.relationship and not state.executor.name:
            return f"What is your {state.executor.relationship}'s full legal name?"
        if state.has_specific_gifts is None or state.get_field_status("has_specific_gifts") != "confirmed":
            return "Do you have any specific gifts you'd like to leave (e.g. heirloom, car), or would you like to skip this?"
        if state.additional_wishes is None or state.get_field_status("additional_wishes") != "confirmed":
            return "Do you have any additional wishes, such as funeral instructions or personal notes?"

        return "Your draft Personal Wishes Document is complete! Feel free to review the preview or make any corrections."
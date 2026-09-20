from app.domain.state import PersonalWishesState

class DocumentGenerator:
    DISCLAIMER = "> **DISCLAIMER: This document is entirely fictional and for demonstration purposes only. It does not constitute legal advice.**\n\n"

    @classmethod
    def generate(cls, state: PersonalWishesState) -> str:
        doc = [cls.DISCLAIMER]
        doc.append("# Personal Wishes Document\n")

        name_str = state.full_name if state.full_name else "[Full Name Pending]"
        address_str = state.home_address if state.home_address else "[Address Pending]"
        doc.append(f"**Principal:** {name_str}  \n**Address:** {address_str}\n")

        doc.append("## 1. Scope of Assets")
        if state.covers_worldwide_assets is True:
            doc.append("This document expresses wishes covering assets situated globally and worldwide.")
        elif state.covers_worldwide_assets is False:
            doc.append("This document applies solely to domestic/local assets.")
        else:
            doc.append("*Scope of assets has not been determined.*")
        doc.append("")

        doc.append("## 2. Family & Dependents")
        if state.has_children is True:
            if state.children_names:
                children_list = ", ".join(state.children_names)
                doc.append(f"The principal has children: {children_list}.")
            else:
                doc.append("The principal has confirmed having children. (Names pending).")
        elif state.has_children is False:
            doc.append("The principal has no children.")
        else:
            doc.append("*Family information not yet recorded.*")
        doc.append("")

        doc.append("## 3. Executor Appointment")
        exec_name = state.executor.name or "[Pending]"
        exec_rel = f" ({state.executor.relationship})" if state.executor.relationship else ""
        doc.append(f"**Appointed Executor:** {exec_name}{exec_rel}\n")

        doc.append("## 4. Specific Gifts")
        valid_gifts = [g for g in state.specific_gifts if g and g.lower() != "none"]
        if valid_gifts:
            for gift in valid_gifts:
                doc.append(f"- {gift}")
        else:
            doc.append("No specific gifts declared.")
        doc.append("")

        doc.append("## 5. Additional Wishes")
        if state.additional_wishes:
            doc.append(state.additional_wishes)
        else:
            doc.append("No additional wishes specified.")
        doc.append("")

        return "\n".join(doc)
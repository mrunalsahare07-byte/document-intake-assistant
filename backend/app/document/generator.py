from app.domain.state import PersonalWishesState


class DocumentGenerator:
    DISCLAIMER = "> **DISCLAIMER: This document is for personal record-keeping only and does not constitute formal legal advice.**\n\n"

    @classmethod
    def generate(cls, state: PersonalWishesState) -> str:
        doc = [cls.DISCLAIMER]
        doc.append("# Personal Wishes Document\n")

        # Principal details
        name_status = state.get_field_status("full_name")
        if name_status == "unconfirmed":
            name_str = f"{state.full_name} [Unconfirmed]" if state.full_name else "[Unconfirmed]"
        elif name_status == "unknown" or not state.full_name:
            name_str = "[Not provided]"
        else:
            name_str = state.full_name

        addr_status = state.get_field_status("home_address")
        if addr_status == "unconfirmed":
            address_str = f"{state.home_address} [Unconfirmed]" if state.home_address else "[Unconfirmed]"
        elif addr_status == "unknown" or not state.home_address:
            address_str = "[Not provided]"
        else:
            address_str = state.home_address

        doc.append(f"**Principal:** {name_str}  \n**Address:** {address_str}\n")

        # Section 1: Scope of Assets
        doc.append("## 1. Scope of Assets")
        asset_status = state.get_field_status("covers_worldwide_assets")
        if asset_status == "unconfirmed":
            if state.covers_worldwide_assets is True:
                doc.append("This document expresses wishes covering assets situated globally and worldwide. [Unconfirmed]")
            elif state.covers_worldwide_assets is False:
                doc.append("This document applies solely to domestic/local assets. [Unconfirmed]")
            else:
                doc.append("[Unconfirmed]")
        elif asset_status == "unknown" or state.covers_worldwide_assets is None:
            doc.append("[Not provided]")
        elif state.covers_worldwide_assets is True:
            doc.append("This document expresses wishes covering assets situated globally and worldwide.")
        else:
            doc.append("This document applies solely to domestic/local assets.")
        doc.append("")

        # Section 2: Family & Dependents
        doc.append("## 2. Family & Dependents")
        kids_status = state.get_field_status("has_children")
        if kids_status == "unconfirmed":
            if state.has_children is True:
                c_names = ", ".join(state.children_names) if state.children_names else "[Names unconfirmed]"
                doc.append(f"The principal has children: {c_names}. [Unconfirmed]")
            elif state.has_children is False:
                doc.append("The principal has no children. [Unconfirmed]")
            else:
                doc.append("[Unconfirmed]")
        elif kids_status == "unknown" or state.has_children is None:
            doc.append("[Not provided]")
        elif state.has_children is False:
            doc.append("The principal has no children.")
        else:
            names_status = state.get_field_status("children_names")
            if state.children_names:
                c_names = ", ".join(state.children_names)
                suffix = " [Unconfirmed]" if names_status == "unconfirmed" else ""
                doc.append(f"The principal has children: {c_names}.{suffix}")
            else:
                doc.append("The principal has confirmed having children. [Not provided]")
        doc.append("")

        # Section 3: Executor Appointment
        doc.append("## 3. Executor Appointment")
        exec_name_status = state.get_field_status("executor_name")
        if exec_name_status == "unconfirmed":
            exec_name = f"{state.executor.name} [Unconfirmed]" if state.executor.name else "[Unconfirmed]"
        elif exec_name_status == "unknown" or not state.executor.name:
            exec_name = "[Not provided]"
        else:
            exec_name = state.executor.name

        exec_rel_status = state.get_field_status("executor_relationship")
        if state.executor.relationship:
            suffix = " [Unconfirmed]" if exec_rel_status == "unconfirmed" else ""
            exec_rel = f" ({state.executor.relationship}{suffix})"
        else:
            exec_rel = ""
        doc.append(f"**Appointed Executor:** {exec_name}{exec_rel}\n")

        # Section 4: Specific Gifts & Bequests
        doc.append("## 4. Specific Gifts")
        gifts_status = state.get_field_status("has_specific_gifts")
        valid_gifts = [g for g in state.specific_gifts if g and g.lower() != "none"]
        if gifts_status == "unconfirmed":
            if valid_gifts:
                for gift in valid_gifts:
                    doc.append(f"- {gift} [Unconfirmed]")
            else:
                doc.append("[Unconfirmed]")
        elif gifts_status == "unknown" and not valid_gifts:
            doc.append("[Not provided]")
        elif state.has_specific_gifts is False or not valid_gifts:
            doc.append("No specific gifts declared.")
        else:
            for gift in valid_gifts:
                doc.append(f"- {gift}")
        doc.append("")

        # Section 5: Additional Wishes
        doc.append("## 5. Additional Wishes")
        wishes_status = state.get_field_status("additional_wishes")
        if wishes_status == "unconfirmed":
            doc.append(f"{state.additional_wishes} [Unconfirmed]" if state.additional_wishes else "[Unconfirmed]")
        elif wishes_status == "unknown" and not state.additional_wishes:
            doc.append("[Not provided]")
        elif state.additional_wishes and state.additional_wishes.lower() != "none":
            doc.append(state.additional_wishes)
        else:
            doc.append("No additional wishes specified.")
        doc.append("")

        return "\n".join(doc)
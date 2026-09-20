export interface Beneficiary {
  name: string;
  relationship: string;
  allocation_percent?: number | null;
}
export interface Guardian {
  name: string;
  relationship: string;
}
export type MaritalStatus = "single" | "married" | "divorced" | "widowed" | "partnered";
export type FinalArrangement = "burial" | "cremation" | "undecided";
export interface PersonalWishesState {
  full_name: string | null;
  date_of_birth: string | null;
  marital_status: MaritalStatus | null;
  beneficiaries: Beneficiary[];
  guardians_for_children: Guardian[];
  final_arrangement: FinalArrangement | null;
  final_arrangement_details: string | null;
  organ_donor: boolean | null;
  personal_message: string | null;
  special_instructions: string | null;
  executor_name: string | null;
  executor_relationship: string | null;
}
export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}
export interface ConversationResponse {
  session_id: string;
  assistant_message: string;
  state: PersonalWishesState;
  history: ChatTurn[];
  is_complete: boolean;
  missing_fields: string[];
  document_markdown: string;
  disclaimer: string;
}
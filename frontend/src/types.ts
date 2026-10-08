export interface Executor {
  name: string | null;
  relationship: string | null;
}

export type FieldStatus = "unknown" | "unconfirmed" | "confirmed";

export interface PersonalWishesState {
  full_name: string | null;
  home_address: string | null;
  covers_worldwide_assets: boolean | null;
  has_children: boolean | null;
  children_names: string[];
  executor: Executor;
  has_specific_gifts?: boolean | null;
  specific_gifts: string[];
  additional_wishes: string | null;
  field_statuses?: Record<string, FieldStatus>;
}

// Backward compatibility alias for components
export type IntakeState = PersonalWishesState;

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
  text?: string;
  timestamp?: string;
  validatedFields?: string[];
}

export interface ApiError {
  code: string;
  message: string;
}

export interface ConversationResponse {
  session_id?: string;
  assistant_message?: string;
  state: PersonalWishesState;
  history: ChatTurn[];
  is_complete: boolean;
  missing_fields: string[];
  document?: string;
  document_markdown: string;
  disclaimer: string;
  error?: ApiError | null;
}

export type StatusType = "connected" | "processing" | "draft" | "confirmed" | "needs_review" | "error" | "saved" | "idle";
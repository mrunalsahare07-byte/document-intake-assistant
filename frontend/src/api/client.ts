/**
 * Thin API client for the Document Intake Assistant backend. All HTTP
 * concerns (base URL, JSON parsing) are isolated here so components never
 * call fetch() directly.
 */
import type { ConversationResponse } from "../types";

const BASE_URL = "/api";

async function postJSON<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`Request to ${url} failed with status ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  sendMessage(sessionId: string, message: string): Promise<ConversationResponse> {
    return postJSON(`${BASE_URL}/chat`, { session_id: sessionId, message });
  },

  getState(sessionId: string): Promise<ConversationResponse> {
    return fetch(`${BASE_URL}/state/${sessionId}`).then((r) => r.json());
  },

  correctField(sessionId: string, fieldName: string, value: unknown): Promise<ConversationResponse> {
    return postJSON(`${BASE_URL}/correct`, { session_id: sessionId, field_name: fieldName, value });
  },

  resetSession(sessionId: string): Promise<ConversationResponse> {
    return fetch(`${BASE_URL}/reset/${sessionId}`, { method: "POST" }).then((r) => r.json());
  },
};


/**
 * Thin API client for the Document Intake Assistant backend. All HTTP
 * concerns (base URL, JSON parsing) are isolated here so components never
 * call fetch() directly.
 */
import type { ConversationResponse } from "../types";

const BASE_URL = "/api";

export interface ApiClientError extends Error {
  status?: number;
}

async function postJSON<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const error: ApiClientError = new Error(`Request to ${url} failed with status ${res.status}`);
    error.status = res.status;
    throw error;
  }
  return res.json() as Promise<T>;
}

export const api = {
  sendMessage(sessionId: string | undefined, message: string): Promise<ConversationResponse> {
    const body: { message: string; session_id?: string } = { message };
    if (sessionId) {
      body.session_id = sessionId;
    }
    return postJSON(`${BASE_URL}/chat`, body);
  },

  async getState(sessionId: string): Promise<ConversationResponse> {
    const res = await fetch(`${BASE_URL}/state/${sessionId}`);
    if (!res.ok) {
      const error: ApiClientError = new Error(`Request to ${BASE_URL}/state/${sessionId} failed with status ${res.status}`);
      error.status = res.status;
      throw error;
    }
    return res.json();
  },

  correctField(sessionId: string, fieldName: string, value: unknown): Promise<ConversationResponse> {
    return postJSON(`${BASE_URL}/correct`, { session_id: sessionId, field_name: fieldName, value });
  },

  async resetSession(sessionId: string): Promise<ConversationResponse> {
    const res = await fetch(`${BASE_URL}/reset/${sessionId}`, { method: "POST" });
    if (!res.ok) {
      const error: ApiClientError = new Error(`Request to reset ${sessionId} failed with status ${res.status}`);
      error.status = res.status;
      throw error;
    }
    return res.json();
  },

  async deleteSession(sessionId: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/sessions/${sessionId}`, { method: "DELETE" });
    if (!res.ok) {
      const error: ApiClientError = new Error(`Request to delete ${sessionId} failed with status ${res.status}`);
      error.status = res.status;
      throw error;
    }
  },
};

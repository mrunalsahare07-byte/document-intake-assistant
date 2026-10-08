import { useCallback, useEffect, useState, useRef } from "react";
import {
  Box,
  useMediaQuery,
  useTheme,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from "@mui/material";
import { AppShell } from "./components/layout/AppShell";
import { ChatPanel } from "./components/chat/ChatPanel";
import { StatePreviewPanel } from "./components/state/StatePreviewPanel";
import { DocumentPreviewPanel } from "./components/document/DocumentPreviewPanel";
import { ErrorState } from "./components/common/ErrorState";
import { Button } from "./components/common/Button";
import { api } from "./api/client";
import type { ConversationResponse } from "./types";
import type { SessionItem } from "./components/layout/Sidebar";

const SESSION_ID_KEY = "dia_session_id";
const SESSIONS_STORAGE_KEY = "dia_sessions_metadata";

function getStoredSessions(): SessionItem[] {
  try {
    const raw = localStorage.getItem(SESSIONS_STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw);
    }
  } catch (e) {
    console.error("Failed to parse sessions", e);
  }
  return [];
}

function saveSessions(sessions: SessionItem[]) {
  try {
    localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(sessions));
  } catch (e) {
    console.error("Failed to save sessions", e);
  }
}

export default function App() {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down("lg"));

  const [sessions, setSessions] = useState<SessionItem[]>(() => {
    const stored = getStoredSessions();
    if (stored.length === 0) {
      const initialId = crypto.randomUUID();
      const initial: SessionItem = {
        id: initialId,
        name: "Intake #1",
        date: new Date().toLocaleDateString(undefined, { month: "short", day: "numeric" }),
        isInitialized: false,
      };
      saveSessions([initial]);
      localStorage.setItem(SESSION_ID_KEY, initialId);
      return [initial];
    }
    return stored;
  });

  const [sessionId, setSessionId] = useState<string>(() => {
    const storedId = localStorage.getItem(SESSION_ID_KEY);
    const stored = getStoredSessions();
    if (storedId && stored.some((s) => s.id === storedId)) {
      return storedId;
    }
    return stored[0]?.id || "";
  });

  const [conversation, setConversation] = useState<ConversationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [error, setError] = useState<{ title: string; message: string; details?: string } | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  // Delete confirmation dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const deleteTriggerRef = useRef<HTMLElement | null>(null);
  const cancelButtonRef = useRef<HTMLButtonElement | null>(null);

  // Remove a session from state, localStorage, and handle fallback
  const removeSession = useCallback(
    (targetId: string) => {
      setSessions((prev) => {
        const remaining = prev.filter((s) => s.id !== targetId);
        saveSessions(remaining);

        if (targetId === sessionId) {
          // Clear chat, state preview, and document preview so no stale data shows
          setConversation(null);
          if (remaining.length > 0) {
            const nextSession = remaining[0];
            setSessionId(nextSession.id);
            localStorage.setItem(SESSION_ID_KEY, nextSession.id);
          } else {
            // No sessions remain: start a new empty session
            const newId = crypto.randomUUID();
            const newSessionItem: SessionItem = {
              id: newId,
              name: "Intake #1",
              date: new Date().toLocaleDateString(undefined, { month: "short", day: "numeric" }),
              isInitialized: false,
            };
            saveSessions([newSessionItem]);
            localStorage.setItem(SESSION_ID_KEY, newId);
            setSessionId(newId);
            return [newSessionItem];
          }
        }
        return remaining;
      });
    },
    [sessionId]
  );

  // Load conversation state for active session
  const loadState = useCallback(
    async (sid: string) => {
      if (!sid) {
        setConversation(null);
        return;
      }

      const currentItem = sessions.find((s) => s.id === sid);
      if (currentItem && currentItem.isInitialized === false) {
        // Brand new session not yet sent to backend
        setConversation(null);
        return;
      }

      try {
        setError(null);
        const resp = await api.getState(sid);
        setConversation(resp);
      } catch (err: any) {
        if (err?.status === 404 || err?.message?.includes("404")) {
          // If any call returns 404 for active session, clear stale data, drop id, start new empty session
          removeSession(sid);
          return;
        }
        console.error(err);
        setError({
          title: "Connection Error",
          message: "Unable to load session state from intake engine.",
          details: err?.message || String(err),
        });
      }
    },
    [sessions, removeSession]
  );

  useEffect(() => {
    loadState(sessionId);
  }, [sessionId, loadState]);

  // Update session metadata name when principal name becomes known
  useEffect(() => {
    if (conversation?.state.full_name) {
      const principalName = conversation.state.full_name;
      setSessions((prev) => {
        const next = prev.map((s) => {
          if (s.id === sessionId) {
            return {
              ...s,
              name: `${principalName}`,
              isComplete: conversation.is_complete,
              isInitialized: true,
            };
          }
          return s;
        });
        saveSessions(next);
        return next;
      });
    }
  }, [conversation?.state.full_name, conversation?.is_complete, sessionId]);

  const handleSend = useCallback(
    async (message: string) => {
      setLoading(true);
      setError(null);
      try {
        const currentItem = sessions.find((s) => s.id === sessionId);
        const sendSid = currentItem && currentItem.isInitialized === false ? undefined : sessionId;
        const resp = await api.sendMessage(sendSid, message);

        if (resp.session_id && currentItem && currentItem.isInitialized === false) {
          const backendId = resp.session_id;
          setSessionId(backendId);
          localStorage.setItem(SESSION_ID_KEY, backendId);
          setSessions((prev) => {
            const next = prev.map((s) => {
              if (s.id === sessionId) {
                return {
                  ...s,
                  id: backendId,
                  isInitialized: true,
                  name: resp.state.full_name || s.name,
                  isComplete: resp.is_complete,
                };
              }
              return s;
            });
            saveSessions(next);
            return next;
          });
        }
        setConversation(resp);
      } catch (err: any) {
        if (err?.status === 404 || err?.message?.includes("404")) {
          removeSession(sessionId);
          return;
        }
        console.error(err);
        setError({
          title: "Message Transmission Failed",
          message: "The intake assistant was unable to process your message.",
          details: err?.message || String(err),
        });
      } finally {
        setLoading(false);
      }
    },
    [sessionId, sessions, removeSession]
  );

  const handleReset = useCallback(async () => {
    const currentItem = sessions.find((s) => s.id === sessionId);
    if (currentItem && currentItem.isInitialized === false) {
      setConversation(null);
      return;
    }
    setResetLoading(true);
    setError(null);
    try {
      const resp = await api.resetSession(sessionId);
      setConversation(resp);
    } catch (err: any) {
      if (err?.status === 404 || err?.message?.includes("404")) {
        removeSession(sessionId);
        return;
      }
      console.error(err);
      setError({
        title: "Reset Failed",
        message: "Unable to reset the intake session on backend.",
        details: err?.message || String(err),
      });
    } finally {
      setResetLoading(false);
    }
  }, [sessionId, sessions, removeSession]);

  const handleNewIntake = useCallback(() => {
    const newId = crypto.randomUUID();
    const count = sessions.length + 1;
    const newSessionItem: SessionItem = {
      id: newId,
      name: `Intake #${count}`,
      date: new Date().toLocaleDateString(undefined, { month: "short", day: "numeric" }),
      isInitialized: false,
    };

    const nextSessions = [newSessionItem, ...sessions];
    setSessions(nextSessions);
    saveSessions(nextSessions);

    localStorage.setItem(SESSION_ID_KEY, newId);
    setSessionId(newId);
    setConversation(null);
  }, [sessions]);

  const handleSelectSession = useCallback(
    (selectedId: string) => {
      if (selectedId === sessionId) return;
      localStorage.setItem(SESSION_ID_KEY, selectedId);
      setSessionId(selectedId);
      setConversation(null);
    },
    [sessionId]
  );

  const handleOpenDeleteDialog = useCallback((targetId: string, triggerEl?: HTMLElement) => {
    deleteTriggerRef.current = triggerEl ?? null;
    setSessionToDelete(targetId);
    setDeleteDialogOpen(true);
  }, []);

  const handleCloseDeleteDialog = useCallback(() => {
    if (isDeleting) return;
    setDeleteDialogOpen(false);
    setSessionToDelete(null);
    setTimeout(() => {
      deleteTriggerRef.current?.focus();
    }, 0);
  }, [isDeleting]);

  const handleConfirmDelete = useCallback(async () => {
    if (!sessionToDelete) return;
    setIsDeleting(true);
    try {
      await api.deleteSession(sessionToDelete);
      removeSession(sessionToDelete);
      setDeleteDialogOpen(false);
      setSessionToDelete(null);
      setTimeout(() => {
        deleteTriggerRef.current?.focus();
      }, 0);
    } catch (err: any) {
      if (err?.status === 404 || err?.message?.includes("404")) {
        // If DELETE returns 404 for an id in the list, remove it without error
        removeSession(sessionToDelete);
        setDeleteDialogOpen(false);
        setSessionToDelete(null);
        setTimeout(() => {
          deleteTriggerRef.current?.focus();
        }, 0);
      } else {
        setError({
          title: "Delete Failed",
          message: "Unable to delete the intake session.",
          details: err?.message || String(err),
        });
        setDeleteDialogOpen(false);
        setSessionToDelete(null);
      }
    } finally {
      setIsDeleting(false);
    }
  }, [sessionToDelete, removeSession]);

  const principalName = conversation?.state.full_name || "New Intake";

  return (
    <AppShell
      breadcrumb={principalName}
      subBreadcrumb="Personal wishes"
      isProcessing={loading}
      onReset={handleReset}
      resetLoading={resetLoading}
      onDeleteSession={handleOpenDeleteDialog}
      onDeleteCurrentSession={(triggerEl) => handleOpenDeleteDialog(sessionId, triggerEl)}
      sidebarCollapsed={sidebarCollapsed}
      onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
      currentSessionId={sessionId}
      sessions={sessions}
      onSelectSession={handleSelectSession}
      onNewIntake={handleNewIntake}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      isSmallScreen={isSmallScreen}
    >
      {error && (
        <ErrorState
          title={error.title}
          message={error.message}
          details={error.details}
          onRetry={() => loadState(sessionId)}
        />
      )}

      {/* Main Workspace Regions */}
      {isSmallScreen ? (
        // Mobile / Tablet Tabbed View
        <Box sx={{ height: "100%", width: "100%", overflow: "hidden" }}>
          {activeTab === 0 && (
            <ChatPanel
              history={conversation?.history ?? []}
              onSend={handleSend}
              loading={loading}
              apiError={conversation?.error}
            />
          )}
          {activeTab === 1 && (
            <StatePreviewPanel
              state={conversation?.state}
              missingFields={conversation?.missing_fields ?? []}
              isComplete={conversation?.is_complete ?? false}
              loading={loading}
            />
          )}
          {activeTab === 2 && (
            <DocumentPreviewPanel
              markdown={conversation?.document_markdown ?? conversation?.document ?? ""}
              disclaimer={
                conversation?.disclaimer ??
                "This document is prepared for personal documentation and does not constitute formal legal counsel."
              }
              isComplete={conversation?.is_complete ?? false}
              loading={loading}
            />
          )}
        </Box>
      ) : (
        // Desktop 3 Integrated Regions
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "36% 32% 32%",
            height: "100%",
            width: "100%",
            overflow: "hidden",
            backgroundColor: "var(--background)",
          }}
        >
          {/* Region 1: Conversation */}
          <Box sx={{ height: "100%", overflow: "hidden" }}>
            <ChatPanel
              history={conversation?.history ?? []}
              onSend={handleSend}
              loading={loading}
              apiError={conversation?.error}
            />
          </Box>

          {/* Region 2: Extracted Information */}
          <Box sx={{ height: "100%", overflow: "hidden" }}>
            <StatePreviewPanel
              state={conversation?.state}
              missingFields={conversation?.missing_fields ?? []}
              isComplete={conversation?.is_complete ?? false}
              loading={loading}
            />
          </Box>

          {/* Region 3: Generated Document */}
          <Box sx={{ height: "100%", overflow: "hidden" }}>
            <DocumentPreviewPanel
              markdown={conversation?.document_markdown ?? conversation?.document ?? ""}
              disclaimer={
                conversation?.disclaimer ??
                "This document is prepared for personal documentation and does not constitute formal legal counsel."
              }
              isComplete={conversation?.is_complete ?? false}
              loading={loading}
            />
          </Box>
        </Box>
      )}

      {/* Confirmation Dialog for Deleting Intake */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
        PaperProps={{
          sx: {
            backgroundColor: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-sm, 6px)",
            p: 1,
            minWidth: { xs: 280, sm: 360 },
          },
        }}
      >
        <DialogTitle
          id="delete-dialog-title"
          sx={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", pb: 1 }}
        >
          Delete this intake?
        </DialogTitle>
        <DialogContent>
          <DialogContentText
            id="delete-dialog-description"
            sx={{ fontSize: "14px", color: "var(--text-secondary)" }}
          >
            This permanently removes the collected information and the draft document. This cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 2, pb: 1.5, gap: 1 }}>
          <Button
            ref={cancelButtonRef}
            autoFocus
            variant="secondary"
            onClick={handleCloseDeleteDialog}
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button
            variant="secondary"
            onClick={handleConfirmDelete}
            disabled={isDeleting}
            loading={isDeleting}
            sx={{
              backgroundColor: "var(--surface-active, #334155)",
              color: "#FFFFFF",
              borderColor: "var(--border-strong, #475569)",
              "&:hover": {
                backgroundColor: "#1E293B",
                borderColor: "#334155",
              },
            }}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </AppShell>
  );
}

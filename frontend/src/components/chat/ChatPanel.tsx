import { useEffect, useRef } from "react";
import { Box, Typography } from "@mui/material";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import { Panel } from "../layout/Panel";
import { PanelHeader } from "../layout/PanelHeader";
import { ChatMessage } from "./ChatMessage";
import { ChatComposer } from "./ChatComposer";
import { EmptyState } from "../common/EmptyState";
import type { ChatTurn, ApiError } from "../../types";

interface ChatPanelProps {
  history: ChatTurn[];
  onSend: (message: string) => Promise<void>;
  loading: boolean;
  apiError?: ApiError | null;
}

export function ChatPanel({ history, onSend, loading, apiError }: ChatPanelProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [history, loading]);

  return (
    <Panel borderRight sx={{ height: "100%" }}>
      {/* Header */}
      <PanelHeader
        title="Conversation"
      />

      {/* Messages Stream */}
      <Box
        ref={scrollContainerRef}
        sx={{
          flexGrow: 1,
          overflowY: "auto",
          p: 2,
          display: "flex",
          flexDirection: "column",
          gap: 1.5,
        }}
      >
        {history.length === 0 ? (
          <EmptyState
            title="Start conversation"
            description="Enter your information or personal wishes to begin the intake process."
            action={
              <Box sx={{ display: "flex", flexDirection: "column", gap: 1, mt: 1, width: "100%" }}>
                <Box
                  onClick={() => onSend("My name is John Doe, living in San Francisco, CA.")}
                  sx={{
                    p: 1.25,
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius-xs)",
                    backgroundColor: "var(--surface)",
                    fontSize: "13px",
                    color: "var(--text-secondary)",
                    cursor: "pointer",
                    textAlign: "left",
                    transition: "border-color var(--transition-fast), background-color var(--transition-fast)",
                    "&:hover": {
                      borderColor: "var(--border-strong)",
                      color: "var(--text-primary)",
                      backgroundColor: "var(--surface-hover)",
                    },
                  }}
                >
                  <Typography sx={{ fontSize: "12px", color: "var(--text-secondary)", mb: 0.25 }}>
                    Example prompt:
                  </Typography>
                  "My name is John Doe, living in San Francisco, CA."
                </Box>
              </Box>
            }
          />
        ) : (
          history.map((turn, idx) => (
            <ChatMessage key={idx} turn={turn} index={idx} />
          ))
        )}

        {/* Phase 5 API Error Display */}
        {apiError && (
          <Box
            sx={{
              p: 1.5,
              borderRadius: "var(--radius-xs)",
              backgroundColor: "#FEF2F2",
              border: "1px solid #FCA5A5",
              display: "flex",
              alignItems: "flex-start",
              gap: 1.25,
            }}
          >
            <ErrorOutlineIcon sx={{ fontSize: 18, color: "#991B1B", mt: 0.2, flexShrink: 0 }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography sx={{ fontSize: "14px", fontWeight: 600, color: "#991B1B" }}>
                API Error: {apiError.code}
              </Typography>
              <Typography sx={{ fontSize: "13px", color: "#4B5563", mt: 0.25 }}>
                {apiError.message}
              </Typography>
            </Box>
          </Box>
        )}

        {/* Muted Text Typing Indicator */}
        {loading && (
          <Box
            sx={{
              py: 1,
              px: 0.5,
            }}
          >
            <Typography
              sx={{
                fontSize: "12px",
                color: "var(--text-secondary)",
              }}
            >
              Thinking...
            </Typography>
          </Box>
        )}
      </Box>

      {/* Composer */}
      <ChatComposer onSend={onSend} loading={loading} />
    </Panel>
  );
}

import { useCallback, useEffect, useState } from "react";
import { AppBar, Box, Button, Container, Grid, Toolbar, Typography, CssBaseline } from "@mui/material";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import { ChatPanel } from "./components/ChatPanel";
import { StatePreviewPanel } from "./components/StatePreviewPanel";
import { DocumentPreviewPanel } from "./components/DocumentPreviewPanel";
import { api } from "./api/client";
import type { ConversationResponse } from "./types";

const SESSION_ID_KEY = "dia_session_id";

function getOrCreateSessionId(): string {
  let id = localStorage.getItem(SESSION_ID_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(SESSION_ID_KEY, id);
  }
  return id;
}

/**
 * App: top-level application component. Owns the ConversationResponse
 * (the single source of truth received from the backend) and wires the
 * chat, state preview, and document preview panels together.
 */
export default function App() {
  const [sessionId] = useState(getOrCreateSessionId);
  const [conversation, setConversation] = useState<ConversationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getState(sessionId).then(setConversation).catch(console.error);
  }, [sessionId]);

  const handleSend = useCallback(
    async (message: string) => {
      setLoading(true);
      try {
        const resp = await api.sendMessage(sessionId, message);
        setConversation(resp);
      } finally {
        setLoading(false);
      }
    },
    [sessionId]
  );

  const handleReset = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await api.resetSession(sessionId);
      setConversation(resp);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  return (
    <>
      <CssBaseline />
      <AppBar position="static" color="primary" elevation={0}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Document Intake Assistant
          </Typography>
          <Button color="inherit" startIcon={<RestartAltIcon />} onClick={handleReset}>
            Reset
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 3, height: "calc(100vh - 64px)" }}>
        <Grid container spacing={2} sx={{ height: "100%" }}>
          <Grid item xs={12} md={4} sx={{ height: { md: "100%" } }}>
            <ChatPanel history={conversation?.history ?? []} onSend={handleSend} loading={loading} />
          </Grid>
          <Grid item xs={12} md={4} sx={{ height: { md: "100%" } }}>
            <StatePreviewPanel
              state={
                conversation?.state ?? {
                  full_name: null,
                  date_of_birth: null,
                  marital_status: null,
                  beneficiaries: [],
                  guardians_for_children: [],
                  final_arrangement: null,
                  final_arrangement_details: null,
                  organ_donor: null,
                  personal_message: null,
                  special_instructions: null,
                  executor_name: null,
                  executor_relationship: null,
                }
              }
              missingFields={conversation?.missing_fields ?? []}
              isComplete={conversation?.is_complete ?? false}
            />
          </Grid>
          <Grid item xs={12} md={4} sx={{ height: { md: "100%" } }}>
            <DocumentPreviewPanel
              markdown={conversation?.document_markdown ?? ""}
              disclaimer={conversation?.disclaimer ?? "This document is fictional and not legal advice."}
            />
          </Grid>
        </Grid>
      </Container>
      <Box component="footer" textAlign="center" py={1}>
        <Typography variant="caption" color="text.secondary">
          This document is fictional and not legal advice.
        </Typography>
      </Box>
    </>
  );
}


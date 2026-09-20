import { useEffect, useRef, useState } from "react";
import { Box, Paper, TextField, IconButton, Typography, Stack, Avatar, CircularProgress } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import PersonIcon from "@mui/icons-material/Person";
import type { ChatTurn } from "../types";
interface ChatPanelProps {
  history: ChatTurn[];
  onSend: (message: string) => Promise<void>;
  loading: boolean;
}
export function ChatPanel({ history, onSend, loading }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);
  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    setInput("");
    await onSend(trimmed);
  };
  return (
    <Paper elevation={2} sx={{ display: "flex", flexDirection: "column", height: "100%", p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Conversation
      </Typography>
      <Box sx={{ flexGrow: 1, overflowY: "auto", pr: 1, mb: 1 }}>
        <Stack spacing={1.5}>
          {history.length === 0 && (
            <Typography variant="body2" color="text.secondary">
              Say hello to get started - e.g. "My name is Jane Doe".
            </Typography>
          )}
          {history.map((turn, idx) => (
            <Stack
              key={idx}
              direction="row"
              spacing={1}
              alignItems="flex-start"
              justifyContent={turn.role === "user" ? "flex-end" : "flex-start"}
            >
              {turn.role === "assistant" && (
                <Avatar sx={{ bgcolor: "primary.main", width: 28, height: 28 }}>
                  <SmartToyIcon fontSize="small" />
                </Avatar>
              )}
              <Box
                sx={{
                  bgcolor: turn.role === "user" ? "primary.main" : "grey.100",
                  color: turn.role === "user" ? "primary.contrastText" : "text.primary",
                  borderRadius: 2,
                  px: 1.5,
                  py: 1,
                  maxWidth: "75%",
                  whiteSpace: "pre-wrap",
                }}
              >
                <Typography variant="body2">{turn.content}</Typography>
              </Box>
              {turn.role === "user" && (
                <Avatar sx={{ bgcolor: "secondary.main", width: 28, height: 28 }}>
                  <PersonIcon fontSize="small" />
                </Avatar>
              )}
            </Stack>
          ))}
          {loading && (
            <Stack direction="row" spacing={1} alignItems="center">
              <Avatar sx={{ bgcolor: "primary.main", width: 28, height: 28 }}>
                <SmartToyIcon fontSize="small" />
              </Avatar>
              <CircularProgress size={16} />
            </Stack>
          )}
          <div ref={bottomRef} />
        </Stack>
      </Box>
      <Stack direction="row" spacing={1}>
        <TextField
          fullWidth
          size="small"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSend();
          }}
        />
        <IconButton color="primary" onClick={handleSend} disabled={loading || !input.trim()}>
          <SendIcon />
        </IconButton>
      </Stack>
    </Paper>
  );
}
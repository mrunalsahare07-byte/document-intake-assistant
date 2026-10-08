import React from "react";
import { Box, Typography } from "@mui/material";
import { ChatTurn } from "../../types";

interface ChatMessageProps {
  turn: ChatTurn;
  index: number;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ turn }) => {
  const isUser = turn.role === "user";

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: isUser ? "flex-end" : "flex-start",
        width: "100%",
        py: 0.75,
      }}
    >
      {/* Role Label */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1,
          mb: 0.5,
          px: 0.5,
        }}
      >
        <Typography
          sx={{
            fontSize: "12px",
            fontWeight: 500,
            color: "var(--text-secondary)",
          }}
        >
          {isUser ? "You" : "Assistant"}
        </Typography>
      </Box>

      {/* Message Bubble */}
      <Box
        sx={{
          maxWidth: "88%",
          width: isUser ? "auto" : "100%",
          backgroundColor: isUser ? "var(--surface)" : "var(--surface-3)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-md)",
          px: 1.75,
          py: 1.25,
        }}
      >
        <Typography
          sx={{
            fontSize: "14px",
            lineHeight: 1.5,
            color: "var(--text-primary)",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          {turn.content}
        </Typography>
      </Box>
    </Box>
  );
};

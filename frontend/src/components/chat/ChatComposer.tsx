import React, { useState, useRef, useEffect } from "react";
import { Box, Typography, TextareaAutosize } from "@mui/material";
import { Button } from "../common/Button";

interface ChatComposerProps {
  onSend: (message: string) => Promise<void>;
  loading: boolean;
  disabled?: boolean;
}

export const ChatComposer: React.FC<ChatComposerProps> = ({
  onSend,
  loading,
  disabled = false,
}) => {
  const [value, setValue] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const canSend = value.trim().length > 0 && !loading && !disabled;

  const handleSubmit = async () => {
    if (!canSend) return;
    const msg = value.trim();
    setValue("");
    await onSend(msg);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  useEffect(() => {
    if (!loading && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [loading]);

  return (
    <Box
      sx={{
        p: 1.5,
        borderTop: "1px solid var(--border)",
        backgroundColor: "var(--surface)",
        flexShrink: 0,
      }}
    >
      <Box
        sx={{
          backgroundColor: "var(--surface)",
          border: "1px solid",
          borderColor: isFocused ? "var(--border-focus)" : "var(--border)",
          outline: isFocused ? "2px solid #334155" : "none",
          outlineOffset: isFocused ? "1px" : "0",
          borderRadius: "var(--radius-xs)",
          transition: "border-color var(--transition-fast)",
          display: "flex",
          flexDirection: "column",
          p: 1,
        }}
      >
        <TextareaAutosize
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={loading ? "Waiting for response..." : "Type a message..."}
          disabled={loading || disabled}
          aria-label="Chat message input"
          minRows={1}
          maxRows={6}
          style={{
            width: "100%",
            background: "transparent",
            border: "none",
            outline: "none",
            resize: "none",
            color: "var(--text-primary)",
            fontFamily: "var(--font-sans)",
            fontSize: "14px",
            lineHeight: "1.5",
            padding: "4px 6px",
          }}
        />

        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            mt: 0.75,
            pt: 0.5,
            borderTop: "1px solid var(--border)",
          }}
        >
          {/* Hint */}
          <Typography
            sx={{
              fontSize: "12px",
              color: "var(--text-secondary)",
              userSelect: "none",
            }}
          >
            Press Enter to send
          </Typography>

          {/* Send Button */}
          <Button
            variant="primary"
            size="small"
            onClick={handleSubmit}
            disabled={!canSend}
            aria-label="Send message"
          >
            Send
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

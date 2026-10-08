import React, { useState } from "react";
import { Box, Typography, Collapse } from "@mui/material";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import { Button } from "./Button";

interface ErrorStateProps {
  title?: string;
  message?: string;
  details?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "An error occurred",
  message = "The intake service couldn't complete this request.",
  details,
  onRetry,
}) => {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <Box
      sx={{
        p: 2,
        m: 2,
        borderRadius: "var(--radius-xs)",
        bgcolor: "var(--danger-subtle)",
        border: "1px solid #FCA5A5",
      }}
    >
      <Box sx={{ display: "flex", alignItems: "flex-start", gap: 1.5 }}>
        <ErrorOutlineIcon
          sx={{ color: "var(--danger)", fontSize: "1.2rem", mt: 0.25, flexShrink: 0 }}
        />
        <Box sx={{ flexGrow: 1 }}>
          <Typography
            sx={{
              fontSize: "14px",
              fontWeight: 600,
              color: "var(--danger)",
              mb: 0.25,
            }}
          >
            {title}
          </Typography>
          <Typography
            sx={{
              fontSize: "12px",
              color: "var(--text-secondary)",
              lineHeight: 1.45,
              mb: 1.5,
            }}
          >
            {message}
          </Typography>

          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            {onRetry && (
              <Button variant="danger" size="small" onClick={onRetry}>
                Retry
              </Button>
            )}

            {details && (
              <Button
                variant="ghost"
                size="small"
                onClick={() => setShowDetails(!showDetails)}
                endIcon={
                  showDetails ? (
                    <KeyboardArrowUpIcon fontSize="small" />
                  ) : (
                    <KeyboardArrowDownIcon fontSize="small" />
                  )
                }
              >
                {showDetails ? "Hide details" : "View details"}
              </Button>
            )}
          </Box>

          {details && (
            <Collapse in={showDetails}>
              <Box
                sx={{
                  mt: 1.5,
                  p: 1.5,
                  bgcolor: "var(--surface)",
                  borderRadius: "var(--radius-xs)",
                  border: "1px solid var(--border)",
                  fontFamily: "var(--font-sans)",
                  fontSize: "12px",
                  color: "var(--text-secondary)",
                  maxHeight: 160,
                  overflowY: "auto",
                  whiteSpace: "pre-wrap",
                }}
              >
                {details}
              </Box>
            </Collapse>
          )}
        </Box>
      </Box>
    </Box>
  );
};

import React from "react";
import { Typography } from "@mui/material";

export type StatusVariant =
  | "connected"
  | "processing"
  | "draft"
  | "confirmed"
  | "needs_review"
  | "error"
  | "saved"
  | "live"
  | "idle";

interface StatusIndicatorProps {
  status: StatusVariant;
  label?: string;
  size?: "small" | "medium";
  pulse?: boolean;
}

const defaultLabels: Record<StatusVariant, string> = {
  connected: "Connected",
  live: "Live",
  saved: "Saved",
  confirmed: "Confirmed",
  processing: "Processing...",
  draft: "Draft",
  needs_review: "Needs confirmation",
  error: "Error",
  idle: "Idle",
};

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  size = "small",
}) => {
  const displayLabel = label ?? defaultLabels[status] ?? "Idle";

  return (
    <Typography
      component="span"
      sx={{
        fontSize: size === "small" ? "12px" : "14px",
        fontWeight: 400,
        color: "var(--text-secondary)",
        lineHeight: 1.4,
        userSelect: "none",
      }}
    >
      {displayLabel}
    </Typography>
  );
};

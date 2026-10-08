import React from "react";
import { Box, Typography } from "@mui/material";
import type { FieldStatus } from "../../types";

interface StateFieldProps {
  label: string;
  value: React.ReactNode;
  isConfirmed?: boolean;
  status?: FieldStatus;
  isUpdated?: boolean;
  updateType?: "added" | "updated";
  isMissing?: boolean;
  monoValue?: boolean;
}

export const StateField: React.FC<StateFieldProps> = ({
  label,
  value,
  isConfirmed,
  status,
  isMissing = false,
}) => {
  const effectiveStatus: FieldStatus =
    status ?? (isConfirmed ? "confirmed" : isMissing ? "unconfirmed" : "unknown");

  const renderStatus = () => {
    switch (effectiveStatus) {
      case "confirmed":
        return (
          <Typography
            sx={{
              fontSize: "12px",
              fontWeight: 400,
              color: "#6B7280",
              whiteSpace: "nowrap",
            }}
          >
            Confirmed
          </Typography>
        );
      case "unconfirmed":
        return (
          <Typography
            sx={{
              fontSize: "12px",
              fontWeight: 500,
              color: "#1A1A1A",
              borderLeft: "2px solid #D97706",
              pl: 0.75,
              whiteSpace: "nowrap",
            }}
          >
            Needs confirmation
          </Typography>
        );
      case "unknown":
      default:
        return (
          <Typography
            sx={{
              fontSize: "12px",
              fontWeight: 400,
              fontStyle: "italic",
              color: "#6B7280",
              whiteSpace: "nowrap",
            }}
          >
            Not provided
          </Typography>
        );
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        py: 1,
        px: 1,
        borderRadius: "var(--radius-xs)",
        transition: "background-color 150ms ease",
        borderBottom: "1px solid var(--border)",
        "&:last-child": {
          borderBottom: "none",
        },
        "&:hover": {
          backgroundColor: "var(--surface-hover)",
        },
      }}
    >
      {/* Left: Label & Value */}
      <Box sx={{ overflow: "hidden", pr: 1.5, flexGrow: 1 }}>
        <Typography
          sx={{
            fontSize: "12px",
            color: "var(--text-secondary)",
            mb: 0.25,
            fontWeight: 400,
          }}
        >
          {label}
        </Typography>

        <Typography
          sx={{
            fontSize: "14px",
            fontWeight: effectiveStatus === "confirmed" ? 500 : 400,
            color: effectiveStatus === "confirmed" ? "var(--text-primary)" : "var(--text-secondary)",
            fontStyle: effectiveStatus === "confirmed" ? "normal" : "italic",
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {value}
        </Typography>
      </Box>

      {/* Right: Validation Status Label */}
      <Box sx={{ flexShrink: 0, pl: 1 }}>
        {renderStatus()}
      </Box>
    </Box>
  );
};

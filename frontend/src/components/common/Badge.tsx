import React from "react";
import { Box, Typography } from "@mui/material";

export type BadgeVariant =
  | "default"
  | "confirmed"
  | "pending"
  | "added"
  | "updated"
  | "accent"
  | "muted";

interface BadgeProps {
  label: React.ReactNode;
  variant?: BadgeVariant;
  size?: "small" | "medium";
  icon?: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  label,
  size = "small",
  icon,
  className,
}) => {
  return (
    <Box
      component="span"
      className={className}
      sx={{
        display: "inline-flex",
        alignItems: "center",
        gap: 0.5,
        backgroundColor: "var(--surface-3)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-xs)",
        px: size === "small" ? "6px" : "8px",
        py: size === "small" ? "2px" : "3px",
        lineHeight: 1,
        userSelect: "none",
      }}
    >
      {icon && (
        <Box
          component="span"
          sx={{
            display: "inline-flex",
            alignItems: "center",
            fontSize: size === "small" ? "12px" : "14px",
            color: "var(--text-secondary)",
          }}
        >
          {icon}
        </Box>
      )}
      <Typography
        component="span"
        sx={{
          fontSize: size === "small" ? "12px" : "14px",
          fontWeight: 400,
          color: "var(--text-secondary)",
          fontFamily: "var(--font-sans)",
        }}
      >
        {label}
      </Typography>
    </Box>
  );
};

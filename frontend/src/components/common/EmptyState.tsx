import React from "react";
import { Box, Typography } from "@mui/material";

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  action,
  icon,
}) => {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        py: 6,
        px: 3,
        height: "100%",
        minHeight: 180,
      }}
    >
      {icon && (
        <Box
          sx={{
            mb: 1.5,
            color: "var(--text-secondary)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {icon}
        </Box>
      )}
      <Typography
        sx={{
          fontSize: "14px",
          fontWeight: 600,
          color: "var(--text-primary)",
          mb: 0.5,
        }}
      >
        {title}
      </Typography>
      {description && (
        <Typography
          sx={{
            fontSize: "12px",
            color: "var(--text-secondary)",
            maxWidth: 320,
            mb: action ? 2 : 0,
            lineHeight: 1.45,
          }}
        >
          {description}
        </Typography>
      )}
      {action && <Box sx={{ mt: 1 }}>{action}</Box>}
    </Box>
  );
};

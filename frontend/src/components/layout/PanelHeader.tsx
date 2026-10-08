import React from "react";
import { Box, Typography } from "@mui/material";

interface PanelHeaderProps {
  title: string;
  subtitle?: string;
  statusIndicator?: React.ReactNode;
  actions?: React.ReactNode;
}

export const PanelHeader: React.FC<PanelHeaderProps> = ({
  title,
  subtitle,
  statusIndicator,
  actions,
}) => {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        px: { xs: 1.5, sm: 2 },
        height: 48,
        minHeight: 48,
        borderBottom: "1px solid var(--border)",
        backgroundColor: "var(--surface)",
        flexShrink: 0,
        boxSizing: "border-box",
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1.25,
          overflow: "hidden",
          minWidth: 0,
          flexShrink: 1,
          mr: 1,
        }}
      >
        <Box sx={{ minWidth: 0, overflow: "hidden" }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, minWidth: 0 }}>
            <Typography
              sx={{
                fontSize: "16px",
                fontWeight: 600,
                color: "var(--text-primary)",
                lineHeight: 1.35,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {title}
            </Typography>
            {statusIndicator && (
              <Box sx={{ flexShrink: 0, display: "inline-flex" }}>
                {statusIndicator}
              </Box>
            )}
          </Box>
          {subtitle && (
            <Typography
              sx={{
                fontSize: "12px",
                color: "var(--text-secondary)",
                lineHeight: 1.3,
                mt: 0.25,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {subtitle}
            </Typography>
          )}
        </Box>
      </Box>

      {actions && (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: { xs: 0.5, sm: 1 },
            flexShrink: 0,
            flexWrap: "nowrap",
          }}
        >
          {actions}
        </Box>
      )}
    </Box>
  );
};

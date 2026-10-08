import React from "react";
import { Box, Typography } from "@mui/material";

interface StateSectionProps {
  title: string;
  badge?: string;
  children: React.ReactNode;
}

export const StateSection: React.FC<StateSectionProps> = ({
  title,
  badge,
  children,
}) => {
  return (
    <Box sx={{ mb: 2.5 }}>
      {/* Section Header */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          pb: 0.75,
          mb: 0.5,
          borderBottom: "1px solid var(--border)",
        }}
      >
        <Typography
          sx={{
            fontSize: "12px",
            fontWeight: 500,
            color: "var(--text-secondary)",
          }}
        >
          {title}
        </Typography>

        {badge && (
          <Typography
            sx={{
              fontSize: "12px",
              color: "var(--text-secondary)",
            }}
          >
            {badge}
          </Typography>
        )}
      </Box>

      {/* Rows */}
      <Box sx={{ display: "flex", flexDirection: "column" }}>
        {children}
      </Box>
    </Box>
  );
};

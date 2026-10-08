import React from "react";
import { Box, BoxProps } from "@mui/material";

interface PanelProps extends Omit<BoxProps, "borderRight" | "borderLeft"> {
  children: React.ReactNode;
  borderRight?: boolean;
  borderLeft?: boolean;
}

export const Panel: React.FC<PanelProps> = ({
  children,
  borderRight = false,
  borderLeft = false,
  sx,
  ...props
}) => {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        backgroundColor: "var(--surface)",
        borderRight: borderRight ? "1px solid var(--border)" : "none",
        borderLeft: borderLeft ? "1px solid var(--border)" : "none",
        overflow: "hidden",
        position: "relative",
        ...sx,
      }}
      {...props}
    >
      {children}
    </Box>
  );
};

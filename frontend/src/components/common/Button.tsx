import React from "react";
import { Button as MuiButton, ButtonProps as MuiButtonProps, CircularProgress } from "@mui/material";

export interface ButtonProps extends Omit<MuiButtonProps, "variant" | "color"> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "small" | "medium" | "large";
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = "secondary",
  size = "small",
  loading = false,
  disabled,
  children,
  sx,
  ...props
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case "primary":
        return {
          backgroundColor: "var(--accent)",
          color: "#FFFFFF",
          border: "1px solid var(--accent)",
          "&:hover": {
            backgroundColor: "var(--accent-hover)",
            borderColor: "var(--accent-hover)",
          },
          "&:active": {
            backgroundColor: "var(--accent-active)",
            borderColor: "var(--accent-active)",
          },
          "&.Mui-disabled": {
            backgroundColor: "var(--surface-3)",
            color: "var(--text-disabled)",
            borderColor: "var(--border)",
          },
        };
      case "ghost":
        return {
          backgroundColor: "transparent",
          color: "var(--text-secondary)",
          border: "1px solid transparent",
          "&:hover": {
            backgroundColor: "var(--surface-hover)",
            color: "var(--text-primary)",
          },
          "&.Mui-disabled": {
            color: "var(--text-disabled)",
          },
        };
      case "danger":
        return {
          backgroundColor: "var(--danger-subtle)",
          color: "var(--danger)",
          border: "1px solid #FCA5A5",
          "&:hover": {
            backgroundColor: "#FEE2E2",
            borderColor: "#F87171",
          },
        };
      case "secondary":
      default:
        return {
          backgroundColor: "var(--surface)",
          color: "var(--text-primary)",
          border: "1px solid var(--border)",
          "&:hover": {
            backgroundColor: "var(--surface-hover)",
            borderColor: "var(--border-strong)",
          },
          "&.Mui-disabled": {
            backgroundColor: "var(--surface-2)",
            color: "var(--text-disabled)",
            borderColor: "var(--border)",
          },
        };
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case "large":
        return {
          py: "8px",
          px: "16px",
          fontSize: "14px",
          height: 36,
        };
      case "small":
        return {
          py: "4px",
          px: "10px",
          fontSize: "12px",
          height: 28,
        };
      case "medium":
      default:
        return {
          py: "6px",
          px: "12px",
          fontSize: "14px",
          height: 32,
        };
    }
  };

  return (
    <MuiButton
      disabled={disabled || loading}
      sx={{
        borderRadius: "var(--radius-xs)",
        fontWeight: 500,
        textTransform: "none",
        letterSpacing: "normal",
        transition: "all var(--transition-fast)",
        "&:focus-visible": {
          outline: "2px solid #334155",
          outlineOffset: 1,
        },
        ...getSizeStyles(),
        ...getVariantStyles(),
        ...sx,
      }}
      {...props}
    >
      {loading ? (
        <CircularProgress size={size === "small" ? 12 : 14} color="inherit" sx={{ mr: 1 }} />
      ) : null}
      {children}
    </MuiButton>
  );
};

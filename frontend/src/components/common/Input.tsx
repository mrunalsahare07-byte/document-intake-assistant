import React from "react";
import {
  TextField as MuiTextField,
  TextFieldProps as MuiTextFieldProps,
} from "@mui/material";

export interface InputProps extends Omit<MuiTextFieldProps, "variant"> {
  mono?: boolean;
}

export const Input: React.FC<InputProps> = ({ mono, sx, ...props }) => {
  return (
    <MuiTextField
      variant="outlined"
      size="small"
      sx={{
        "& .MuiOutlinedInput-root": {
          backgroundColor: "var(--surface)",
          borderRadius: "var(--radius-xs)",
          transition: "border-color var(--transition-fast)",
          "& fieldset": {
            borderColor: "var(--border)",
          },
          "&:hover fieldset": {
            borderColor: "var(--border-strong)",
          },
          "&.Mui-focused fieldset": {
            borderColor: "var(--border-focus)",
            borderWidth: 1,
          },
          "&.Mui-focused": {
            outline: "2px solid #334155",
            outlineOffset: 1,
          },
        },
        "& .MuiInputBase-input": {
          color: "var(--text-primary)",
          fontSize: "14px",
          fontFamily: "var(--font-sans)",
          py: "8px",
          px: "12px",
          "&::placeholder": {
            color: "var(--text-muted)",
            opacity: 1,
          },
        },
        ...sx,
      }}
      {...props}
    />
  );
};

import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    background: {
      default: "#F9FAFB",
      paper: "#FFFFFF",
    },
    primary: {
      main: "#0F172A",
      dark: "#1E293B",
      light: "#334155",
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: "#6B7280",
      dark: "#4B5563",
      light: "#9CA3AF",
      contrastText: "#1A1A1A",
    },
    error: {
      main: "#991B1B",
      dark: "#7F1D1D",
      light: "#FEF2F2",
    },
    warning: {
      main: "#B45309",
      dark: "#92400E",
      light: "#FFFBEB",
    },
    success: {
      main: "#166534",
      dark: "#14532D",
      light: "#F0FDF4",
    },
    text: {
      primary: "#1A1A1A",
      secondary: "#6B7280",
      disabled: "#9CA3AF",
    },
    divider: "#E5E7EB",
    action: {
      hover: "#F3F4F6",
      selected: "#E5E7EB",
      disabled: "#9CA3AF",
      disabledBackground: "#F3F4F6",
    },
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    fontSize: 14,
    htmlFontSize: 16,
    h1: { fontSize: "20px", fontWeight: 600, lineHeight: 1.3, letterSpacing: "-0.01em" },
    h2: { fontSize: "16px", fontWeight: 600, lineHeight: 1.35, letterSpacing: "-0.01em" },
    h3: { fontSize: "16px", fontWeight: 600, lineHeight: 1.35 },
    h4: { fontSize: "14px", fontWeight: 600, lineHeight: 1.4 },
    h5: { fontSize: "14px", fontWeight: 600, lineHeight: 1.4 },
    h6: { fontSize: "14px", fontWeight: 600, lineHeight: 1.4 },
    subtitle1: { fontSize: "14px", fontWeight: 500, color: "#6B7280" },
    subtitle2: { fontSize: "12px", fontWeight: 500, color: "#6B7280" },
    body1: { fontSize: "14px", lineHeight: 1.5, color: "#1A1A1A" },
    body2: { fontSize: "12px", lineHeight: 1.45, color: "#6B7280" },
    caption: { fontSize: "12px", lineHeight: 1.4, color: "#6B7280" },
    button: { textTransform: "none", fontWeight: 500, fontSize: "14px" },
  },
  shape: {
    borderRadius: 6,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: "#FFFFFF",
          color: "#1A1A1A",
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: "#FFFFFF",
          backgroundImage: "none !important",
          border: "1px solid #E5E7EB",
          boxShadow: "none",
          borderRadius: 6,
        },
      },
    },
    MuiButton: {
      defaultProps: {
        disableElevation: true,
        disableRipple: true,
      },
      styleOverrides: {
        root: {
          borderRadius: 4,
          fontWeight: 500,
          fontSize: "14px",
          padding: "5px 12px",
          textTransform: "none",
          transition: "background-color 150ms ease, border-color 150ms ease, color 150ms ease",
          "&:focus-visible": {
            outline: "2px solid #334155",
            outlineOffset: 1,
          },
        },
        containedPrimary: {
          backgroundColor: "#0F172A",
          color: "#FFFFFF",
          border: "1px solid #0F172A",
          "&:hover": {
            backgroundColor: "#1E293B",
            borderColor: "#1E293B",
          },
          "&.Mui-disabled": {
            backgroundColor: "#F3F4F6",
            color: "#9CA3AF",
            border: "1px solid #E5E7EB",
          },
        },
        outlined: {
          borderColor: "#E5E7EB",
          color: "#1A1A1A",
          backgroundColor: "#FFFFFF",
          "&:hover": {
            backgroundColor: "#F9FAFB",
            borderColor: "#D1D5DB",
          },
        },
        text: {
          color: "#6B7280",
          "&:hover": {
            color: "#1A1A1A",
            backgroundColor: "#F3F4F6",
          },
        },
      },
    },
    MuiIconButton: {
      defaultProps: {
        disableRipple: true,
      },
      styleOverrides: {
        root: {
          borderRadius: 4,
          color: "#6B7280",
          padding: 6,
          transition: "all 150ms ease",
          "&:hover": {
            backgroundColor: "#F3F4F6",
            color: "#1A1A1A",
          },
          "&.Mui-disabled": {
            color: "#D1D5DB",
          },
          "&:focus-visible": {
            outline: "2px solid #334155",
            outlineOffset: 1,
          },
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          backgroundColor: "#FFFFFF",
          borderRadius: 4,
          transition: "border-color 150ms ease",
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "#E5E7EB",
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "#D1D5DB",
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: "#334155",
            borderWidth: 1,
          },
          "&.Mui-focused": {
            outline: "2px solid #334155",
            outlineOffset: 1,
          },
        },
        input: {
          padding: "8px 12px",
          fontSize: "14px",
          color: "#1A1A1A",
          "&::placeholder": {
            color: "#6B7280",
            opacity: 1,
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          height: 22,
          fontSize: "12px",
          fontWeight: 400,
          border: "1px solid #E5E7EB",
        },
        filled: {
          backgroundColor: "#F3F4F6",
          color: "#1A1A1A",
        },
        outlined: {
          borderColor: "#E5E7EB",
          color: "#6B7280",
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: "#E5E7EB",
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: "#1A1A1A",
          border: "1px solid #334155",
          color: "#FFFFFF",
          fontSize: "12px",
          borderRadius: 4,
          padding: "4px 8px",
          boxShadow: "none",
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundColor: "#FFFFFF",
          border: "1px solid #E5E7EB",
          borderRadius: 6,
        },
      },
    },
  },
});

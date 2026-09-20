import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#2f3e46" },
    secondary: { main: "#84a98c" },
    background: { default: "#f6f7f5" },
  },
  shape: { borderRadius: 10 },
});

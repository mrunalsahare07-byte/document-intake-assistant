import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Allows pointing the dev server at a backend running on another machine,
// e.g. set BACKEND_URL=http://192.168.1.10:8000 before running `npm run dev`.
const backendTarget = process.env.BACKEND_URL || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": {
        target: backendTarget,
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          mui: ["@mui/material", "@mui/icons-material", "@emotion/react", "@emotion/styled"],
        },
      },
    },
  },
});

import { Alert, Paper, Typography, Box } from "@mui/material";
import ReactMarkdown from "react-markdown";

interface DocumentPreviewPanelProps {
  markdown: string;
  disclaimer: string;
}

/**
 * DocumentPreviewPanel: renders the generated fictional Personal Wishes
 * Document as Markdown. Always displays the legal disclaimer prominently.
 */
export function DocumentPreviewPanel({ markdown, disclaimer }: DocumentPreviewPanelProps) {
  return (
    <Paper elevation={2} sx={{ height: "100%", p: 2, overflowY: "auto" }}>
      <Typography variant="h6" gutterBottom>
        Document Preview
      </Typography>
      <Alert severity="warning" sx={{ mb: 2 }}>
        {disclaimer}
      </Alert>
      <Box
        sx={{
          "& h1": { fontSize: "1.4rem" },
          "& h2": { fontSize: "1.15rem", mt: 2 },
          fontFamily: "Georgia, serif",
        }}
      >
        <ReactMarkdown>{markdown}</ReactMarkdown>
      </Box>
    </Paper>
  );
}


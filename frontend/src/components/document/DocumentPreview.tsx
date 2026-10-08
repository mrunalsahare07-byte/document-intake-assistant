import React from "react";
import { Box, Typography } from "@mui/material";
import ReactMarkdown from "react-markdown";

interface DocumentPreviewProps {
  markdown: string;
  disclaimer: string;
  isComplete?: boolean;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  markdown,
  disclaimer,
  isComplete = false,
}) => {
  return (
    <Box
      sx={{
        width: "100%",
        display: "flex",
        justifyContent: "center",
        py: { xs: 2, sm: 3 },
        px: { xs: 1.5, sm: 2 },
      }}
    >
      {/* Real document paper canvas */}
      <Box
        id="printable-document"
        sx={{
          width: "100%",
          maxWidth: 720,
          backgroundColor: "#FFFFFF",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-md)",
          boxShadow: "0 1px 3px rgba(0, 0, 0, 0.04)",
          p: { xs: 3, sm: 5 },
          position: "relative",
        }}
      >
        {/* Document Header Status */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            pb: 2,
            mb: 3,
            borderBottom: "1px solid var(--border)",
          }}
        >
          <Typography
            sx={{
              fontSize: "12px",
              color: "var(--text-secondary)",
              fontWeight: 500,
            }}
          >
            {isComplete ? "Finalized draft" : "Working draft"}
          </Typography>

          <Typography
            sx={{
              fontSize: "12px",
              color: "var(--text-secondary)",
            }}
          >
            Ref: DIA-EST-{new Date().toISOString().slice(0, 10).replace(/-/g, "")}
          </Typography>
        </Box>

        {/* Disclaimer Notice */}
        {disclaimer && (
          <Box
            sx={{
              p: 1.5,
              mb: 3,
              borderRadius: "var(--radius-xs)",
              backgroundColor: "var(--surface-2)",
              border: "1px solid var(--border)",
            }}
          >
            <Typography
              sx={{
                fontSize: "12px",
                color: "var(--text-secondary)",
                lineHeight: 1.5,
              }}
            >
              Notice: {disclaimer}
            </Typography>
          </Box>
        )}

        {/* Formatted Serif Markdown Content */}
        <Box
          sx={{
            color: "#1A1A1A",
            fontFamily: 'Georgia, "Times New Roman", Times, serif',
            lineHeight: 1.7,
            fontSize: "15px",
            "& h1": {
              fontFamily: 'Georgia, "Times New Roman", Times, serif',
              fontSize: "22px",
              fontWeight: 600,
              color: "#1A1A1A",
              mb: 2,
              mt: 0,
              borderBottom: "1px solid var(--border)",
              pb: 1.5,
            },
            "& h2": {
              fontFamily: 'Georgia, "Times New Roman", Times, serif',
              fontSize: "18px",
              fontWeight: 600,
              color: "#1A1A1A",
              mt: 3.5,
              mb: 1.25,
              pb: 0.5,
              borderBottom: "1px solid var(--border)",
            },
            "& p": {
              my: 1.25,
              color: "#1A1A1A",
              fontSize: "15px",
              lineHeight: 1.7,
            },
            "& strong": {
              color: "#1A1A1A",
              fontWeight: 600,
            },
            "& ul": {
              pl: 3,
              my: 1.25,
            },
            "& li": {
              mb: 0.5,
              color: "#1A1A1A",
              fontSize: "15px",
              lineHeight: 1.7,
            },
            "& blockquote": {
              borderLeft: "2px solid var(--border-strong)",
              pl: 2,
              ml: 0,
              my: 2,
              color: "var(--text-secondary)",
              fontStyle: "italic",
            },
          }}
        >
          <ReactMarkdown>{markdown}</ReactMarkdown>
        </Box>

        {/* Document Footer */}
        <Box
          sx={{
            mt: 5,
            pt: 2.5,
            borderTop: "1px solid var(--border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Typography
            sx={{
              fontSize: "12px",
              color: "var(--text-secondary)",
            }}
          >
            Intake intake record
          </Typography>

          <Typography
            sx={{
              fontSize: "12px",
              color: "var(--text-secondary)",
            }}
          >
            Page 1 of 1
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

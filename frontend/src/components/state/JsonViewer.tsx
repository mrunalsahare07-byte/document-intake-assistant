import React, { useState } from "react";
import { Box, Typography, Collapse, Tooltip, IconButton } from "@mui/material";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import CheckIcon from "@mui/icons-material/Check";

interface JsonViewerProps {
  data: unknown;
  defaultExpanded?: boolean;
}

export const JsonViewer: React.FC<JsonViewerProps> = ({
  data,
  defaultExpanded = false,
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [copied, setCopied] = useState(false);

  const jsonString = JSON.stringify(data, null, 2);
  const lineCount = jsonString.split("\n").length;

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Neutral syntax coloring for light mode
  const highlightJson = (json: string) => {
    const regex = /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g;
    return json.replace(regex, (match) => {
      let cls = "color: #1E40AF;"; // number / value
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = "color: #374151; font-weight: 500;"; // key
        } else {
          cls = "color: #166534;"; // string
        }
      } else if (/true|false/.test(match)) {
        cls = "color: #92400E;"; // boolean
      } else if (/null/.test(match)) {
        cls = "color: #6B7280; font-style: italic;"; // null
      }
      return `<span style="${cls}">${match}</span>`;
    });
  };

  return (
    <Box
      sx={{
        mt: 2.5,
        borderRadius: "var(--radius-xs)",
        border: "1px solid var(--border)",
        backgroundColor: "var(--surface)",
        overflow: "hidden",
      }}
    >
      {/* Header bar */}
      <Box
        onClick={() => setExpanded(!expanded)}
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          px: 1.5,
          py: 0.75,
          backgroundColor: "var(--surface-2)",
          cursor: "pointer",
          userSelect: "none",
          transition: "background-color var(--transition-fast)",
          "&:hover": {
            backgroundColor: "var(--surface-hover)",
          },
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
          <IconButton size="small" sx={{ p: 0.25 }} aria-label={expanded ? "Collapse JSON view" : "Expand JSON view"}>
            {expanded ? (
              <KeyboardArrowDownIcon sx={{ fontSize: 16 }} />
            ) : (
              <KeyboardArrowRightIcon sx={{ fontSize: 16 }} />
            )}
          </IconButton>
          <Typography
            sx={{
              fontSize: "12px",
              fontWeight: 500,
              color: "var(--text-primary)",
            }}
          >
            Raw state (JSON)
          </Typography>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Typography
            sx={{
              fontSize: "12px",
              color: "var(--text-secondary)",
            }}
          >
            {lineCount} lines
          </Typography>

          <Tooltip title={copied ? "Copied" : "Copy JSON"}>
            <IconButton
              size="small"
              onClick={handleCopy}
              aria-label="Copy JSON to clipboard"
              sx={{
                p: 0.5,
                color: "var(--text-secondary)",
              }}
            >
              {copied ? <CheckIcon sx={{ fontSize: 14 }} /> : <ContentCopyIcon sx={{ fontSize: 14 }} />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Code Body */}
      <Collapse in={expanded}>
        <Box
          sx={{
            p: 1.5,
            backgroundColor: "var(--surface-2)",
            fontFamily: "var(--font-mono)",
            fontSize: "12px",
            lineHeight: 1.6,
            maxHeight: 280,
            overflowY: "auto",
            overflowX: "auto",
            borderTop: "1px solid var(--border)",
          }}
        >
          <pre
            style={{ margin: 0, fontFamily: "inherit" }}
            dangerouslySetInnerHTML={{ __html: highlightJson(jsonString) }}
          />
        </Box>
      </Collapse>
    </Box>
  );
};

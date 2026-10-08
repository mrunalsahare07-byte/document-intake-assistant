import React, { useState } from "react";
import { Box, Tooltip, IconButton } from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import CheckIcon from "@mui/icons-material/Check";
import DownloadIcon from "@mui/icons-material/Download";
import PrintIcon from "@mui/icons-material/Print";
import { Panel } from "../layout/Panel";
import { PanelHeader } from "../layout/PanelHeader";
import { StatusIndicator } from "../common/StatusIndicator";
import { DocumentPreview } from "./DocumentPreview";
import { EmptyState } from "../common/EmptyState";
import { LoadingState } from "../common/LoadingState";

export interface DocumentPreviewPanelProps {
  markdown: string;
  disclaimer: string;
  isComplete?: boolean;
  loading?: boolean;
}

export const DocumentPreviewPanel: React.FC<DocumentPreviewPanelProps> = ({
  markdown,
  disclaimer,
  isComplete = false,
  loading = false,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!markdown) return;
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!markdown) return;
    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `personal-wishes-${new Date().toISOString().slice(0, 10)}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  const actionBtnSx = {
    width: 32,
    height: 32,
    minWidth: 32,
    p: 0,
    borderRadius: "var(--radius-xs, 4px)",
    border: "1px solid var(--border)",
    backgroundColor: "var(--surface)",
    color: "var(--text-secondary)",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "all var(--transition-fast)",
    "&:hover": {
      backgroundColor: "var(--surface-hover)",
      borderColor: "var(--border-strong)",
      color: "var(--text-primary)",
    },
    "&:focus-visible": {
      outline: "2px solid #334155",
      outlineOffset: 1,
    },
    "&.Mui-disabled": {
      backgroundColor: "var(--surface-2)",
      borderColor: "var(--border)",
      color: "var(--text-disabled)",
    },
  };

  const headerActions = (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        flexWrap: "nowrap",
        gap: { xs: 0.5, sm: 1 },
        flexShrink: 0,
      }}
    >
      <Tooltip title={copied ? "Copied" : "Copy document"}>
        <span>
          <IconButton
            size="small"
            onClick={handleCopy}
            disabled={!markdown}
            aria-label="Copy document"
            sx={actionBtnSx}
          >
            {copied ? <CheckIcon sx={{ fontSize: 16 }} /> : <ContentCopyIcon sx={{ fontSize: 16 }} />}
          </IconButton>
        </span>
      </Tooltip>

      <Tooltip title="Download document (.md)">
        <span>
          <IconButton
            size="small"
            onClick={handleDownload}
            disabled={!markdown}
            aria-label="Download document (.md)"
            sx={actionBtnSx}
          >
            <DownloadIcon sx={{ fontSize: 16 }} />
          </IconButton>
        </span>
      </Tooltip>

      <Tooltip title="Print document">
        <span>
          <IconButton
            size="small"
            onClick={handlePrint}
            disabled={!markdown}
            aria-label="Print document"
            sx={actionBtnSx}
          >
            <PrintIcon sx={{ fontSize: 16 }} />
          </IconButton>
        </span>
      </Tooltip>
    </Box>
  );

  return (
    <Panel sx={{ height: "100%" }}>
      {/* Header */}
      <PanelHeader
        title="Document preview"
        statusIndicator={
          isComplete ? (
            <StatusIndicator status="confirmed" label="Finalized" size="small" />
          ) : (
            <StatusIndicator status="draft" label="Draft" size="small" />
          )
        }
        actions={headerActions}
      />

      {/* Body Area */}
      <Box
        sx={{
          flexGrow: 1,
          overflowY: "auto",
          backgroundColor: "var(--surface-2)",
        }}
      >
        {loading ? (
          <LoadingState type="document" />
        ) : !markdown ? (
          <EmptyState
            title="No document yet"
            description="A preview will appear here as information is collected."
          />
        ) : (
          <DocumentPreview
            markdown={markdown}
            disclaimer={disclaimer}
            isComplete={isComplete}
          />
        )}
      </Box>
    </Panel>
  );
};

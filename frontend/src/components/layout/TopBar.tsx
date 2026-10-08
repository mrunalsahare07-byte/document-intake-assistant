import React from "react";
import { Box, Typography, IconButton, Tabs, Tab, Tooltip } from "@mui/material";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import MenuIcon from "@mui/icons-material/Menu";
import { StatusIndicator } from "../common/StatusIndicator";
import { Button } from "../common/Button";

interface TopBarProps {
  breadcrumb: string;
  subBreadcrumb?: string;
  isSaved?: boolean;
  isProcessing?: boolean;
  onReset: () => void;
  resetLoading?: boolean;
  onDeleteCurrentSession?: (triggerElement?: HTMLElement) => void;
  onToggleMobileMenu?: () => void;
  // Responsive tabs
  activeTab?: number;
  onTabChange?: (tab: number) => void;
  isSmallScreen?: boolean;
  onOpenSettings?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  breadcrumb,
  subBreadcrumb = "Personal Wishes Intake",
  isSaved = true,
  isProcessing = false,
  onReset,
  resetLoading = false,
  onDeleteCurrentSession,
  onToggleMobileMenu,
  activeTab = 0,
  onTabChange,
  isSmallScreen = false,
}) => {
  return (
    <Box
      sx={{
        height: 48,
        backgroundColor: "var(--surface)",
        borderBottom: "1px solid var(--border)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        px: { xs: 1.5, sm: 2.5 },
        flexShrink: 0,
        zIndex: 10,
      }}
    >
      {/* Left: Mobile menu toggle + Breadcrumbs */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, overflow: "hidden" }}>
        {onToggleMobileMenu && (
          <IconButton
            size="small"
            onClick={onToggleMobileMenu}
            aria-label="Toggle navigation menu"
            sx={{ display: { xs: "inline-flex", md: "none" } }}
          >
            <MenuIcon sx={{ fontSize: 18 }} />
          </IconButton>
        )}

        <Box sx={{ display: "flex", alignItems: "center", gap: 1, overflow: "hidden" }}>
          <Typography
            sx={{
              fontSize: "14px",
              fontWeight: 500,
              color: "var(--text-secondary)",
              whiteSpace: "nowrap",
            }}
          >
            Document Intake
          </Typography>
          <Typography sx={{ color: "var(--border-strong)", fontSize: "12px" }}>/</Typography>
          <Typography
            sx={{
              fontSize: "14px",
              fontWeight: 600,
              color: "var(--text-primary)",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {breadcrumb}
          </Typography>
          <Typography
            sx={{
              fontSize: "12px",
              color: "var(--text-secondary)",
              whiteSpace: "nowrap",
              display: { xs: "none", lg: "inline" },
            }}
          >
            — {subBreadcrumb}
          </Typography>
        </Box>
      </Box>

      {/* Center: Responsive tabs on smaller screens */}
      {isSmallScreen && onTabChange && (
        <Tabs
          value={activeTab}
          onChange={(_, val) => onTabChange(val)}
          sx={{
            minHeight: 36,
            "& .MuiTabs-indicator": {
              backgroundColor: "var(--accent)",
              height: 2,
            },
            "& .MuiTab-root": {
              minHeight: 36,
              py: 0,
              px: 1.5,
              fontSize: "12px",
              fontWeight: 500,
              textTransform: "none",
              color: "var(--text-secondary)",
              "&.Mui-selected": {
                color: "var(--text-primary)",
                fontWeight: 600,
              },
            },
          }}
        >
          <Tab label="Conversation" />
          <Tab label="Collected information" />
          <Tab label="Document preview" />
        </Tabs>
      )}

      {/* Right: Save status, Reset action, Delete action */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1.25, flexShrink: 0 }}>
        {isProcessing ? (
          <StatusIndicator status="processing" label="Processing..." size="small" />
        ) : isSaved ? (
          <StatusIndicator status="saved" label="Saved" size="small" />
        ) : (
          <StatusIndicator status="idle" label="Unsaved" size="small" />
        )}

        <Box sx={{ width: 1, height: 16, backgroundColor: "var(--border)", mx: 0.25 }} />

        <Button
          variant="secondary"
          onClick={onReset}
          loading={resetLoading}
          aria-label="Reset Session"
          startIcon={<RestartAltIcon sx={{ fontSize: 14 }} />}
          sx={{
            height: 32,
            minHeight: 32,
            py: "6px",
            px: "12px",
            gap: "8px",
            flexShrink: 0,
            whiteSpace: "nowrap",
            "& .MuiButton-startIcon": { mr: 0, ml: 0 },
          }}
        >
          Reset Session
        </Button>

        {onDeleteCurrentSession && (
          <Tooltip title="Delete intake">
            <span>
              <IconButton
                size="small"
                onClick={(e) => onDeleteCurrentSession(e.currentTarget)}
                aria-label="Delete intake"
                sx={{
                  width: 32,
                  height: 32,
                  minWidth: 32,
                  p: 0,
                  borderRadius: "var(--radius-xs, 4px)",
                  border: "1px solid var(--border)",
                  backgroundColor: "var(--surface)",
                  color: "var(--text-secondary)",
                  flexShrink: 0,
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
                }}
              >
                <DeleteOutlineIcon sx={{ fontSize: 16 }} />
              </IconButton>
            </span>
          </Tooltip>
        )}
      </Box>
    </Box>
  );
};

import React from "react";
import { Box, Typography, Tooltip, IconButton, Divider } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import { Button } from "../common/Button";

export interface SessionItem {
  id: string;
  name: string;
  date: string;
  isComplete?: boolean;
  isInitialized?: boolean;
}

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  currentSessionId: string;
  sessions: SessionItem[];
  onSelectSession: (id: string) => void;
  onNewIntake: () => void;
  onDeleteSession?: (id: string, triggerElement?: HTMLElement) => void;
  activeNav?: string;
  onSelectNav?: (nav: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  collapsed,
  onToggleCollapse,
  currentSessionId,
  sessions,
  onNewIntake,
  onSelectSession,
  onDeleteSession,
  activeNav = "intake",
  onSelectNav,
}) => {
  return (
    <Box
      sx={{
        width: collapsed ? 56 : 240,
        height: "100%",
        backgroundColor: "var(--surface-2)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        transition: "width var(--transition-normal)",
        flexShrink: 0,
        overflow: "hidden",
        position: "relative",
      }}
    >
      {/* Product Header */}
      <Box
        sx={{
          height: 48,
          display: "flex",
          alignItems: "center",
          justifyContent: collapsed ? "center" : "space-between",
          px: collapsed ? 1 : 2,
          borderBottom: "1px solid var(--border)",
          backgroundColor: "var(--surface)",
          flexShrink: 0,
        }}
      >
        {!collapsed && (
          <Typography
            sx={{
              fontSize: "14px",
              fontWeight: 600,
              color: "var(--text-primary)",
              whiteSpace: "nowrap",
            }}
          >
            Document Intake
          </Typography>
        )}

        <IconButton
          onClick={onToggleCollapse}
          size="small"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          sx={{
            width: 24,
            height: 24,
            display: { xs: "none", md: "inline-flex" },
          }}
        >
          {collapsed ? <ChevronRightIcon sx={{ fontSize: 16 }} /> : <ChevronLeftIcon sx={{ fontSize: 16 }} />}
        </IconButton>
      </Box>

      {/* New Intake Action */}
      <Box sx={{ p: 1.5, flexShrink: 0 }}>
        {collapsed ? (
          <Tooltip title="New Intake" placement="right">
            <IconButton
              onClick={onNewIntake}
              aria-label="New Intake"
              sx={{
                width: "100%",
                height: 32,
                backgroundColor: "var(--accent)",
                color: "#FFFFFF",
                borderRadius: "var(--radius-xs)",
                "&:hover": {
                  backgroundColor: "var(--accent-hover)",
                },
              }}
            >
              <AddIcon sx={{ fontSize: 18 }} />
            </IconButton>
          </Tooltip>
        ) : (
          <Button
            variant="primary"
            size="medium"
            fullWidth
            startIcon={<AddIcon sx={{ fontSize: 16 }} />}
            onClick={onNewIntake}
            aria-label="New Intake"
            sx={{ justifyContent: "center" }}
          >
            New Intake
          </Button>
        )}
      </Box>

      {/* Navigation Sections */}
      <Box
        sx={{
          flexGrow: 1,
          overflowY: "auto",
          px: 1,
          display: "flex",
          flexDirection: "column",
          gap: 1.5,
        }}
      >
        {/* Core Nav */}
        <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
          {!collapsed && (
            <Typography
              sx={{
                fontSize: "12px",
                fontWeight: 500,
                color: "var(--text-secondary)",
                px: 1,
                py: 0.5,
              }}
            >
              Workspace
            </Typography>
          )}

          <NavItem
            icon={<ChatBubbleOutlineIcon sx={{ fontSize: 16 }} />}
            label="Current Intake"
            active={activeNav === "intake"}
            collapsed={collapsed}
            onClick={() => onSelectNav?.("intake")}
          />

          <NavItem
            icon={<DescriptionOutlinedIcon sx={{ fontSize: 16 }} />}
            label="Documents"
            active={activeNav === "documents"}
            collapsed={collapsed}
            badge={`${sessions.length}`}
            onClick={() => onSelectNav?.("documents")}
          />
        </Box>

        {/* Sessions Section */}
        <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
          {!collapsed && (
            <Typography
              sx={{
                fontSize: "12px",
                fontWeight: 500,
                color: "var(--text-secondary)",
                px: 1,
                py: 0.5,
              }}
            >
              Intake sessions
            </Typography>
          )}

          {sessions.map((s) => {
            const isSelected = s.id === currentSessionId;
            return collapsed ? (
              <Tooltip key={s.id} title={`${s.name} (${s.date})`} placement="right">
                <Box
                  onClick={() => onSelectSession(s.id)}
                  sx={{
                    width: 36,
                    height: 32,
                    mx: "auto",
                    borderRadius: "var(--radius-xs)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: "pointer",
                    backgroundColor: isSelected ? "var(--surface-active)" : "transparent",
                    color: isSelected ? "var(--text-primary)" : "var(--text-secondary)",
                    border: isSelected ? "1px solid var(--border)" : "1px solid transparent",
                    "&:hover": {
                      backgroundColor: "var(--surface-hover)",
                      color: "var(--text-primary)",
                    },
                  }}
                >
                  <Typography sx={{ fontSize: "12px", fontWeight: isSelected ? 600 : 400 }}>
                    {s.name.slice(0, 1)}
                  </Typography>
                </Box>
              </Tooltip>
            ) : (
              <Box
                key={s.id}
                onClick={() => onSelectSession(s.id)}
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  px: 1.25,
                  py: 0.75,
                  borderRadius: "var(--radius-xs)",
                  cursor: "pointer",
                  backgroundColor: isSelected ? "var(--surface-active)" : "transparent",
                  color: isSelected ? "var(--text-primary)" : "var(--text-secondary)",
                  border: isSelected ? "1px solid var(--border)" : "1px solid transparent",
                  transition: "background-color var(--transition-fast)",
                  "&:hover": {
                    backgroundColor: "var(--surface-hover)",
                    color: "var(--text-primary)",
                  },
                  "&:hover .sidebar-delete-btn, &:focus-within .sidebar-delete-btn": {
                    opacity: 1,
                    visibility: "visible",
                  },
                }}
              >
                <Box sx={{ overflow: "hidden", pr: 1, minWidth: 0, flexGrow: 1 }}>
                  <Typography
                    sx={{
                      fontSize: "12px",
                      fontWeight: isSelected ? 600 : 400,
                      color: isSelected ? "var(--text-primary)" : "var(--text-secondary)",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {s.name}
                  </Typography>
                  <Typography
                    sx={{
                      fontSize: "12px",
                      color: "var(--text-secondary)",
                    }}
                  >
                    {s.date}
                  </Typography>
                </Box>

                {onDeleteSession && (
                  <Tooltip title="Delete intake">
                    <IconButton
                      className="sidebar-delete-btn"
                      size="small"
                      aria-label="Delete intake"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteSession(s.id, e.currentTarget);
                      }}
                      sx={{
                        color: "var(--text-secondary)",
                        p: { xs: 1, sm: 0.5 },
                        minWidth: { xs: 40, sm: 28 },
                        minHeight: { xs: 40, sm: 28 },
                        width: { xs: 40, sm: 28 },
                        height: { xs: 40, sm: 28 },
                        borderRadius: "var(--radius-xs, 4px)",
                        opacity: { xs: 1, sm: 0 },
                        visibility: { xs: "visible", sm: "hidden" },
                        flexShrink: 0,
                        "&:focus-visible": {
                          opacity: 1,
                          visibility: "visible",
                          outline: "2px solid #334155",
                          outlineOffset: 1,
                        },
                        "&:hover": {
                          color: "var(--text-primary)",
                          backgroundColor: "var(--surface-active)",
                        },
                      }}
                    >
                      <DeleteOutlineIcon sx={{ fontSize: 16 }} />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
            );
          })}
        </Box>
      </Box>

      {/* Settings Item */}
      <Box sx={{ px: 1, py: 1 }}>
        <NavItem
          icon={<SettingsOutlinedIcon sx={{ fontSize: 16 }} />}
          label="Settings"
          active={activeNav === "settings"}
          collapsed={collapsed}
          onClick={() => onSelectNav?.("settings")}
        />
      </Box>

      <Divider sx={{ borderColor: "var(--border)" }} />

      {/* Bottom Profile */}
      <Box
        sx={{
          p: collapsed ? 1 : 1.5,
          borderTop: "1px solid var(--border)",
          backgroundColor: "var(--surface)",
          display: "flex",
          alignItems: "center",
          gap: 1.25,
          flexShrink: 0,
        }}
      >
        <Box
          sx={{
            width: 28,
            height: 28,
            borderRadius: "var(--radius-xs)",
            backgroundColor: "var(--surface-3)",
            border: "1px solid var(--border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "12px",
            fontWeight: 500,
            color: "var(--text-primary)",
            flexShrink: 0,
          }}
        >
          JD
        </Box>

        {!collapsed && (
          <Box sx={{ overflow: "hidden", flexGrow: 1 }}>
            <Typography
              sx={{
                fontSize: "12px",
                fontWeight: 600,
                color: "var(--text-primary)",
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              Intake Counsel
            </Typography>
            <Typography
              sx={{
                fontSize: "12px",
                color: "var(--text-secondary)",
              }}
            >
              Session active
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
};

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  collapsed?: boolean;
  badge?: string;
  onClick?: () => void;
}

const NavItem: React.FC<NavItemProps> = ({
  icon,
  label,
  active,
  collapsed,
  badge,
  onClick,
}) => {
  const content = (
    <Box
      onClick={onClick}
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: collapsed ? "center" : "space-between",
        px: collapsed ? 1 : 1.25,
        py: 0.75,
        borderRadius: "var(--radius-xs)",
        cursor: "pointer",
        backgroundColor: active ? "var(--surface-active)" : "transparent",
        color: active ? "var(--text-primary)" : "var(--text-secondary)",
        border: active ? "1px solid var(--border)" : "1px solid transparent",
        transition: "background-color var(--transition-fast)",
        "&:hover": {
          backgroundColor: "var(--surface-hover)",
          color: "var(--text-primary)",
        },
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 1.25 }}>
        <Box sx={{ display: "flex", alignItems: "center", color: active ? "var(--text-primary)" : "inherit" }}>
          {icon}
        </Box>
        {!collapsed && (
          <Typography
            sx={{
              fontSize: "14px",
              fontWeight: active ? 600 : 400,
              color: "inherit",
              whiteSpace: "nowrap",
            }}
          >
            {label}
          </Typography>
        )}
      </Box>

      {!collapsed && badge && (
        <Box
          sx={{
            fontSize: "12px",
            px: 0.75,
            py: 0.1,
            borderRadius: "var(--radius-xs)",
            backgroundColor: "var(--surface-3)",
            color: "var(--text-secondary)",
          }}
        >
          {badge}
        </Box>
      )}
    </Box>
  );

  if (collapsed) {
    return (
      <Tooltip title={label} placement="right">
        {content}
      </Tooltip>
    );
  }

  return content;
};

import React from "react";
import { Box, Typography } from "@mui/material";
import { Sidebar, SessionItem } from "./Sidebar";
import { TopBar } from "./TopBar";

interface AppShellProps {
  children: React.ReactNode;
  breadcrumb: string;
  subBreadcrumb?: string;
  isProcessing?: boolean;
  onReset: () => void;
  resetLoading?: boolean;
  onDeleteSession?: (id: string, triggerElement?: HTMLElement) => void;
  onDeleteCurrentSession?: (triggerElement?: HTMLElement) => void;
  sidebarCollapsed: boolean;
  onToggleSidebar: () => void;
  currentSessionId: string;
  sessions: SessionItem[];
  onSelectSession: (id: string) => void;
  onNewIntake: () => void;
  activeTab?: number;
  onTabChange?: (tab: number) => void;
  isSmallScreen?: boolean;
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  breadcrumb,
  subBreadcrumb,
  isProcessing,
  onReset,
  resetLoading,
  onDeleteSession,
  onDeleteCurrentSession,
  sidebarCollapsed,
  onToggleSidebar,
  currentSessionId,
  sessions,
  onSelectSession,
  onNewIntake,
  activeTab,
  onTabChange,
  isSmallScreen,
}) => {
  return (
    <Box
      sx={{
        display: "flex",
        height: "100vh",
        width: "100vw",
        backgroundColor: "var(--background)",
        overflow: "hidden",
      }}
    >
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggleCollapse={onToggleSidebar}
        currentSessionId={currentSessionId}
        sessions={sessions}
        onSelectSession={onSelectSession}
        onNewIntake={onNewIntake}
        onDeleteSession={onDeleteSession}
      />

      {/* Main Content Area */}
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          flexGrow: 1,
          height: "100%",
          overflow: "hidden",
          backgroundColor: "var(--background)",
        }}
      >
        {/* TopBar */}
        <TopBar
          breadcrumb={breadcrumb}
          subBreadcrumb={subBreadcrumb}
          isProcessing={isProcessing}
          onReset={onReset}
          resetLoading={resetLoading}
          onDeleteCurrentSession={onDeleteCurrentSession}
          onToggleMobileMenu={onToggleSidebar}
          activeTab={activeTab}
          onTabChange={onTabChange}
          isSmallScreen={isSmallScreen}
        />

        {/* Informational Guidance Notice */}
        <Box
          sx={{
            backgroundColor: "var(--surface-3)",
            borderBottom: "1px solid var(--border)",
            px: 2,
            py: 0.5,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
            zIndex: 9,
          }}
        >
          <Typography
            sx={{
              fontSize: "12px",
              color: "var(--text-secondary)",
              fontWeight: 400,
              textAlign: "center",
            }}
          >
            Notice: This intake document is prepared for personal documentation and record-keeping; it does not constitute formal legal counsel.
          </Typography>
        </Box>

        {/* Workspace Container */}
        <Box
          sx={{
            flexGrow: 1,
            height: "100%",
            overflow: "hidden",
            position: "relative",
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

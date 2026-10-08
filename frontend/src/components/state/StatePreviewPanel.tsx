import React from "react";
import { Box, Typography, LinearProgress } from "@mui/material";
import { Panel } from "../layout/Panel";
import { PanelHeader } from "../layout/PanelHeader";
import { StateSection } from "./StateSection";
import { StateField } from "./StateField";
import { JsonViewer } from "./JsonViewer";
import type { PersonalWishesState, FieldStatus } from "../../types";

export interface StatePreviewPanelProps {
  state?: PersonalWishesState | null;
  missingFields?: string[];
  isComplete?: boolean;
  loading?: boolean;
}

export const StatePreviewPanel: React.FC<StatePreviewPanelProps> = ({
  state,
  missingFields = [],
}) => {
  // Safe fallback state matching domain model
  const safeState: PersonalWishesState = {
    full_name: state?.full_name ?? null,
    home_address: state?.home_address ?? null,
    covers_worldwide_assets: state?.covers_worldwide_assets ?? null,
    has_children: state?.has_children ?? null,
    children_names: state?.children_names ?? [],
    executor: {
      name: state?.executor?.name ?? null,
      relationship: state?.executor?.relationship ?? null,
    },
    has_specific_gifts: state?.has_specific_gifts ?? null,
    specific_gifts: state?.specific_gifts ?? [],
    additional_wishes: state?.additional_wishes ?? null,
    field_statuses: state?.field_statuses ?? {},
  };

  const getFieldStatus = (key: string, fallbackConfirmed: boolean): FieldStatus => {
    if (state?.field_statuses?.[key]) {
      return state.field_statuses[key];
    }
    return fallbackConfirmed ? "confirmed" : "unknown";
  };

  // Compute completion count dynamically from applicable fields
  // Skip children_names when has_children is false or unknown
  const applicableFieldKeys = [
    "full_name",
    "home_address",
    "covers_worldwide_assets",
    "has_children",
    ...(safeState.has_children === true ? ["children_names"] : []),
    "executor_name",
    "executor_relationship",
  ];

  const isFieldConfirmed = (key: string): boolean => {
    switch (key) {
      case "full_name":
        return Boolean(safeState.full_name) && getFieldStatus("full_name", true) === "confirmed";
      case "home_address":
        return Boolean(safeState.home_address) && getFieldStatus("home_address", true) === "confirmed";
      case "covers_worldwide_assets":
        return (
          safeState.covers_worldwide_assets !== null &&
          getFieldStatus("covers_worldwide_assets", true) === "confirmed"
        );
      case "has_children":
        return (
          safeState.has_children !== null &&
          getFieldStatus("has_children", true) === "confirmed"
        );
      case "children_names":
        return (
          safeState.has_children === true &&
          Array.isArray(safeState.children_names) &&
          safeState.children_names.length > 0 &&
          getFieldStatus("children_names", true) === "confirmed"
        );
      case "executor_name":
        return Boolean(safeState.executor.name) && getFieldStatus("executor_name", true) === "confirmed";
      case "executor_relationship":
        return (
          Boolean(safeState.executor.relationship) &&
          getFieldStatus("executor_relationship", true) === "confirmed"
        );
      default:
        return false;
    }
  };

  const confirmedCount = applicableFieldKeys.filter(isFieldConfirmed).length;
  const totalApplicable = applicableFieldKeys.length;
  const progressPercent = totalApplicable > 0 ? Math.round((confirmedCount / totalApplicable) * 100) : 0;

  return (
    <Panel borderRight sx={{ height: "100%" }}>
      {/* Header */}
      <PanelHeader
        title="Collected information"
      />

      <Box sx={{ flexGrow: 1, overflowY: "auto", p: 2 }}>
        {/* Dynamic Completeness Summary */}
        <Box sx={{ mb: 2.5, pb: 2, borderBottom: "1px solid var(--border)" }}>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              mb: 1,
            }}
          >
            <Typography
              sx={{
                fontSize: "12px",
                color: "var(--text-secondary)",
              }}
            >
              {confirmedCount} of {totalApplicable} fields confirmed
            </Typography>
            <Typography
              sx={{
                fontSize: "12px",
                color: "var(--text-secondary)",
              }}
            >
              {progressPercent}%
            </Typography>
          </Box>

          <LinearProgress
            variant="determinate"
            value={progressPercent}
            sx={{
              height: 2,
              borderRadius: 0,
              backgroundColor: "var(--border)",
              "& .MuiLinearProgress-bar": {
                backgroundColor: "var(--accent)",
              },
            }}
          />
        </Box>

        {/* 1. Principal identification */}
        <StateSection title="Principal identification">
          <StateField
            label="Full legal name"
            value={safeState.full_name || "Awaiting input..."}
            status={getFieldStatus("full_name", Boolean(safeState.full_name))}
            isMissing={missingFields.includes("full_name")}
          />
          <StateField
            label="Home address"
            value={safeState.home_address || "Awaiting input..."}
            status={getFieldStatus("home_address", Boolean(safeState.home_address))}
            isMissing={missingFields.includes("home_address")}
          />
          <StateField
            label="Worldwide asset scope"
            value={
              safeState.covers_worldwide_assets === true
                ? "Global (Worldwide Assets)"
                : safeState.covers_worldwide_assets === false
                ? "Domestic Jurisdiction Only"
                : "Awaiting input..."
            }
            status={getFieldStatus("covers_worldwide_assets", safeState.covers_worldwide_assets !== null)}
            isMissing={missingFields.includes("covers_worldwide_assets")}
          />
        </StateSection>

        {/* 2. Family and dependents */}
        <StateSection title="Family and dependents">
          <StateField
            label="Children or dependents"
            value={
              safeState.has_children === true
                ? "Yes (Has children)"
                : safeState.has_children === false
                ? "No children"
                : "Awaiting input..."
            }
            status={getFieldStatus("has_children", safeState.has_children !== null)}
            isMissing={missingFields.includes("has_children")}
          />
          {safeState.has_children !== false && (
            <StateField
              label="Children names"
              value={
                safeState.children_names && safeState.children_names.length > 0
                  ? safeState.children_names.join(", ")
                  : "Awaiting names..."
              }
              status={getFieldStatus(
                "children_names",
                Boolean(safeState.children_names && safeState.children_names.length > 0)
              )}
              isMissing={safeState.has_children === true && safeState.children_names.length === 0}
            />
          )}
        </StateSection>

        {/* 3. Appointed executor */}
        <StateSection title="Appointed executor">
          <StateField
            label="Executor legal name"
            value={safeState.executor.name || "Awaiting nomination..."}
            status={getFieldStatus("executor_name", Boolean(safeState.executor.name))}
            isMissing={missingFields.includes("executor_name")}
          />
          <StateField
            label="Relationship to principal"
            value={safeState.executor.relationship || "Awaiting clarification..."}
            status={getFieldStatus("executor_relationship", Boolean(safeState.executor.relationship))}
            isMissing={missingFields.includes("executor_relationship")}
          />
        </StateSection>

        {/* 4. Bequests and instructions */}
        <StateSection title="Bequests and instructions">
          <StateField
            label="Specific gifts or bequests"
            value={
              safeState.specific_gifts && safeState.specific_gifts.length > 0
                ? safeState.specific_gifts.join("; ")
                : "None recorded"
            }
            status={getFieldStatus(
              "has_specific_gifts",
              Boolean(safeState.specific_gifts && safeState.specific_gifts.length > 0)
            )}
          />
          <StateField
            label="Additional wishes"
            value={safeState.additional_wishes || "None recorded"}
            status={getFieldStatus("additional_wishes", Boolean(safeState.additional_wishes))}
          />
        </StateSection>

        {/* JSON Inspector */}
        <JsonViewer data={safeState} />
      </Box>
    </Panel>
  );
};

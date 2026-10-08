import React from "react";
import { Box, Skeleton, Stack } from "@mui/material";

interface LoadingStateProps {
  type?: "rows" | "document" | "chat";
  count?: number;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  type = "rows",
  count = 4,
}) => {
  if (type === "chat") {
    return (
      <Box sx={{ p: 2, display: "flex", flexDirection: "column", gap: 2 }}>
        <Skeleton
          variant="rectangular"
          height={38}
          sx={{
            borderRadius: "var(--radius-xs)",
            bgcolor: "rgba(0, 0, 0, 0.05)",
            maxWidth: "70%",
          }}
        />
        <Skeleton
          variant="rectangular"
          height={50}
          sx={{
            borderRadius: "var(--radius-xs)",
            bgcolor: "rgba(0, 0, 0, 0.05)",
            maxWidth: "85%",
            alignSelf: "flex-end",
          }}
        />
      </Box>
    );
  }

  if (type === "document") {
    return (
      <Box sx={{ p: 4, display: "flex", flexDirection: "column", gap: 2 }}>
        <Skeleton
          variant="text"
          width="40%"
          height={32}
          sx={{ bgcolor: "rgba(0, 0, 0, 0.06)" }}
        />
        <Skeleton
          variant="rectangular"
          height={60}
          sx={{ borderRadius: "var(--radius-xs)", bgcolor: "rgba(0, 0, 0, 0.04)" }}
        />
        <Skeleton
          variant="text"
          width="60%"
          height={24}
          sx={{ bgcolor: "rgba(0, 0, 0, 0.05)", mt: 2 }}
        />
        <Skeleton
          variant="rectangular"
          height={80}
          sx={{ borderRadius: "var(--radius-xs)", bgcolor: "rgba(0, 0, 0, 0.04)" }}
        />
        <Skeleton
          variant="rectangular"
          height={80}
          sx={{ borderRadius: "var(--radius-xs)", bgcolor: "rgba(0, 0, 0, 0.04)" }}
        />
      </Box>
    );
  }

  return (
    <Stack spacing={1.5} sx={{ p: 2 }}>
      {Array.from({ length: count }).map((_, i) => (
        <Box
          key={i}
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            p: 1.5,
            bgcolor: "var(--surface)",
            borderRadius: "var(--radius-xs)",
            border: "1px solid var(--border)",
          }}
        >
          <Box sx={{ width: "40%" }}>
            <Skeleton
              variant="text"
              width="70%"
              height={18}
              sx={{ bgcolor: "rgba(0, 0, 0, 0.06)" }}
            />
          </Box>
          <Skeleton
            variant="rectangular"
            width={72}
            height={20}
            sx={{ borderRadius: "var(--radius-xs)", bgcolor: "rgba(0, 0, 0, 0.05)" }}
          />
        </Box>
      ))}
    </Stack>
  );
};

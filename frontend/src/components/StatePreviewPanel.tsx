import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { IntakeState } from '../types';

interface StatePreviewPanelProps {
  state?: IntakeState | null;
}

export const StatePreviewPanel: React.FC<StatePreviewPanelProps> = ({ state }) => {
  // Safe defaults if state is null/undefined during initial boot
  const safeState: IntakeState = {
    full_name: state?.full_name ?? null,
    home_address: state?.home_address ?? null,
    covers_worldwide_assets: state?.covers_worldwide_assets ?? null,
    has_children: state?.has_children ?? null,
    children_names: state?.children_names ?? [],
    executor: {
      name: state?.executor?.name ?? null,
      relationship: state?.executor?.relationship ?? null,
    },
    specific_gifts: state?.specific_gifts ?? [],
    additional_wishes: state?.additional_wishes ?? null,
  };

  const renderStatusChip = (value: any) => {
    const isSet = value !== null && value !== undefined && value !== '';
    return isSet ? (
      <Chip
        icon={<CheckCircleIcon />}
        label="Confirmed"
        size="small"
        color="success"
        variant="outlined"
      />
    ) : (
      <Chip
        icon={<HelpOutlineIcon />}
        label="Pending"
        size="small"
        color="default"
        variant="outlined"
      />
    );
  };

  return (
    <Box sx={{ p: 2, height: '100%', overflowY: 'auto' }}>
      <Typography variant="h6" gutterBottom fontWeight={600}>
        Structured State
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Real-time view of verified personal data extracted by the intake engine.
      </Typography>

      <Paper variant="outlined" sx={{ p: 2, mb: 2, borderRadius: 2 }}>
        <List disablePadding>
          {/* Full Name */}
          <ListItem disableGutters secondaryAction={renderStatusChip(safeState.full_name)}>
            <ListItemText
              primary="Full Legal Name"
              secondary={safeState.full_name || 'Not provided'}
            />
          </ListItem>
          <Divider component="li" />

          {/* Home Address */}
          <ListItem disableGutters secondaryAction={renderStatusChip(safeState.home_address)}>
            <ListItemText
              primary="Home Address"
              secondary={safeState.home_address || 'Not provided'}
            />
          </ListItem>
          <Divider component="li" />

          {/* Worldwide Assets */}
          <ListItem
            disableGutters
            secondaryAction={renderStatusChip(safeState.covers_worldwide_assets)}
          >
            <ListItemText
              primary="Worldwide Asset Coverage"
              secondary={
                safeState.covers_worldwide_assets === true
                  ? 'Yes (Global)'
                  : safeState.covers_worldwide_assets === false
                  ? 'No (Domestic only)'
                  : 'Pending confirmation'
              }
            />
          </ListItem>
          <Divider component="li" />

          {/* Children */}
          <ListItem disableGutters secondaryAction={renderStatusChip(safeState.has_children)}>
            <ListItemText
              primary="Children / Dependents"
              secondary={
                safeState.has_children === true
                  ? safeState.children_names && safeState.children_names.length > 0
                    ? `Yes: ${safeState.children_names.join(', ')}`
                    : 'Yes (Names pending)'
                  : safeState.has_children === false
                  ? 'No children'
                  : 'Pending confirmation'
              }
            />
          </ListItem>
          <Divider component="li" />

          {/* Executor */}
          <ListItem
            disableGutters
            secondaryAction={renderStatusChip(safeState.executor?.name)}
          >
            <ListItemText
              primary="Appointed Executor"
              secondary={
                safeState.executor?.name
                  ? `${safeState.executor.name}${
                      safeState.executor.relationship
                        ? ` (${safeState.executor.relationship})`
                        : ''
                    }`
                  : 'Pending nomination'
              }
            />
          </ListItem>
          <Divider component="li" />

          {/* Specific Gifts */}
          <ListItem
            disableGutters
            secondaryAction={renderStatusChip(
              safeState.specific_gifts && safeState.specific_gifts.length > 0 ? true : null
            )}
          >
            <ListItemText
              primary="Specific Gifts / Bequests"
              secondary={
                safeState.specific_gifts && safeState.specific_gifts.length > 0
                  ? safeState.specific_gifts.join(', ')
                  : 'None declared'
              }
            />
          </ListItem>
          <Divider component="li" />

          {/* Additional Wishes */}
          <ListItem
            disableGutters
            secondaryAction={renderStatusChip(safeState.additional_wishes)}
          >
            <ListItemText
              primary="Additional Wishes"
              secondary={safeState.additional_wishes || 'None'}
            />
          </ListItem>
        </List>
      </Paper>

      {/* Raw JSON Inspector */}
      <Typography variant="subtitle2" sx={{ mb: 1 }} fontWeight={600}>
        Raw JSON Inspector
      </Typography>
      <Paper
        variant="outlined"
        sx={{
          p: 1.5,
          bgcolor: 'grey.50',
          fontFamily: 'monospace',
          fontSize: '0.8rem',
          borderRadius: 2,
          maxHeight: 220,
          overflowY: 'auto',
        }}
      >
        <pre style={{ margin: 0 }}>{JSON.stringify(safeState, null, 2)}</pre>
      </Paper>
    </Box>
  );
};
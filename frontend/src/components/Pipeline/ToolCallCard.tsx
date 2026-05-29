import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Box,
  Chip,
  Typography,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import type { PipelineStep } from '@/types/pipeline';

interface ToolCallCardProps {
  step: PipelineStep;
  defaultExpanded?: boolean;
}

function statusColor(status: string): 'default' | 'success' | 'error' | 'warning' {
  if (status === 'completed') return 'success';
  if (status === 'failed') return 'error';
  if (status === 'running') return 'warning';
  return 'default';
}

function summarize(step: PipelineStep): string {
  if (!step.output) return 'Awaiting result...';
  const out = step.output;

  // If tool returned an error object, show the error
  if (out.error) return `Error: ${String(out.error).slice(0, 80)}`;

  switch (step.tool) {
    case 'ingest_nav_package':
      return `Parsed ${(out.row_count as number)?.toLocaleString()} rows across ${out.column_count} columns`;
    case 'build_fund_profile':
      return `${out.fund_name} — ${out.fund_type} (${out.risk_tier} risk)`;
    case 'extract_market_context':
      return `Market regime: ${out.market_regime} — ${((out.key_indices as unknown[]) ?? []).length} indices`;
    case 'detect_anomalies':
      return `${out.anomalies_detected} anomalies found (score: ${((out.anomaly_score as number) * 100).toFixed(0)}%)`;
    case 'cross_validate_nav':
      return `NAV change: ${out.nav_change_bps} bps — ${out.cross_validation_status}`;
    case 'analyze_position_drivers':
      return `${out.total_positions} positions analyzed`;
    case 'score_exceptions':
      return `${out.total_exceptions} exceptions — ${out.review_time_savings_pct}% time saved`;
    case 'generate_review_pack':
      return `Recommendation: ${out.recommendation ?? 'Pending'}`;
    default:
      return 'Completed';
  }
}

const ToolCallCard = ({ step, defaultExpanded = false }: ToolCallCardProps) => (
  <Accordion defaultExpanded={defaultExpanded} disableGutters variant="outlined" sx={{ '&:before': { display: 'none' } }}>
    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap', width: '100%' }}>
        <Chip label={step.label} size="small" variant="outlined" color="secondary" />
        <Chip label={step.status} size="small" color={statusColor(step.status)} />
        {step.source && step.source !== 'live' && (
          <Chip label={step.source} size="small" variant="outlined" color="info" />
        )}
        <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }} noWrap>
          {summarize(step)}
        </Typography>
      </Box>
    </AccordionSummary>
    <AccordionDetails>
      {step.input && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" fontWeight={600} gutterBottom>
            Input
          </Typography>
          <Box
            component="pre"
            sx={{
              p: 1.5,
              borderRadius: 1,
              bgcolor: 'action.hover',
              overflow: 'auto',
              maxHeight: 200,
              fontSize: '0.75rem',
              fontFamily: 'monospace',
            }}
          >
            {JSON.stringify(step.input, null, 2)}
          </Box>
        </Box>
      )}
      {step.output && (
        <Box>
          <Typography variant="caption" fontWeight={600} gutterBottom>
            Output
          </Typography>
          <Box
            component="pre"
            sx={{
              p: 1.5,
              borderRadius: 1,
              bgcolor: 'action.hover',
              overflow: 'auto',
              maxHeight: 300,
              fontSize: '0.75rem',
              fontFamily: 'monospace',
            }}
          >
            {JSON.stringify(step.output, null, 2)}
          </Box>
        </Box>
      )}
    </AccordionDetails>
  </Accordion>
);

export default ToolCallCard;

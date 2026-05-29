import { Box, Paper, Skeleton, Typography } from '@mui/material';
import type { PipelineStep, ToolName } from '@/types/pipeline';
import NavDataViz from './visualizations/NavDataViz';
import FundProfileViz from './visualizations/FundProfileViz';
import MarketContextViz from './visualizations/MarketContextViz';
import AnomalyDetectionViz from './visualizations/AnomalyDetectionViz';
import CrossValidationViz from './visualizations/CrossValidationViz';
import PositionDriversViz from './visualizations/PositionDriversViz';
import ExceptionScoringViz from './visualizations/ExceptionScoringViz';
import ReviewPackViz from './visualizations/ReviewPackViz';

interface DataVisualizationPanelProps {
  steps: PipelineStep[];
  activeStepIndex: number;
}

const vizComponents: Record<ToolName, React.FC<{ output: Record<string, unknown> }>> = {
  ingest_nav_package: NavDataViz,
  build_fund_profile: FundProfileViz,
  extract_market_context: MarketContextViz,
  detect_anomalies: AnomalyDetectionViz,
  cross_validate_nav: CrossValidationViz,
  analyze_position_drivers: PositionDriversViz,
  score_exceptions: ExceptionScoringViz,
  generate_review_pack: ReviewPackViz,
};

const DataVisualizationPanel = ({ steps, activeStepIndex }: DataVisualizationPanelProps) => {
  const step = steps[activeStepIndex];

  if (!step) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
        <Typography color="text.secondary">Waiting for review to start...</Typography>
      </Box>
    );
  }

  if (step.status === 'pending') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
        <Typography color="text.secondary">
          {step.label} — waiting to execute
        </Typography>
      </Box>
    );
  }

  if (step.status === 'running' && !step.output) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom>{step.label}</Typography>
        <Skeleton variant="rectangular" height={120} sx={{ borderRadius: 1, mb: 1 }} />
        <Skeleton variant="rectangular" height={80} sx={{ borderRadius: 1, mb: 1 }} />
        <Skeleton variant="rectangular" height={60} sx={{ borderRadius: 1 }} />
      </Box>
    );
  }

  if (!step.output) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
        <Typography color="text.secondary">No data available for {step.label}</Typography>
      </Box>
    );
  }

  if ('error' in step.output) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle1" color="error" gutterBottom>{step.label} — Error</Typography>
        <Typography color="error">{String(step.output.error)}</Typography>
      </Box>
    );
  }

  const VizComponent = vizComponents[step.tool];

  return (
    <Paper
      variant="outlined"
      sx={{ p: 2, overflow: 'auto', maxHeight: 'calc(100vh - 280px)' }}
    >
      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
        {step.label}
      </Typography>
      <VizComponent output={step.output} />
    </Paper>
  );
};

export default DataVisualizationPanel;

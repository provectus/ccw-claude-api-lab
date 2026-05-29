import { useState, useCallback, useEffect, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Grid2,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import AssessmentIcon from '@mui/icons-material/Assessment';
import HistoryIcon from '@mui/icons-material/History';
import { usePipelineStore, deriveSteps, deriveCurrentStepIndex } from '@/stores/pipelineStore';
import { usePipelineStream } from '@/hooks/usePipelineStream';
import { runPipeline, getScenarios, getPipelineEvents } from '@/services/api';
import type { DemoScenario, PipelineSSEEvent, PipelineStatus } from '@/types/pipeline';
import ProgressStepper from './ProgressStepper';
import AgentReasoningPanel from './AgentReasoningPanel';
import DataVisualizationPanel from './DataVisualizationPanel';

function statusChipColor(status: PipelineStatus): 'default' | 'info' | 'success' | 'error' {
  switch (status) {
    case 'running': return 'info';
    case 'completed': return 'success';
    case 'failed': return 'error';
    default: return 'default';
  }
}


const PipelineExecutionPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const { pipelineId: urlPipelineId } = useParams<{ pipelineId?: string }>();

  const storePipelineId = usePipelineStore((s) => s.pipelineId);
  const status = usePipelineStore((s) => s.status);
  const errorMessage = usePipelineStore((s) => s.errorMessage);
  const startPipeline = usePipelineStore((s) => s.startPipeline);
  const appendEvent = usePipelineStore((s) => s.appendEvent);
  const events = usePipelineStore((s) => s.events);

  // Historical mode: URL has a pipeline ID that differs from the live store
  const isHistorical = !!urlPipelineId && urlPipelineId !== storePipelineId;
  const effectivePipelineId = urlPipelineId ?? storePipelineId;

  // Derive steps from events via useMemo (not Zustand selectors) to avoid
  // infinite re-render from new array references on each snapshot check
  const steps = useMemo(() => deriveSteps(events), [events]);
  const currentStepIndex = useMemo(() => deriveCurrentStepIndex(events), [events]);
  const isTerminal = status === 'completed' || status === 'failed';

  const { connectionState } = usePipelineStream({
    pipelineId: isHistorical ? null : storePipelineId,
    enabled: !isTerminal && !isHistorical,
  });

  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [launching, setLaunching] = useState(false);
  const [scenario, setScenario] = useState<DemoScenario | null>(null);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Load historical pipeline events when viewing a past run
  useEffect(() => {
    if (!isHistorical || !urlPipelineId) return;
    setLoadingHistory(true);
    getPipelineEvents(urlPipelineId)
      .then((res) => {
        startPipeline(urlPipelineId);
        for (const event of res.data.events as PipelineSSEEvent[]) {
          appendEvent(event);
        }
      })
      .catch((err) => {
        console.error('Failed to load historical pipeline:', err);
      })
      .finally(() => setLoadingHistory(false));
    // Only run when urlPipelineId changes — startPipeline/appendEvent are stable refs
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlPipelineId]);

  // Track current step for auto-follow
  useEffect(() => {
    if (!isTerminal) {
      setActiveStepIndex(currentStepIndex);
    }
  }, [currentStepIndex, isTerminal]);

  // Load scenario on mount
  useEffect(() => {
    getScenarios().then((res) => {
      const scenarios = res.data.scenarios;
      if (scenarios.length > 0) {
        setScenario(scenarios[0]);
      }
    }).catch(() => {
      // Scenarios endpoint may not be available
    });
  }, []);

  const handleLaunch = useCallback(async () => {
    if (!scenario) return;
    setLaunching(true);
    try {
      const res = await runPipeline({
        file_paths: scenario.file_paths,
        fund_metadata: scenario.fund_metadata,
      });
      startPipeline(res.data.pipeline_id);
      setActiveStepIndex(0);
      // Navigate to the new pipeline URL
      navigate(`/review/${res.data.pipeline_id}`, { replace: true });
    } catch (err) {
      console.error('Failed to launch pipeline:', err);
    } finally {
      setLaunching(false);
    }
  }, [scenario, startPipeline, navigate]);

  const handleStepClick = useCallback((index: number) => {
    setActiveStepIndex(index);
  }, []);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 100px)' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
        <Typography variant="h5" fontWeight={600}>Pipeline Execution</Typography>

        {effectivePipelineId && (
          <>
            <Chip
              label={
                isHistorical
                  ? status
                  : status === 'running' && connectionState === 'connected'
                    ? 'Running (Live)'
                    : status === 'running' && connectionState === 'reconnecting'
                      ? 'Reconnecting...'
                      : status
              }
              color={statusChipColor(status)}
              size="small"
            />
            {isHistorical && (
              <Chip icon={<HistoryIcon />} label="Historical" size="small" variant="outlined" />
            )}
          </>
        )}

        <Box sx={{ ml: 'auto', display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            color="secondary"
            startIcon={launching ? <CircularProgress size={16} color="inherit" /> : <PlayArrowIcon />}
            onClick={handleLaunch}
            disabled={launching || (status === 'running')}
          >
            {scenario ? `Launch: ${scenario.name}` : 'No scenario available'}
          </Button>

          {isTerminal && status === 'completed' && effectivePipelineId && (
            <Button
              variant="outlined"
              startIcon={<AssessmentIcon />}
              onClick={() => navigate(`/review-pack/${effectivePipelineId}`)}
            >
              View Assessment
            </Button>
          )}
        </Box>
      </Box>

      {/* Error banner */}
      {errorMessage && status === 'failed' && (
        <Box sx={{ mb: 1, p: 1.5, bgcolor: 'error.main', color: 'error.contrastText', borderRadius: 1 }}>
          <Typography variant="body2">{errorMessage}</Typography>
        </Box>
      )}

      {/* Main content: dual panel */}
      {loadingHistory ? (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1 }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress color="secondary" size={40} sx={{ mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
              Loading pipeline history...
            </Typography>
          </Box>
        </Box>
      ) : !effectivePipelineId ? (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1 }}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No active pipeline
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Click the launch button to start a demo scenario.
            </Typography>
          </Box>
        </Box>
      ) : (
        <>
          <Box sx={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
            <Grid2 container spacing={2} sx={{ height: '100%' }}>
              <Grid2
                size={{ xs: 12, md: 5 }}
                sx={{ height: isMobile ? 'auto' : '100%', overflow: 'auto' }}
              >
                <AgentReasoningPanel
                  steps={steps}
                  currentStepIndex={activeStepIndex}
                  onStepClick={handleStepClick}
                />
              </Grid2>
              <Grid2
                size={{ xs: 12, md: 7 }}
                sx={{ height: isMobile ? 'auto' : '100%', overflow: 'auto' }}
              >
                <DataVisualizationPanel
                  steps={steps}
                  activeStepIndex={activeStepIndex}
                />
              </Grid2>
            </Grid2>
          </Box>

          {/* Bottom stepper */}
          <Box sx={{ mt: 1, borderTop: 1, borderColor: 'divider', pt: 1 }}>
            <ProgressStepper
              steps={steps}
              currentStepIndex={activeStepIndex}
              onStepClick={handleStepClick}
            />
          </Box>
        </>
      )}
    </Box>
  );
};

export default PipelineExecutionPage;

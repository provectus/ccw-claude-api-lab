import { useEffect, useRef, useState, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Typography,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import TimelineIcon from '@mui/icons-material/Timeline';
import type { AxiosError } from 'axios';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ReviewPack, PipelineSSEEvent } from '@/types/pipeline';
import { usePipelineStore } from '@/stores/pipelineStore';
import { getPipelineAssessment, getPipelineStatus } from '@/services/api';
import { formatDollars } from '@/utils/format';
import RecommendationBadge from '@/components/common/RecommendationBadge';
import ConfidenceBar from '@/components/common/ConfidenceBar';
// Legacy sub-components available but not used in NAV review flow
// import CohortAnalyticsGrid from './CohortAnalyticsGrid';
// import RiskTable from './RiskTable';
// import DataGapsTable from './DataGapsTable';
// import SensitivityTornado from './SensitivityTornado';

/** Normalize recommendation strings from Claude to our Recommendation type. */
function normalizeRecommendation(raw: string): ReviewPack['recommendation'] {
  const upper = String(raw ?? '').toUpperCase().replace(/[\s-]+/g, '_');
  if (upper === 'APPROVE') return 'APPROVE';
  if (upper.includes('EXCEPTION')) return 'APPROVE_WITH_EXCEPTIONS';
  if (upper.includes('ESCALATE')) return 'ESCALATE';
  if (upper.includes('HOLD')) return 'HOLD';
  return 'APPROVE_WITH_EXCEPTIONS';
}

const ReviewPackPage = () => {
  const navigate = useNavigate();
  const { pipelineId: urlPipelineId } = useParams<{ pipelineId?: string }>();

  const storeAssessment = usePipelineStore((s) => s.assessment);
  const storePipelineId = usePipelineStore((s) => s.pipelineId);
  const events = usePipelineStore((s) => s.events);

  // Use URL param if provided, otherwise fall back to store
  const effectivePipelineId = urlPipelineId ?? storePipelineId;
  // Only use store assessment if viewing the same pipeline that's in the store
  const useStoreData = !urlPipelineId || urlPipelineId === storePipelineId;

  const [restAssessment, setRestAssessment] = useState<ReviewPack | null>(null);
  const [narrative, setNarrative] = useState<string[]>([]);
  const [, setRestToolOutputs] = useState<Record<string, Record<string, unknown>>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [waitingForCompletion, setWaitingForCompletion] = useState(false);
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Stop polling on unmount
  useEffect(() => {
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, []);

  // Fetch from REST if store doesn't have assessment or viewing a different pipeline
  useEffect(() => {
    if (useStoreData && storeAssessment) return;
    if (!effectivePipelineId) return;
    setLoading(true);
    setRestAssessment(null);
    setNarrative([]);
    setRestToolOutputs({});
    setError(null);
    setWaitingForCompletion(false);
    getPipelineAssessment(effectivePipelineId)
      .then((res) => {
        if (res.data.assessment) setRestAssessment(res.data.assessment);
        if (res.data.narrative) setNarrative(res.data.narrative);
        if (res.data.tool_outputs) setRestToolOutputs(res.data.tool_outputs);
      })
      .catch((err) => {
        const axiosErr = err as AxiosError;
        if (axiosErr.response?.status === 409) {
          // Pipeline still running — start polling
          setWaitingForCompletion(true);
        } else {
          setError(err instanceof Error ? err.message : 'Failed to load assessment');
        }
      })
      .finally(() => setLoading(false));
  }, [useStoreData, storeAssessment, effectivePipelineId]);

  // Poll for completion when pipeline is still running
  useEffect(() => {
    if (!waitingForCompletion || !effectivePipelineId) return;
    if (pollTimerRef.current) clearInterval(pollTimerRef.current);

    pollTimerRef.current = setInterval(() => {
      getPipelineStatus(effectivePipelineId)
        .then((res) => {
          if (res.data.status === 'completed' || res.data.status === 'failed') {
            setWaitingForCompletion(false);
            if (pollTimerRef.current) clearInterval(pollTimerRef.current);
            // Re-fetch assessment
            setLoading(true);
            getPipelineAssessment(effectivePipelineId)
              .then((aRes) => {
                if (aRes.data.assessment) setRestAssessment(aRes.data.assessment);
                if (aRes.data.narrative) setNarrative(aRes.data.narrative);
                if (aRes.data.tool_outputs) setRestToolOutputs(aRes.data.tool_outputs);
              })
              .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load assessment'))
              .finally(() => setLoading(false));
          }
        })
        .catch(() => {
          // Ignore polling errors — will retry next interval
        });
    }, 3000);

    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, [waitingForCompletion, effectivePipelineId]);

  const assessment = (useStoreData ? storeAssessment : null) ?? restAssessment;

  const storeEvents = useStoreData ? events : [];

  // Build narrative from reasoning events if REST narrative is empty
  const displayNarrative = useMemo(() => {
    if (narrative.length > 0) return narrative;
    // Fallback: collect reasoning from store events (only if same pipeline)
    return storeEvents
      .filter((e: PipelineSSEEvent): e is Extract<PipelineSSEEvent, { type: 'reasoning' }> => e.type === 'reasoning')
      .slice(-3)
      .map((e) => e.text);
  }, [narrative, storeEvents]);

  // Empty state
  if (!assessment && !loading && !error) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No Assessment Available
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Run a pipeline first to generate a deal assessment.
        </Typography>
        <Button
          variant="contained"
          color="secondary"
          startIcon={<UploadFileIcon />}
          onClick={() => navigate('/upload')}
        >
          Upload Files
        </Button>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box>
        <Skeleton height={40} width={300} />
        <Skeleton height={24} width="60%" sx={{ mt: 1 }} />
        <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} variant="rectangular" height={80} sx={{ flex: 1, borderRadius: 1 }} />
          ))}
        </Box>
      </Box>
    );
  }

  if (waitingForCompletion) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <CircularProgress color="secondary" size={40} sx={{ mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Pipeline is still running...
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          The assessment will load automatically when the pipeline completes.
        </Typography>
        <Button
          variant="outlined"
          startIcon={<TimelineIcon />}
          onClick={() => navigate(effectivePipelineId ? `/pipeline/${effectivePipelineId}` : '/pipeline')}
        >
          View Live Pipeline
        </Button>
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!assessment) return null;

  const summary = assessment.executive_summary;
  const recommendation = normalizeRecommendation(assessment.recommendation);

  return (
    <Box sx={{ maxWidth: 1100, mx: 'auto' }}>
      {/* Header: Recommendation + Confidence */}
      <Box sx={{ display: 'flex', gap: 3, mb: 3, alignItems: 'center', flexWrap: 'wrap' }}>
        <Box>
          <Typography variant="h5" fontWeight={600} gutterBottom>
            Deal Assessment
          </Typography>
          <RecommendationBadge recommendation={recommendation} />
        </Box>
        <Box sx={{ minWidth: 250, flex: 1, maxWidth: 400 }}>
          <Typography variant="caption" color="text.secondary">Confidence</Typography>
          <ConfidenceBar value={assessment.confidence} label={assessment.confidence_level} />
        </Box>
      </Box>

      {/* Executive narrative (rendered as Markdown) */}
      {displayNarrative.length > 0 && (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent sx={{
            '& h1, & h2, & h3, & h4': { mt: 1.5, mb: 0.5, fontSize: '0.95rem', fontWeight: 600 },
            '& p': { fontSize: '0.875rem', lineHeight: 1.6, mb: 1 },
            '& ul, & ol': { pl: 2.5, mb: 1 },
            '& li': { fontSize: '0.875rem', mb: 0.25 },
            '& table': { width: '100%', borderCollapse: 'collapse', mb: 1, fontSize: '0.8125rem' },
            '& th, & td': { border: '1px solid', borderColor: 'divider', px: 1, py: 0.5, textAlign: 'left' },
            '& th': { fontWeight: 600, bgcolor: 'action.hover' },
            '& strong': { fontWeight: 600 },
            '& hr': { my: 1.5, borderColor: 'divider' },
          }}>
            <Typography variant="subtitle2" gutterBottom>Executive Summary</Typography>
            <Markdown remarkPlugins={[remarkGfm]}>{displayNarrative.join('\n\n')}</Markdown>
          </CardContent>
        </Card>
      )}

      {/* Key metrics cards */}
      {summary && (
        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          {[
            { label: 'Total NAV', value: summary.total_nav != null ? formatDollars(summary.total_nav) : '—' },
            { label: 'NAV Change', value: summary.nav_change_bps != null ? `${summary.nav_change_bps} bps` : '—' },
            { label: 'Data Quality', value: summary.data_quality_score != null ? `${(summary.data_quality_score * 100).toFixed(0)}%` : '—' },
            { label: 'Exceptions', value: summary.total_exceptions != null ? `${summary.total_exceptions} (${summary.critical_exceptions} critical)` : '—' },
            { label: 'Auto-Resolved', value: summary.auto_resolved != null ? String(summary.auto_resolved) : '—' },
          ].map((item) => (
            <Card key={item.label} variant="outlined" sx={{ flex: 1, minWidth: 130 }}>
              <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Typography variant="caption" color="text.secondary">{item.label}</Typography>
                <Typography variant="h6" fontWeight={700}>{item.value}</Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      <Divider sx={{ mb: 3 }} />

      {/* Key Variances */}
      {assessment.key_variances?.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Key Variances</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Driver</TableCell>
                  <TableCell align="right">Impact (bps)</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Explanation</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {assessment.key_variances.map((v: { driver: string; impact_bps: number; status: string; explanation: string }, i: number) => (
                  <TableRow key={i} hover>
                    <TableCell sx={{ fontWeight: 500 }}>{v.driver}</TableCell>
                    <TableCell align="right">{v.impact_bps}</TableCell>
                    <TableCell>
                      <Chip label={v.status} size="small" color={v.status === 'EXPLAINED' ? 'success' : 'warning'} variant="outlined" />
                    </TableCell>
                    <TableCell sx={{ fontSize: '0.8125rem' }}>{v.explanation}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Exception Summary */}
      {assessment.exception_summary?.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Exceptions</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Disposition</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {assessment.exception_summary.map((e: { id: string; priority: string; description: string; disposition: string }, i: number) => (
                  <TableRow key={i} hover>
                    <TableCell sx={{ fontFamily: 'monospace' }}>{e.id}</TableCell>
                    <TableCell>
                      <Chip label={e.priority} size="small" color={e.priority === 'HIGH' ? 'error' : e.priority === 'MEDIUM' ? 'warning' : 'default'} />
                    </TableCell>
                    <TableCell>{e.description}</TableCell>
                    <TableCell sx={{ fontSize: '0.8125rem' }}>{e.disposition}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Conditions for Approval */}
      {assessment.conditions_for_approval?.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Conditions for Approval</Typography>
          <Card variant="outlined">
            <CardContent>
              {assessment.conditions_for_approval.map((c: string, i: number) => (
                <Typography key={i} variant="body2" sx={{ mb: 0.5, pl: 1 }}>
                  {i + 1}. {c}
                </Typography>
              ))}
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Next Steps */}
      {assessment.next_steps?.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Next Steps</Typography>
          <Card variant="outlined">
            <CardContent>
              {assessment.next_steps.map((step, i) => (
                <Typography key={i} variant="body2" sx={{ mb: 0.5, pl: 1 }}>
                  {i + 1}. {step}
                </Typography>
              ))}
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
};

export default ReviewPackPage;

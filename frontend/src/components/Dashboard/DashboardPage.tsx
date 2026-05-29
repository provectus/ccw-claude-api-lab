import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import TimelineIcon from '@mui/icons-material/Timeline';
import type { DashboardStats } from '@/types';
import type { PipelineRunSummary, PipelineStatus, Recommendation } from '@/types/pipeline';
import { getStats, listPipelines } from '@/services/api';
import { formatNumber } from '@/utils/format';
import RecommendationBadge from '@/components/common/RecommendationBadge';

function formatDuration(seconds: number): string {
  if (seconds <= 0) return '\u2014';
  const min = Math.floor(seconds / 60);
  const sec = Math.round(seconds % 60);
  if (min === 0) return `${sec}s`;
  return `${min}m ${sec}s`;
}

function durationBetween(start: string, end: string | null): string {
  if (!end) return '\u2014';
  const ms = new Date(end).getTime() - new Date(start).getTime();
  if (isNaN(ms) || ms < 0) return '\u2014';
  return formatDuration(ms / 1000);
}

function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

const statusChipColor: Record<PipelineStatus, 'default' | 'info' | 'success' | 'error'> = {
  pending: 'default',
  running: 'info',
  completed: 'success',
  failed: 'error',
};

function normalizeRecommendation(raw: string | null): Recommendation | null {
  if (!raw) return null;
  const upper = raw.toUpperCase().replace(/[\s-]+/g, '_');
  if (upper === 'APPROVE') return 'APPROVE';
  if (upper.includes('EXCEPTION')) return 'APPROVE_WITH_EXCEPTIONS';
  if (upper.includes('ESCALATE')) return 'ESCALATE';
  if (upper.includes('HOLD')) return 'HOLD';
  return 'APPROVE_WITH_EXCEPTIONS';
}

const DashboardPage = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [pipelines, setPipelines] = useState<PipelineRunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getStats(), listPipelines()])
      .then(([statsRes, pipelinesRes]) => {
        setStats(statsRes.data);
        setPipelines(pipelinesRes.data.pipelines);
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load data'))
      .finally(() => setLoading(false));
  }, []);

  const cards = stats
    ? [
        { label: 'Reviews Run', value: formatNumber(stats.pipelines_run) },
        { label: 'Files Processed', value: formatNumber(stats.files_processed) },
        { label: 'Positions Reviewed', value: formatNumber(stats.records_validated) },
        { label: 'Avg Review Time', value: formatDuration(stats.avg_completion_time_seconds) },
      ]
    : [];

  return (
    <Box>
      <Typography variant="h5" fontWeight={600} gutterBottom>
        Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
      )}

      {/* Stat cards */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        {loading
          ? Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} variant="outlined" sx={{ flex: 1, minWidth: 180 }}>
                <CardContent sx={{ py: 2, '&:last-child': { pb: 2 } }}>
                  <Skeleton width={100} height={18} />
                  <Skeleton width={60} height={32} sx={{ mt: 0.5 }} />
                </CardContent>
              </Card>
            ))
          : cards.map((card) => (
              <Card key={card.label} variant="outlined" sx={{ flex: 1, minWidth: 180 }}>
                <CardContent sx={{ py: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="caption" color="text.secondary">
                    {card.label}
                  </Typography>
                  <Typography variant="h5" fontWeight={700}>
                    {card.value}
                  </Typography>
                </CardContent>
              </Card>
            ))}
      </Box>

      {/* Pipeline run history */}
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent sx={{ pb: '16px !important' }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            NAV Review History
          </Typography>

          {loading ? (
            <Box>
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} height={40} sx={{ mb: 0.5 }} />
              ))}
            </Box>
          ) : pipelines.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
              No NAV reviews yet. Upload fund data to get started.
            </Typography>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Fund</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Recommendation</TableCell>
                    <TableCell align="right">Quality</TableCell>
                    <TableCell>Started</TableCell>
                    <TableCell align="right">Duration</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {pipelines.map((p) => {
                    const rec = normalizeRecommendation(p.recommendation);
                    return (
                      <TableRow
                        key={p.id}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => navigate(`/review/${p.id}`)}
                      >
                        <TableCell sx={{ fontWeight: 500 }}>
                          {p.fund_name}
                          {p.fund_type && (
                            <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                              {p.fund_type}
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={p.status}
                            color={statusChipColor[p.status]}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          {rec ? (
                            <RecommendationBadge recommendation={rec} size="small" />
                          ) : (
                            '\u2014'
                          )}
                        </TableCell>
                        <TableCell align="right">
                          {p.data_quality_score != null
                            ? `${(p.data_quality_score * 100).toFixed(0)}%`
                            : '\u2014'}
                        </TableCell>
                        <TableCell>{formatTimestamp(p.created_at)}</TableCell>
                        <TableCell align="right">
                          {durationBetween(p.created_at, p.completed_at)}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Quick actions */}
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          color="secondary"
          startIcon={<UploadFileIcon />}
          onClick={() => navigate('/upload')}
        >
          Upload Files
        </Button>
        <Button
          variant="outlined"
          startIcon={<TimelineIcon />}
          onClick={() => navigate('/review')}
        >
          View Reviews
        </Button>
      </Box>
    </Box>
  );
};

export default DashboardPage;

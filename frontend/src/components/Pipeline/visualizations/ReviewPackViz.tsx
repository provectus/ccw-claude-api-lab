import { Box, Card, CardContent, Chip, Grid2, List, ListItem, ListItemText, Typography } from '@mui/material';

const ReviewPackViz = ({ output }: { output: Record<string, unknown> }) => {
  const summary = (output.executive_summary || {}) as Record<string, unknown>;
  const variances = (output.key_variances || []) as Array<Record<string, unknown>>;
  const conditions = (output.conditions_for_approval || []) as string[];
  const metrics = (output.review_metrics || {}) as Record<string, unknown>;
  const recommendation = String(output.recommendation || '');
  const confidence = Number(output.confidence || 0);

  const recColor = recommendation === 'APPROVE' ? 'success'
    : recommendation === 'APPROVE_WITH_EXCEPTIONS' ? 'warning'
    : recommendation === 'ESCALATE' ? 'error'
    : 'default';

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 2, mb: 3, alignItems: 'center' }}>
        <Chip
          label={recommendation.replace(/_/g, ' ')}
          color={recColor as 'success' | 'warning' | 'error' | 'default'}
          sx={{ fontSize: '1rem', fontWeight: 700, px: 2, py: 2.5 }}
        />
        <Box>
          <Typography variant="caption" color="text.secondary">Confidence</Typography>
          <Typography variant="body1" fontWeight={600}>{(confidence * 100).toFixed(0)}% ({String(output.confidence_level)})</Typography>
        </Box>
      </Box>

      <Grid2 container spacing={2} sx={{ mb: 2 }}>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined">
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">Fund</Typography>
              <Typography variant="body2" fontWeight={600}>{String(summary.fund_name)}</Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined">
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">Total NAV</Typography>
              <Typography variant="body2" fontWeight={600}>${(Number(summary.total_nav) / 1_000_000).toFixed(0)}M</Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined">
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">NAV Change</Typography>
              <Typography variant="body2" fontWeight={600}>{Number(summary.nav_change_bps)} bps</Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined">
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">Exceptions</Typography>
              <Typography variant="body2" fontWeight={600}>
                {String(summary.total_exceptions)} ({String(summary.critical_exceptions)} critical)
              </Typography>
            </CardContent>
          </Card>
        </Grid2>
      </Grid2>

      {variances.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Key Variances</Typography>
          {variances.map((v, i) => (
            <Card key={i} variant="outlined" sx={{ mb: 1, p: 1.5 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                <Typography variant="body2" fontWeight={600}>{String(v.driver)}</Typography>
                <Chip label={String(v.status)} size="small"
                  color={v.status === 'EXPLAINED' ? 'success' : 'warning'} variant="outlined" />
              </Box>
              <Typography variant="body2" color="text.secondary">{String(v.explanation)}</Typography>
            </Card>
          ))}
        </Box>
      )}

      {conditions.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Conditions for Approval</Typography>
          <List dense>
            {conditions.map((c, i) => (
              <ListItem key={i} sx={{ py: 0 }}>
                <ListItemText primary={c} primaryTypographyProps={{ variant: 'body2' }} />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {metrics.review_time_savings_pct ? (
        <Typography variant="body2" color="text.secondary">
          Estimated review time: {String(metrics.estimated_review_time_minutes)} min
          (saved {String(metrics.review_time_savings_pct)}% vs {String(metrics.baseline_review_time_minutes)} min baseline)
        </Typography>
      ) : null}
    </Box>
  );
};

export default ReviewPackViz;

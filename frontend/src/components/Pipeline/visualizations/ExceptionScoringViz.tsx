import { Box, Card, CardContent, Chip, Grid2, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';

const ExceptionScoringViz = ({ output }: { output: Record<string, unknown> }) => {
  const queue = (output.exception_queue || []) as Array<Record<string, unknown>>;
  const byPriority = (output.exceptions_by_priority || {}) as Record<string, number>;

  return (
    <Box>
      <Grid2 container spacing={2} sx={{ mb: 2 }}>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined">
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">Total Exceptions</Typography>
              <Typography variant="h5" fontWeight={700}>{String(output.total_exceptions)}</Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined">
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">Review Time</Typography>
              <Typography variant="h5" fontWeight={700}>{String(output.estimated_review_time_minutes)} min</Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined" sx={{ bgcolor: 'success.50' }}>
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">Time Saved</Typography>
              <Typography variant="h5" fontWeight={700} color="success.main">{String(output.review_time_savings_pct)}%</Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined">
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">Auto-Resolved</Typography>
              <Typography variant="h5" fontWeight={700}>{String(output.auto_resolvable_count)}</Typography>
            </CardContent>
          </Card>
        </Grid2>
      </Grid2>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Chip label={`HIGH: ${byPriority.high || 0}`} color="error" size="small" />
        <Chip label={`MEDIUM: ${byPriority.medium || 0}`} color="warning" size="small" />
        <Chip label={`LOW: ${byPriority.low || 0}`} size="small" />
      </Box>

      <Typography variant="subtitle2" gutterBottom>Exception Queue (ranked)</Typography>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>#</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="right">Impact (bps)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {queue.map((item) => {
              const priorityColor = item.priority === 'HIGH' ? 'error' : item.priority === 'MEDIUM' ? 'warning' : 'default';
              return (
                <TableRow key={String(item.rank)}>
                  <TableCell>{String(item.rank)}</TableCell>
                  <TableCell>
                    <Chip label={String(item.priority)} color={priorityColor as 'error' | 'warning' | 'default'} size="small" />
                  </TableCell>
                  <TableCell>{String(item.category)}</TableCell>
                  <TableCell sx={{ fontSize: '0.8rem', maxWidth: 300 }}>{String(item.description)}</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>{Number(item.nav_impact_bps).toFixed(1)}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default ExceptionScoringViz;

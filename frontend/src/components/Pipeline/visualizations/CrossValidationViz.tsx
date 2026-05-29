import { Box, Card, CardContent, Chip, Grid2, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';

const CrossValidationViz = ({ output }: { output: Record<string, unknown> }) => {
  const peer = (output.peer_comparison || {}) as Record<string, unknown>;
  const benchmarks = (output.benchmark_comparison || []) as Array<{ name: string; return_pct: number; delta_bps: number }>;
  const variance = (output.variance_decomposition || {}) as Record<string, unknown>;
  const status = String(output.cross_validation_status || '');
  const statusColor = status === 'PASS' ? 'success' : status === 'FAIL' ? 'error' : 'warning';

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Chip label={status.replace(/_/g, ' ')} color={statusColor as 'success' | 'warning' | 'error'} />
        <Chip label={`NAV Change: ${output.nav_change_bps} bps`} variant="outlined" />
      </Box>

      <Grid2 container spacing={2} sx={{ mb: 2 }}>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined">
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">Current NAV</Typography>
              <Typography variant="body1" fontWeight={600}>${Number(output.nav_current).toLocaleString()}</Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined">
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">Prior NAV</Typography>
              <Typography variant="body1">${Number(output.nav_prior).toLocaleString()}</Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined">
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">Explained</Typography>
              <Typography variant="body1" color="success.main" fontWeight={600}>{Number(variance.explained_variance_pct).toFixed(1)}%</Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 6, sm: 3 }}>
          <Card variant="outlined">
            <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="caption" color="text.secondary">Unexplained</Typography>
              <Typography variant="body1" color="warning.main" fontWeight={600}>{Number(variance.unexplained_variance_pct).toFixed(1)}%</Typography>
            </CardContent>
          </Card>
        </Grid2>
      </Grid2>

      {peer.peer_group ? (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Peer Comparison — {String(peer.peer_group)}</Typography>
          <Typography variant="body2">
            Fund return: <strong>{Number(peer.fund_return_pct).toFixed(2)}%</strong> |
            Peer avg: {Number(peer.peer_avg_return_pct).toFixed(2)}% |
            Percentile: {String(peer.percentile_rank)}th
          </Typography>
        </Box>
      ) : null}

      <Typography variant="subtitle2" gutterBottom>Benchmark Comparison</Typography>
      <TableContainer>
        <Table size="small">
          <TableHead><TableRow><TableCell>Benchmark</TableCell><TableCell align="right">Return</TableCell><TableCell align="right">Delta (bps)</TableCell></TableRow></TableHead>
          <TableBody>
            {benchmarks.map((b) => (
              <TableRow key={b.name}>
                <TableCell>{b.name}</TableCell>
                <TableCell align="right">{b.return_pct >= 0 ? '+' : ''}{b.return_pct.toFixed(2)}%</TableCell>
                <TableCell align="right" sx={{ color: b.delta_bps >= 0 ? 'success.main' : 'error.main' }}>
                  {b.delta_bps >= 0 ? '+' : ''}{b.delta_bps}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default CrossValidationViz;

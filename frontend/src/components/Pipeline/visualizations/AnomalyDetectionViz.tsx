import { Box, Card, CardContent, Chip, LinearProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';

const AnomalyDetectionViz = ({ output }: { output: Record<string, unknown> }) => {
  const score = (output.anomaly_score as number) || 0;
  const bySeverity = (output.anomalies_by_severity || {}) as Record<string, Array<Record<string, unknown>>>;

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
        <Card variant="outlined" sx={{ flex: 1 }}>
          <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
            <Typography variant="caption" color="text.secondary">Anomaly Score</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <LinearProgress variant="determinate" value={score * 100}
                color={score < 0.3 ? 'success' : score < 0.6 ? 'warning' : 'error'}
                sx={{ flex: 1, height: 8, borderRadius: 4 }} />
              <Typography variant="body2" fontWeight={600}>{(score * 100).toFixed(0)}%</Typography>
            </Box>
          </CardContent>
        </Card>
        <Chip label={`${output.total_checks_run} checks`} size="small" />
        <Chip label={`${output.anomalies_detected} anomalies`} color="warning" size="small" />
      </Box>

      {(['critical', 'warning', 'info'] as const).map((severity) => {
        const items = bySeverity[severity] || [];
        if (items.length === 0) return null;
        const color = severity === 'critical' ? 'error' : severity === 'warning' ? 'warning' : 'info';
        return (
          <Box key={severity} sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              <Chip label={`${severity.toUpperCase()} (${items.length})`} color={color} size="small" sx={{ mr: 1 }} />
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell align="right">Impact (bps)</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {items.map((item) => (
                    <TableRow key={String(item.id)}>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>{String(item.id)}</TableCell>
                      <TableCell>{String(item.category)}</TableCell>
                      <TableCell sx={{ fontSize: '0.8rem' }}>{String(item.description)}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>
                        {item.nav_impact_bps != null ? `${Number(item.nav_impact_bps).toFixed(1)}` : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        );
      })}
    </Box>
  );
};

export default AnomalyDetectionViz;

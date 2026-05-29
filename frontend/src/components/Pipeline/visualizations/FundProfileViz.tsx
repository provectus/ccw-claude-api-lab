import { Box, Card, CardContent, Chip, Grid2, Typography } from '@mui/material';

const FundProfileViz = ({ output }: { output: Record<string, unknown> }) => {
  const shareClasses = (output.share_classes || []) as Array<{ class_name: string; currency: string; shares_outstanding: number }>;
  const riskColor = output.risk_tier === 'Low' ? 'success' : output.risk_tier === 'Medium' ? 'warning' : 'error';

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 1, mb: 2, alignItems: 'center' }}>
        <Chip label={String(output.fund_type)} color="primary" />
        <Chip label={String(output.risk_tier) + ' Risk'} color={riskColor as 'success' | 'warning' | 'error'} variant="outlined" />
        <Chip label={String(output.base_currency)} size="small" variant="outlined" />
      </Box>

      <Grid2 container spacing={2}>
        <Grid2 size={{ xs: 12, sm: 6 }}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="caption" color="text.secondary">Fund Name</Typography>
              <Typography variant="h6">{String(output.fund_name)}</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {String(output.strategy || '')} | {String(output.domicile || '')}
              </Typography>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 size={{ xs: 12, sm: 6 }}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="caption" color="text.secondary">AUM</Typography>
              <Typography variant="h6">
                ${((output.aum_current as number) / 1_000_000).toFixed(0)}M
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                NAV Date: {String(output.nav_date || '')}
              </Typography>
            </CardContent>
          </Card>
        </Grid2>
      </Grid2>

      {shareClasses.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Share Classes</Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {shareClasses.map((sc) => (
              <Chip
                key={sc.class_name}
                label={`${sc.class_name} (${sc.currency}) — ${sc.shares_outstanding.toLocaleString()} shares`}
                size="small"
                variant="outlined"
              />
            ))}
          </Box>
        </Box>
      )}

      <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        {output.administrator ? <Typography variant="body2" color="text.secondary">Admin: {String(output.administrator)}</Typography> : null}
        {output.custodian ? <Typography variant="body2" color="text.secondary">Custodian: {String(output.custodian)}</Typography> : null}
      </Box>
    </Box>
  );
};

export default FundProfileViz;

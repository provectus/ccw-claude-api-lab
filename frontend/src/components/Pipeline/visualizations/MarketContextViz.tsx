import { Box, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';

const MarketContextViz = ({ output }: { output: Record<string, unknown> }) => {
  const indices = (output.key_indices || []) as Array<{ name: string; return_pct: number; level?: number }>;
  const sectors = (output.sector_performance || {}) as Record<string, number>;
  const fxMoves = (output.fx_moves || []) as Array<{ pair: string; change_pct: number }>;
  const events = (output.key_events || []) as string[];
  const regime = String(output.market_regime || 'NEUTRAL');

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Chip label={`Market: ${regime}`} color={regime === 'RISK_ON' ? 'success' : regime === 'RISK_OFF' ? 'error' : 'default'} />
        <Chip label={String(output.market_date)} size="small" variant="outlined" />
      </Box>

      <Typography variant="subtitle2" gutterBottom>Key Indices</Typography>
      <TableContainer sx={{ mb: 2 }}>
        <Table size="small">
          <TableHead><TableRow><TableCell>Index</TableCell><TableCell align="right">Return</TableCell></TableRow></TableHead>
          <TableBody>
            {indices.map((idx) => (
              <TableRow key={idx.name}>
                <TableCell>{idx.name}</TableCell>
                <TableCell align="right" sx={{ color: idx.return_pct >= 0 ? 'success.main' : 'error.main', fontWeight: 600 }}>
                  {idx.return_pct >= 0 ? '+' : ''}{idx.return_pct.toFixed(2)}%
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Typography variant="subtitle2" gutterBottom>Sector Performance</Typography>
      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 2 }}>
        {Object.entries(sectors).map(([name, ret]) => (
          <Chip key={name} label={`${name}: ${ret >= 0 ? '+' : ''}${ret}%`} size="small"
            color={ret >= 0 ? 'success' : 'error'} variant="outlined" />
        ))}
      </Box>

      {fxMoves.length > 0 && (
        <>
          <Typography variant="subtitle2" gutterBottom>FX Moves</Typography>
          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 2 }}>
            {fxMoves.map((fx) => (
              <Chip key={fx.pair} label={`${fx.pair}: ${fx.change_pct >= 0 ? '+' : ''}${fx.change_pct}%`}
                size="small" variant="outlined" />
            ))}
          </Box>
        </>
      )}

      {events.length > 0 && (
        <>
          <Typography variant="subtitle2" gutterBottom>Key Events</Typography>
          {events.map((e, i) => (
            <Typography key={i} variant="body2" sx={{ mb: 0.5, pl: 1, borderLeft: '2px solid', borderColor: 'divider' }}>
              {e}
            </Typography>
          ))}
        </>
      )}
    </Box>
  );
};

export default MarketContextViz;

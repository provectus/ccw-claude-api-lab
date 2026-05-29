import { Box, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';

const PositionDriversViz = ({ output }: { output: Record<string, unknown> }) => {
  const contributors = (output.top_contributors || []) as Array<Record<string, unknown>>;
  const detractors = (output.top_detractors || []) as Array<Record<string, unknown>>;
  const assetClasses = (output.concentration_by_asset_class || {}) as Record<string, Record<string, unknown>>;
  const stalePrices = (output.stale_prices || []) as Array<Record<string, unknown>>;

  return (
    <Box>
      <Chip label={`${output.total_positions} total positions`} size="small" sx={{ mb: 2 }} />

      <Typography variant="subtitle2" gutterBottom>Top Contributors</Typography>
      <TableContainer sx={{ mb: 2 }}>
        <Table size="small">
          <TableHead><TableRow><TableCell>Security</TableCell><TableCell>Class</TableCell><TableCell align="right">P&L (bps)</TableCell><TableCell align="right">Weight</TableCell></TableRow></TableHead>
          <TableBody>
            {contributors.map((c) => (
              <TableRow key={String(c.security_id)}>
                <TableCell sx={{ fontSize: '0.8rem' }}>{String(c.name)}</TableCell>
                <TableCell>{String(c.asset_class)}</TableCell>
                <TableCell align="right" sx={{ color: 'success.main', fontWeight: 600 }}>+{Number(c.pnl_bps)}</TableCell>
                <TableCell align="right">{Number(c.weight_pct).toFixed(1)}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Typography variant="subtitle2" gutterBottom>Top Detractors</Typography>
      <TableContainer sx={{ mb: 2 }}>
        <Table size="small">
          <TableHead><TableRow><TableCell>Security</TableCell><TableCell>Class</TableCell><TableCell align="right">P&L (bps)</TableCell><TableCell align="right">Weight</TableCell></TableRow></TableHead>
          <TableBody>
            {detractors.map((d) => (
              <TableRow key={String(d.security_id)}>
                <TableCell sx={{ fontSize: '0.8rem' }}>{String(d.name)}</TableCell>
                <TableCell>{String(d.asset_class)}</TableCell>
                <TableCell align="right" sx={{ color: 'error.main', fontWeight: 600 }}>{Number(d.pnl_bps)}</TableCell>
                <TableCell align="right">{Number(d.weight_pct).toFixed(1)}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Typography variant="subtitle2" gutterBottom>Asset Class Breakdown</Typography>
      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 2 }}>
        {Object.entries(assetClasses).map(([name, data]) => (
          <Chip key={name} label={`${name}: ${Number(data.weight_pct).toFixed(1)}% (${data.position_count} pos)`}
            size="small" variant="outlined" />
        ))}
      </Box>

      {stalePrices.length > 0 && (
        <>
          <Typography variant="subtitle2" gutterBottom color="warning.main">Stale Prices</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead><TableRow><TableCell>Security</TableCell><TableCell>Last Price Date</TableCell><TableCell align="right">Days Stale</TableCell><TableCell align="right">Value</TableCell></TableRow></TableHead>
              <TableBody>
                {stalePrices.map((sp) => (
                  <TableRow key={String(sp.security_id)}>
                    <TableCell sx={{ fontSize: '0.8rem' }}>{String(sp.name)}</TableCell>
                    <TableCell>{String(sp.last_price_date)}</TableCell>
                    <TableCell align="right" sx={{ color: 'warning.main', fontWeight: 600 }}>{String(sp.days_stale)}</TableCell>
                    <TableCell align="right">${Number(sp.market_value).toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}
    </Box>
  );
};

export default PositionDriversViz;

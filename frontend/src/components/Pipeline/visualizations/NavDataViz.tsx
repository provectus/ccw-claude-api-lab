import { Box, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';

const NavDataViz = ({ output }: { output: Record<string, unknown> }) => {
  const columns = (output.columns || []) as Array<{ name: string; dtype: string; null_count: number }>;
  const sampleRows = (output.sample_rows || []) as Record<string, unknown>[];
  const sheets = (output.sheets || []) as string[];

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
        <Chip label={`${output.row_count} rows`} color="primary" size="small" />
        <Chip label={`${output.column_count} columns`} size="small" />
        <Chip label={`${output.file_size_kb} KB`} size="small" variant="outlined" />
        {sheets.length > 0 && <Chip label={`Sheets: ${sheets.join(', ')}`} size="small" variant="outlined" />}
      </Box>

      <Typography variant="subtitle2" gutterBottom>Columns</Typography>
      <TableContainer sx={{ mb: 2 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell align="right">Nulls</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {columns.slice(0, 12).map((col) => (
              <TableRow key={col.name}>
                <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>{col.name}</TableCell>
                <TableCell>{col.dtype}</TableCell>
                <TableCell align="right">{col.null_count}</TableCell>
              </TableRow>
            ))}
            {columns.length > 12 && (
              <TableRow>
                <TableCell colSpan={3} sx={{ textAlign: 'center', color: 'text.secondary' }}>
                  + {columns.length - 12} more columns
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {sampleRows.length > 0 && (
        <>
          <Typography variant="subtitle2" gutterBottom>Sample Data</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {Object.keys(sampleRows[0]).slice(0, 8).map((key) => (
                    <TableCell key={key} sx={{ fontSize: '0.75rem' }}>{key}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {sampleRows.slice(0, 3).map((row, i) => (
                  <TableRow key={i}>
                    {Object.values(row).slice(0, 8).map((val, j) => (
                      <TableCell key={j} sx={{ fontSize: '0.75rem' }}>
                        {typeof val === 'number' ? val.toLocaleString() : String(val ?? '')}
                      </TableCell>
                    ))}
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

export default NavDataViz;

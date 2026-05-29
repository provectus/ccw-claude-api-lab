import {
  Box,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import SeverityChip from '@/components/common/SeverityChip';

interface DataGap {
  field: string;
  completeness_pct: number;
  impact: 'HIGH' | 'MEDIUM' | 'LOW';
  recommendation: string;
}

function barColor(pct: number): 'success' | 'warning' | 'error' {
  if (pct >= 95) return 'success';
  if (pct >= 80) return 'warning';
  return 'error';
}

const DataGapsTable = ({ gaps }: { gaps: DataGap[] }) => {
  const sorted = [...gaps].sort((a, b) => a.completeness_pct - b.completeness_pct);

  if (sorted.length === 0) {
    return <Typography variant="body2" color="text.secondary">No data gaps identified</Typography>;
  }

  return (
    <TableContainer sx={{ maxHeight: 320 }}>
      <Table size="small" stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell sx={{ width: 160 }}>Field</TableCell>
            <TableCell sx={{ width: 180 }}>Completeness</TableCell>
            <TableCell sx={{ width: 90 }}>Impact</TableCell>
            <TableCell>Recommendation</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sorted.map((g, i) => (
            <TableRow key={i} hover>
              <TableCell sx={{ fontWeight: 500, fontSize: '0.8125rem' }}>{g.field}</TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={g.completeness_pct}
                    color={barColor(g.completeness_pct)}
                    sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                  />
                  <Typography variant="caption" sx={{ minWidth: 36, textAlign: 'right' }}>
                    {g.completeness_pct.toFixed(0)}%
                  </Typography>
                </Box>
              </TableCell>
              <TableCell><SeverityChip severity={g.impact} /></TableCell>
              <TableCell sx={{ fontSize: '0.8125rem' }}>{g.recommendation}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default DataGapsTable;

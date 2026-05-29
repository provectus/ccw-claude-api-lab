import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import SeverityChip from '@/components/common/SeverityChip';

interface Risk {
  category: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  description: string;
  mitigation: string;
}

const SEVERITY_ORDER: Record<string, number> = { HIGH: 0, MEDIUM: 1, LOW: 2 };

const RiskTable = ({ risks }: { risks: Risk[] }) => {
  const sorted = [...risks].sort(
    (a, b) => (SEVERITY_ORDER[a.severity] ?? 3) - (SEVERITY_ORDER[b.severity] ?? 3),
  );

  if (sorted.length === 0) {
    return <Typography variant="body2" color="text.secondary">No risks identified</Typography>;
  }

  return (
    <TableContainer sx={{ maxHeight: 320 }}>
      <Table size="small" stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell sx={{ width: 100 }}>Severity</TableCell>
            <TableCell sx={{ width: 140 }}>Category</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Mitigation</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sorted.map((r, i) => (
            <TableRow key={i} hover>
              <TableCell><SeverityChip severity={r.severity} /></TableCell>
              <TableCell>{r.category}</TableCell>
              <TableCell sx={{ fontSize: '0.8125rem' }}>{r.description}</TableCell>
              <TableCell sx={{ fontSize: '0.8125rem' }}>{r.mitigation}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default RiskTable;

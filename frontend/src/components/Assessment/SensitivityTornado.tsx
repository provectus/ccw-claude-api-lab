import { Box, Typography } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from 'recharts';

interface SensitivityEntry {
  description: string;
  irr: number;
  irr_delta_bps: number;
  block_pv: number;
  pv_delta_pct: number;
}

interface SensitivityTornadoProps {
  sensitivity: Record<string, SensitivityEntry>;
  baseCaseIrr: number | null;
}

const SensitivityTornado = ({ sensitivity, baseCaseIrr }: SensitivityTornadoProps) => {
  const entries = Object.entries(sensitivity);
  if (entries.length === 0) {
    return <Typography variant="body2" color="text.secondary">No sensitivity data</Typography>;
  }

  // Sort by absolute delta (largest impact first)
  const chartData = entries
    .map(([, s]) => ({
      name: s.description,
      delta: s.irr_delta_bps,
    }))
    .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta));

  return (
    <Box>
      {baseCaseIrr != null && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Base case IRR: {(baseCaseIrr * 100).toFixed(2)}%
        </Typography>
      )}
      <Box sx={{ height: Math.max(200, chartData.length * 40 + 60) }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              type="number"
              tickFormatter={(v: number) => `${v > 0 ? '+' : ''}${v.toFixed(0)} bps`}
            />
            <YAxis type="category" dataKey="name" width={160} tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={(v: number) => `${v > 0 ? '+' : ''}${v.toFixed(1)} bps`}
              labelFormatter={(label: string) => label}
            />
            <ReferenceLine x={0} stroke="#666" strokeWidth={2} />
            <Bar dataKey="delta" name="IRR Delta (bps)">
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.delta < 0 ? '#C62828' : '#66BB6A'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};

export default SensitivityTornado;

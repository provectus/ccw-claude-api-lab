import { Box, Card, CardContent, Typography } from '@mui/material';
import Grid2 from '@mui/material/Grid2';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { formatDollars, formatPercent } from '@/utils/format';

interface CohortData {
  age_distribution?: Array<{
    band: string;
    count: number;
    pct: number;
    mean_reserve: number;
    total_reserve: number;
  }>;
  reserve_summary?: {
    total: number;
    mean: number;
    median: number;
    by_injury_type?: Record<string, { total: number; count: number; mean: number }>;
    by_gender?: Record<string, { total: number; count: number; mean: number }>;
  };
  payment_structure?: {
    pct_life_contingent?: number;
    pct_period_certain?: number;
    pct_with_cola?: number;
    pct_without_cola?: number;
  };
  data_completeness?: {
    overall: number;
    by_field?: Record<string, number>;
  };
}

const COLORS = ['#0A1628', '#00897B', '#5DADE2', '#F57F17', '#C62828', '#66BB6A', '#AB47BC', '#FF7043'];

function completenessColor(pct: number): string {
  if (pct >= 0.95) return '#66BB6A';
  if (pct >= 0.80) return '#F57F17';
  return '#C62828';
}

const CohortAnalyticsGrid = ({ data }: { data: CohortData }) => {
  const ageDist = data.age_distribution ?? [];
  const byInjury = data.reserve_summary?.by_injury_type ?? {};
  const payment = data.payment_structure;
  const byField = data.data_completeness?.by_field ?? {};

  // Chart 1: Age distribution with reserve overlay
  const ageChartData = ageDist.map((a) => ({
    band: a.band,
    count: a.count,
    mean_reserve: a.mean_reserve,
  }));

  // Chart 2: Reserve by injury type (horizontal bar)
  const injuryData = Object.entries(byInjury)
    .map(([name, v]) => ({ name, total: v.total }))
    .sort((a, b) => b.total - a.total);

  // Chart 3: Payment structure donut
  const paymentData = payment
    ? [
        { name: 'Life Contingent', value: payment.pct_life_contingent ?? 0 },
        { name: 'Period Certain', value: payment.pct_period_certain ?? 0 },
      ].filter((d) => d.value > 0)
    : [];

  const colaData = payment
    ? [
        { name: 'With COLA', value: payment.pct_with_cola ?? 0 },
        { name: 'Without COLA', value: payment.pct_without_cola ?? 0 },
      ].filter((d) => d.value > 0)
    : [];

  // Chart 4: Data completeness by field
  const completenessData = Object.entries(byField)
    .map(([name, pct]) => ({ name, pct }))
    .sort((a, b) => a.pct - b.pct);

  return (
    <Grid2 container spacing={2}>
      {/* Age Distribution Histogram */}
      <Grid2 size={{ xs: 12, md: 6 }}>
        <Card variant="outlined" sx={{ height: '100%' }}>
          <CardContent>
            <Typography variant="subtitle2" gutterBottom>Age Distribution</Typography>
            {ageChartData.length > 0 ? (
              <Box sx={{ height: 240 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={ageChartData} margin={{ left: 10, right: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="band" tick={{ fontSize: 10 }} />
                    <YAxis yAxisId="count" tickFormatter={(v: number) => v.toLocaleString()} />
                    <YAxis yAxisId="reserve" orientation="right" tickFormatter={(v: number) => formatDollars(v)} />
                    <Tooltip
                      formatter={(value: number, name: string) =>
                        name === 'mean_reserve' ? formatDollars(value) : value.toLocaleString()
                      }
                    />
                    <Legend />
                    <Bar yAxisId="count" dataKey="count" name="Policies" fill="#00897B" radius={[4, 4, 0, 0]} />
                    <Bar yAxisId="reserve" dataKey="mean_reserve" name="Avg Reserve" fill="#5DADE2" radius={[4, 4, 0, 0]} opacity={0.7} />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">No data</Typography>
            )}
          </CardContent>
        </Card>
      </Grid2>

      {/* Reserve by Injury Type */}
      <Grid2 size={{ xs: 12, md: 6 }}>
        <Card variant="outlined" sx={{ height: '100%' }}>
          <CardContent>
            <Typography variant="subtitle2" gutterBottom>Reserve by Injury Type</Typography>
            {injuryData.length > 0 ? (
              <Box sx={{ height: 240 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={injuryData} layout="vertical" margin={{ left: 20, right: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" tickFormatter={(v: number) => formatDollars(v)} />
                    <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 11 }} />
                    <Tooltip formatter={(v: number) => formatDollars(v)} />
                    <Bar dataKey="total" name="Total Reserve" fill="#0A1628" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">No data</Typography>
            )}
          </CardContent>
        </Card>
      </Grid2>

      {/* Payment Structure Donut */}
      <Grid2 size={{ xs: 12, md: 6 }}>
        <Card variant="outlined" sx={{ height: '100%' }}>
          <CardContent>
            <Typography variant="subtitle2" gutterBottom>Payment Structure</Typography>
            {paymentData.length > 0 || colaData.length > 0 ? (
              <Box sx={{ height: 240, display: 'flex' }}>
                {paymentData.length > 0 && (
                  <ResponsiveContainer width="50%" height="100%">
                    <PieChart>
                      <Pie
                        data={paymentData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={35}
                        outerRadius={65}
                        label={({ name, value }: { name: string; value: number }) =>
                          `${name} ${formatPercent(value)}`
                        }
                        labelLine={{ strokeWidth: 1 }}
                      >
                        {paymentData.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(v: number) => formatPercent(v)} />
                    </PieChart>
                  </ResponsiveContainer>
                )}
                {colaData.length > 0 && (
                  <ResponsiveContainer width="50%" height="100%">
                    <PieChart>
                      <Pie
                        data={colaData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={35}
                        outerRadius={65}
                        label={({ name, value }: { name: string; value: number }) =>
                          `${name} ${formatPercent(value)}`
                        }
                        labelLine={{ strokeWidth: 1 }}
                      >
                        {colaData.map((_, i) => (
                          <Cell key={i} fill={COLORS[(i + 2) % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(v: number) => formatPercent(v)} />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">No data</Typography>
            )}
          </CardContent>
        </Card>
      </Grid2>

      {/* Data Completeness */}
      <Grid2 size={{ xs: 12, md: 6 }}>
        <Card variant="outlined" sx={{ height: '100%' }}>
          <CardContent>
            <Typography variant="subtitle2" gutterBottom>Data Completeness by Field</Typography>
            {completenessData.length > 0 ? (
              <Box sx={{ height: 240 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={completenessData} layout="vertical" margin={{ left: 20, right: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[0, 1]} tickFormatter={(v: number) => formatPercent(v, 0)} />
                    <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 10 }} />
                    <Tooltip formatter={(v: number) => formatPercent(v)} />
                    <Bar dataKey="pct" name="Completeness">
                      {completenessData.map((entry, i) => (
                        <Cell key={i} fill={completenessColor(entry.pct)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">No data</Typography>
            )}
          </CardContent>
        </Card>
      </Grid2>
    </Grid2>
  );
};

export default CohortAnalyticsGrid;

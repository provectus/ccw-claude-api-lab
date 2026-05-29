import { Box, LinearProgress, Typography } from '@mui/material';

interface ConfidenceBarProps {
  value: number; // 0-1
  label?: string;
  height?: number;
}

function getColor(value: number): 'error' | 'warning' | 'success' {
  if (value < 0.6) return 'error';
  if (value < 0.8) return 'warning';
  return 'success';
}

const ConfidenceBar = ({ value: rawValue, label, height = 8 }: ConfidenceBarProps) => {
  const value = Number.isFinite(rawValue) ? rawValue : 0;
  return (
  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
    {label && (
      <Typography variant="body2" color="text.secondary" sx={{ minWidth: 60 }}>
        {label}
      </Typography>
    )}
    <LinearProgress
      variant="determinate"
      value={Math.round(value * 100)}
      color={getColor(value)}
      sx={{ flexGrow: 1, height, borderRadius: height / 2 }}
    />
    <Typography variant="body2" fontWeight={600} sx={{ minWidth: 40, textAlign: 'right' }}>
      {Math.round(value * 100)}%
    </Typography>
  </Box>
  );
};

export default ConfidenceBar;

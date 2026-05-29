import { Chip } from '@mui/material';
import type { ChipProps } from '@mui/material';

interface SeverityChipProps {
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  size?: ChipProps['size'];
}

const colorMap: Record<string, ChipProps['color']> = {
  HIGH: 'error',
  MEDIUM: 'warning',
  LOW: 'success',
};

const SeverityChip = ({ severity, size = 'small' }: SeverityChipProps) => (
  <Chip label={severity} color={colorMap[severity] ?? 'default'} size={size} variant="outlined" />
);

export default SeverityChip;

import { Chip } from '@mui/material';
import type { Recommendation } from '@/types/pipeline';

interface RecommendationBadgeProps {
  recommendation: Recommendation;
  size?: 'small' | 'medium';
}

const config: Record<Recommendation, { label: string; color: 'success' | 'warning' | 'error' | 'info' }> = {
  APPROVE: { label: 'Approve', color: 'success' },
  APPROVE_WITH_EXCEPTIONS: { label: 'Approve with Exceptions', color: 'warning' },
  ESCALATE: { label: 'Escalate', color: 'error' },
  HOLD: { label: 'Hold', color: 'info' },
};

const RecommendationBadge = ({ recommendation, size = 'medium' }: RecommendationBadgeProps) => {
  const { label, color } = config[recommendation] ?? { label: recommendation, color: 'warning' as const };
  return (
    <Chip
      label={label}
      color={color}
      size={size}
      sx={{
        fontWeight: 700,
        fontSize: size === 'medium' ? '1rem' : '0.8125rem',
        py: size === 'medium' ? 2.5 : 0.5,
        px: size === 'medium' ? 1 : 0,
      }}
    />
  );
};

export default RecommendationBadge;

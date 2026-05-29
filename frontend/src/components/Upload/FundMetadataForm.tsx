import { useState, useCallback } from 'react';
import type { FormEvent } from 'react';
import {
  Box,
  Button,
  CircularProgress,
  Grid2,
  InputAdornment,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material';
import type { FundMetadata } from '@/types';

interface FundMetadataFormProps {
  onSubmit: (metadata: FundMetadata) => void;
  initialValues?: Partial<FundMetadata>;
  submitLabel?: string;
  submitting?: boolean;
  disabled?: boolean;
}

const FUND_TYPES = [
  { value: 'HedgeFund', label: 'Hedge Fund' },
  { value: 'PrivateEquity', label: 'Private Equity' },
  { value: 'RealAssets', label: 'Real Assets' },
  { value: 'Traditional', label: 'Traditional / Mutual Fund' },
] as const;

const CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CHF'] as const;

const defaultValues: FundMetadata = {
  fund_name: '',
  fund_type: 'HedgeFund',
  strategy: '',
  base_currency: 'USD',
  nav_date: new Date().toISOString().slice(0, 10),
  reported_aum: null,
};

const FundMetadataForm = ({
  onSubmit,
  initialValues,
  submitLabel = 'Review NAV',
  submitting = false,
  disabled = false,
}: FundMetadataFormProps) => {
  const [values, setValues] = useState<FundMetadata>({
    ...defaultValues,
    ...initialValues,
  });
  const [errors, setErrors] = useState<Partial<Record<keyof FundMetadata, string>>>({});

  const handleChange = useCallback((field: keyof FundMetadata, raw: string) => {
    setErrors((prev) => ({ ...prev, [field]: undefined }));

    if (field === 'reported_aum') {
      const num = raw === '' ? null : Number(raw);
      setValues((prev) => ({ ...prev, [field]: num }));
    } else if (field === 'fund_type') {
      setValues((prev) => ({ ...prev, fund_type: raw as FundMetadata['fund_type'] }));
    } else {
      setValues((prev) => ({ ...prev, [field]: raw }));
    }
  }, []);

  const validate = useCallback((): boolean => {
    const next: Partial<Record<keyof FundMetadata, string>> = {};
    if (!values.fund_name.trim()) next.fund_name = 'Required';
    if (!values.nav_date.trim()) next.nav_date = 'Required';
    if (values.reported_aum != null && values.reported_aum <= 0)
      next.reported_aum = 'Must be positive';
    setErrors(next);
    return Object.keys(next).length === 0;
  }, [values]);

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      if (validate()) onSubmit(values);
    },
    [validate, values, onSubmit],
  );

  const isReady = values.fund_name.trim().length > 0;

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
        Fund Metadata
      </Typography>

      <Grid2 container spacing={2}>
        <Grid2 size={{ xs: 12, sm: 6 }}>
          <TextField
            label="Fund Name"
            required
            fullWidth
            size="small"
            value={values.fund_name}
            onChange={(e) => handleChange('fund_name', e.target.value)}
            error={!!errors.fund_name}
            helperText={errors.fund_name}
            disabled={disabled}
          />
        </Grid2>
        <Grid2 size={{ xs: 12, sm: 6 }}>
          <TextField
            label="Fund Type"
            select
            fullWidth
            size="small"
            value={values.fund_type}
            onChange={(e) => handleChange('fund_type', e.target.value)}
            disabled={disabled}
          >
            {FUND_TYPES.map((ft) => (
              <MenuItem key={ft.value} value={ft.value}>{ft.label}</MenuItem>
            ))}
          </TextField>
        </Grid2>
        <Grid2 size={{ xs: 12, sm: 4 }}>
          <TextField
            label="Strategy"
            fullWidth
            size="small"
            value={values.strategy}
            onChange={(e) => handleChange('strategy', e.target.value)}
            placeholder="e.g., Multi-Strategy, Long/Short Equity"
            disabled={disabled}
          />
        </Grid2>
        <Grid2 size={{ xs: 12, sm: 4 }}>
          <TextField
            label="Base Currency"
            select
            fullWidth
            size="small"
            value={values.base_currency}
            onChange={(e) => handleChange('base_currency', e.target.value)}
            disabled={disabled}
          >
            {CURRENCIES.map((c) => (
              <MenuItem key={c} value={c}>{c}</MenuItem>
            ))}
          </TextField>
        </Grid2>
        <Grid2 size={{ xs: 12, sm: 4 }}>
          <TextField
            label="NAV Date"
            fullWidth
            size="small"
            type="date"
            required
            value={values.nav_date}
            onChange={(e) => handleChange('nav_date', e.target.value)}
            error={!!errors.nav_date}
            helperText={errors.nav_date}
            disabled={disabled}
            slotProps={{ inputLabel: { shrink: true } }}
          />
        </Grid2>
        <Grid2 size={{ xs: 12, sm: 6 }}>
          <TextField
            label="Reported AUM"
            fullWidth
            size="small"
            type="number"
            slotProps={{
              input: {
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              },
            }}
            value={values.reported_aum ?? ''}
            onChange={(e) => handleChange('reported_aum', e.target.value)}
            error={!!errors.reported_aum}
            helperText={errors.reported_aum}
            disabled={disabled}
          />
        </Grid2>
      </Grid2>

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          type="submit"
          variant="contained"
          color="secondary"
          size="large"
          disabled={!isReady || submitting || disabled}
          startIcon={submitting ? <CircularProgress size={18} color="inherit" /> : undefined}
        >
          {submitting ? 'Starting...' : submitLabel}
        </Button>
      </Box>
    </Box>
  );
};

export default FundMetadataForm;

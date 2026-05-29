import { Box, Stepper, Step, StepLabel, styled, keyframes } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import type { PipelineStep } from '@/types/pipeline';

interface ProgressStepperProps {
  steps: PipelineStep[];
  currentStepIndex: number;
  onStepClick: (index: number) => void;
}

const pulse = keyframes`
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
`;

const PulsingIcon = styled('span')(({ theme }) => ({
  display: 'inline-flex',
  animation: `${pulse} 1.5s ease-in-out infinite`,
  color: theme.palette.secondary.main,
}));

function StepIcon({ step }: { step: PipelineStep }) {
  if (step.status === 'completed') {
    return <CheckCircleIcon color="success" fontSize="small" />;
  }
  if (step.status === 'failed') {
    return <ErrorIcon color="error" fontSize="small" />;
  }
  if (step.status === 'running') {
    return (
      <PulsingIcon>
        <RadioButtonUncheckedIcon color="secondary" fontSize="small" />
      </PulsingIcon>
    );
  }
  return <RadioButtonUncheckedIcon sx={{ color: 'text.disabled' }} fontSize="small" />;
}

const ProgressStepper = ({ steps, currentStepIndex, onStepClick }: ProgressStepperProps) => (
  <Box sx={{ width: '100%', overflowX: 'auto', py: 1 }}>
    <Stepper activeStep={currentStepIndex} alternativeLabel nonLinear>
      {steps.map((step, i) => (
        <Step key={step.tool} completed={step.status === 'completed'}>
          <StepLabel
            StepIconComponent={() => <StepIcon step={step} />}
            onClick={() => onStepClick(i)}
            sx={{
              cursor: 'pointer',
              '& .MuiStepLabel-label': {
                fontSize: { xs: '0.625rem', sm: '0.75rem' },
                mt: 0.5,
              },
            }}
          >
            {step.label}
          </StepLabel>
        </Step>
      ))}
    </Stepper>
  </Box>
);

export default ProgressStepper;

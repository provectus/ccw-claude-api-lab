import { useEffect, useRef, useState } from 'react';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Skeleton,
  Typography,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import HourglassBottomIcon from '@mui/icons-material/HourglassBottom';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { PipelineStep } from '@/types/pipeline';
import ToolCallCard from './ToolCallCard';
import ConfidenceBar from '@/components/common/ConfidenceBar';

/** Shared sx for compact markdown rendering in the reasoning panel */
const markdownSx = {
  '& p': { fontSize: '0.875rem', lineHeight: 1.6, my: 0.5, color: 'text.secondary' },
  '& ul, & ol': { pl: 2, my: 0.5 },
  '& li': { fontSize: '0.875rem', color: 'text.secondary' },
  '& strong': { fontWeight: 600, color: 'text.primary' },
  '& h1, & h2, & h3, & h4': { fontSize: '0.875rem', fontWeight: 600, mt: 1, mb: 0.25 },
  fontStyle: 'italic',
};

interface AgentReasoningPanelProps {
  steps: PipelineStep[];
  currentStepIndex: number;
  onStepClick: (index: number) => void;
}

function StepIcon({ status }: { status: string }) {
  switch (status) {
    case 'completed':
      return <CheckCircleIcon color="success" fontSize="small" />;
    case 'failed':
      return <ErrorIcon color="error" fontSize="small" />;
    case 'running':
      return <HourglassBottomIcon color="secondary" fontSize="small" />;
    default:
      return <RadioButtonUncheckedIcon sx={{ color: 'text.disabled' }} fontSize="small" />;
  }
}

function statusText(step: PipelineStep): string {
  switch (step.status) {
    case 'completed':
      return 'Completed';
    case 'failed':
      return 'Failed';
    case 'running':
      return 'Processing...';
    default:
      return 'Pending';
  }
}

const AgentReasoningPanel = ({ steps, currentStepIndex, onStepClick }: AgentReasoningPanelProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  // Track which accordions are expanded — allows user to freely toggle
  const [expandedSet, setExpandedSet] = useState<Set<number>>(() => new Set());
  // Track the last auto-expanded running step to avoid re-forcing after user collapses
  const lastAutoExpandedRef = useRef<number>(-1);

  // Auto-expand the currently running step when it changes
  useEffect(() => {
    const runningIdx = steps.findIndex((s) => s.status === 'running');
    if (runningIdx >= 0 && runningIdx !== lastAutoExpandedRef.current) {
      lastAutoExpandedRef.current = runningIdx;
      setExpandedSet((prev) => {
        const next = new Set(prev);
        next.add(runningIdx);
        return next;
      });
    }
  }, [steps]);

  // Auto-scroll to the current active step
  useEffect(() => {
    if (scrollRef.current) {
      const activeAccordion = scrollRef.current.querySelector(`[data-step-index="${currentStepIndex}"]`);
      activeAccordion?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [currentStepIndex]);

  const handleToggle = (index: number) => {
    setExpandedSet((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
    onStepClick(index);
  };

  // Extract confidence from output if present
  const getConfidence = (step: PipelineStep): number | null => {
    if (!step.output) return null;
    const conf = step.output.confidence ?? step.output.mapping_quality_score ?? step.output.quality_score;
    return typeof conf === 'number' ? conf : null;
  };

  return (
    <Box ref={scrollRef} sx={{ overflow: 'auto', maxHeight: 'calc(100vh - 280px)' }}>
      {steps.map((step, i) => (
        <Accordion
          key={step.tool}
          data-step-index={i}
          expanded={expandedSet.has(i)}
          onChange={() => handleToggle(i)}
          disableGutters
          sx={{
            '&:before': { display: 'none' },
            border: 1,
            borderColor: 'divider',
            mb: 0.5,
            borderRadius: '8px !important',
            overflow: 'hidden',
          }}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            sx={{
              minHeight: 48,
              '& .MuiAccordionSummary-content': { alignItems: 'center', gap: 1 },
            }}
          >
            <StepIcon status={step.status} />
            <Box sx={{ flex: 1, ml: 0.5 }}>
              <Typography variant="subtitle2">{step.label}</Typography>
              <Typography variant="caption" color="text.secondary">{statusText(step)}</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ pt: 0 }}>
            {step.status === 'pending' && (
              <Typography variant="body2" color="text.secondary" fontStyle="italic">
                Waiting for previous steps to complete...
              </Typography>
            )}

            {step.status === 'running' && !step.output && (
              <Box>
                {step.reasoningText && (
                  <Box sx={{ mb: 1.5, ...markdownSx }}>
                    <Markdown remarkPlugins={[remarkGfm]}>{step.reasoningText}</Markdown>
                  </Box>
                )}
                <Skeleton variant="rectangular" height={60} sx={{ borderRadius: 1 }} />
              </Box>
            )}

            {(step.status === 'completed' || step.status === 'failed') && (
              <Box>
                {step.reasoningText && (
                  <Box sx={{ mb: 1.5, ...markdownSx }}>
                    <Markdown remarkPlugins={[remarkGfm]}>{step.reasoningText}</Markdown>
                  </Box>
                )}
                {getConfidence(step) != null && (
                  <Box sx={{ mb: 1.5, maxWidth: 300 }}>
                    <ConfidenceBar value={getConfidence(step)!} label="Confidence" />
                  </Box>
                )}
                <ToolCallCard step={step} />
              </Box>
            )}
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};

export default AgentReasoningPanel;

// Pipeline execution Zustand store

import { create } from 'zustand';
import type {
  PipelineStatus,
  PipelineSSEEvent,
  PipelineStep,
  ReviewPack,
  SSEConnectionState,
  ToolName,
  StepStatus,
} from '@/types/pipeline';
import { TOOL_NAMES, TOOL_LABELS, TOTAL_STEPS } from '@/types/pipeline';

// -- State shape --

interface PipelineState {
  pipelineId: string | null;
  status: PipelineStatus;
  events: PipelineSSEEvent[];
  assessment: ReviewPack | null;
  errorMessage: string | null;
  connectionState: SSEConnectionState;
}

interface PipelineActions {
  startPipeline: (id: string) => void;
  appendEvent: (event: PipelineSSEEvent) => void;
  setConnectionState: (state: SSEConnectionState) => void;
  reset: () => void;
}

type PipelineStore = PipelineState & PipelineActions;

const initialState: PipelineState = {
  pipelineId: null,
  status: 'pending',
  events: [],
  assessment: null,
  errorMessage: null,
  connectionState: 'idle',
};

export const usePipelineStore = create<PipelineStore>()((set) => ({
  ...initialState,

  startPipeline: (id: string) =>
    set({
      ...initialState,
      pipelineId: id,
      status: 'pending',
      connectionState: 'idle',
    }),

  appendEvent: (event: PipelineSSEEvent) =>
    set((state) => {
      const events = [...state.events, event];
      const patch: Partial<PipelineState> = { events };

      if (event.type === 'status') {
        patch.status = event.status;
      } else if (event.type === 'complete') {
        patch.status = 'completed';
        if (event.assessment) {
          patch.assessment = event.assessment;
        }
      } else if (event.type === 'error') {
        patch.errorMessage = event.message;
        if (!event.recoverable) {
          patch.status = 'failed';
        }
      }

      return patch;
    }),

  setConnectionState: (connectionState: SSEConnectionState) =>
    set({ connectionState }),

  reset: () => set(initialState),
}));

// -- Pure derivation functions (use with useMemo in components) --

/** Derive PipelineStep[] from flat events array. */
export function deriveSteps(events: PipelineSSEEvent[]): PipelineStep[] {
  const steps: PipelineStep[] = TOOL_NAMES.map((tool, i) => ({
    stepIndex: i,
    tool,
    label: TOOL_LABELS[tool],
    status: 'pending' as StepStatus,
    reasoningText: null,
    input: null,
    output: null,
    source: null,
    toolUseId: null,
  }));

  // Build a lookup from tool name → step index for matching events by tool name
  const toolToIdx = new Map(TOOL_NAMES.map((t, i) => [t, i]));
  let pendingReasoning: string[] = [];

  for (const event of events) {
    if (event.type === 'reasoning') {
      pendingReasoning.push(event.text);
    } else if (event.type === 'tool_start') {
      // Match by tool name (robust to extra tool calls shifting step_index)
      const idx = toolToIdx.get(event.tool as ToolName);
      if (idx !== undefined) {
        steps[idx].status = 'running';
        steps[idx].input = event.input;
        steps[idx].toolUseId = event.tool_use_id;
        if (pendingReasoning.length > 0) {
          steps[idx].reasoningText = pendingReasoning.join('\n\n');
          pendingReasoning = [];
        }
      }
    } else if (event.type === 'tool_result') {
      const idx = toolToIdx.get(event.tool as ToolName);
      if (idx !== undefined) {
        steps[idx].status = event.source === 'error' ? 'failed' : 'completed';
        steps[idx].output = event.output;
        steps[idx].source = event.source;
      }
    } else if (event.type === 'error' && !event.recoverable) {
      const running = steps.find((s) => s.status === 'running');
      if (running) running.status = 'failed';
    }
  }

  return steps;
}

/** Index of the first running step, or first pending if none running. */
export function deriveCurrentStepIndex(events: PipelineSSEEvent[]): number {
  const steps = deriveSteps(events);
  const running = steps.findIndex((s) => s.status === 'running');
  if (running >= 0) return running;
  const pending = steps.findIndex((s) => s.status === 'pending');
  if (pending >= 0) return pending;
  return TOTAL_STEPS - 1;
}

// -- Zustand selectors (for simple scalar values) --

/** Whether pipeline has reached a terminal state. */
export function selectIsTerminal(state: PipelineStore): boolean {
  return state.status === 'completed' || state.status === 'failed';
}

/** Count of completed steps. */
export function selectStepsCompleted(events: PipelineSSEEvent[]): number {
  return deriveSteps(events).filter((s) => s.status === 'completed').length;
}

/** Get output for a specific tool. */
export function selectToolOutput(toolName: ToolName, events: PipelineSSEEvent[]): Record<string, unknown> | null {
  const steps = deriveSteps(events);
  const step = steps.find((s) => s.tool === toolName);
  return step?.output ?? null;
}

/** All reasoning texts in order. */
export function selectAllReasoning(events: PipelineSSEEvent[]): string[] {
  return events
    .filter((e): e is Extract<PipelineSSEEvent, { type: 'reasoning' }> => e.type === 'reasoning')
    .map((e) => e.text);
}

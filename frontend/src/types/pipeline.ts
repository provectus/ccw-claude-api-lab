// Pipeline types aligned with backend SSE events and REST responses

// -- Tool names (ordered) --

export const TOOL_NAMES = [
  'ingest_nav_package',
  'build_fund_profile',
  'extract_market_context',
  'detect_anomalies',
  'cross_validate_nav',
  'analyze_position_drivers',
  'score_exceptions',
  'generate_review_pack',
] as const;

export type ToolName = (typeof TOOL_NAMES)[number];

export const TOTAL_STEPS = 8;

export const TOOL_LABELS: Record<ToolName, string> = {
  ingest_nav_package: 'Data Ingestion',
  build_fund_profile: 'Fund Profile',
  extract_market_context: 'Market Context',
  detect_anomalies: 'Anomaly Detection',
  cross_validate_nav: 'Cross-Validation',
  analyze_position_drivers: 'Position Drivers',
  score_exceptions: 'Exception Scoring',
  generate_review_pack: 'Review Pack',
};

// -- Pipeline status --

export type PipelineStatus = 'pending' | 'running' | 'completed' | 'failed';

// -- SSE events (discriminated union matching backend agent_runner.py) --

export interface StatusEvent {
  type: 'status';
  status: PipelineStatus;
}

export interface ReasoningEvent {
  type: 'reasoning';
  text: string;
}

export interface ToolStartEvent {
  type: 'tool_start';
  tool: string;
  input: Record<string, unknown>;
  tool_use_id: string;
  step_index: number;
}

export interface ToolResultEvent {
  type: 'tool_result';
  tool: string;
  output: Record<string, unknown>;
  source: 'live' | 'fallback' | 'error';
  tool_use_id: string;
  step_index: number;
}

export interface CompleteEvent {
  type: 'complete';
  assessment: ReviewPack | null;
}

export interface ErrorEvent {
  type: 'error';
  message: string;
  recoverable: boolean;
}

export type PipelineSSEEvent =
  | StatusEvent
  | ReasoningEvent
  | ToolStartEvent
  | ToolResultEvent
  | CompleteEvent
  | ErrorEvent;

// -- Derived step state --

export type StepStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface PipelineStep {
  stepIndex: number;
  tool: ToolName;
  label: string;
  status: StepStatus;
  reasoningText: string | null;
  input: Record<string, unknown> | null;
  output: Record<string, unknown> | null;
  source: 'live' | 'fallback' | 'error' | null;
  toolUseId: string | null;
}

// -- Review pack (matches generate_review_pack output) --

export type Recommendation =
  | 'APPROVE'
  | 'APPROVE_WITH_EXCEPTIONS'
  | 'ESCALATE'
  | 'HOLD';

export interface ReviewPack {
  recommendation: Recommendation;
  confidence: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  executive_summary: {
    fund_name: string;
    nav_date: string;
    nav_per_share: Record<string, number>;
    total_nav: number;
    nav_change_pct: number;
    nav_change_bps: number;
    data_quality_score: number;
    total_exceptions: number;
    critical_exceptions: number;
    auto_resolved: number;
    requires_attention: number;
  };
  key_variances: Array<{
    driver: string;
    impact_bps: number;
    explanation: string;
    status: string;
  }>;
  exception_summary: Array<{
    id: string;
    priority: 'HIGH' | 'MEDIUM' | 'LOW';
    description: string;
    disposition: string;
  }>;
  review_metrics: {
    estimated_review_time_minutes: number;
    baseline_review_time_minutes: number;
    review_time_savings_pct: number;
    checks_performed: number;
    data_sources_cross_referenced: number;
  };
  conditions_for_approval: string[];
  next_steps: string[];
}

// -- REST response types --

export interface PipelineRunResponse {
  pipeline_id: string;
  status: PipelineStatus;
  created_at: string;
}

export interface PipelineStatusResponse {
  pipeline_id: string;
  status: PipelineStatus;
  steps_completed: number;
  total_steps: number;
  event_count: number;
  created_at: string;
  completed_at: string | null;
}

export interface PipelineAssessmentResponse {
  pipeline_id: string;
  status: PipelineStatus;
  assessment: ReviewPack | null;
  narrative: string[];
  tool_outputs?: Record<string, Record<string, unknown>>;
}

export interface PipelineEventsResponse {
  pipeline_id: string;
  status: PipelineStatus;
  events: PipelineSSEEvent[];
  metadata: Record<string, unknown>;
}

export interface PipelineRunSummary {
  id: string;
  status: PipelineStatus;
  created_at: string;
  completed_at: string | null;
  event_count: number;
  fund_name: string;
  fund_type: string;
  recommendation: string | null;
  data_quality_score: number | null;
}

export interface PipelineListResponse {
  pipelines: PipelineRunSummary[];
}

export interface DemoScenario {
  id: string;
  name: string;
  description: string;
  file_paths: string[];
  fund_metadata: Record<string, unknown>;
}

export interface ScenariosResponse {
  scenarios: DemoScenario[];
}

// -- SSE connection state --

export type SSEConnectionState =
  | 'idle'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'closed'
  | 'error';

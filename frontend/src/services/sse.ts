// SSE client for pipeline event streaming

import type { PipelineSSEEvent, SSEConnectionState } from '@/types/pipeline';

const SSE_EVENT_TYPES = [
  'status',
  'reasoning',
  'tool_start',
  'tool_result',
  'complete',
  'error',
] as const;

interface PipelineSSEClientOptions {
  pipelineId: string;
  onEvent: (event: PipelineSSEEvent) => void;
  onStateChange: (state: SSEConnectionState) => void;
  onError?: (error: Event) => void;
  maxRetries?: number;
  baseDelay?: number;
}

export class PipelineSSEClient {
  private eventSource: EventSource | null = null;
  private retryCount = 0;
  private retryTimer: ReturnType<typeof setTimeout> | null = null;
  private closed = false;

  private readonly pipelineId: string;
  private readonly onEvent: (event: PipelineSSEEvent) => void;
  private readonly onStateChange: (state: SSEConnectionState) => void;
  private readonly onError?: (error: Event) => void;
  private readonly maxRetries: number;
  private readonly baseDelay: number;

  constructor(options: PipelineSSEClientOptions) {
    this.pipelineId = options.pipelineId;
    this.onEvent = options.onEvent;
    this.onStateChange = options.onStateChange;
    this.onError = options.onError;
    this.maxRetries = options.maxRetries ?? 5;
    this.baseDelay = options.baseDelay ?? 1000;
  }

  connect(): void {
    if (this.closed) return;
    this.onStateChange('connecting');

    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
    const url = `${baseUrl}/pipeline/${this.pipelineId}/stream`;
    this.eventSource = new EventSource(url);

    this.eventSource.onopen = () => {
      this.retryCount = 0;
      this.onStateChange('connected');
    };

    // Register named event listeners (backend sets `event:` field per type)
    for (const eventType of SSE_EVENT_TYPES) {
      this.eventSource.addEventListener(eventType, (e: MessageEvent) => {
        this.handleMessage(e, eventType);
      });
    }

    this.eventSource.onerror = (e) => {
      if (this.closed) return;
      this.onError?.(e);
      this.eventSource?.close();
      this.eventSource = null;
      this.attemptReconnect();
    };
  }

  close(): void {
    this.closed = true;
    if (this.retryTimer) {
      clearTimeout(this.retryTimer);
      this.retryTimer = null;
    }
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.onStateChange('closed');
  }

  private handleMessage(e: MessageEvent, _eventType: string): void {
    try {
      const parsed = JSON.parse(e.data) as PipelineSSEEvent;
      this.onEvent(parsed);

      // Auto-close on terminal events
      if (parsed.type === 'complete' || (parsed.type === 'error' && !parsed.recoverable)) {
        this.close();
      }
    } catch {
      // Ignore unparseable messages
    }
  }

  private attemptReconnect(): void {
    if (this.closed) return;
    if (this.retryCount >= this.maxRetries) {
      this.onStateChange('error');
      return;
    }

    this.onStateChange('reconnecting');
    const delay = this.baseDelay * Math.pow(2, this.retryCount);
    this.retryCount++;

    this.retryTimer = setTimeout(() => {
      if (!this.closed) {
        this.connect();
      }
    }, delay);
  }
}

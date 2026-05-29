// Hook to manage SSE connection lifecycle for pipeline streaming

import { useEffect, useRef } from 'react';
import { PipelineSSEClient } from '@/services/sse';
import { usePipelineStore } from '@/stores/pipelineStore';
import type { SSEConnectionState } from '@/types/pipeline';

interface UsePipelineStreamOptions {
  pipelineId: string | null;
  enabled?: boolean;
}

interface UsePipelineStreamResult {
  connectionState: SSEConnectionState;
  disconnect: () => void;
}

export function usePipelineStream({
  pipelineId,
  enabled = true,
}: UsePipelineStreamOptions): UsePipelineStreamResult {
  const connectionState = usePipelineStore((s) => s.connectionState);
  const appendEvent = usePipelineStore((s) => s.appendEvent);
  const setConnectionState = usePipelineStore((s) => s.setConnectionState);
  const clientRef = useRef<PipelineSSEClient | null>(null);

  useEffect(() => {
    if (!pipelineId || !enabled) return;

    const client = new PipelineSSEClient({
      pipelineId,
      onEvent: appendEvent,
      onStateChange: setConnectionState,
    });

    clientRef.current = client;
    client.connect();

    return () => {
      client.close();
      clientRef.current = null;
    };
  }, [pipelineId, enabled, appendEvent, setConnectionState]);

  const disconnect = () => {
    clientRef.current?.close();
    clientRef.current = null;
  };

  return { connectionState, disconnect };
}

import { z } from 'zod';
import type { SSEEvent, SSEConnectionState } from '../../types/sse';

const DataChangedEventSchema = z.object({
  event_type: z.literal('data_changed'),
  timestamp: z.string(),
});

export function parseSSEEventData(data: string): SSEEvent | null {
  try {
    const parsed = JSON.parse(data);
    const result = DataChangedEventSchema.safeParse(parsed);
    return result.success ? result.data : null;
  } catch {
    return null;
  }
}

export function isDataChangedEvent(event: SSEEvent): event is SSEEvent & { event_type: 'data_changed' } {
  return event.event_type === 'data_changed';
}

export function formatConnectionStatus(state: SSEConnectionState): { label: string; color: string } {
  switch (state) {
    case 'connected':
      return { label: 'Live', color: 'text-green-600' };
    case 'connecting':
      return { label: 'Connecting...', color: 'text-yellow-600' };
    case 'disconnected':
      return { label: 'Disconnected', color: 'text-red-600' };
    case 'error':
      return { label: 'Connection Error', color: 'text-red-600' };
    default:
      return { label: 'Unknown', color: 'text-gray-600' };
  }
}

export function calculateReconnectDelay(attempt: number): number {
  const baseDelay = 1000;
  const maxDelay = 30000;
  const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
  return delay + Math.random() * 1000;
}

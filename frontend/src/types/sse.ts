export type SSEConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface DataChangedEvent {
  event_type: 'data_changed';
  timestamp: string;
}

export type SSEEvent = DataChangedEvent;

export interface SSEConnectionStatus {
  state: SSEConnectionState;
  lastEvent?: SSEEvent;
  lastEventTime?: Date;
  error?: string;
  reconnectAttempts?: number;
}

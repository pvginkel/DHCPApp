export type SSEConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface ConnectionEstablishedEvent {
  event_type: 'connection_established';
  client_id: string;
  message: string;
  active_connections: number;
}

export interface DataChangedEvent {
  event_type: 'data_changed';
  timestamp: string;
}

export interface HeartbeatEvent {
  event_type: 'heartbeat';
  timestamp: number;
  active_connections: number;
}

export type SSEEvent = ConnectionEstablishedEvent | DataChangedEvent | HeartbeatEvent;

export interface SSEConnectionStatus {
  state: SSEConnectionState;
  lastEvent?: SSEEvent;
  lastEventTime?: Date;
  error?: string;
  reconnectAttempts?: number;
}

export interface SSEEventData {
  type: string;
  data: Record<string, unknown>;
}
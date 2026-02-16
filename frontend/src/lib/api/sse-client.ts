import type { SSEEvent, SSEConnectionState, SSEConnectionStatus } from '../../types/sse';
import { parseSSEEventData, calculateReconnectDelay } from '../utils/sse-utils';

export interface SSEClientOptions {
  url: string;
  onConnectionChange?: (status: SSEConnectionStatus) => void;
  onEvent?: (event: SSEEvent) => void;
  onError?: (error: Error) => void;
  maxReconnectAttempts?: number;
}

export class SSEClient {
  private eventSource: EventSource | null = null;
  private connectionStatus: SSEConnectionStatus;
  private reconnectAttempts = 0;
  private reconnectTimeoutId: number | null = null;
  private options: SSEClientOptions;

  constructor(options: SSEClientOptions) {
    this.options = options;
    this.connectionStatus = {
      state: 'disconnected',
      reconnectAttempts: 0,
    };
  }

  connect(): void {
    if (this.eventSource?.readyState === EventSource.OPEN) {
      this.updateConnectionStatus('connected');
      return;
    }

    this.disconnect();
    this.updateConnectionStatus('connecting');

    try {
      this.eventSource = new EventSource(this.options.url);
      this.setupEventListeners();
    } catch (error) {
      this.handleError(error instanceof Error ? error : new Error('Failed to create EventSource'));
    }
  }

  disconnect(): void {
    if (this.reconnectTimeoutId) {
      clearTimeout(this.reconnectTimeoutId);
      this.reconnectTimeoutId = null;
    }

    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }

    this.updateConnectionStatus('disconnected');
    this.reconnectAttempts = 0;
  }

  getConnectionStatus(): SSEConnectionStatus {
    return { ...this.connectionStatus };
  }

  private setupEventListeners(): void {
    if (!this.eventSource) return;

    this.eventSource.onopen = () => {
      this.reconnectAttempts = 0;
      this.updateConnectionStatus('connected');
    };

    this.eventSource.onmessage = (event) => {
      this.handleMessage(event);
    };

    this.eventSource.onerror = () => {
      this.handleConnectionError();
    };

    this.eventSource.addEventListener('data_changed', (event) => {
      this.handleMessage(event as MessageEvent);
    });
  }

  private handleMessage(event: MessageEvent): void {
    const parsedEvent = parseSSEEventData(event.data);

    if (parsedEvent) {
      this.connectionStatus.lastEvent = parsedEvent;
      this.connectionStatus.lastEventTime = new Date();
      this.options.onEvent?.(parsedEvent);
    }
  }

  private handleConnectionError(): void {
    if (this.eventSource?.readyState === EventSource.CLOSED) {
      this.scheduleReconnect();
    }
  }

  private handleError(error: Error): void {
    this.updateConnectionStatus('error', error.message);
    this.options.onError?.(error);
    this.scheduleReconnect();
  }

  private scheduleReconnect(): void {
    const maxAttempts = this.options.maxReconnectAttempts ?? 10;

    if (this.reconnectAttempts >= maxAttempts) {
      this.updateConnectionStatus('error', 'Maximum reconnection attempts exceeded');
      return;
    }

    const delay = calculateReconnectDelay(this.reconnectAttempts);
    this.reconnectAttempts++;

    this.reconnectTimeoutId = window.setTimeout(() => {
      if (this.connectionStatus.state !== 'connected') {
        this.connect();
      }
    }, delay);
  }

  private updateConnectionStatus(state: SSEConnectionState, error?: string): void {
    this.connectionStatus = {
      ...this.connectionStatus,
      state,
      error,
      reconnectAttempts: this.reconnectAttempts,
    };

    this.options.onConnectionChange?.(this.connectionStatus);
  }
}

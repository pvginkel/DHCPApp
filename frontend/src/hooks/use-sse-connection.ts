import { useEffect, useState, useCallback, useRef } from 'react';
import { SSEClient } from '../lib/api/sse-client';
import type { SSEEvent, SSEConnectionStatus } from '../types/sse';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export interface UseSSEConnectionOptions {
  onEvent?: (event: SSEEvent) => void;
  onError?: (error: Error) => void;
  autoConnect?: boolean;
  maxReconnectAttempts?: number;
}

export interface UseSSEConnectionReturn {
  connectionStatus: SSEConnectionStatus;
  connect: () => void;
  disconnect: () => void;
  isConnected: boolean;
  isConnecting: boolean;
  hasError: boolean;
}

export function useSSEConnection(options: UseSSEConnectionOptions = {}): UseSSEConnectionReturn {
  const {
    onEvent,
    onError,
    autoConnect = true,
    maxReconnectAttempts = 10,
  } = options;

  const [connectionStatus, setConnectionStatus] = useState<SSEConnectionStatus>({
    state: 'disconnected',
    reconnectAttempts: 0,
  });

  const clientRef = useRef<SSEClient | null>(null);

  const handleConnectionChange = useCallback((status: SSEConnectionStatus) => {
    setConnectionStatus(status);
  }, []);

  const handleEvent = useCallback((event: SSEEvent) => {
    onEvent?.(event);
  }, [onEvent]);

  const handleError = useCallback((error: Error) => {
    onError?.(error);
  }, [onError]);

  const connect = useCallback(() => {
    if (!clientRef.current) {
      clientRef.current = new SSEClient({
        url: `${API_BASE_URL}/leases/stream`,
        onConnectionChange: handleConnectionChange,
        onEvent: handleEvent,
        onError: handleError,
        maxReconnectAttempts,
      });
    }
    
    clientRef.current.connect();
  }, [handleConnectionChange, handleEvent, handleError, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    clientRef.current?.disconnect();
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    connectionStatus,
    connect,
    disconnect,
    isConnected: connectionStatus.state === 'connected',
    isConnecting: connectionStatus.state === 'connecting',
    hasError: connectionStatus.state === 'error',
  };
}
import { createContext, useContext, useCallback } from 'react';
import type { ReactNode } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useSSEConnection } from '@/hooks/use-sse-connection';
import type { UseSSEConnectionReturn } from '@/hooks/use-sse-connection';
import type { SSEEvent } from '@/types/sse';
import { isDataChangedEvent } from '@/lib/utils/sse-utils';
import { apiKeys } from '@/lib/api/generated/queries';

interface SSEContextValue extends UseSSEConnectionReturn {
  // Add any additional context-specific properties if needed
}

const SSEContext = createContext<SSEContextValue | null>(null);

interface SSEProviderProps {
  children: ReactNode;
}

export function SSEProvider({ children }: SSEProviderProps) {
  const queryClient = useQueryClient();

  const handleSSEEvent = useCallback((event: SSEEvent) => {
    if (isDataChangedEvent(event)) {
      queryClient.invalidateQueries({ queryKey: [...apiKeys.all, 'leases'] });
      queryClient.invalidateQueries({ queryKey: [...apiKeys.all, 'status'] });
    }
  }, [queryClient]);

  const handleSSEError = useCallback((error: Error) => {
    console.warn('SSE connection error:', error.message);
  }, []);

  const sseConnection = useSSEConnection({
    onEvent: handleSSEEvent,
    onError: handleSSEError,
    autoConnect: true,
    maxReconnectAttempts: 10,
  });

  return (
    <SSEContext.Provider value={sseConnection}>
      {children}
    </SSEContext.Provider>
  );
}

export function useSSEContext(): SSEContextValue {
  const context = useContext(SSEContext);
  if (!context) {
    throw new Error('useSSEContext must be used within an SSEProvider');
  }
  return context;
}
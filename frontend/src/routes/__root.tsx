import { createRootRoute, Outlet } from '@tanstack/react-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ErrorBoundary } from '@/components/common/error-boundary'
import { Layout } from '@/components/layout/layout'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
    },
  },
})

export const Route = createRootRoute({
  component: () => (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <Layout>
          <Outlet />
        </Layout>
      </ErrorBoundary>
    </QueryClientProvider>
  ),
})

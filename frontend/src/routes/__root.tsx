import { createRootRoute, Outlet } from '@tanstack/react-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ErrorBoundary } from '@/components/common/error-boundary'
import { Layout } from '@/components/layout/layout'
import { useSystemTheme } from '@/hooks/use-system-theme'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
    },
  },
})

function RootComponent() {
  useSystemTheme()
  
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <Layout>
          <Outlet />
        </Layout>
      </ErrorBoundary>
    </QueryClientProvider>
  )
}

export const Route = createRootRoute({
  component: RootComponent,
})

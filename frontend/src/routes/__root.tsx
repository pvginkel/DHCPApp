import { createRootRoute, Outlet } from '@tanstack/react-router'
import { ErrorBoundary } from '@/components/common/error-boundary'
import { Layout } from '@/components/layout/layout'

export const Route = createRootRoute({
  component: () => (
    <ErrorBoundary>
      <Layout>
        <Outlet />
      </Layout>
    </ErrorBoundary>
  ),
})

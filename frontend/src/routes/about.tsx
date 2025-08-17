import { createFileRoute } from '@tanstack/react-router'

function AboutPage() {
  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">About DHCP Monitor</h1>
        <p className="text-lg text-muted-foreground mt-2">
          Real-time DHCP lease monitoring for homelab environments
        </p>
      </div>

      <div className="space-y-6">
        <section className="rounded-lg border border-border bg-card p-6">
          <h2 className="text-xl font-semibold mb-4">Overview</h2>
          <p className="text-muted-foreground leading-relaxed">
            DHCP Monitor provides a clean, real-time interface for monitoring DHCP lease 
            information in homelab environments. The application connects to a DHCP monitoring 
            backend service to display active DHCP leases with real-time updates via Server-Sent Events (SSE).
          </p>
        </section>

        <section className="rounded-lg border border-border bg-card p-6">
          <h2 className="text-xl font-semibold mb-4">Key Features</h2>
          <ul className="space-y-2 text-muted-foreground">
            <li className="flex items-center space-x-2">
              <div className="h-1.5 w-1.5 rounded-full bg-primary"></div>
              <span>Real-time DHCP lease display with interactive table</span>
            </li>
            <li className="flex items-center space-x-2">
              <div className="h-1.5 w-1.5 rounded-full bg-primary"></div>
              <span>Live update notifications with visual flash animations</span>
            </li>
            <li className="flex items-center space-x-2">
              <div className="h-1.5 w-1.5 rounded-full bg-primary"></div>
              <span>Multi-column sorting with persistent preferences</span>
            </li>
            <li className="flex items-center space-x-2">
              <div className="h-1.5 w-1.5 rounded-full bg-primary"></div>
              <span>Live search functionality for filtering lease data</span>
            </li>
            <li className="flex items-center space-x-2">
              <div className="h-1.5 w-1.5 rounded-full bg-primary"></div>
              <span>Clean, modern UI optimized for data readability</span>
            </li>
          </ul>
        </section>

        <section className="rounded-lg border border-border bg-card p-6">
          <h2 className="text-xl font-semibold mb-4">Technology Stack</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h3 className="font-medium mb-2">Frontend</h3>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li>React with TypeScript</li>
                <li>Vite build tool</li>
                <li>TanStack Router & Query</li>
                <li>Tailwind CSS + Radix UI</li>
                <li>Zod for validation</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium mb-2">Features</h3>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li>Server-Sent Events (SSE)</li>
                <li>Real-time data updates</li>
                <li>Persistent user preferences</li>
                <li>Responsive design</li>
                <li>Type-safe API integration</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="rounded-lg border border-border bg-card p-6">
          <h2 className="text-xl font-semibold mb-4">Purpose</h2>
          <p className="text-muted-foreground leading-relaxed">
            The primary purpose is to provide an easy-to-use interface for identifying active 
            DHCP clients to facilitate manual assignment of static IP addresses. The application 
            focuses on simplicity and clarity, presenting lease data in a sortable, searchable 
            table format with visual feedback for real-time updates.
          </p>
        </section>
      </div>
    </div>
  )
}

export const Route = createFileRoute('/about')({
  component: AboutPage,
})

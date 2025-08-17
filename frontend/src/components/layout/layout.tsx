import React from "react"

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-background font-sans antialiased">
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center space-x-8">
            <a href="/" className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                <span className="text-sm font-bold text-primary-foreground">
                  D
                </span>
              </div>
              <span className="text-lg font-semibold">DHCP Monitor</span>
            </a>
            <nav className="hidden md:flex items-center space-x-6">
              <a
                href="/"
                className="text-sm font-medium transition-colors hover:text-primary"
              >
                Leases
              </a>
              <a
                href="/about"
                className="text-sm font-medium transition-colors hover:text-primary"
              >
                About
              </a>
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-muted-foreground">
              Real-time DHCP Monitoring
            </span>
          </div>
        </div>
      </header>
      <main className="flex-1 container px-4 py-8">
        {children}
      </main>
      <footer className="border-t border-border py-6">
        <div className="container px-4 text-center text-sm text-muted-foreground">
          © 2024 DHCP Monitor. Built for homelab environments.
        </div>
      </footer>
    </div>
  )
}

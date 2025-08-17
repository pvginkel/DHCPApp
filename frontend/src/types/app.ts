// Application-specific type definitions



// Component props
export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}



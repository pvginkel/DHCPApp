interface DefaultErrorFallbackProps {
  error: Error
  resetError: () => void 
}

export function DefaultErrorFallback({ 
  error, 
  resetError 
}: DefaultErrorFallbackProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center p-8 text-center">
      <div className="max-w-md">
        <h2 className="mb-4 text-xl font-semibold text-destructive">
          Something went wrong
        </h2>
        <p className="mb-4 text-sm text-muted-foreground">
          {error.message || "An unexpected error occurred"}
        </p>
        <button
          onClick={resetError}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          Try again
        </button>
      </div>
    </div>
  )
}
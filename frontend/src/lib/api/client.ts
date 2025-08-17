// API client configuration wrapper
import { apiClient } from './generated/client'

// Configure global defaults
apiClient.use({
  onRequest(options) {
    // Add any global request configuration here
    // e.g., authentication headers, logging, etc.
    console.log('API Request:', options.schemaPath, options.params)
  }
})

apiClient.use({
  onResponse(options) {
    // Add any global response handling here
    // e.g., error handling, logging, etc.
    console.log('API Response:', options.schemaPath, options.response.status)
  }
})

// Re-export the configured client
export { apiClient }
export * from './generated/client'

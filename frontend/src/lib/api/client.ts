// API client configuration wrapper
import { apiClient } from './generated/client'
import { redirectToLogin } from './auth'

// Configure global defaults
apiClient.use({
  onRequest(options) {
    console.log('API Request:', options.schemaPath, options.params)
  }
})

apiClient.use({
  onResponse(options) {
    if (options.response.status === 401) {
      redirectToLogin()
    }
    console.log('API Response:', options.schemaPath, options.response.status)
  }
})

// Re-export the configured client
export { apiClient }
export * from './generated/client'

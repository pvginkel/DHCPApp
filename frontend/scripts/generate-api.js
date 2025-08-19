#!/usr/bin/env node
import { execSync } from 'child_process'
import { writeFileSync, mkdirSync, existsSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const projectRoot = join(__dirname, '..')
const generatedDir = join(projectRoot, 'src', 'lib', 'api', 'generated')

// Configuration
const isProd = process.argv.includes('--prod')
const baseUrl = isProd 
  ? process.env.VITE_API_BASE_URL || 'https://your-prod-domain.com/api/v1'
  : process.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'

const openApiUrl = `${baseUrl}/openapi.json`

/**
 * Fetches OpenAPI specification from the backend
 * @param {string} url - The OpenAPI specification URL
 * @returns {Promise<object>} The OpenAPI specification object
 */
async function fetchOpenApiSpec(url) {
  console.log(`📡 Fetching OpenAPI specification from: ${url}`)
  
  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const spec = await response.json()
    console.log(`✅ Successfully fetched OpenAPI spec (version: ${spec.openapi || 'unknown'})`)
    
    // Basic validation
    if (!spec.openapi || !spec.paths || !spec.components) {
      throw new Error('Invalid OpenAPI specification: missing required fields')
    }
    
    return spec
  } catch (error) {
    console.error(`❌ Failed to fetch OpenAPI specification:`, error.message)
    
    if (error.message.includes('fetch')) {
      console.error(`
🔧 Troubleshooting:
   1. Make sure the backend is running: workon dhcp-backend && python3 run.py
   2. Verify the backend is accessible at: ${baseUrl}
   3. Check the health endpoint: ${baseUrl}/health
      `)
    }
    
    throw error
  }
}

/**
 * Generates TypeScript types from OpenAPI specification
 * @param {string} specPath - Path to the OpenAPI spec file
 * @param {string} outputPath - Path for generated types
 */
function generateTypes(specPath, outputPath) {
  console.log('🔧 Generating TypeScript types...')
  
  try {
    const cmd = `npx openapi-typescript "${specPath}" --output "${outputPath}"`
    execSync(cmd, { stdio: 'pipe' })
    console.log(`✅ Generated types: ${outputPath}`)
  } catch (error) {
    console.error(`❌ Failed to generate types:`, error.message)
    throw error
  }
}

/**
 * Generates API client using openapi-fetch
 * @param {string} outputPath - Path for generated client
 */
function generateClient(outputPath) {
  console.log('🔧 Generating API client...')
  
  // Create a basic fetch client wrapper
  const clientCode = `// Generated API client - Do not edit manually
import createClient from 'openapi-fetch'
import { API_BASE_URL } from '../config'
import type { paths } from './types'

// Create the base client
export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
})

// Export types for convenience
export type { paths } from './types'
export type ApiClient = typeof apiClient
`

  try {
    writeFileSync(outputPath, clientCode, 'utf-8')
    console.log(`✅ Generated client: ${outputPath}`)
  } catch (error) {
    console.error(`❌ Failed to generate client:`, error.message)
    throw error
  }
}

/**
 * Generates TanStack Query hooks for API endpoints
 * @param {object} spec - The OpenAPI specification
 * @param {string} outputPath - Path for generated hooks
 */
function generateQueryHooks(spec, outputPath) {
  console.log('🔧 Generating TanStack Query hooks...')
  
  const paths = spec.paths || {}
  const hooks = []
  
  // Generate imports
  hooks.push(`// Generated TanStack Query hooks - Do not edit manually
import { useQuery, useMutation, type UseQueryOptions, type UseMutationOptions } from '@tanstack/react-query'
import { apiClient } from './client'
import type { paths } from './types'

// Query key factory
export const apiKeys = {
  all: ['api'] as const,
  lists: () => [...apiKeys.all, 'list'] as const,
  list: (filters: string) => [...apiKeys.lists(), { filters }] as const,
  details: () => [...apiKeys.all, 'detail'] as const,
  detail: (id: string) => [...apiKeys.details(), id] as const,
} as const
`)

  // Generate hooks for each endpoint
  Object.entries(paths).forEach(([path, methods]) => {
    Object.entries(methods).forEach(([method, operation]) => {
      if (!operation || typeof operation !== 'object') return
      
      const hookName = generateHookName(method, path)
      
      // Check if this is an SSE endpoint
      const isSSE = operation.responses?.['200']?.content?.['text/event-stream']
      
      if (method === 'get') {
        if (!isSSE) {
          // Generate regular query hook with endpoint-specific query key and proper typing
          const pathKey = path.replace(/[{}\/]/g, '_').replace(/^_+|_+$/g, '')
          const responseType = `paths['${path}']['${method}']['responses']['200']['content']['application/json']`
          hooks.push(`
export function ${hookName}(
  params?: paths['${path}']['${method}']['parameters'],
  options?: Omit<UseQueryOptions<${responseType}, Error>, 'queryKey' | 'queryFn'>
) {
  return useQuery<${responseType}, Error>({
    queryKey: [...apiKeys.all, '${pathKey}', params] as const,
    queryFn: async () => {
      const { data, error } = await apiClient.GET('${path}', params)
      if (error) throw error
      return data as ${responseType}
    },
    ...options,
  })
}`)
        }
      } else {
        // Generate mutation hook
        const hasRequestBody = operation.requestBody && operation.requestBody.content
        
        if (hasRequestBody) {
          hooks.push(`
export function ${hookName}(
  options?: UseMutationOptions<
    paths['${path}']['${method}']['responses']['200']['content']['application/json'],
    Error,
    paths['${path}']['${method}']['requestBody']['content']['application/json']
  >
) {
  return useMutation({
    mutationFn: async (data) => {
      const { data: response, error } = await apiClient.${method.toUpperCase()}('${path}', {
        body: data,
      })
      if (error) throw error
      return response
    },
    ...options,
  })
}`)
        } else {
          hooks.push(`
export function ${hookName}(
  options?: UseMutationOptions<
    paths['${path}']['${method}']['responses']['200']['content']['application/json'],
    Error,
    void
  >
) {
  return useMutation({
    mutationFn: async () => {
      const { data: response, error } = await apiClient.${method.toUpperCase()}('${path}')
      if (error) throw error
      return response
    },
    ...options,
  })
}`)
        }
      }
    })
  })
  
  const hooksCode = hooks.join('\n')
  
  try {
    writeFileSync(outputPath, hooksCode, 'utf-8')
    console.log(`✅ Generated query hooks: ${outputPath}`)
  } catch (error) {
    console.error(`❌ Failed to generate query hooks:`, error.message)
    throw error
  }
}

/**
 * Generates a clean hook name from HTTP method and path
 */
function generateHookName(method, path) {
  // Create readable name from path
  let baseName = path
    .replace(/^\//, '') // Remove leading slash
    .replace(/\/\{[^}]+\}/g, 'ById') // Replace path params with "ById"
    .split('/')
    .map(segment => {
      // Convert kebab-case and snake_case to camelCase
      return segment
        .replace(/[-_]/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())
        .replace(/\s/g, '')
    })
    .join('')
  
  // Use the generated name directly - it's already clean
  const cleanName = baseName
  
  const prefix = 'use'
  const suffix = method === 'get' ? 'Query' : 'Mutation'

  return `${prefix}${cleanName}${suffix}`
}

/**
 * Creates type re-exports file
 * @param {string} outputPath - Path for type re-exports
 */
function createTypeReExports(outputPath) {
  console.log('🔧 Creating type re-exports...')
  
  const reExportsCode = `// Generated type re-exports - Do not edit manually
export type { paths, components } from './generated/types'
export { apiClient } from './generated/client'
export * from './generated/queries'
`

  try {
    writeFileSync(outputPath, reExportsCode, 'utf-8')
    console.log(`✅ Generated type re-exports: ${outputPath}`)
  } catch (error) {
    console.error(`❌ Failed to generate type re-exports:`, error.message)
    throw error
  }
}

/**
 * Creates API client wrapper with configuration
 * @param {string} outputPath - Path for client wrapper
 */
function createClientWrapper(outputPath) {
  console.log('🔧 Creating client wrapper...')
  
  const wrapperCode = `// API client configuration wrapper
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
`

  try {
    writeFileSync(outputPath, wrapperCode, 'utf-8')
    console.log(`✅ Generated client wrapper: ${outputPath}`)
  } catch (error) {
    console.error(`❌ Failed to generate client wrapper:`, error.message)
    throw error
  }
}

/**
 * Main orchestration function
 */
async function generateApiCode() {
  try {
    console.log('🚀 Starting OpenAPI code generation...')
    console.log(`📍 Environment: ${isProd ? 'Production' : 'Development'}`)
    
    // Ensure output directory exists
    if (!existsSync(generatedDir)) {
      mkdirSync(generatedDir, { recursive: true })
      console.log(`📁 Created directory: ${generatedDir}`)
    }
    
    // Fetch OpenAPI specification
    const spec = await fetchOpenApiSpec(openApiUrl)
    
    // Save the spec for reference
    const specPath = join(generatedDir, 'openapi-spec.json')
    writeFileSync(specPath, JSON.stringify(spec, null, 2), 'utf-8')
    console.log(`💾 Saved OpenAPI spec: ${specPath}`)
    
    // Generate TypeScript types
    const typesPath = join(generatedDir, 'types.ts')
    generateTypes(specPath, typesPath)
    
    // Generate API client
    const clientPath = join(generatedDir, 'client.ts')
    generateClient(clientPath)
    
    // Generate TanStack Query hooks
    const hooksPath = join(generatedDir, 'queries.ts')
    generateQueryHooks(spec, hooksPath)
    
    // Create integration files
    const apiDir = join(projectRoot, 'src', 'lib', 'api')
    if (!existsSync(apiDir)) {
      mkdirSync(apiDir, { recursive: true })
    }
    
    const typesReExportPath = join(apiDir, 'types.ts')
    createTypeReExports(typesReExportPath)
    
    const clientWrapperPath = join(apiDir, 'client.ts')
    createClientWrapper(clientWrapperPath)
    
    console.log('\n🎉 OpenAPI code generation completed successfully!')
    console.log(`
📊 Generated files:
   • ${typesPath}
   • ${clientPath} 
   • ${hooksPath}
   • ${typesReExportPath}
   • ${clientWrapperPath}

🔄 Next steps:
   1. Run 'pnpm install' to install new dependencies
   2. Update your components to use the generated types and client
   3. The generated code is excluded from git via .gitignore
    `)
    
  } catch (error) {
    console.error('\n💥 OpenAPI code generation failed:', error.message)
    process.exit(1)
  }
}

// Run the generation
generateApiCode()
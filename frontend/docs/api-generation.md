# API Code Generation

This project automatically generates TypeScript types, API clients, and TanStack Query hooks from the backend's OpenAPI specification.

## Quick Start

```bash
# Generate API code from local backend
pnpm generate:api

# Generate API code from production backend  
pnpm generate:api:prod

# Generate API code and restart dev server
pnpm update:api

# Validate API generation and type checking
pnpm validate:api
```

## What Gets Generated

The code generation creates the following files in `src/lib/api/generated/`:

- `types.ts` - TypeScript interfaces from OpenAPI schemas
- `client.ts` - Type-safe fetch client using openapi-fetch
- `queries.ts` - TanStack Query hooks for all endpoints
- `openapi-spec.json` - Saved OpenAPI specification for reference

## Integration Files

These files provide easy access to generated code:

- `src/lib/api/types.ts` - Re-exports all generated types and hooks
- `src/lib/api/client.ts` - Configured API client wrapper
- `src/lib/api/utils.ts` - Data transformation utilities and enhanced hooks

## Usage Examples

### Using Generated Types

```typescript
import type { DhcpLeaseAPI, DHCPLease } from '@/api/types'
import { convertApiLeaseToFrontend } from '@/api/utils'
```

### Using Generated Hooks

```typescript
import { useDhcpLeases, useHealthCheck } from '@/api/types'

function MyComponent() {
  const { data: leases, isLoading } = useDhcpLeases()
  const { data: health } = useHealthCheck()
  
  // leases is properly typed as DhcpLeaseAPI[]
  return <div>{/* component code */}</div>
}
```

### Using Enhanced Hooks with Data Transformation

```typescript
import { useDhcpLeasesTransformed } from '@/api/utils'

function MyComponent() {
  const { data: leases, isLoading } = useDhcpLeasesTransformed()
  
  // leases is properly typed as DHCPLease[] (frontend format)
  return <div>{/* component code */}</div>
}
```

## Development Workflow

1. **Backend Changes**: When the backend API changes, simply run `pnpm generate:api`
2. **Type Safety**: All API calls are fully type-safe with IntelliSense support
3. **Build Integration**: API generation runs automatically during build process
4. **Git Ignore**: Generated files are excluded from version control

## Configuration

Set the backend URL via environment variables:

```bash
# .env.local
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

## Troubleshooting

### Backend Not Accessible

```bash
# Make sure backend is running
cd ../backend
workon dhcp-backend
python3 run.py
```

### Generation Fails

1. Check backend health: `curl http://localhost:5000/api/v1/health`
2. Verify OpenAPI spec: `curl http://localhost:5000/api/v1/openapi.json`
3. Check console output for specific error messages

### Type Errors

Run `pnpm validate:api` to regenerate types and check for issues.

# OpenAPI Code Generation Setup - Technical Plan

## Brief Description

Implement automatic TypeScript type definitions and API client generation from the backend's OpenAPI specification using openapi-typescript and openapi-fetch libraries. The feature will provide a complete development workflow that automatically generates type-safe API clients, interfaces, and validation schemas from the backend's existing OpenAPI 3.0 specification, ensuring the frontend maintains type safety and consistency with the backend API while providing an easy mechanism to update generated code when the API changes.

## Relevant Files and Functions

### Files to Create
- `src/lib/api/generated/` - Directory for all generated code (excluded from git)
- `src/lib/api/client.ts` - Type-safe API client wrapper using generated types
- `src/lib/api/types.ts` - Re-exports of generated types for easier importing
- `scripts/generate-api.js` - Node.js script to fetch OpenAPI spec and generate code
- `scripts/generate-api.sh` - Shell script wrapper for easier execution
- `.gitignore` updates - Exclude generated code directory
- `package.json` scripts - Add code generation and update commands

### Files to Modify
- `package.json` - Add openapi-typescript, openapi-fetch, and related dependencies
- `src/types/app.ts` - Replace manual DHCPLease interface with generated types
- `vite.config.ts` - Add path alias for generated API types
- `tsconfig.json` - Include generated types directory in compilation
- Future components using API - Update to use generated client and types

### Key Functions to Implement
- `generateApiCode()` - Main function in generate-api.js to orchestrate code generation
- `fetchOpenApiSpec()` - Fetch OpenAPI specification from backend at http://localhost:5000/api/v1/openapi.json
- `generateTypes()` - Generate TypeScript types from OpenAPI spec (validated working with backend)
- `generateClient()` - Generate fetch-based API client with type safety
- `createApiClient()` - Factory function for configured API client instances  
- `validateApiResponse()` - Runtime validation using generated schemas

### Verified API Structure (from running backend)
The backend provides a complete OpenAPI 3.0.2 specification with:
- **5 endpoints**: `/health`, `/status`, `/leases`, `/leases/stream`, `/internal/notify-lease-change`
- **5 schemas**: `DhcpLease`, `Error`, `LeaseUpdateEvent`, `SseConnectionEstablished`, `SseHeartbeat`
- **Working server**: Confirmed accessible at http://localhost:5000/api/v1/
- **Complete documentation**: Full descriptions, examples, and proper schema references

## Algorithm Explanation

### OpenAPI Code Generation Workflow

1. **Specification Retrieval**:
   - Script connects to backend at configurable URL (default: http://localhost:5000)
   - Fetches OpenAPI specification from `/api/v1/openapi.json` endpoint
   - Validates that spec is valid OpenAPI 3.0 format
   - Handles connection errors gracefully with informative messages

2. **TypeScript Type Generation**:
   - Use `openapi-typescript` to generate TypeScript interfaces from OpenAPI components
   - Generate complete type definitions for all schemas: DhcpLease, Error, SSE events
   - Create union types for API responses and request payloads
   - Generate path parameter types and query parameter interfaces
   - Output types to `src/lib/api/generated/types.ts`

3. **API Client Generation**:
   - Use `openapi-fetch` to generate type-safe fetch-based client
   - Generate methods for each endpoint: GET /leases, GET /health, GET /status, POST /internal/notify-lease-change
   - Include proper TypeScript generics for request/response typing
   - Generate SSE client types for `/leases/stream` endpoint
   - Output client to `src/lib/api/generated/client.ts`

4. **Integration Layer**:
   - Create wrapper client in `src/lib/api/client.ts` with:
     - Base URL configuration from environment variables
     - Error handling and response transformation
     - Authentication headers (if needed in future)
     - Request/response interceptors for logging
     - Type-safe methods that wrap generated client

5. **Type Re-exports**:
   - Create `src/lib/api/types.ts` for clean imports throughout application
   - Re-export key types: DHCPLease, APIError, SSEEvent types
   - Export utility types for common patterns (API responses, paginated data)

### Development Workflow Integration

1. **Automatic Generation**:
   - `pnpm generate:api` - Generate API code from running backend
   - `pnpm generate:api:prod` - Generate from production backend URL
   - `pnpm update:api` - Regenerate and restart dev server

2. **Development Integration**:
   - Generated code excluded from git via .gitignore
   - Types available immediately in IDE with full autocomplete
   - Runtime type safety with generated validation schemas
   - Hot module replacement works with generated types

3. **Build Process**:
   - Generate API code as pre-build step in CI/CD
   - Validate that backend is accessible before generating
   - Fail build if API generation fails or types are invalid

## Implementation Phases

### Phase 1: Core Infrastructure Setup
- Add openapi-typescript, openapi-fetch, and supporting dependencies to package.json
- Create generation script infrastructure with proper error handling
- Set up generated code directory structure with .gitignore rules
- Implement basic OpenAPI spec fetching with retry logic and validation

### Phase 2: Type Generation Implementation
- Implement TypeScript interface generation using openapi-typescript
- Generate complete type definitions for all backend schemas
- Create utility types for common API patterns (responses, errors, SSE events)
- Set up proper module declarations and path aliases in TypeScript config

### Phase 3: API Client Generation
- Implement type-safe API client generation using openapi-fetch
- Create wrapper client with configuration, error handling, and interceptors
- Generate methods for all REST endpoints with proper typing
- Implement SSE client types and utilities for real-time connections

### Phase 4: Integration and Replacement
- Replace manual DHCPLease interface in src/types/app.ts with generated types
  - Current manual interface has fields: id, ipAddress, macAddress, hostname, leaseStart, leaseEnd, deviceType, status, isNew
  - Backend DhcpLease schema has: ip_address, mac_address, hostname, client_id, lease_time, is_active, is_static
  - Generated types will use proper backend field names and add missing fields
- Update any existing API calls to use generated client
- Create comprehensive type re-exports for clean importing  
- Add package.json scripts for easy code generation and updates

### Phase 5: Development Workflow Enhancement
- Add pre-commit hooks to validate API code is up-to-date
- Implement backend health check before generation
- Create documentation for updating generated code
- Add error handling for offline development scenarios

## Reference Materials

### Backend API Access
- **OpenAPI Specification URL**: http://localhost:5000/api/v1/openapi.json
- **API Base URL**: http://localhost:5000/api/v1/
- **Backend Startup**: `workon dhcp-backend && python3 run.py` (from backend directory)
- **Health Check**: http://localhost:5000/api/v1/health

### Saved Specifications
- **Current OpenAPI Spec**: `docs/features/openapi_code_generation/backend-openapi-spec.json`
- **Reference for validation and testing during implementation**

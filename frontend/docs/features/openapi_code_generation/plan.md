# OpenAPI Code Generation Setup - Technical Plan

## Brief Description

Implement automatic TypeScript type definitions and API client generation from the backend's OpenAPI specification using openapi-typescript and openapi-fetch libraries with TanStack Query integration. The code generator must be completely agnostic to the API structure and generate everything solely from the OpenAPI JSON specification without any hardcoded knowledge of endpoints, schemas, or business logic. The feature will provide a complete development workflow that automatically generates type-safe API clients, TanStack Query hooks, interfaces, and validation schemas from the backend's existing OpenAPI 3.0 specification, ensuring the frontend maintains type safety and consistency with the backend API while providing an easy mechanism to update generated code when the API changes.

## Relevant Files and Functions

### Files to Create
- `src/lib/api/generated/` - Directory for all generated code (excluded from git)
- `src/lib/api/generated/types.ts` - Generated TypeScript interfaces (auto-generated)
- `src/lib/api/generated/client.ts` - Generated fetch client (auto-generated)
- `src/lib/api/generated/queries.ts` - Generated TanStack Query hooks (auto-generated)
- `src/lib/api/client.ts` - Thin wrapper for configuration only (no API knowledge)
- `src/lib/api/types.ts` - Re-exports of generated types for easier importing
- `scripts/generate-api.js` - Generic OpenAPI code generator (API-agnostic)
- `scripts/generate-api.sh` - Shell script wrapper for easier execution
- `.gitignore` updates - Exclude generated code directory
- `package.json` scripts - Add code generation and update commands

### Files to Modify
- `package.json` - Add openapi-typescript, openapi-fetch, and TanStack Query code generation dependencies
- `src/types/app.ts` - Replace manual DHCPLease interface with generated types
- `vite.config.ts` - Add path alias for generated API types
- `tsconfig.json` - Include generated types directory in compilation
- Future components using API - Update to use generated client and types

### Key Functions to Implement
- `generateApiCode()` - Generic orchestration function (no API knowledge, purely OpenAPI-driven)
- `fetchOpenApiSpec()` - Generic OpenAPI spec fetcher (configurable URL, no hardcoded endpoints)
- `generateTypes()` - Generate TypeScript types purely from OpenAPI components schema
- `generateClient()` - Generate fetch-based API client purely from OpenAPI paths
- `generateQueryHooks()` - Generate TanStack Query hooks purely from OpenAPI operations
- `createApiClient()` - Generic factory function for configured API client instances

### Verified API Structure (from running backend)
The backend provides a complete OpenAPI 3.0.2 specification with:
- **5 endpoints**: `/health`, `/status`, `/leases`, `/leases/stream`, `/internal/notify-lease-change`
- **5 schemas**: `DhcpLease`, `Error`, `LeaseUpdateEvent`, `SseConnectionEstablished`, `SseHeartbeat`
- **Working server**: Confirmed accessible at http://localhost:5000/api/v1/
- **Complete documentation**: Full descriptions, examples, and proper schema references

## Critical Design Principle

**COMPLETE API AGNOSTICISM**: The code generator must have ZERO knowledge of the specific API being consumed. All code generation must be driven purely by parsing the OpenAPI JSON specification. The generator should work with ANY valid OpenAPI 3.0 specification, not just the DHCP API.

### Enforced Constraints:
- NO hardcoded endpoint paths (e.g., `/leases`, `/health`)
- NO hardcoded schema names (e.g., `DhcpLease`, `Error`)  
- NO hardcoded HTTP methods or response structures
- NO business logic or domain-specific knowledge
- ALL generated code must be derived from OpenAPI spec parsing
- Generator must work with different APIs by simply changing the OpenAPI JSON URL

## Algorithm Explanation

### OpenAPI Code Generation Workflow

1. **Specification Retrieval**:
   - Script connects to backend at configurable URL (default: http://localhost:5000)
   - Fetches OpenAPI specification from `/api/v1/openapi.json` endpoint
   - Validates that spec is valid OpenAPI 3.0 format
   - Handles connection errors gracefully with informative messages

2. **TypeScript Type Generation**:
   - Use `openapi-typescript` to generate TypeScript interfaces purely from OpenAPI components schema
   - Generate complete type definitions for all schemas found in the spec (no hardcoded schema names)
   - Create union types for API responses and request payloads based on OpenAPI definitions
   - Generate path parameter types and query parameter interfaces from OpenAPI paths
   - Output types to `src/lib/api/generated/types.ts` (purely generated, no manual additions)

3. **API Client Generation**:
   - Use `openapi-fetch` to generate type-safe fetch-based client purely from OpenAPI paths
   - Generate methods for each endpoint discovered in the OpenAPI spec (no hardcoded endpoints)
   - Include proper TypeScript generics for request/response typing based on OpenAPI operation definitions
   - Generate SSE client types for any `text/event-stream` endpoints found in spec
   - Output client to `src/lib/api/generated/client.ts` (purely generated, no manual additions)

4. **TanStack Query Hook Generation**:
   - Generate custom hooks for each GET endpoint using TanStack Query
   - Generate mutation hooks for POST/PUT/PATCH/DELETE endpoints using TanStack Query
   - Include proper TypeScript typing for query keys, variables, and responses
   - Generate SSE hooks for real-time data using TanStack Query with custom logic
   - Output hooks to `src/lib/api/generated/queries.ts` (purely generated, no manual additions)

5. **Integration Layer** (Minimal, Configuration Only):
   - Create thin wrapper client in `src/lib/api/client.ts` with ONLY:
     - Base URL configuration from environment variables
     - Generic error handling and response transformation
     - Authentication headers (if needed in future)
     - Request/response interceptors for logging
     - NO hardcoded API knowledge, purely configuration

6. **Type Re-exports** (Generated Types Only):
   - Create `src/lib/api/types.ts` for clean imports throughout application
   - Re-export generated types discovered from OpenAPI spec (no hardcoded type names)
   - Export utility types for common patterns based on generated API responses

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
- Add openapi-typescript, openapi-fetch, TanStack Query codegen, and supporting dependencies to package.json
- Create generation script infrastructure with proper error handling
- Set up generated code directory structure with .gitignore rules
- Implement basic OpenAPI spec fetching with retry logic and validation

### Phase 2: Type Generation Implementation
- Implement generic TypeScript interface generation using openapi-typescript
- Generate complete type definitions purely from OpenAPI components (no hardcoded schemas)
- Create utility types dynamically based on discovered API patterns in the spec
- Set up proper module declarations and path aliases in TypeScript config

### Phase 3: API Client and TanStack Query Generation
- Implement generic type-safe API client generation using openapi-fetch (no hardcoded endpoints)
- Generate TanStack Query hooks for all endpoints discovered in OpenAPI spec
- Create thin configuration wrapper client with NO API knowledge
- Generate SSE client types and TanStack Query integration for event-stream endpoints found in spec

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

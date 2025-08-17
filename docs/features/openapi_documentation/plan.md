# OpenAPI Documentation Generation - Technical Plan

## Brief Description

Implement automatic OpenAPI 3.0 specification generation for the DHCP monitoring Flask API using Marshmallow schemas and APISpec library. The feature will generate comprehensive API documentation that can be consumed by SPA applications to automatically generate TypeScript type definitions, ensuring type safety and reducing integration errors.

## Relevant Files and Functions

### Files to Create
- `app/api/openapi.py` - OpenAPI specification generator service using APISpec
- `app/api/v1/openapi_routes.py` - Routes for serving OpenAPI JSON and Swagger UI
- `app/schemas/__init__.py` - Schema module initialization
- `app/schemas/dhcp_lease_schema.py` - Marshmallow schema for DHCP lease objects
- `app/schemas/error_schema.py` - Marshmallow schema for error responses
- `app/schemas/sse_schema.py` - Marshmallow schemas for SSE event types
- `app/schemas/base_schema.py` - Base Marshmallow schema definitions

### Files to Modify
- `requirements.txt` - Add apispec and marshmallow dependencies
- `app/api/v1/__init__.py` - Import new OpenAPI routes
- `app/__init__.py` - Register OpenAPI generator and configure spec generation

### Key Functions to Implement
- `OpenApiGenerator.generate_spec()` - Generate complete OpenAPI specification using APISpec
- `OpenApiGenerator.register_schemas()` - Register Marshmallow schemas with APISpec
- `OpenApiGenerator._register_endpoints()` - Register API endpoints with documentation
- `get_openapi_spec()` - Route handler to serve OpenAPI JSON specification
- `get_swagger_ui()` - Route handler to serve Swagger UI interface

## Algorithm Explanation

### OpenAPI Specification Generation Algorithm

1. **Schema Definition**:
   - Create lightweight Marshmallow schemas for data models (DhcpLease, LeaseUpdateEvent, Error responses)
   - Define field types, descriptions, and examples in Marshmallow field definitions
   - Use APISpec's automatic OpenAPI schema generation from Marshmallow schemas

2. **Specification Generation**:
   - Initialize APISpec with OpenAPI 3.0 configuration and MarshmallowPlugin
   - Register Marshmallow schemas using `spec.components.schema()`
   - Define endpoint documentation with schema references using `spec.path()`
   - APISpec automatically converts Marshmallow schemas to OpenAPI format

3. **Endpoint Documentation**:
   - Manually define each API endpoint with HTTP methods, descriptions, and responses
   - Reference registered schemas using `{"$ref": "#/components/schemas/SchemaName"}`
   - Include response status codes, content types, and error scenarios
   - Add comprehensive descriptions and examples for each endpoint

4. **Runtime Serving**:
   - Serve complete OpenAPI specification at `/api/v1/openapi.json`
   - Serve interactive Swagger UI at `/api/v1/docs`
   - Generate specification on-demand using `spec.to_dict()`

## Implementation Phases

### Phase 1: Core Infrastructure
- Add apispec and marshmallow dependencies to requirements.txt
- Create OpenApiGenerator service with APISpec initialization
- Implement basic OpenAPI 3.0 specification structure with project metadata
- Register generator with Flask application factory

### Phase 2: Schema Implementation
- Create lightweight Marshmallow schemas for DHCP lease, error responses, and SSE events
- Register schemas with APISpec using MarshmallowPlugin for automatic conversion
- Ensure schema field definitions include descriptions and examples for documentation

### Phase 3: Endpoint Documentation
- Implement manual endpoint registration in OpenApiGenerator._register_endpoints()
- Document all existing API endpoints: /health, /status, /leases, /leases/stream, /internal/notify-lease-change
- Add comprehensive response documentation with proper HTTP status codes and schema references
- Include detailed endpoint descriptions and SSE event format examples

### Phase 4: Documentation Serving
- Create OpenAPI routes for serving JSON specification at /api/v1/openapi.json
- Implement Swagger UI serving at /api/v1/docs with embedded HTML template
- Add proper error handling and logging for documentation endpoints

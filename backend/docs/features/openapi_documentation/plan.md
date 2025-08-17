# OpenAPI Documentation Generation - Technical Plan

## Brief Description

Implement automatic OpenAPI 3.0 specification generation for the DHCP monitoring Flask API to enable type-safe frontend development. The feature will generate comprehensive API documentation with schema definitions that can be consumed by SPA applications to automatically generate TypeScript type definitions, ensuring type safety and reducing integration errors.

## Relevant Files and Functions

### Files to Create
- `app/api/openapi.py` - OpenAPI specification generator service
- `app/api/v1/openapi_routes.py` - Routes for serving OpenAPI documentation
- `app/schemas/` - Directory for schema definitions
- `app/schemas/__init__.py` - Schema module initialization
- `app/schemas/dhcp_lease_schema.py` - DHCP lease response schemas
- `app/schemas/error_schema.py` - Error response schemas
- `app/schemas/sse_schema.py` - SSE event schemas
- `app/schemas/base_schema.py` - Base schema definitions

### Files to Modify
- `requirements.txt` - Add apispec and marshmallow dependencies
- `app/api/v1/__init__.py` - Import new OpenAPI routes
- `app/__init__.py` - Register OpenAPI blueprint and configure spec generation
- `app/models/dhcp_lease.py` - Add schema generation methods
- `app/models/lease_update_event.py` - Add schema generation methods
- `app/utils/__init__.py` - Enhance ResponseHelper with schema-aware methods

### Key Functions to Implement
- `OpenApiGenerator.generate_spec()` - Core specification generation
- `OpenApiGenerator.register_schemas()` - Register all data schemas
- `OpenApiGenerator.register_endpoints()` - Register API endpoints with documentation
- `DhcpLeaseSchema.get_schema()` - Generate lease object schema
- `ErrorResponseSchema.get_schema()` - Generate error response schema
- `SseEventSchema.get_schema()` - Generate SSE event schema

### Key Functions to Modify
- `api_v1_bp` blueprint registration - Add OpenAPI endpoint documentation
- `DhcpLease.to_dict()` - Ensure consistent schema mapping
- `LeaseUpdateEvent.to_dict()` - Ensure consistent schema mapping
- `ResponseHelper.success_response()` - Add schema validation capabilities
- `ResponseHelper.error_response()` - Add schema validation capabilities

## Algorithm Explanation

### OpenAPI Specification Generation Algorithm

1. **Schema Definition Phase**:
   - Create Marshmallow schemas for all data models (DhcpLease, LeaseUpdateEvent, Error responses)
   - Define base schemas for common response patterns (success, error)
   - Map Python types to OpenAPI schema types with validation rules

2. **Endpoint Discovery Phase**:
   - Iterate through registered Flask blueprints and routes
   - Extract HTTP methods, paths, and route functions
   - Parse docstrings for endpoint descriptions and parameter information
   - Map route parameters to OpenAPI path/query parameters

3. **Documentation Generation Phase**:
   - Use apispec library to generate OpenAPI 3.0 specification
   - Register schemas with specification generator
   - Register endpoints with request/response schema references
   - Generate complete specification JSON/YAML

4. **Runtime Serving Phase**:
   - Serve OpenAPI specification at `/api/v1/openapi.json` endpoint
   - Optionally serve Swagger UI at `/api/v1/docs` for interactive documentation
   - Cache generated specification for performance

### Schema Mapping Algorithm

1. **Model Analysis**:
   - Analyze existing `to_dict()` methods in models
   - Extract field types, nullability, and validation rules
   - Map datetime fields to ISO 8601 string format
   - Map boolean fields with explicit true/false values

2. **Schema Generation**:
   - Create Marshmallow schema classes with field definitions
   - Add validation rules (required fields, format constraints)
   - Include field descriptions from model docstrings
   - Generate example values for documentation

3. **Response Schema Integration**:
   - Wrap data schemas in response containers
   - Define success response format (direct data return)
   - Define error response format (error message + optional details)
   - Handle array responses for list endpoints

## Implementation Phases

### Phase 1: Core Infrastructure (Foundation)
- Install and configure apispec and marshmallow dependencies
- Create base schema infrastructure and OpenAPI generator service
- Implement basic specification generation without endpoint documentation
- Create simple test endpoint to serve OpenAPI JSON specification

### Phase 2: Data Schema Implementation (Models)
- Implement Marshmallow schemas for all existing data models
- Add schema generation methods to DhcpLease and LeaseUpdateEvent models
- Create comprehensive response schemas for success and error cases
- Validate schema generation against existing API responses

### Phase 3: Endpoint Documentation (API Integration)
- Add OpenAPI documentation to all existing API endpoints
- Implement automatic endpoint discovery and documentation generation
- Add request/response schema mapping for each endpoint
- Include proper HTTP status codes and error response documentation

### Phase 4: Documentation Serving (User Interface)
- Create dedicated routes for serving OpenAPI specification
- Optionally implement Swagger UI integration for interactive documentation
- Add endpoint for downloading specification in JSON/YAML formats
- Implement caching for performance optimization

### Phase 5: Validation and Testing (Quality Assurance)
- Validate generated OpenAPI specification against OpenAPI 3.0 standard
- Test type generation workflow with sample frontend TypeScript generation
- Ensure all existing endpoints are properly documented
- Add automated tests for specification generation accuracy

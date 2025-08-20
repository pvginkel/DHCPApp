# Docker NGINX Deployment Plan

## Brief Description
Create a Dockerfile that builds the React frontend application and deploys it into an NGINX server for production deployment. The container will serve the built static assets through NGINX with appropriate configuration for a Single Page Application.

## Relevant Files and Functions

### Files to Create
- `Dockerfile` - Multi-stage Docker build file for frontend application
- `.dockerignore` - Docker ignore file to exclude unnecessary files from build context
- `nginx.conf` - NGINX configuration file for SPA routing and static file serving
- `openapi-schema.json` - Cached OpenAPI schema file for Docker builds (checked into git)

### Files to Reference
- `package.json:8` - Build script: `"build": "pnpm generate:api && tsc -b && vite build"`
- `package.json:15` - Prebuild script: `"prebuild": "pnpm generate:api"`
- `vite.config.ts:7-25` - Vite configuration with build output settings
- `scripts/generate-api.js` - API generation script that requires backend connection

### Files to Modify
- `scripts/generate-api.js` - Update to support using cached schema file during Docker builds

### Build Process Analysis
- Build command: `pnpm build` which runs:
  1. `pnpm generate:api` - Generates API client from OpenAPI spec (or cached schema)
  2. `tsc -b` - TypeScript compilation
  3. `vite build` - Vite production build
- Build output: Static files in `dist/` directory (default Vite output)
- Dependencies: pnpm package manager, Node.js runtime
- Schema caching: Uses `openapi-schema.json` when backend is not available (Docker builds)

## Step-by-Step Implementation

### Phase 1: Core Dockerfile Structure
1. **Multi-stage build setup**
   - Stage 1: Build stage using Node.js base image with pnpm
   - Stage 2: Production stage using NGINX alpine image

2. **Build stage implementation**
   - Install pnpm package manager
   - Copy package.json and pnpm-lock.yaml for dependency caching
   - Install dependencies with `pnpm install --frozen-lockfile`
   - Copy source code, configuration files, and cached OpenAPI schema
   - Set environment flag to use cached schema for API generation
   - Run build process: `pnpm build` (uses cached schema)

3. **Production stage implementation**
   - Use lightweight NGINX alpine base image
   - Copy built static assets from build stage `dist/` directory
   - Configure NGINX for SPA routing with fallback to index.html

### Phase 2: NGINX Configuration
1. **Create NGINX configuration file**
   - Configure server block for port 80
   - Set document root to serve static files
   - Enable gzip compression for better performance
   - Configure SPA routing: try_files directive to fallback to index.html
   - Set appropriate cache headers for static assets
   - Configure security headers

2. **SPA routing configuration**
   - Handle client-side routing for TanStack Router
   - Serve index.html for unmatched routes
   - Proper MIME type handling for static assets

### Phase 3: Docker Optimization
1. **Create .dockerignore file**
   - Exclude node_modules, dist, .git directories
   - Exclude development files and documentation
   - Exclude IDE and OS specific files

2. **Build optimization**
   - Use specific Node.js version for reproducible builds
   - Leverage Docker layer caching for dependencies
   - Minimize final image size with alpine base images
   - Multi-stage build to exclude development dependencies

### Phase 4: Cached Schema Implementation
1. **Implement cached schema system**
   - Create `openapi-schema.json` file in project root (checked into git)
   - Modify `scripts/generate-api.js` to detect cached schema usage
   - Add environment variable `USE_CACHED_SCHEMA` for Docker builds

2. **API generation logic updates**
   - During development: Download schema from running backend and update cache
   - During Docker build: Use cached schema file when backend unavailable
   - Fallback mechanism: Use cached schema if backend connection fails
   - Validate cached schema exists before using it

3. **Development workflow**
   - `pnpm generate:api` - Uses backend if available, falls back to cached schema
   - `pnpm build` - In Docker: uses cached schema, in development: uses backend

## Algorithm Details

### Multi-Stage Docker Build Process
```
Stage 1 (Build):
1. Start with Node.js base image
2. Install pnpm package manager
3. Set working directory
4. Copy package files for dependency caching
5. Install production and development dependencies
6. Copy source code, configuration, and cached OpenAPI schema
7. Set USE_CACHED_SCHEMA=true environment variable
8. Run API generation (uses cached schema file)
9. Execute build process (TypeScript + Vite)
10. Output static files to dist/ directory

Stage 2 (Production):
1. Start with NGINX alpine base image
2. Copy custom NGINX configuration
3. Copy static files from build stage
4. Expose port 80
5. Set NGINX as default command
```

### NGINX SPA Configuration Algorithm
```
1. Configure server block for port 80
2. Set root directory to served static files
3. Configure default index file (index.html)
4. Add gzip compression for text assets
5. Set cache headers for static assets (js, css, images)
6. Configure try_files directive:
   - Try exact file match
   - Try directory match
   - Fallback to index.html for SPA routing
7. Add security headers
8. Handle CORS if needed for API communication
```

## Implementation Phases

### Phase 1: Cached Schema Setup
- Implement cached schema system in `scripts/generate-api.js`
- Create initial `openapi-schema.json` file
- Test schema caching functionality

### Phase 2: Basic Dockerfile
- Create working multi-stage Dockerfile with cached schema support
- Basic NGINX configuration
- Verify build process and container functionality

### Phase 3: Optimization and Configuration
- Add .dockerignore for build optimization
- Enhanced NGINX configuration with caching and compression
- Environment variable support for API configuration

### Phase 4: Production Readiness
- Security headers and hardening
- Build optimization and layer caching
- Documentation and deployment instructions
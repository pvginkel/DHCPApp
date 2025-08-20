# Docker NGINX Deployment Plan

## Brief Description
Create a Dockerfile that builds the React frontend application and deploys it into an NGINX server for production deployment. The container will serve the built static assets through NGINX with appropriate configuration for a Single Page Application.

## Relevant Files and Functions

### Files to Create
- `Dockerfile` - Multi-stage Docker build file for frontend application
- `.dockerignore` - Docker ignore file to exclude unnecessary files from build context
- `nginx.conf` - NGINX configuration file for SPA routing and static file serving

### Files to Reference
- `package.json:8` - Build script: `"build": "pnpm generate:api && tsc -b && vite build"`
- `package.json:15` - Prebuild script: `"prebuild": "pnpm generate:api"`
- `vite.config.ts:7-25` - Vite configuration with build output settings
- `scripts/generate-api.js` - API generation script that requires backend connection

### Build Process Analysis
- Build command: `pnpm build` which runs:
  1. `pnpm generate:api` - Generates API client from OpenAPI spec
  2. `tsc -b` - TypeScript compilation
  3. `vite build` - Vite production build
- Build output: Static files in `dist/` directory (default Vite output)
- Dependencies: pnpm package manager, Node.js runtime

## Step-by-Step Implementation

### Phase 1: Core Dockerfile Structure
1. **Multi-stage build setup**
   - Stage 1: Build stage using Node.js base image with pnpm
   - Stage 2: Production stage using NGINX alpine image

2. **Build stage implementation**
   - Install pnpm package manager
   - Copy package.json and pnpm-lock.yaml for dependency caching
   - Install dependencies with `pnpm install --frozen-lockfile`
   - Copy source code and configuration files
   - Handle API generation requirement (may need mock/prod endpoint)
   - Run build process: `pnpm build`

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

### Phase 4: API Generation Considerations
1. **Handle API generation requirement**
   - Option A: Use production API endpoint during build
   - Option B: Pre-generate API client and include in source
   - Option C: Build-time environment variable configuration
   - Configure VITE_API_BASE_URL for containerized deployment

2. **Environment configuration**
   - Support runtime environment variable injection
   - Configure API base URL for different deployment environments
   - Handle production vs development API endpoints

## Algorithm Details

### Multi-Stage Docker Build Process
```
Stage 1 (Build):
1. Start with Node.js base image
2. Install pnpm package manager
3. Set working directory
4. Copy package files for dependency caching
5. Install production and development dependencies
6. Copy source code and configuration
7. Set environment variables for API generation
8. Run API generation (with prod endpoint or mock)
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

### Phase 1: Basic Dockerfile
- Create working multi-stage Dockerfile
- Basic NGINX configuration
- Verify build process and container functionality

### Phase 2: Optimization and Configuration
- Add .dockerignore for build optimization
- Enhanced NGINX configuration with caching and compression
- Environment variable support for API configuration

### Phase 3: Production Readiness
- Security headers and hardening
- Build optimization and layer caching
- Documentation and deployment instructions
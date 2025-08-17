#!/bin/bash

# OpenAPI Code Generation Script
# Generates TypeScript types and API client from backend OpenAPI specification

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL=${1:-"http://localhost:5000"}
HEALTH_ENDPOINT="${BACKEND_URL}/api/v1/health"
OPENAPI_ENDPOINT="${BACKEND_URL}/api/v1/openapi.json"

echo -e "${BLUE}🚀 OpenAPI Code Generation${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "Backend URL: ${BACKEND_URL}"
echo -e "Health Check: ${HEALTH_ENDPOINT}"
echo -e "OpenAPI Spec: ${OPENAPI_ENDPOINT}"
echo

# Check if backend is accessible
echo -e "${YELLOW}📡 Checking backend accessibility...${NC}"
if curl -s --fail "${HEALTH_ENDPOINT}" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is accessible${NC}"
else
    echo -e "${RED}❌ Backend is not accessible at ${HEALTH_ENDPOINT}${NC}"
    echo -e "${YELLOW}💡 Make sure to start the backend:${NC}"
    echo -e "   cd backend && workon dhcp-backend && python3 run.py"
    exit 1
fi

# Check if OpenAPI spec is available
echo -e "${YELLOW}📄 Checking OpenAPI specification...${NC}"
if curl -s --fail "${OPENAPI_ENDPOINT}" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OpenAPI specification is available${NC}"
else
    echo -e "${RED}❌ OpenAPI specification is not available at ${OPENAPI_ENDPOINT}${NC}"
    exit 1
fi

# Run the generation script
echo -e "${YELLOW}🔧 Running code generation...${NC}"
if [[ "$1" == "--prod" ]]; then
    node scripts/generate-api.js --prod
else
    node scripts/generate-api.js
fi

echo -e "${GREEN}🎉 Code generation completed successfully!${NC}"

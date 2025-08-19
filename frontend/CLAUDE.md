# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Essential Commands
- `pnpm dev` - Start development server on port 3000
- `pnpm build` - Build for production (includes API generation and type checking)
- `pnpm lint` - Run ESLint
- `pnpm type-check` - Run TypeScript type checking
- `pnpm generate:api` - Generate API client from OpenAPI spec (requires backend running)
- `pnpm generate:api:prod` - Generate API client for production environment

### API Generation
- API client is auto-generated from OpenAPI spec at backend `/api/v1/openapi.json`
- Generated files are in `src/lib/api/generated/` and excluded from git
- Always run `pnpm generate:api` before development when backend changes
- For production builds, use `pnpm generate:api:prod`
- **Important**: Backend only runs on IPv4 - use `curl -4` when testing endpoints manually

## Architecture Overview

This is a React SPA for DHCP lease monitoring with real-time updates via Server-Sent Events (SSE).

### Key Architectural Patterns
- **BFF Pattern**: Backend types are used directly in frontend without translation
- **Functional Programming**: All code uses functional style, no OOP
- **Type Safety**: End-to-end type safety with OpenAPI-generated types and Zod validation
- **Real-time First**: Components handle live data updates via SSE

### Tech Stack
- **Core**: React 19 + Vite + TypeScript
- **Routing**: TanStack Router with file-based routing
- **State Management**: TanStack Query for server state, React hooks for client state
- **Styling**: Tailwind CSS + Radix UI components
- **API**: OpenAPI-generated client with openapi-fetch
- **Validation**: Zod for runtime type validation
- **Package Manager**: pnpm

### Project Structure
```
src/
├── components/           # React components organized by domain
│   ├── common/          # Shared components (error-boundary, loading-spinner)
│   ├── dhcp/            # DHCP-specific components (lease-table)
│   ├── layout/          # Layout components
│   └── ui/              # Base UI components (button, input, table)
├── lib/
│   ├── api/             # API client and generated types
│   │   └── generated/   # Auto-generated from OpenAPI (gitignored)
│   └── utils/           # Utility functions
├── routes/              # TanStack Router pages
└── types/               # Application-specific type definitions
```

### API Integration
- Uses OpenAPI-generated client with TanStack Query hooks
- API client wrapper in `src/lib/api/client.ts` with global request/response logging
- Generated TanStack Query hooks provide type-safe data fetching
- SSE connections for real-time lease updates (custom implementation required)

### Key Features
- Real-time DHCP lease table with sorting and search
- Visual flash animations for updated lease entries
- Persistent user preferences in localStorage
- Responsive design optimized for data presentation

## Development Guidelines

### Code Style
- Use functional programming exclusively - no classes or OOP patterns
- Prefer composition over inheritance
- Use TypeScript strict mode for type safety
- Follow existing component patterns and naming conventions
- Only write code directly needed for features being implemented - avoid scaffolding or "future-useful" code
- Keep .gitignore files as brief as possible
- Use `pnpm` as the package manager (not npm or yarn)
- Don't auto-start the application during development

### State Management
- Use TanStack Query for all server state
- Use React hooks (useState, useReducer) for local component state
- Persist user preferences in localStorage via custom hooks

### Component Guidelines
- Components are in TypeScript (.tsx files)
- Use Radix UI primitives for interactive components
- Style with Tailwind CSS utility classes
- Include proper TypeScript types for all props

### API Usage
- Always regenerate API client after backend schema changes
- Use generated TanStack Query hooks for data fetching
- Handle loading and error states consistently
- Configure proper cache invalidation for real-time data

## Development Workflow

1. Start backend server first (required for API generation)
2. Run `pnpm generate:api` to generate current API client
3. Start development with `pnpm dev`
4. Run linting and type checking before commits

## Environment Configuration

- `VITE_API_BASE_URL` - Backend API URL (defaults to http://localhost:5000)
- Development server runs on port 3000 with auto-open browser
- Build output goes to `dist/` directory

## Testing

No test framework is currently configured. When adding tests, follow the established patterns and update this documentation.
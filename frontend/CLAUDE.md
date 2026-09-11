# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running commands in this environment
This repo runs inside a KubeCoder pod where pnpm and Node live in the `modern-app` tool container, not the main dev container. The curated verbs are `kc project setup|build|test|lint [--project FRONTEND]`, run from the repo root. Ad-hoc commands are prefixed with `cexec modern-app` (e.g. `cexec modern-app pnpm check`). The whole dev stack (backend + frontend + SSE gateway) starts together with `scripts/dev.py` from the repo root.

### Essential Commands
- `pnpm dev` - Start development server on port 3300
- `pnpm build` - Build for production (also runs API generation, route generation and `pnpm check`)
- `pnpm check` - Run the full check gate: ESLint, TypeScript, knip
- `pnpm check:lint` / `pnpm check:type-check` / `pnpm check:knip` - Run the individual checks
- `pnpm playwright test` - Run the Playwright end-to-end suite
- `pnpm generate:api` - Generate API client from OpenAPI spec (requires backend running)

### API Generation
- API client is auto-generated from OpenAPI spec at backend `/api/docs/openapi.json`
- Generated files are in `src/lib/api/generated/` and excluded from git
- Always run `pnpm generate:api` before development when backend changes
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

1. Start backend server first (only needed for `pnpm generate:api`; `scripts/dev.py` from the repo root starts backend, frontend and gateway together)
2. Run `pnpm generate:api` to generate current API client
3. Start development with `pnpm dev`
4. Run `pnpm check` before commits

## Environment Configuration

### API Configuration
- The frontend always uses `/api` as the API base URL (relative path)
- In development, Vite's proxy forwards `/api` requests to the backend (configured in `vite.config.ts`)
- In production, NGINX proxies `/api` to the backend
- Development server runs on port 3300 and does not auto-open a browser
- Build output goes to `dist/` directory

### Backend URL for Dev Proxy and API Generation
- `BACKEND_URL` - Backend host for Vite dev proxy and OpenAPI generation (defaults to `http://localhost:3301`)
- `SSE_GATEWAY_URL` - SSE gateway host for Vite dev proxy (defaults to `http://localhost:3302`)
- Set these in your environment or `.env.local` if the backend is on a different host

## Product brief

@docs/product_brief.md is the functional context for changes here.


## Testing

There is a full Playwright end-to-end test suite. Config lives at `playwright.config.ts` and specs live under `tests/`. The suite boots its own backend, frontend and SSE gateway per worker on free ports, so nothing needs starting first. Run it with `pnpm playwright test`, or `kc project test --project FRONTEND` from the repo root. There is one `chromium` project running with 2 workers. Tests tagged `@slow` are excluded unless `INCLUDE_SLOW_TESTS` is set. Follow the established patterns and update this documentation when adding tests.

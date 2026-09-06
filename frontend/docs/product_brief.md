# DHCP Monitoring Application - Frontend Product Brief

## Project Overview and Description

The DHCP Monitoring Frontend is a Single Page Application (SPA) that provides a clean, real-time interface for monitoring DHCP lease information in homelab environments. This frontend connects to the DHCP Monitoring backend service to display active DHCP leases with real-time updates via Server-Sent Events (SSE).

The primary purpose is to provide an easy-to-use interface for identifying active DHCP clients to facilitate manual assignment of static IP addresses. The application focuses on simplicity and clarity, presenting lease data in a sortable, searchable table format with visual feedback for real-time updates.

## Target Audience

- **Personal Homelab Use**: Single-user interface designed for personal network administration
- **Network Administrators**: Homelab users who need to monitor DHCP leases and identify devices for static IP assignment
- **Self-Service Management**: No authentication required - streamlined for individual use in trusted environments

## Primary Benefits and Features

### Core Features
- **Real-time DHCP Lease Display**: Interactive table showing active DHCP leases with device information
- **Live Update Notifications**: Visual flash animations with fade-out effects when lease data changes via SSE
- **Multi-column Sorting**: All table columns sortable with lease expiration as default sort order
- **Persistent Sort Preferences**: User's selected sort order saved in browser storage
- **Live Search Functionality**: Real-time filtering of lease data (session-based, not persisted)
- **Clean, Modern UI**: Simple but visually appealing interface optimized for data readability

### Key Benefits
- **Instant Lease Visibility**: Real-time awareness of active DHCP clients and their lease status
- **Efficient Device Identification**: Easy identification of devices requiring static IP assignment
- **Responsive User Experience**: Visual feedback for data changes with smooth animations
- **Persistent User Preferences**: Maintains user's preferred sorting across sessions
- **Homelab Optimized**: Designed specifically for personal network monitoring workflows

## High-Level Technology and Architecture

### Technology Stack
- **Frontend Framework**: React with Vite build tool and TypeScript
- **Routing**: TanStack Router for client-side navigation
- **Data Fetching**: TanStack Query for server state management and caching
- **Styling**: Tailwind CSS with Radix UI component library
- **Type Safety**: Zod for runtime validation and OpenAPI-generated types/client
- **Package Manager**: pnpm for dependency management
- **Real-time Communication**: Server-Sent Events (SSE) client for live updates
- **Data Persistence**: Browser localStorage for user preferences
- **Development Environment**: Local development setup with Vite dev server
- **Architecture Pattern**: Backend for Frontend (BFF) pattern - backend types are used directly in frontend
- **Deployment**: Kubernetes in production environment

### System Architecture
- **Single Page Application**: React-based client-side rendered interface with TypeScript
- **API Integration**: OpenAPI-generated client for type-safe Flask backend consumption
- **Real-time Updates**: SSE connection for live lease change notifications
- **State Management**: TanStack Query for server state and React hooks for client state
- **Functional Design**: Functional programming approach with React components (no OOP)
- **Type Safety**: End-to-end type safety with TypeScript and Zod validation
- **Responsive Design**: Tailwind CSS with Radix UI for mobile-friendly interface
- **BFF Pattern**: Backend types used directly in frontend for seamless integration

### Core Components
- DHCP lease data table with sortable columns (IP, MAC, hostname, lease expiration, device type)
- Real-time SSE client for receiving lease updates from backend
- Visual notification system with flash animations for updated lease entries
- Search/filter component for real-time data filtering
- Sort state management with localStorage persistence
- Clean, modern UI components optimized for data presentation

### Integration Points
- **Backend API**: Consumes RESTful endpoints from Python Flask backend
- **SSE Stream**: Maintains persistent connection for real-time lease updates
- **Browser Storage**: Utilizes localStorage for persisting user preferences
- **Responsive Layout**: Adapts to different screen sizes for optimal viewing

## Development Guidelines

### Code Standards
- **Functional Programming**: Use functional programming style exclusively - no object-oriented programming
- **Minimal Code**: Only write code directly needed for features being implemented - avoid scaffolding or "future-useful" code
- **Minimal Dependencies**: Keep .gitignore files brief and focused
- **Package Management**: Use pnpm as the package manager
- **No Auto-Start**: Development environment should not auto-start the application

### Tech Stack Overview
- **Frontend**: React + Vite + TypeScript + TanStack Router + TanStack Query + Tailwind (+ Radix UI) + Zod + OpenAPI-generated types/client
- **Deployment**: Kubernetes in production
- **Development**: Functional programming approach with minimal scaffolding

### Architecture Principles
- **BFF Pattern**: Backend for Frontend pattern allows direct use of backend types
- **Type Safety**: Leverage OpenAPI-generated types for end-to-end type safety
- **Real-time First**: Design components to handle live data updates gracefully
- **Production Ready**: Code should be production-ready for Kubernetes deployment

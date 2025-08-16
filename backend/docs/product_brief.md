# DHCP Monitoring Application - Product Brief

## Project Overview and Description

The DHCP Monitoring Application is a real-time network management tool designed for homelab environments to provide comprehensive visibility into DHCP lease information from dnsmasq services. The backend service reads DHCP lease data from mounted files and receives notifications of lease changes, enabling real-time monitoring of IP address allocations and device connectivity.

This backend component will serve as the data layer for a future Single Page Application (SPA) frontend, providing RESTful APIs and real-time data streaming capabilities for DHCP lease monitoring.

## Target Audience

- **Personal Homelab Use**: Single-user application designed for personal network monitoring and management in a homelab environment
- **Self-Service Monitoring**: No authentication or multi-user features required - streamlined for individual use

## Primary Benefits and Features

### Core Features
- **DHCP Lease Monitoring**: Real-time access to active DHCP leases from mounted dnsmasq files
- **Configuration Analysis**: Identification of devices with fixed IP assignments vs. dynamic allocations
- **Real-time Updates**: Server-Sent Events (SSE) streaming for immediate notification of lease changes
- **Device Classification**: Clear distinction between statically configured and dynamically assigned devices
- **Simple Architecture**: No authentication required - designed for single-user homelab environment

### Key Benefits
- **Real-time Visibility**: Instant awareness of new client connections and lease updates
- **Homelab Focused**: Streamlined for personal network monitoring without enterprise complexity
- **Easy Integration**: API-first design for seamless frontend integration
- **File-based Monitoring**: Direct access to dnsmasq lease and configuration files

## High-Level Technology and Architecture

### Technology Stack
- **Runtime**: Python with Flask web framework
- **Deployment**: Containerized homelab environment
- **Dependency Management**: Python virtual environment (.venv) with requirements.txt
- **Architecture Pattern**: Object-Oriented Programming (OOP) design

### System Architecture
- **Backend Service**: Flask-based REST API server
- **Data Source**: Direct file access through mounted volumes (paths configured via environment variables)
- **Real-time Communication**: Server-Sent Events (SSE) for live data streaming
- **Notification System**: Internal API endpoint called by companion container for lease change notifications
- **Future Integration**: Designed to support SPA frontend development
- **Deployment Target**: Containerized homelab environment

### Core Components
- DHCP lease file reading and parsing from mounted volumes
- Configuration file analysis for static/dynamic IP classification
- RESTful API endpoints for lease information retrieval
- SSE streaming service for real-time updates
- Internal notification endpoint for receiving lease change events from companion containers
- Environment variable configuration for file paths and settings

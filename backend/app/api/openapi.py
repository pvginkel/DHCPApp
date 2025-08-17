"""OpenAPI specification generator service using APISpec."""

import logging
from typing import Dict, Any
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from app.schemas import (
    DhcpLeaseSchema,
    ErrorSchema,
    LeaseUpdateEventSchema,
    SseConnectionEstablishedSchema,
    SseHeartbeatSchema
)

logger = logging.getLogger(__name__)


class OpenApiGenerator:
    """Service for generating OpenAPI 3.0 specifications using APISpec."""
    
    def __init__(self) -> None:
        """Initialize OpenAPI generator with APISpec configuration."""
        self.spec = APISpec(
            title="DHCP Network Management API",
            version="1.0.0",
            openapi_version="3.0.2",
            info={
                "description": (
                    "Real-time network management API for homelab environments "
                    "providing comprehensive visibility into DHCP lease information "
                    "from dnsmasq services with real-time updates via Server-Sent Events."
                ),
                "contact": {
                    "name": "DHCP Monitoring Application"
                },
                "license": {
                    "name": "MIT"
                }
            },
            servers=[
                {
                    "url": "/api/v1",
                    "description": "API Version 1"
                }
            ],
            plugins=[MarshmallowPlugin()]
        )
        
        # Track whether schemas and endpoints have been registered to prevent duplicates
        self._schemas_registered = False
        self._endpoints_registered = False
        
        logger.info("Initialized OpenAPI generator with APISpec")
    
    def generate_spec(self) -> Dict[str, Any]:
        """Generate complete OpenAPI specification.
        
        Returns:
            OpenAPI specification as dictionary
        """
        logger.debug("Generating OpenAPI specification")
        
        # Register schemas only once
        if not self._schemas_registered:
            self._register_schemas()
            self._schemas_registered = True
        
        # Register endpoints only once
        if not self._endpoints_registered:
            self._register_endpoints()
            self._endpoints_registered = True
        
        # Return complete specification
        spec_dict = self.spec.to_dict()
        logger.info("Successfully generated OpenAPI specification")
        return spec_dict
    
    def _register_schemas(self) -> None:
        """Register Marshmallow schemas with APISpec."""
        logger.debug("Registering Marshmallow schemas")
        
        # Register data model schemas
        self.spec.components.schema("DhcpLease", schema=DhcpLeaseSchema)
        self.spec.components.schema("Error", schema=ErrorSchema)
        
        # Register SSE event schemas
        self.spec.components.schema("LeaseUpdateEvent", schema=LeaseUpdateEventSchema)
        self.spec.components.schema("SseConnectionEstablished", schema=SseConnectionEstablishedSchema)
        self.spec.components.schema("SseHeartbeat", schema=SseHeartbeatSchema)
        
        logger.debug("Registered all Marshmallow schemas")
    
    def _register_endpoints(self) -> None:
        """Register API endpoints with comprehensive documentation."""
        logger.debug("Registering API endpoints")
        
        # Health check endpoint
        self.spec.path(
            path="/health",
            operations={
                "get": {
                    "tags": ["Health"],
                    "summary": "Health check endpoint",
                    "description": "Check if the DHCP monitoring service is running and healthy",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {
                                                "type": "string",
                                                "example": "healthy"
                                            },
                                            "service": {
                                                "type": "string",
                                                "example": "DHCP Backend API"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        )
        
        # Status endpoint
        self.spec.path(
            path="/status",
            operations={
                "get": {
                    "tags": ["System"],
                    "summary": "Service status information",
                    "description": "Get basic status information about the DHCP monitoring service",
                    "responses": {
                        "200": {
                            "description": "Service status information",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "version": {
                                                "type": "string",
                                                "example": "1.0.0"
                                            },
                                            "api_version": {
                                                "type": "string",
                                                "example": "v1"
                                            },
                                            "description": {
                                                "type": "string",
                                                "example": "DHCP Network Management API"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        )
        
        # DHCP leases endpoint
        self.spec.path(
            path="/leases",
            operations={
                "get": {
                    "tags": ["DHCP Leases"],
                    "summary": "Get all DHCP leases",
                    "description": (
                        "Retrieve all DHCP lease information from dnsmasq lease files. "
                        "Returns both active and expired leases with static/dynamic classification."
                    ),
                    "responses": {
                        "200": {
                            "description": "Successfully retrieved DHCP leases",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/DhcpLease"}
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Server error retrieving leases",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            }
        )
        
        # SSE stream endpoint
        self.spec.path(
            path="/leases/stream",
            operations={
                "get": {
                    "tags": ["Real-time Updates"],
                    "summary": "Server-Sent Events stream for lease updates",
                    "description": (
                        "Establish a Server-Sent Events (SSE) connection to receive real-time "
                        "notifications of DHCP lease changes. Events include lease additions, "
                        "updates, removals, and periodic heartbeats."
                    ),
                    "responses": {
                        "200": {
                            "description": "SSE stream established successfully",
                            "content": {
                                "text/event-stream": {
                                    "schema": {
                                        "type": "string",
                                        "description": (
                                            "Server-Sent Events stream with the following event types:\\n"
                                            "- connection_established: Initial connection confirmation\\n"
                                            "- lease_update: DHCP lease change notification\\n"
                                            "- heartbeat: Periodic keep-alive message"
                                        ),
                                        "examples": {
                                            "connection_established": {
                                                "value": (
                                                    "event: connection_established\\n"
                                                    "data: {\"client_id\": \"client_abc123\", \"message\": \"Successfully connected\", \"active_connections\": 1}\\n\\n"
                                                )
                                            },
                                            "lease_update": {
                                                "value": (
                                                    "event: lease_update\\n"
                                                    "data: {\"event_type\": \"lease_added\", \"lease\": {...}, \"timestamp\": \"2024-01-15T14:30:00Z\"}\\n\\n"
                                                )
                                            },
                                            "heartbeat": {
                                                "value": (
                                                    "event: heartbeat\\n"
                                                    "data: {\"timestamp\": 1705324200.123, \"active_connections\": 2}\\n\\n"
                                                )
                                            }
                                        }
                                    }
                                }
                            },
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "no-cache"
                                },
                                "Connection": {
                                    "schema": {"type": "string"},
                                    "description": "keep-alive"
                                }
                            }
                        }
                    }
                }
            }
        )
        
        # Internal notification endpoint
        self.spec.path(
            path="/internal/notify-lease-change",
            operations={
                "post": {
                    "tags": ["Internal"],
                    "summary": "Internal lease change notification",
                    "description": (
                        "Internal endpoint called by companion containers to notify "
                        "the API of DHCP lease file changes. Triggers re-reading of "
                        "lease files and broadcasts changes to SSE clients."
                    ),
                    "responses": {
                        "200": {
                            "description": "Notification processed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {
                                                "type": "string",
                                                "example": "success"
                                            },
                                            "message": {
                                                "type": "string",
                                                "example": "Lease change notification processed successfully"
                                            },
                                            "active_connections": {
                                                "type": "integer",
                                                "example": 2
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Error processing notification",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {
                                                "type": "string",
                                                "example": "error"
                                            },
                                            "message": {
                                                "type": "string",
                                                "example": "Failed to process lease change notification: error details"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        )
        
        logger.debug("Registered all API endpoints")

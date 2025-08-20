"""SSE routes for DHCP lease updates."""

import logging
import queue
import time
from flask import Response, request, current_app
from app.api.v1 import api_v1_bp


logger = logging.getLogger(__name__)


@api_v1_bp.route('/leases/stream', methods=['GET'])
def lease_updates_stream() -> Response:
    """SSE endpoint for streaming lease updates.
    
    Returns:
        Flask Response with SSE stream
    """
    logger.info("New SSE client connecting to lease updates stream")
    
    # Get SSE service from app context before generator execution
    sse_service = current_app.sse_service
    
    def generate_sse_stream():
        """Generator function for SSE events."""
        
        # Generate unique client ID
        client_id = sse_service.generate_client_id()
        
        try:
            # Register client with SSE service and get message queue
            message_queue = sse_service.add_client(client_id)
            
            # Send initial connection confirmation
            initial_message = sse_service._format_sse_message(
                'connection_established',
                {
                    'client_id': client_id,
                    'message': 'Successfully connected to lease updates stream',
                    'active_connections': sse_service.get_active_connections_count()
                }
            )
            yield initial_message
            
            # Send periodic heartbeat and process queued messages. The heartbeat is
            # set quite low because waitress doesn't properly detect client disconnections.
            # This is a workaround to ensure we can detect disconnections in a timely manner.
            heartbeat_interval = 5  # seconds
            start = time.perf_counter()
            
            while True:
                while True:
                    elapsed = time.perf_counter() - start
                    if elapsed >= heartbeat_interval:
                        break

                    remaining = heartbeat_interval - elapsed

                    # Check for queued messages
                    try:
                        # Non-blocking check for new messages
                        logger.info(f"Checking for messages in queue for client {client_id} waiting for {remaining:.2f} seconds")
                        message = message_queue.get(timeout=remaining)
                        yield message
                    except queue.Empty:
                        pass
                
                start += heartbeat_interval

                heartbeat_message = sse_service._format_sse_message(
                    'heartbeat',
                    {
                        'timestamp': time.time(),
                        'active_connections': sse_service.get_active_connections_count()
                    }
                )
                yield heartbeat_message
                
        except GeneratorExit:
            # Client disconnected
            logger.info(f"SSE client {client_id} disconnected")
            sse_service.remove_client(client_id)
        except Exception as e:
            logger.error(f"Error in SSE stream for client {client_id}: {e}")
            sse_service.remove_client(client_id)
    
    # Create SSE response with appropriate headers
    response = Response(
        generate_sse_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )
    
    return response


@api_v1_bp.route('/internal/notify-lease-change', methods=['POST'])
def notify_lease_change() -> tuple[dict, int]:
    """Internal notification endpoint that triggers lease re-read.
    
    This endpoint is called by companion containers to notify the app
    of lease file changes. It triggers a re-read of the lease file
    and broadcasts any detected changes to connected SSE clients.
    
    Returns:
        JSON response with success status
    """
    logger.info("Received lease change notification from companion container")
    
    try:
        # Get SSE service from app context
        sse_service = current_app.sse_service
        
        # Process the lease change notification
        sse_service.process_lease_change_notification()
        
        # Return success response
        return {
            'status': 'success',
            'message': 'Lease change notification processed successfully',
            'active_connections': sse_service.get_active_connections_count()
        }, 200
        
    except Exception as e:
        logger.error(f"Error processing lease change notification: {e}")
        return {
            'status': 'error',
            'message': f'Failed to process lease change notification: {str(e)}'
        }, 500

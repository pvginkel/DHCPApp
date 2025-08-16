"""Utilities package for essential utilities."""

import logging
from typing import Any, Dict, Optional


class Logger:
    """Utility class for logging operations."""
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get logger instance.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)


class ResponseHelper:
    """Utility class for API response formatting."""
    
    @staticmethod
    def success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
        """Create success response.
        
        Args:
            data: Response data
            message: Optional success message
            
        Returns:
            Formatted success response
        """
        response = {
            'success': True,
            'data': data
        }
        if message:
            response['message'] = message
        return response
    
    @staticmethod
    def error_response(message: str, code: Optional[str] = None) -> Dict[str, Any]:
        """Create error response.
        
        Args:
            message: Error message
            code: Optional error code
            
        Returns:
            Formatted error response
        """
        response = {
            'success': False,
            'error': message
        }
        if code:
            response['code'] = code
        return response

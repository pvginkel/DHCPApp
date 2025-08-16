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
    """Utility class for API response formatting following REST principles."""
    
    @staticmethod
    def success_response(data: Any) -> Any:
        """Create success response with direct data return.
        
        Args:
            data: Response data to return directly
            
        Returns:
            Data directly without wrapper attributes
        """
        return data
    
    @staticmethod
    def error_response(message: str, details: Optional[str] = None) -> Dict[str, Any]:
        """Create structured error response.
        
        Args:
            message: Error message
            details: Optional error details
            
        Returns:
            Structured error object
        """
        response = {
            'error': message
        }
        if details:
            response['details'] = details
        return response

"""Services package for business logic layer."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from app.services.sse_service import SseService


class BaseService(ABC):
    """Base service class following OOP principles."""
    
    def __init__(self) -> None:
        """Initialize base service."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def validate_input(self, data: Any) -> bool:
        """Validate input data.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass

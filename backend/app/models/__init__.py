"""Models package for data representation."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseModel(ABC):
    """Base model class following OOP principles."""
    
    def __init__(self) -> None:
        """Initialize base model."""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation.
        
        Returns:
            Dictionary representation of the model
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model instance from dictionary.
        
        Args:
            data: Dictionary data to create model from
            
        Returns:
            Model instance
        """
        pass

"""
Paginated response model for Easy Appointments API responses.
"""
from typing import Generic, List, Optional, Type, TypeVar, Any, Dict, cast
from pydantic import BaseModel, create_model

T = TypeVar('T')


class PaginatedResponse(Generic[T]):
    """
    A generic paginated response model for Easy Appointments API responses.
    
    Attributes:
        next: URL for the next page of results, or None if there are no more pages
        previous: URL for the previous page of results, or None if this is the first page
        total: Total number of items available across all pages
        results: List of items in the current page
    """
    def __init__(
        self,
        next_page: Optional[str],
        previous_page: Optional[str],
        total: int,
        results: List[T]
    ):
        """
        Initialize a new PaginatedResponse.
        
        Args:
            next_page: URL for the next page of results, or None if there are no more pages
            previous_page: URL for the previous page of results, or None if this is the first page
            total: Total number of items available across all pages
            results: List of items in the current page
        """
        self.next = next_page
        self.previous = previous_page
        self.total = total
        self.results = results
    
    @classmethod
    def from_list(cls, data: List[Dict[str, Any]], item_class: Type[T]) -> 'PaginatedResponse[T]':
        """
        Create a PaginatedResponse instance from a list.
        
        Args:
            data: List containing the response data
            item_class: The class to use for creating the items in the results list
            
        Returns:
            A new PaginatedResponse instance
        """
        # For list responses, we don't have pagination info
        results = []
        for item in data:
            try:
                if hasattr(item_class, "model_validate"):
                    # Pydantic v2
                    results.append(item_class.model_validate(item))
                else:
                    # Fallback for any other class with from_dict method
                    results.append(item_class.from_dict(item))
            except Exception as e:
                import logging
                logger = logging.getLogger("easyappointments")
                logger.warning(f"Failed to parse item in results: {e}")
                
        return cls(
            next_page=None,
            previous_page=None,
            total=len(results),
            results=results
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], item_class: Type[T]) -> 'PaginatedResponse[T]':
        """
        Create a PaginatedResponse instance from a dictionary.
        
        Args:
            data: Dictionary containing the paginated response data
            item_class: The class to use for creating the items in the results list
            
        Returns:
            A new PaginatedResponse instance
        """
        # If data is a list, delegate to from_list
        if isinstance(data, list):
            return cls.from_list(data, item_class)
            
        # Handle case where data is None or not a dict
        if not data or not isinstance(data, dict):
            return cls(next_page=None, previous_page=None, total=0, results=[])
            
        # Get results safely
        results_data = data.get('results', [])
        if not isinstance(results_data, list):
            results_data = []
            
        # Create result objects
        results = []
        for item in results_data:
            try:
                if hasattr(item_class, "model_validate"):
                    # Pydantic v2
                    results.append(item_class.model_validate(item))
                else:
                    # Fallback for any other class with from_dict method
                    results.append(item_class.from_dict(item))
            except Exception as e:
                import logging
                logger = logging.getLogger("easyappointments")
                logger.warning(f"Failed to parse item in results: {e}")
                
        return cls(
            next_page=data.get('next'),
            previous_page=data.get('previous'),
            total=data.get('total', len(results)),
            results=results
        )

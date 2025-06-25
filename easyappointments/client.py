"""
Main client module for interacting with the Easy Appointments API.
"""
from typing import Optional

import httpx

from easyappointments.api.admins import AdminsAPI
from easyappointments.api.providers import ProvidersAPI
from easyappointments.api.customers import CustomersAPI


class EasyAppointmentsClient:
    """
    Client for interacting with the Easy Appointments API.
    
    This client delegates to domain-specific managers for different API endpoints.
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "http://localhost/index.php/api/v1",
        http_client: Optional[httpx.AsyncClient] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 30.0,
        logging_enabled: bool = True
    ):
        """
        Initialize a new Easy Appointments API client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API (defaults to http://localhost/index.php/api/v1)
            http_client: Optional HTTP client to use (defaults to a new httpx.AsyncClient)
            max_retries: Maximum number of retries for failed requests
            retry_delay: Base delay between retries in seconds (exponential backoff is applied)
            timeout: Default timeout for requests in seconds
            logging_enabled: Whether to enable logging
        """
        self._api_key = api_key
        self._base_url = base_url.rstrip('/')
        self._http_client = http_client or httpx.AsyncClient(
            timeout=timeout, follow_redirects=True
        )
        
        # Initialize domain-specific API managers
        self.admins = AdminsAPI(
            api_key, 
            base_url, 
            http_client=self._http_client,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
            logging_enabled=logging_enabled
        )
        
        self.providers = ProvidersAPI(
            api_key, 
            base_url, 
            http_client=self._http_client,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
            logging_enabled=logging_enabled
        )
        
        self.customers = CustomersAPI(
            api_key, 
            base_url, 
            http_client=self._http_client,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
            logging_enabled=logging_enabled
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()

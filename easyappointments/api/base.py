"""
Base API client module providing common functionality for all API managers.
"""
import json
import logging
from typing import Any, Dict, List, Optional, TypeVar, Union
from urllib.parse import urljoin

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)

from easyappointments.exceptions import (
    EasyAppointmentsError,
    RateLimitError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    ServerError,
)

# Set up logging
logger = logging.getLogger("easyappointments")

T = TypeVar("T")


class BaseAPI:
    """
    Base class for all API managers providing common functionality.
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
        Initialize a new API manager.
        
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
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._timeout = timeout
        self._logging_enabled = logging_enabled
        
        if logging_enabled and not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
    
    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get headers for API requests including authentication.
        
        Args:
            additional_headers: Optional additional headers to include
            
        Returns:
            Dictionary of headers
        """
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if additional_headers:
            headers.update(additional_headers)
            
        return headers
    
    def _handle_error_response(self, response: httpx.Response) -> None:
        """
        Handle error responses from the API.
        
        Args:
            response: HTTP response
            
        Raises:
            AuthenticationError: For authentication errors (401)
            ResourceNotFoundError: For not found errors (404)
            ValidationError: For validation errors (400)
            RateLimitError: For rate limit errors (429)
            ServerError: For server errors (5xx)
            EasyAppointmentsError: For other API errors
        """
        status_code = response.status_code
        request_id = response.headers.get("X-Request-ID")
        
        try:
            response_body = response.json()
            
            # Try to extract error message from various possible formats
            if isinstance(response_body, list) and len(response_body) > 0:
                # Handle list-type error responses
                error_message = "; ".join(str(item) for item in response_body)
            elif isinstance(response_body, dict):
                if "message" in response_body:
                    error_message = response_body["message"]
                elif "error" in response_body:
                    error_message = response_body["error"]
                # Handle validation errors which may be a dict of field-specific errors
                elif any(isinstance(v, list) for v in response_body.values()):
                    # Format validation errors like: "field1: error1, error2; field2: error3"
                    validation_errors = []
                    for field, errors in response_body.items():
                        if isinstance(errors, list):
                            field_errors = ", ".join(str(error) for error in errors)
                            validation_errors.append(f"{field}: {field_errors}")
                        else:
                            validation_errors.append(f"{field}: {errors}")
                    error_message = "; ".join(validation_errors)
                else:
                    error_message = str(response_body)
            else:
                error_message = "Unknown error"
        except json.JSONDecodeError:
            response_body = None
            error_message = response.text or f"HTTP error {status_code}"
        
        if status_code == 401:
            raise AuthenticationError(status_code, error_message, response_body, request_id, response)
        elif status_code == 404:
            raise ResourceNotFoundError(status_code, error_message, response_body, request_id, response)
        elif status_code == 400:
            raise ValidationError(status_code, error_message, response_body, request_id, response)
        elif status_code == 429:
            raise RateLimitError(status_code, error_message, response_body, request_id, response)
        elif 500 <= status_code < 600:
            raise ServerError(status_code, error_message, response_body, request_id, response)
        else:
            raise EasyAppointmentsError(status_code, error_message, response_body, request_id, response)
    
    def _should_retry(self, exception: Exception) -> bool:
        """
        Determine if a request should be retried based on the exception.
        
        Args:
            exception: The exception that was raised
            
        Returns:
            True if the request should be retried, False otherwise
        """
        if isinstance(exception, RateLimitError):
            return True
        if isinstance(exception, ServerError):
            return True
        if isinstance(exception, httpx.TimeoutException):
            return True
        if isinstance(exception, httpx.TransportError):
            return True
        return False
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask sensitive data for logging.
        
        Args:
            data: Request data
            
        Returns:
            Data with sensitive fields masked
        """
        if not data:
            return data
            
        sensitive_fields = ["api_key", "key", "secret", "password", "token"]
        masked_data = data.copy()
        
        for field in sensitive_fields:
            if field in masked_data and masked_data[field]:
                masked_data[field] = "*****"
                
        return masked_data
        
    async def _make_request(
        self, 
        method: str, 
        path: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        return_raw: bool = False,
    ) -> Union[Dict[str, Any], List[Any], httpx.Response]:
        """
        Make an HTTP request to the API with retry support.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API endpoint path (will be joined with base_url)
            params: Optional query parameters
            data: Optional request body data
            additional_headers: Optional additional headers
            timeout: Optional request timeout in seconds
            return_raw: If True, return the raw httpx.Response instead of parsing JSON
            
        Returns:
            Union[Dict, List, httpx.Response]: The response data or raw response
        
        Raises:
            EasyAppointmentsError: For API errors
            httpx.HTTPError: For HTTP errors that are not handled by EasyAppointmentsError
        """
        # Handle path joining correctly - if path starts with /, remove it
        if path.startswith('/'):
            path = path[1:]
        url = urljoin(self._base_url + '/', path)
        headers = self._get_headers(additional_headers)
        
        request_kwargs = {
            "headers": headers,
            "params": params,
        }
        
        if data is not None:
            request_kwargs["json"] = data
            
        if timeout is not None:
            request_kwargs["timeout"] = timeout
        
        if self._logging_enabled:
            # Log the request details
            if method == "GET":
                logger.info("Making %s request to %s (params: %s)", method, url, params)
            else:
                masked_data = self._mask_sensitive_data(data) if data else None
                logger.info("Making %s request to %s (params: %s, data: %s)", 
                            method, url, params, masked_data)
        
        # Define retry decorator
        @retry(
            retry=retry_if_exception_type(
                (RateLimitError, ServerError, httpx.TimeoutException, httpx.TransportError)
            ),
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=self._retry_delay, min=self._retry_delay, max=self._retry_delay * 10),
            reraise=True,
        )
        async def _execute_request():
            try:
                response = await self._http_client.request(method, url, **request_kwargs)
                
                if self._logging_enabled:
                    logger.info("Received response from %s (status: %s)", url, response.status_code)
                    
                # Check if response is not successful
                if not response.is_success:
                    self._handle_error_response(response)
                
                # If we want the raw response, return it directly
                if return_raw:
                    return response
                    
                # Otherwise parse JSON
                try:
                    if response.status_code == 204:  # No Content
                        return {}
                    data = response.json()
                    return data
                except json.JSONDecodeError:
                    if self._logging_enabled:
                        logger.error("Invalid JSON response from %s", url)
                    raise EasyAppointmentsError(
                        message=f"Invalid JSON response: {response.text[:100]}...",
                        status_code=response.status_code,
                        response=response
                    )
            except (EasyAppointmentsError, httpx.HTTPError) as e:
                if self._logging_enabled:
                    logger.error("Error making request to %s: %s", url, str(e))
                raise
        
        try:
            return await _execute_request()
        except RetryError as e:
            if self._logging_enabled:
                logger.error("Max retries exceeded for request to %s: %s", url, str(e))
            # Re-raise the last exception
            raise e.last_attempt.exception()
    
    async def _get(
        self, 
        path: str, 
        params: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        return_raw: bool = False,
    ) -> Union[Dict[str, Any], List[Any], httpx.Response]:
        """
        Make a GET request to the API.
        
        Args:
            path: API endpoint path
            params: Optional query parameters
            additional_headers: Optional additional headers
            timeout: Optional request timeout in seconds
            return_raw: If True, return the raw httpx.Response instead of parsing JSON
            
        Returns:
            Union[Dict, List, httpx.Response]: The response data or raw response
        """
        return await self._make_request(
            "GET", 
            path, 
            params=params,
            additional_headers=additional_headers,
            timeout=timeout,
            return_raw=return_raw,
        )
    
    async def _post(
        self, 
        path: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Make a POST request to the API.
        
        Args:
            path: API endpoint path
            data: Optional request body data
            params: Optional query parameters
            additional_headers: Optional additional headers
            timeout: Optional request timeout in seconds
            
        Returns:
            Union[Dict, List]: The response data
        """
        return await self._make_request(
            "POST", 
            path, 
            data=data,
            params=params,
            additional_headers=additional_headers,
            timeout=timeout,
        )
    
    async def _put(
        self, 
        path: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Make a PUT request to the API.
        
        Args:
            path: API endpoint path
            data: Optional request body data
            params: Optional query parameters
            additional_headers: Optional additional headers
            timeout: Optional request timeout in seconds
            
        Returns:
            Union[Dict, List]: The response data
        """
        return await self._make_request(
            "PUT", 
            path, 
            data=data,
            params=params,
            additional_headers=additional_headers,
            timeout=timeout,
        )
    
    async def _delete(
        self, 
        path: str, 
        params: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> None:
        """
        Make a DELETE request to the API.
        
        Args:
            path: API endpoint path
            params: Optional query parameters
            additional_headers: Optional additional headers
            timeout: Optional request timeout in seconds
        """
        await self._make_request(
            "DELETE", 
            path, 
            params=params,
            additional_headers=additional_headers,
            timeout=timeout,
        )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

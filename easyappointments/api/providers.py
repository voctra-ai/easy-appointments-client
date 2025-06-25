"""
Providers API manager for interacting with Easy Appointments providers.
"""
from typing import Dict, List, Optional, Union, Any

from easyappointments.api.base import BaseAPI
from easyappointments.models import Provider, PaginatedResponse


class ProvidersAPI(BaseAPI):
    """
    Manager for Easy Appointments Providers API endpoints.
    
    This class provides methods for interacting with providers including
    listing, creating, updating, and deleting providers.
    
    Methods:
        list_providers() -> PaginatedResponse[Provider]: List all providers
        get_provider(provider_id: int) -> Provider: Get details of a specific provider
        create_provider(provider: Provider) -> Provider: Create a new provider
        update_provider(provider_id: int, provider: Provider) -> Provider: Update an existing provider
        delete_provider(provider_id: int) -> None: Delete a provider
    """
    
    async def list_providers(
        self,
        page: int = 1,
        length: int = 10,
        sort: str = "-id"
    ) -> PaginatedResponse[Provider]:
        """
        List all providers with pagination support.
        
        Args:
            page: Page number (1-based)
            length: Number of items per page
            sort: Sort order (prefix with - for descending)
            
        Returns:
            PaginatedResponse containing Provider objects
            
        Raises:
            EasyAppointmentsError: If the API request fails
            
        Example:
            ```python
            # Get first page of 10 providers, sorted by ID descending (default)
            providers = await client.providers.list_providers()
            
            # Get second page with 20 items per page
            providers = await client.providers.list_providers(page=2, length=20)
            
            # Sort by name ascending
            providers = await client.providers.list_providers(sort="first_name")
            
            # Access the provider objects
            for provider in providers.results:
                print(f"Provider: {provider.first_name} {provider.last_name} (ID: {provider.id})")
            ```
        """
        params = {
            "page": page,
            "length": length,
            "sort": sort
        }
        response = await self._get("/providers", params=params)
        return PaginatedResponse.from_dict(response, Provider)
    
    async def get_provider(self, provider_id: int) -> Provider:
        """
        Get details of a specific provider.
        
        Args:
            provider_id: ID of the provider to get
            
        Returns:
            Provider object
            
        Raises:
            ResourceNotFoundError: If the provider does not exist
            EasyAppointmentsError: For other API errors
            
        Example:
            ```python
            # Get provider by ID
            provider = await client.providers.get_provider(1)
            print(f"Provider: {provider.first_name} {provider.last_name}")
            ```
        """
        response = await self._get(f"/providers/{provider_id}")
        return Provider.model_validate(response)
    
    async def create_provider(self, provider: Union[Provider, Dict[str, Any]]) -> Provider:
        """
        Create a new provider.
        
        Args:
            provider: Provider object or dictionary containing provider data
            
        Returns:
            Provider object representing the created provider
            
        Raises:
            ValidationError: If the provider data is invalid
            EasyAppointmentsError: For other API errors
            
        Example:
            ```python
            # Using a Provider object
            from easyappointments.models import Provider, ProviderSettings, WorkingPlan
            
            # Create working plan
            working_plan = {
                "sunday": {"start": None, "end": None, "breaks": []},
                "monday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "tuesday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "wednesday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "thursday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "friday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "saturday": {"start": None, "end": None, "breaks": []}
            }
            
            # Create provider settings
            settings = ProviderSettings(
                username="johndoe",
                password="SecurePassword123!",
                working_plan=working_plan
            )
            
            # Create provider
            new_provider = Provider(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="123-456-7890",
                settings=settings,
                services=[1]
            )
            
            # Create the provider
            created_provider = await client.providers.create_provider(new_provider)
            print(f"Created provider with ID: {created_provider.id}")
            
            # Using a dictionary
            provider_data = {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "phone": "123-456-7890",
                "settings": {
                    "username": "johndoe",
                    "password": "SecurePassword123!",
                    "workingPlan": {
                        "sunday": {"start": None, "end": None, "breaks": []},
                        "monday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                        "tuesday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                        "wednesday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                        "thursday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                        "friday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                        "saturday": {"start": None, "end": None, "breaks": []}
                    }
                },
                "services": [1]
            }
            
            created_provider = await client.providers.create_provider(provider_data)
            print(f"Created provider with ID: {created_provider.id}")
            ```
        """
        if isinstance(provider, Provider):
            # Convert Provider object to dictionary
            provider_data = provider.model_dump(by_alias=True)
        else:
            provider_data = provider
            
        response = await self._post("/providers", data=provider_data)
        return Provider.model_validate(response)
    
    async def update_provider(self, provider_id: int, provider: Union[Provider, Dict[str, Any]]) -> Provider:
        """
        Update an existing provider.
        
        Args:
            provider_id: ID of the provider to update
            provider: Provider object or dictionary containing provider data
            
        Returns:
            Provider object representing the updated provider
            
        Raises:
            ResourceNotFoundError: If the provider does not exist
            ValidationError: If the provider data is invalid
            EasyAppointmentsError: For other API errors
            
        Example:
            ```python
            # Update provider by ID
            provider = await client.providers.get_provider(1)
            provider.first_name = "Jane"
            updated_provider = await client.providers.update_provider(1, provider)
            print(f"Updated provider: {updated_provider.first_name} {updated_provider.last_name}")
            ```
        """
        if isinstance(provider, Provider):
            # Convert Provider object to dictionary
            provider_data = provider.model_dump(by_alias=True)
        else:
            provider_data = provider
            
        response = await self._put(f"/providers/{provider_id}", data=provider_data)
        return Provider.model_validate(response)
    
    async def delete_provider(self, provider_id: int) -> None:
        """
        Delete a provider.
        
        Args:
            provider_id: ID of the provider to delete
            
        Raises:
            ResourceNotFoundError: If the provider does not exist
            EasyAppointmentsError: For other API errors
            
        Example:
            ```python
            # Delete provider by ID
            await client.providers.delete_provider(1)
            ```
        """
        await self._delete(f"/providers/{provider_id}")

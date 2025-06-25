"""
Admins API manager for interacting with Easy Appointments admins.
"""
from typing import Optional

from easyappointments.api.base import BaseAPI
from easyappointments.models import Admin, PaginatedResponse


class AdminsAPI(BaseAPI):
    """
    Manager for Easy Appointments Admins API endpoints.
    
    This class provides methods for interacting with admin users including
    listing, creating, updating, and deleting admin users.
    
    Methods:
        list_admins() -> PaginatedResponse[Admin]: List all admin users
        get_admin(admin_id: int) -> Admin: Get details of a specific admin
    """
    
    async def list_admins(
        self,
        page: int = 1,
        length: int = 10,
        sort: str = "-id"
    ) -> PaginatedResponse[Admin]:
        """
        List all admin users with pagination support.
        
        Args:
            page: Page number (1-based)
            length: Number of items per page
            sort: Sort order (prefix with - for descending)
            
        Returns:
            PaginatedResponse containing Admin objects
            
        Raises:
            EasyAppointmentsError: If the API request fails
            
        Example:
            ```python
            # Get first page of 10 admins, sorted by ID descending (default)
            admins = await client.admins.list_admins()
            
            # Get second page with 20 items per page
            admins = await client.admins.list_admins(page=2, length=20)
            
            # Sort by email ascending
            admins = await client.admins.list_admins(sort="email")
            
            # Access the admin objects
            for admin in admins.results:
                print(f"Admin: {admin.first_name} {admin.last_name} (ID: {admin.id})")
            ```
        """
        params = {
            "page": page,
            "length": length,
            "sort": sort
        }
        response = await self._get("/admins", params=params)
        return PaginatedResponse.from_dict(response, Admin)
    
    async def get_admin(self, admin_id: int) -> Admin:
        """
        Get details of a specific admin.
        
        Args:
            admin_id: ID of the admin to get
            
        Returns:
            Admin object
            
        Raises:
            ResourceNotFoundError: If the admin does not exist
            EasyAppointmentsError: For other API errors
            
        Example:
            ```python
            # Get admin by ID
            admin = await client.admins.get_admin(1)
            print(f"Admin: {admin.first_name} {admin.last_name}")
            ```
        """
        response = await self._get(f"/admins/{admin_id}")
        return Admin.model_validate(response)

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
    
    async def list_admins(self) -> PaginatedResponse[Admin]:
        """
        List all admin users.
        
        Returns:
            PaginatedResponse containing Admin objects
            
        Raises:
            EasyAppointmentsError: If the API request fails
            
        Example:
            ```python
            # Get all admins
            admins = await client.admins.list_admins()
            
            # Access the admin objects
            for admin in admins.results:
                print(f"Admin: {admin.first_name} {admin.last_name} (ID: {admin.id})")
            ```
        """
        response = await self._get("/admins")
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

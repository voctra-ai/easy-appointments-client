"""
Customers API manager for interacting with Easy Appointments customers.
"""
from typing import Optional

from easyappointments.api.base import BaseAPI
from easyappointments.exceptions import ResourceNotFoundError
from easyappointments.models import Customer, PaginatedResponse


class CustomersAPI(BaseAPI):
    """
    Manager for Easy Appointments Customers API endpoints.
    
    This class provides methods for interacting with customers including
    listing, creating, updating, and deleting customers.
    """
    
    async def list_customers(
        self,
        page: int = 1,
        length: int = 10,
        sort: str = "-id"
    ) -> PaginatedResponse[Customer]:
        """
        List all customers with pagination support.
        
        Args:
            page: Page number (1-based)
            length: Number of items per page
            sort: Sort order (prefix with - for descending)
            
        Returns:
            PaginatedResponse containing Customer objects
            
        Raises:
            EasyAppointmentsError: If the API request fails
            
        Example:
            ```python
            # Get first page of 10 customers, sorted by ID descending (default)
            customers = await client.customers.list_customers()
            
            # Get second page with 20 items per page
            customers = await client.customers.list_customers(page=2, length=20)
            
            # Sort by last name ascending
            customers = await client.customers.list_customers(sort="last_name")
            
            # Access the customer objects
            for customer in customers.results:
                print(f"Customer: {customer.first_name} {customer.last_name} (ID: {customer.id})")
            ```
        """
        params = {
            "page": page,
            "length": length,
            "sort": sort
        }
        response = await self._get("/customers", params=params)
        return PaginatedResponse.from_dict(response, Customer)
    
    async def get_customer(self, customer_id: int) -> Optional[Customer]:
        """
        Get details of a specific customer.
        
        Args:
            customer_id: ID of the customer to retrieve
            
        Returns:
            Customer object if found, None otherwise
            
        Raises:
            EasyAppointmentsError: If the API request fails for reasons other than 404
        """
        try:
            response = await self._get(f"/customers/{customer_id}")
            return Customer(**response)
        except ResourceNotFoundError:
            return None
    
    async def create_customer(self, customer: Customer) -> Customer:
        """
        Create a new customer.
        
        Args:
            customer: Customer object containing the customer data
            
        Returns:
            Created Customer object with ID and other server-generated fields
            
        Raises:
            EasyAppointmentsError: If the API request fails or validation fails
        """
        # Convert the customer to a dictionary, excluding unset fields
        customer_data = customer.model_dump(exclude_unset=True, by_alias=True)
        
        # Remove ID if it's None (shouldn't be sent for creation)
        if 'id' in customer_data and customer_data['id'] is None:
            del customer_data['id']
            
        response = await self._post("/customers", data=customer_data)
        return Customer(**response)
    
    async def update_customer(self, customer_id: int, customer: Customer) -> Customer:
        """
        Update an existing customer.
        
        Args:
            customer_id: ID of the customer to update
            customer: Customer object with updated data
            
        Returns:
            Updated Customer object
            
        Raises:
            EasyAppointmentsError: If the API request fails or validation fails
        """
        customer_data = customer.model_dump(exclude_unset=True, by_alias=True)
        
        # Don't include the ID in the update data
        if 'id' in customer_data:
            del customer_data['id']
            
        response = await self._put(f"/customers/{customer_id}", data=customer_data)
        return Customer(**response)
    
    async def delete_customer(self, customer_id: int) -> bool:
        """
        Delete a customer.
        
        Args:
            customer_id: ID of the customer to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            EasyAppointmentsError: If the API request fails for reasons other than 404
        """
        try:
            await self._delete(f"/customers/{customer_id}")
            return True
        except ResourceNotFoundError:
            return False

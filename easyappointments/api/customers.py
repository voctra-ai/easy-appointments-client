"""
Customers API manager for interacting with Easy Appointments customers.
"""
from typing import Optional

from easyappointments.api.base import BaseAPI
from easyappointments.models import Customer, PaginatedResponse


class CustomersAPI(BaseAPI):
    """
    Manager for Easy Appointments Customers API endpoints.
    
    This class provides methods for interacting with customers including
    listing, creating, updating, and deleting customers.
    """
    
    async def list_customers(self) -> PaginatedResponse[Customer]:
        """
        List all customers.
        
        Returns:
            PaginatedResponse containing Customer objects
            
        Raises:
            EasyAppointmentsError: If the API request fails
        """
        response = await self._get("/customers")
        return PaginatedResponse.from_dict(response, Customer)
    
    async def get_customer(self, customer_id: int) -> Customer:
        """
        Get details of a specific customer.
        
        Args:
            customer_id: ID of the customer to retrieve
            
        Returns:
            Customer object with the specified ID
            
        Raises:
            EasyAppointmentsError: If the API request fails or customer is not found
        """
        response = await self._get(f"/customers/{customer_id}")
        return Customer(**response)
    
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
    
    async def delete_customer(self, customer_id: int) -> None:
        """
        Delete a customer.
        
        Args:
            customer_id: ID of the customer to delete
            
        Raises:
            EasyAppointmentsError: If the API request fails or customer is not found
        """
        await self._delete(f"/customers/{customer_id}")

"""
Appointments API client for Easy Appointments.
"""
from typing import Optional, TypeVar

import httpx

from ..models import Appointment, PaginatedResponse
from ..exceptions import ResourceNotFoundError
from .base import BaseAPI

T = TypeVar('T')


class AppointmentsAPI(BaseAPI):
    """
    Client for interacting with the Appointments API.
    """

    async def list_appointments(
            self,
            page: int = 1,
            length: int = 10,
            sort: str = "-id"
    ) -> PaginatedResponse[Appointment]:
        """
        List appointments with pagination.
        
        Args:
            page: Page number to retrieve (1-based)
            length: Number of items per page
            sort: Sort order (prefix with - for descending)
            
        Returns:
            Paginated response containing list of appointments
        """
        params = {
            "page": max(1, page),
            "length": max(1, min(100, length)),  # Clamp between 1 and 100
            "sort": sort
        }

        response = await self._request(
            "GET",
            f"{self._base_url}/appointments",
            params=params
        )

        return PaginatedResponse.from_list(
            response,
            Appointment,
            next_page=response.get("next"),
            previous_page=response.get("previous"),
            total=response.get("total", 0)
        )

    async def get_appointment(self, appointment_id: int) -> Optional[Appointment]:
        """
        Get a single appointment by ID.
        
        Args:
            appointment_id: ID of the appointment to retrieve
            
        Returns:
            Appointment object if found, None otherwise
        """
        try:
            response = await self._get(f"/appointments/{appointment_id}")
            return Appointment.from_dict(response)
        except ResourceNotFoundError:
            return None

    async def create_appointment(self, appointment: Appointment) -> Appointment:
        """
        Create a new appointment.
        
        Args:
            appointment: Appointment object containing appointment details
            
        Returns:
            Created Appointment object with ID and other server-generated fields
        """
        data = appointment.model_dump(by_alias=True, exclude_unset=True)

        # Remove ID if it's None (new appointment)
        if 'id' in data and data['id'] is None:
            del data['id']


        response = await self._post(
            "/appointments",
            data=data
        )

        # Use from_dict to handle status conversion properly
        return Appointment.from_dict(response)

    async def update_appointment(
            self,
            appointment_id: int,
            appointment: Appointment
    ) -> Appointment:
        """
        Update an existing appointment.
        
        Args:
            appointment_id: ID of the appointment to update
            appointment: Appointment object containing updated details
            
        Returns:
            Updated Appointment object
        """
        data = appointment.model_dump(by_alias=True, exclude_unset=True)
        response = await self._put(
            f"/appointments/{appointment_id}",
            data=data
        )
        return Appointment.from_dict(response)

    async def delete_appointment(self, appointment_id: int) -> bool:
        """
        Delete an appointment.
        
        Args:
            appointment_id: ID of the appointment to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            await self._delete(
                f"/appointments/{appointment_id}"
            )
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise

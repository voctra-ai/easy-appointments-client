"""
API client for Easy!Appointments availabilities endpoints.
"""
from datetime import date
from typing import Optional, Dict, Any

from .base import BaseAPI
from ..models.availability import Availability

class AvailabilitiesAPI(BaseAPI):
    """API client for checking provider availabilities."""

    async def get_provider_availability(
        self,
        provider_id: int,
        service_id: Optional[int] = 1,
        date_str: Optional[str] = None,
    ) -> Availability:
        """
        Get available time slots for a provider and service.

        Args:
            provider_id: The ID of the provider
            service_id: The ID of the service
            date_str: Date in YYYY-MM-DD format. Defaults to today.

        Returns:
            Availability object containing available time slots
        """
        params: Dict[str, Any] = {
            "providerId": provider_id,
            "serviceId": service_id,
        }
        
        if date_str:
            params["date"] = date_str
            
        response = await self._get("/availabilities", params=params)
        return Availability(**response)

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

        # The API returns an array of time slots in HH:MM format
        available_slots = []

        if isinstance(response, list):
            # Convert array of time strings to time slots (each slot is 15 minutes)
            for i in range(len(response) - 1):
                start = response[i]
                end = response[i + 1]
                available_slots.append({"start": start, "end": end})
        elif isinstance(response, dict) and 'available' in response:
            # Handle the case where response is already in the expected format
            available_slots = response['available']

        return Availability(available=available_slots)

    def _format_time(self, time_val) -> str:
        """Convert a time value to HH:MM format.
        
        Args:
            time_val: Either a string in HH:MM format or a numeric value
            
        Returns:
            Time string in HH:MM format
        """
        if isinstance(time_val, str) and ':' in time_val:
            return time_val  # Already in HH:MM format

        try:
            # Try to convert numeric value to HH:MM
            hour = int(float(time_val))
            return f"{hour:02d}:00"
        except (ValueError, TypeError):
            # If conversion fails, return a default time
            return "09:00"

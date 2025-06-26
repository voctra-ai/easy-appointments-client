"""
Appointment model for Easy Appointments API.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator


class Status(str, Enum):
    """Possible statuses for an appointment."""
    BOOKED = "Booked"
    CANCELLED = "Cancelled"

    @classmethod
    def _missing_(cls, value: object) -> 'Status':
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value.lower() == value:
                    return member
        return super()._missing_(value)

    @classmethod
    def validate(cls, v: Any) -> 'Status':
        """Validate and convert input to Status enum."""
        if isinstance(v, Status):
            return v
        if isinstance(v, str):
            try:
                return Status(v.lower())
            except ValueError:
                pass
        raise ValueError(f"Invalid status: {v}. Must be one of {', '.join([s.value for s in Status])}")


class Appointment(BaseModel):
    """
    Represents an appointment in the Easy Appointments system.
    
    Attributes:
        id: Unique identifier for the appointment
        start: Start time of the appointment in ISO 8601 format
        end: End time of the appointment in ISO 8601 format
        location: Location of the appointment
        notes: Additional notes about the appointment
        customer_id: ID of the customer for the appointment
        provider_id: ID of the provider for the appointment
        service_id: ID of the service being provided
        hash: Unique hash for the appointment
        google_calendar_id: Google Calendar event ID if synced
        status: Status of the appointment (e.g., 'Booked', 'Cancelled')
    """
    id: Optional[int] = None
    start: str
    end: str
    location: Optional[str] = None
    notes: Optional[str] = None
    customer_id: int = Field(alias="customerId")
    provider_id: int = Field(alias="providerId")
    service_id: int = Field(alias="serviceId")
    hash: Optional[str] = None
    google_calendar_id: Optional[str] = Field(None, alias="googleCalendarId")
    status: Status = Status.BOOKED

    class Config:
        """Pydantic config."""
        populate_by_name = True
        from_attributes = True

    @field_validator('start', 'end')
    @classmethod
    def validate_datetime_format(cls, v: str) -> str:
        """Validate that the datetime string is in ISO 8601 format."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError as e:
            raise ValueError(f"Datetime must be in ISO 8601 format, got {v}") from e

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Appointment':
        """Create an Appointment instance from a dictionary."""
        # Create a copy to avoid modifying the original data
        data = data.copy()
        
        # Handle status conversion
        if 'status' in data:
            if data['status'] is None or (isinstance(data['status'], str) and not data['status'].strip()):
                data['status'] = Status.BOOKED
            elif isinstance(data['status'], str):
                try:
                    data['status'] = Status(data['status'].lower())
                except ValueError:
                    data['status'] = Status.BOOKED
        else:
            data['status'] = Status.BOOKED
            
        return cls(**data)

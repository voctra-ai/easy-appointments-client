"""
Data models for working with provider availabilities in Easy!Appointments.
"""
from datetime import datetime, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

class TimeSlot(BaseModel):
    """Represents an available time slot."""
    start: str
    end: str
    
    @field_validator('start', 'end')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate that the time string is in HH:MM format."""
        try:
            time.fromisoformat(v)
            return v
        except ValueError as e:
            raise ValueError(f"Time must be in HH:MM format, got {v}") from e

class Availability(BaseModel):
    """Represents available time slots for a provider and service."""
    available: List[TimeSlot] = Field(default_factory=list, description="List of available time slots")
    
    def __bool__(self) -> bool:
        """Return True if there are any available time slots."""
        return bool(self.available)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Availability':
        """Create an Availability instance from the API response dictionary."""
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")
            
        available_slots = []
        # The API might return a dictionary with time ranges as keys
        for slot_range in data.get('available', []):
            if isinstance(slot_range, dict) and 'start' in slot_range and 'end' in slot_range:
                available_slots.append(TimeSlot(**slot_range))
        
        return cls(available=available_slots)

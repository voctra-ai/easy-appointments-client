"""
Provider model for Easy Appointments API responses.
"""
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class Break(BaseModel):
    """
    Represents a break in a provider's working day.
    
    Attributes:
        start: Start time of the break (format: "HH:MM")
        end: End time of the break (format: "HH:MM")
    """
    start: str
    end: str


class WorkingDay(BaseModel):
    """
    Represents a working day for a provider.
    
    Attributes:
        start: Start time of the working day (format: "HH:MM" or null)
        end: End time of the working day (format: "HH:MM" or null)
        breaks: List of breaks during the working day
    """
    start: Optional[str] = None
    end: Optional[str] = None
    breaks: List[Break] = Field(default_factory=list)


class WorkingPlan(BaseModel):
    """
    Represents a provider's working plan for the week.
    
    Attributes:
        sunday: Working hours for Sunday
        monday: Working hours for Monday
        tuesday: Working hours for Tuesday
        wednesday: Working hours for Wednesday
        thursday: Working hours for Thursday
        friday: Working hours for Friday
        saturday: Working hours for Saturday
    """
    sunday: WorkingDay
    monday: WorkingDay
    tuesday: WorkingDay
    wednesday: WorkingDay
    thursday: WorkingDay
    friday: WorkingDay
    saturday: WorkingDay


class ProviderSettings(BaseModel):
    """
    Settings for a provider.
    
    Attributes:
        username: Provider username
        password: Provider password (only included in requests, not responses)
        working_plan: Provider's working plan
    """
    username: str
    password: Optional[str] = None
    working_plan: Optional[WorkingPlan] = Field(None, alias="workingPlan")
    
    class Config:
        """Pydantic model configuration."""
        populate_by_name = True


class Provider(BaseModel):
    """
    Represents a provider from the Easy Appointments API.
    
    Attributes:
        id: Unique identifier for the provider
        first_name: First name of the provider
        last_name: Last name of the provider
        email: Email address of the provider
        mobile: Mobile number of the provider
        phone: Phone number of the provider
        address: Address of the provider
        city: City of the provider
        state: State of the provider
        zip: ZIP code of the provider
        notes: Notes about the provider
        timezone: Timezone of the provider
        language: Language preference of the provider
        settings: Provider settings
        services: List of service IDs associated with the provider
    """
    id: Optional[int] = None  # Optional for creation requests
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: str
    mobile: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    notes: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    settings: ProviderSettings
    services: List[int] = Field(default_factory=list)
    
    class Config:
        """Pydantic model configuration."""
        populate_by_name = True
        arbitrary_types_allowed = True

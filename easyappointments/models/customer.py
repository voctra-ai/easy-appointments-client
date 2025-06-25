"""
Customer model for Easy Appointments API.
"""
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, EmailStr


class CustomerSettings(BaseModel):
    """
    Settings for a customer.
    
    Attributes:
        username: Customer username
        notifications: Whether notifications are enabled
        timezone: Customer's timezone
        calendar_view: Preferred calendar view
        date_format: Preferred date format
    """
    username: Optional[str] = None
    notifications: bool = True
    timezone: Optional[str] = None
    calendar_view: str = "default"
    date_format: str = "DMY"


class Customer(BaseModel):
    """
    Represents a customer in the Easy Appointments system.
    
    Attributes:
        id: Unique identifier for the customer
        first_name: First name of the customer
        last_name: Last name of the customer
        email: Email address of the customer
        phone: Phone number of the customer
        mobile: Mobile number of the customer
        address: Street address of the customer
        city: City of the customer
        state: State/province of the customer
        zip: ZIP/postal code of the customer
        notes: Additional notes about the customer
        timezone: Timezone of the customer
        language: Preferred language of the customer
        settings: Customer settings
    """
    id: Optional[int] = None
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: EmailStr
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = Field(None, alias="zipCode")
    notes: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    settings: Optional[CustomerSettings] = None

    class Config:
        """Pydantic config."""
        populate_by_name = True
        from_attributes = True

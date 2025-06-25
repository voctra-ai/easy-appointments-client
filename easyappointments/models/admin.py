"""
Admin model for Easy Appointments API responses.
"""
from typing import Dict, Optional, Any

from pydantic import BaseModel, Field


class AdminSettings(BaseModel):
    """
    Settings for an admin user.
    
    Attributes:
        username: Admin username
        notifications: Whether notifications are enabled
        calendar_view: Calendar view setting
    """
    username: str
    notifications: bool
    calendar_view: str = Field(alias="calendarView")


class Admin(BaseModel):
    """
    Represents an admin user from the Easy Appointments API.
    
    Attributes:
        id: Unique identifier for the admin
        first_name: First name of the admin
        last_name: Last name of the admin
        email: Email address of the admin
        mobile: Mobile number of the admin
        phone: Phone number of the admin
        address: Address of the admin
        city: City of the admin
        state: State of the admin
        zip: ZIP code of the admin
        notes: Notes about the admin
        timezone: Timezone of the admin
        language: Language preference of the admin
        ldap_dn: LDAP distinguished name
        settings: Admin settings
    """
    id: int
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
    timezone: str
    language: str
    ldap_dn: Optional[str] = Field(None, alias="ldapDn")
    settings: AdminSettings
    
    class Config:
        """Pydantic model configuration."""
        populate_by_name = True
        arbitrary_types_allowed = True

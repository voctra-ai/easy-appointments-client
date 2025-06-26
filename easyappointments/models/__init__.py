"""
Models for the Easy Appointments API client.
"""

from easyappointments.models.admin import Admin
from easyappointments.models.provider import Provider, ProviderSettings
from easyappointments.models.customer import Customer, CustomerSettings
from easyappointments.models.paginated_response import PaginatedResponse
from easyappointments.models.availability import Availability, TimeSlot
from easyappointments.models.appointment import Appointment

__all__ = [
    "Admin", 
    "Provider", 
    "ProviderSettings", 
    "Customer",
    "CustomerSettings",
    "PaginatedResponse",
    "Availability",
    "TimeSlot",
    "Appointment"
]

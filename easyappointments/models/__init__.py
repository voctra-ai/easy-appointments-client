"""
Models for the Easy Appointments API client.
"""

from easyappointments.models.admin import Admin
from easyappointments.models.provider import Provider, ProviderSettings
from easyappointments.models.customer import Customer, CustomerSettings
from easyappointments.models.paginated_response import PaginatedResponse

__all__ = [
    "Admin", 
    "Provider", 
    "ProviderSettings", 
    "Customer",
    "CustomerSettings",
    "PaginatedResponse"
]

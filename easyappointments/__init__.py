"""
Easy Appointments API client.
"""

from easyappointments.client import EasyAppointmentsClient
from easyappointments.exceptions import (
    EasyAppointmentsError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)

__all__ = [
    "EasyAppointmentsClient",
    "EasyAppointmentsError",
    "AuthenticationError",
    "ResourceNotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
]

__version__ = "0.1.0"

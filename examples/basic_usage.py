#!/usr/bin/env python3
"""
Basic usage example for the Easy Appointments client.
"""
import asyncio
import logging

from easyappointments import EasyAppointmentsClient
from easyappointments.models import Provider, ProviderSettings


async def list_admins(client: EasyAppointmentsClient) -> None:
    """List all admins and print their details."""
    print("\n=== Listing Admins ===")
    admins = await client.admins.list_admins()
    print(f"Found {len(admins.results)} admins:")
    for admin in admins.results:
        print(f"- {admin.first_name} {admin.last_name} ({admin.email})")
        print(f"  ID: {admin.id}")
        print(f"  Phone: {admin.phone}")
        print(f"  Username: {admin.settings.username}")
        print()


async def create_provider(client: EasyAppointmentsClient) -> None:
    """Create a new provider with working hours."""
    print("\n=== Creating Provider ===")
    
    # Create provider settings with working plan
    settings = ProviderSettings(
        username="johndoe1",
        password="SecurePassword123!",
        working_plan={
            "sunday": {"start": None, "end": None, "breaks": []},
            "monday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
            "tuesday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
            "wednesday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
            "thursday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
            "friday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
            "saturday": {"start": None, "end": None, "breaks": []}
        }
    )
    
    # Create provider
    new_provider = Provider(
        first_name="John",
        last_name="Doe",
        email="john.doe1@example.com",
        phone="123-456-7890",
        settings=settings,
        services=[1]  # Service IDs the provider offers
    )
    
    try:
        # Create the provider
        created_provider = await client.providers.create_provider(new_provider)
        print(f"Created provider with ID: {created_provider.id}")
        print(f"Name: {created_provider.first_name} {created_provider.last_name}")
        print(f"Email: {created_provider.email}")
        print(f"Username: {created_provider.settings.username}")
    except Exception as e:
        print(f"Error creating provider: {e}")


async def list_providers(client: EasyAppointmentsClient) -> None:
    """List all providers and print their details."""
    print("\n=== Listing Providers ===")
    providers = await client.providers.list_providers()
    print(f"Found {len(providers.results)} providers:")
    for provider in providers.results:
        print(f"- {provider.first_name} {provider.last_name} ({provider.email})")
        print(f"  ID: {provider.id}")
        print(f"  Phone: {provider.phone}")
        print(f"  Username: {provider.settings.username}")
        print()


async def main() -> None:
    """Main function to demonstrate the Easy Appointments client."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the client
    # Replace with your actual API key and base URL
    client = EasyAppointmentsClient(
        api_key="6C497z9p1PFJIiLIEhdxwyuaXk4Ct8EN",
        base_url="http://localhost/index.php/api/v1"
    )
    
    try:
        # List all admins
        await list_admins(client)
        
        # Create a new provider
        await create_provider(client)
        
        # List all providers
        await list_providers(client)
        
    finally:
        # Close the client
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())

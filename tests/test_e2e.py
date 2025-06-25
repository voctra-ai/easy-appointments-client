"""
End-to-end tests for the Easy Appointments client.

These tests require a running Easy Appointments instance and a valid API key.
"""
import os
import asyncio
import pytest
import pytest_asyncio
from datetime import datetime
from typing import AsyncGenerator

from easyappointments import EasyAppointmentsClient
from easyappointments.models import Provider, ProviderSettings, Admin

# Pytest configuration for asyncio
pytest_plugins = ('pytest_asyncio',)
pytestmark = pytest.mark.asyncio

# Test configuration
BASE_URL = os.getenv("EA_BASE_URL", "http://localhost/index.php/api/v1")
API_KEY = "6C497z9p1PFJIiLIEhdxwyuaXk4Ct8EN"  # Using provided API key

# Unique identifiers for test data
TEST_TIMESTAMP = int(datetime.now().timestamp())
TEST_PROVIDER_EMAIL = f"test.provider.{TEST_TIMESTAMP}@example.com"
TEST_PROVIDER_USERNAME = f"testprovider{TEST_TIMESTAMP}"


class TestE2E:
    """End-to-end tests for the Easy Appointments client."""

    @pytest_asyncio.fixture
    async def client(self) -> AsyncGenerator[EasyAppointmentsClient, None]:
        """Fixture that provides an authenticated client using API key."""
        client = EasyAppointmentsClient(
            base_url=BASE_URL,
            api_key=API_KEY
        )
        try:
            yield client
        finally:
            await client.close()

    async def test_provider_workflow(self, client: EasyAppointmentsClient):
        """Test the complete workflow: list admins -> list providers -> create provider -> verify -> delete."""
        # 1. List all admins
        print("\n=== 1. Listing All Admins ===")
        admins_response = await client.admins.list_admins()
        assert hasattr(admins_response, 'results'), "Response should have 'results' attribute"
        admins = admins_response.results
        assert isinstance(admins, list)
        print(f"Found {len(admins)} admins")
        for admin in admins[:5]:  # Print first 5 admins
            print(f"- {admin.first_name} {admin.last_name} ({admin.email})")

        # 2. List existing providers
        print("\n=== 2. Listing Existing Providers ===")
        providers_response = await client.providers.list_providers()
        assert hasattr(providers_response, 'results'), "Response should have 'results' attribute"
        providers = providers_response.results
        assert isinstance(providers, list)
        initial_provider_count = len(providers)
        print(f"Found {initial_provider_count} existing providers")
        
        # 3. Create a new provider
        print("\n=== 3. Creating New Test Provider ===")
        settings = ProviderSettings(
            username=TEST_PROVIDER_USERNAME,
            password="TestPassword123!",
            working_plan={
                "sunday": {"start": None, "end": None, "breaks": []},
                "monday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "tuesday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "wednesday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "thursday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "friday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "saturday": {"start": None, "end": None, "breaks": []},
            }
        )

        new_provider = Provider(
            first_name="Test",
            last_name=f"Provider {TEST_TIMESTAMP}",
            email=TEST_PROVIDER_EMAIL,
            phone="123-456-7890",
            settings=settings,
            services=[1]  # Assuming service with ID 1 exists
        )

        # Create the provider
        created_provider = await client.providers.create_provider(new_provider)
        assert created_provider.id is not None
        assert created_provider.email == TEST_PROVIDER_EMAIL
        print(f"Created provider with ID: {created_provider.id}")
        print(f"Name: {created_provider.first_name} {created_provider.last_name}")
        print(f"Email: {created_provider.email}")

        # 4. Verify the provider was created by listing all providers again
        print("\n=== 4. Verifying Provider Creation ===")
        updated_providers_response = await client.providers.list_providers()
        updated_providers = updated_providers_response.results
        assert len(updated_providers) == initial_provider_count + 1, "Provider count should increase by 1"
        
        # Verify the new provider is in the list
        provider_ids = [p.id for p in updated_providers] if updated_providers else []
        assert created_provider.id in provider_ids, "New provider ID should be in the list"
        print(f"Successfully verified provider {created_provider.id} exists")

        # 5. Clean up: Delete the provider we created
        print("\n=== 5. Cleaning Up: Deleting Test Provider ===")
        await client.providers.delete_provider(created_provider.id)
        
        # Verify deletion by checking the provider count went back to original
        final_providers_response = await client.providers.list_providers()
        final_providers = final_providers_response.results if final_providers_response else []
        assert len(final_providers) == initial_provider_count, "Provider count should return to original after deletion"
        
        # Verify the provider ID is no longer in the list
        final_provider_ids = [p.id for p in final_providers] if final_providers else []
        assert created_provider.id not in final_provider_ids, "Provider ID should be removed after deletion"
        
        print(f"Successfully deleted test provider with ID: {created_provider.id}")
        print("\n✅ All tests completed successfully!")

    # Single test method now handles the complete workflow

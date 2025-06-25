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
from easyappointments.models import Provider, ProviderSettings, Admin, Customer

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
TEST_CUSTOMER_EMAIL = f"test.customer.{TEST_TIMESTAMP}@example.com"


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
        admins: list[Admin] = admins_response.results
        assert isinstance(admins, list)
        print(f"Found {len(admins)} admins")
        for admin in admins[:5]:  # Print first 5 admins
            print(f"- {admin.first_name} {admin.last_name} ({admin.email})")

        # 2. List existing providers
        print("\n=== 2. Listing Existing Providers ===")
        providers_response = await client.providers.list_providers()
        assert hasattr(providers_response, 'results'), "Response should have 'results' attribute"
        providers: list[Provider] = providers_response.results
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
    
    async def test_customer_workflow(self, client: EasyAppointmentsClient):
        """Test the complete workflow: list customers -> create customer -> verify -> delete."""
        # 1. List existing customers
        print("\n=== 1. Listing Existing Customers ===")
        customers_response = await client.customers.list_customers()
        assert hasattr(customers_response, 'results'), "Response should have 'results' attribute"
        customers = customers_response.results
        assert isinstance(customers, list), "Customers should be a list"
        initial_customer_count = len(customers)
        print(f"Found {initial_customer_count} existing customers")
        
        # 2. Create a new customer
        print("\n=== 2. Creating New Test Customer ===")
        new_customer = Customer(
            first_name="Test",
            last_name=f"Customer {TEST_TIMESTAMP}",
            email=TEST_CUSTOMER_EMAIL,
            phone="123-456-7890",
            address="123 Test St",
            city="Testville",
            state="TS",
            zip="12345"
        )
        
        # Create the customer
        created_customer = await client.customers.create_customer(new_customer)
        assert created_customer.id is not None
        assert created_customer.email == TEST_CUSTOMER_EMAIL
        print(f"Created customer with ID: {created_customer.id}")
        print(f"Name: {created_customer.first_name} {created_customer.last_name}")
        print(f"Email: {created_customer.email}")
        
        # 3. Verify the customer was created by listing all customers again
        print("\n=== 3. Verifying Customer Creation ===")
        updated_customers_response = await client.customers.list_customers()
        updated_customers = updated_customers_response.results
        assert len(updated_customers) == initial_customer_count + 1, "Customer count should increase by 1"
        
        # Verify the new customer is in the list
        customer_ids = [c.id for c in updated_customers] if updated_customers else []
        assert created_customer.id in customer_ids, "New customer ID should be in the list"
        print(f"Successfully verified customer {created_customer.id} exists")
        
        # 4. Get the customer by ID to verify details
        print("\n=== 4. Verifying Customer Details ===")
        fetched_customer = await client.customers.get_customer(created_customer.id)
        assert fetched_customer.id == created_customer.id
        assert fetched_customer.email == TEST_CUSTOMER_EMAIL
        assert fetched_customer.first_name == "Test"
        assert fetched_customer.last_name == f"Customer {TEST_TIMESTAMP}"
        print("Successfully verified customer details")
        
        # 5. Clean up: Delete the customer we created
        print("\n=== 5. Cleaning Up: Deleting Test Customer ===")
        await client.customers.delete_customer(created_customer.id)
        
        # Verify deletion by checking the customer count went back to original
        final_customers_response = await client.customers.list_customers()
        final_customers = final_customers_response.results if final_customers_response else []
        assert len(final_customers) == initial_customer_count, "Customer count should return to original after deletion"
        
        # Verify the customer ID is no longer in the list
        final_customer_ids = [c.id for c in final_customers] if final_customers else []
        assert created_customer.id not in final_customer_ids, "Customer ID should be removed after deletion"
        
        print(f"Successfully deleted test customer with ID: {created_customer.id}")
        print("\n✅ All tests completed successfully!")

    # Single test method now handles the complete workflow

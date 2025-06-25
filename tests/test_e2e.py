"""
End-to-end tests for the Easy Appointments client.

These tests require a running Easy Appointments instance and a valid API key.
"""
import os
from datetime import datetime
from typing import AsyncGenerator

import pytest
import pytest_asyncio

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
        # 1. List all admins with pagination
        print("\n=== 1. Listing All Admins ===")
        admins_response = await client.admins.list_admins()
        
        # Verify pagination response structure
        assert hasattr(admins_response, 'results'), "Response should have 'results' attribute"
        assert hasattr(admins_response, 'total'), "Response should have 'total' attribute"
        assert hasattr(admins_response, 'next'), "Response should have 'next' attribute"
        assert hasattr(admins_response, 'previous'), "Response should have 'previous' attribute"
        
        admins: list[Admin] = admins_response.results
        assert isinstance(admins, list)
        print(f"Found {len(admins)} of {admins_response.total} total admins")
        for admin in admins[:5]:  # Print first 5 admins
            print(f"- {admin.first_name} {admin.last_name} ({admin.email})")

        # 2. List existing providers with pagination
        print("\n=== 2. Listing Existing Providers ===")
        providers_response = await client.providers.list_providers()
        
        # Verify pagination response structure
        assert hasattr(providers_response, 'results'), "Response should have 'results' attribute"
        assert hasattr(providers_response, 'total'), "Response should have 'total' attribute"
        assert hasattr(providers_response, 'next'), "Response should have 'next' attribute"
        assert hasattr(providers_response, 'previous'), "Response should have 'previous' attribute"
        
        providers: list[Provider] = providers_response.results
        assert isinstance(providers, list)
        initial_provider_count = providers_response.total
        print(f"Found {len(providers)} of {initial_provider_count} total providers")
        
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
            timezone="UTC",  # Set a valid timezone
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

        # 4. Verify the provider was created by searching for them directly
        print("\n=== 4. Verifying Provider Creation ===")
        # Try to fetch the provider directly by ID first
        try:
            found_provider = await client.providers.get_provider(created_provider.id)
            assert found_provider is not None
            assert found_provider.email == created_provider.email
            print(f"Successfully verified provider {created_provider.id} exists")
        except Exception as e:
            # If direct fetch fails, try to find in paginated results as fallback
            print(f"Direct fetch failed, falling back to paginated search: {e}")
            page = 1
            found = False
            
            while not found:
                updated_providers_response = await client.providers.list_providers(
                    page=page,
                    sort="-id"  # Sort by ID descending to find newest first
                )
                updated_providers = updated_providers_response.results
                
                if not updated_providers:
                    break
                    
                # Check if our new provider is on this page
                if any(p.id == created_provider.id for p in updated_providers):
                    found = True
                    print(f"Found new provider on page {page}")
                    break
                    
                if not updated_providers_response.next:
                    break
                    
                page += 1
            
            assert found, f"New provider with ID {created_provider.id} not found in any page"
            print(f"Successfully verified provider {created_provider.id} exists via pagination")

        # 5. Get provider availability
        print("\n=== 5. Checking Provider Availability ===")
        # Use a default service ID (1) - in a real test, you might want to create a service first
        service_id = 1
        # Use a date in the future to ensure we have availability
        from datetime import datetime, timedelta
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        try:
            availability = await client.availabilities.get_provider_availability(
                provider_id=created_provider.id,
                service_id=service_id,
                date_str=future_date
            )
        except Exception as e:
            print(f"Error checking availability: {e}")
            # Continue with the test to ensure cleanup happens
            availability = None
        
        if availability is not None:
            print(f"Availability for provider {created_provider.id} on {future_date}:")
            if availability.available:
                for slot in availability.available:
                    print(f"  Available: {slot.start} - {slot.end}")
            else:
                print("  No available time slots")
        
        # 6. Clean up: Delete the provider we created
        print("\n=== 6. Cleaning Up: Deleting Test Provider ===")
        await client.providers.delete_provider(created_provider.id)
        
        # Verify deletion by checking the provider count went back to original
        final_providers_response = await client.providers.list_providers()
        final_providers = final_providers_response.results if final_providers_response else []
        assert len(final_providers) == initial_provider_count, "Provider count should return to original after deletion"
        
        # Verify the provider ID is no longer in the list
        final_provider_ids = [p.id for p in final_providers] if final_providers else []
        assert created_provider.id not in final_provider_ids, "Provider ID should be removed after deletion"
        
        print(f"Successfully deleted test provider with ID: {created_provider.id}")
        print("\n✅ All provider workflow tests completed successfully!")
    
    async def test_customer_workflow(self, client: EasyAppointmentsClient):
        """Test the complete workflow: list customers -> create customer -> verify -> delete."""
        # 1. List existing customers with pagination
        print("\n=== 1. Listing Existing Customers ===")
        customers_response = await client.customers.list_customers()
        
        # Verify pagination response structure
        assert hasattr(customers_response, 'results'), "Response should have 'results' attribute"
        assert hasattr(customers_response, 'total'), "Response should have 'total' attribute"
        assert hasattr(customers_response, 'next'), "Response should have 'next' attribute"
        assert hasattr(customers_response, 'previous'), "Response should have 'previous' attribute"
        
        customers: list[Customer] = customers_response.results
        assert isinstance(customers, list)
        initial_customer_count = customers_response.total
        print(f"Found {len(customers)} of {initial_customer_count} total customers")
        
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
        
        # 3. Verify the customer was created by searching for them directly
        print("\n=== 3. Verifying Customer Creation ===")
        # Instead of checking count (which is affected by pagination),
        # directly fetch the customer by ID to verify it was created
        try:
            found_customer = await client.customers.get_customer(created_customer.id)
            assert found_customer is not None
            assert found_customer.email == created_customer.email
            print(f"Successfully verified customer {created_customer.id} exists")
        except Exception as e:
            # If direct fetch fails, try to find in paginated results as fallback
            print(f"Direct fetch failed, falling back to paginated search: {e}")
            page = 1
            found = False
            
            while not found:
                updated_customers_response = await client.customers.list_customers(
                    page=page,
                    sort="-id"  # Sort by ID descending to find newest first
                )
                updated_customers = updated_customers_response.results
                
                if not updated_customers:
                    break
                    
                # Check if our new customer is on this page
                if any(c.id == created_customer.id for c in updated_customers):
                    found = True
                    print(f"Found new customer on page {page}")
                    break
                    
                if not updated_customers_response.next:
                    break
                    
                page += 1
            
            assert found, f"New customer with ID {created_customer.id} not found in any page"
            print(f"Successfully verified customer {created_customer.id} exists via pagination")
        
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

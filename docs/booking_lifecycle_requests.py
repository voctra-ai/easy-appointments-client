import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
BASE_URL = 'http://localhost/index.php/api/v1'
AUTH_TOKEN = '6C497z9p1PFJIiLIEhdxwyuaXk4Ct8EN'
HEADERS = {
    'Authorization': f'Bearer {AUTH_TOKEN}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def make_request(method, endpoint, data=None, params=None):
    """Helper function to make HTTP requests."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=HEADERS,
            json=data,
            params=params
        )
        response.raise_for_status()
        return response.json() if response.text else {}
    except requests.exceptions.RequestException as e:
        print(f"Error making {method} request to {endpoint}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        raise

def list_admins():
    """List all admin users."""
    print("\n--- Listing Admins ---")
    return make_request('GET', 'admins')

def create_provider():
    """Create a new provider with working hours."""
    print("\n--- Creating Provider ---")
    unique_suffix = int(time.time())
    
    provider_data = {
        "firstName": "Provider",
        "lastName": f"Test{unique_suffix}",
        "email": f"provider{unique_suffix}@example.com",
        "phone": "1234567890",
        "services": [1],  # Assuming service with ID 1 exists
        "settings": {
            "username": f"provider{unique_suffix}",
            "password": "password123",
            "working_plan": {
                "monday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "tuesday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "wednesday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "thursday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]},
                "friday": {"start": "09:00", "end": "17:00", "breaks": [{"start": "12:00", "end": "13:00"}]}
            }
        }
    }
    
    return make_request('POST', 'providers', data=provider_data)

def get_provider(provider_id):
    """Retrieve a provider by ID."""
    print(f"\n--- Getting Provider {provider_id} ---")
    return make_request('GET', f'providers/{provider_id}')

def create_customer():
    """Create a new customer."""
    print("\n--- Creating Customer ---")
    unique_suffix = int(time.time())
    
    customer_data = {
        "firstName": "Customer",
        "lastName": f"Test{unique_suffix}",
        "email": f"customer{unique_suffix}@example.com",
        "phone": "9876543210"
    }
    
    return make_request('POST', 'customers', data=customer_data)

def get_availability(provider_id, service_id, date_str):
    """Get available time slots for a provider and service on a specific date."""
    print(f"\n--- Getting Availability for Provider {provider_id} ---")
    params = {
        'providerId': provider_id,
        'serviceId': service_id,
        'date': date_str
    }
    return make_request('GET', 'availabilities', params=params)

def create_appointment(provider_id, service_id, customer_id, start_time):
    """Create a new appointment."""
    print("\n--- Creating Appointment ---")
    # Format: "YYYY-MM-DD HH:MM:SS"
    appointment_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')  # Using tomorrow's date
    start_datetime = f"{appointment_date} {start_time}:00"  # Add seconds
    
    # Calculate end time (1 hour after start)
    start_dt = datetime.strptime(f"{appointment_date} {start_time}", '%Y-%m-%d %H:%M')
    end_datetime = (start_dt + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:00')
    
    appointment_data = {
        "start": start_datetime,
        "end": end_datetime,
        "location": "Test Location",
        "notes": "Test appointment",
        "customerId": customer_id,
        "providerId": provider_id,
        "serviceId": service_id
    }
    
    # Make the API request and return both the response and the start_datetime
    response = make_request('POST', 'appointments', data=appointment_data)
    return response, start_dt

def update_appointment(appointment_id, new_start_dt):
    """Update an existing appointment."""
    print(f"\n--- Updating Appointment {appointment_id} ---")
    # Format: "YYYY-MM-DD HH:MM:SS"
    new_start_time = new_start_dt.strftime('%Y-%m-%d %H:%M:00')
    new_end_time = (new_start_dt + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:00')
    
    update_data = {
        "start": new_start_time,
        "end": new_end_time
    }
    return make_request('PUT', f'appointments/{appointment_id}', data=update_data)

def main():
    try:
        # 1. List admins
        admins = list_admins()
        print("Admins:", json.dumps(admins, indent=2))
        
        # 2. Create a new provider
        provider = create_provider()
        print("Created provider:", json.dumps(provider, indent=2))
        provider_id = provider['id']
        
        # 3. Get the provider to verify
        provider = get_provider(provider_id)
        print("Retrieved provider:", json.dumps(provider, indent=2))
        
        # 4. Create a new customer
        customer = create_customer()
        print("Created customer:", json.dumps(customer, indent=2))
        customer_id = customer['id']
        
        # 5. Get availability (using tomorrow's date)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        availability = get_availability(provider_id, 1, tomorrow)  # Assuming service ID 1 exists
        print("Availability:", json.dumps(availability, indent=2))
        
        if not availability:
            print("No availability found. Please check provider's working hours.")
            return
        
        # 6. Book an appointment (using first available slot)
        start_time = availability[0]  # Use first available slot
        appointment, start_datetime = create_appointment(provider_id, 1, customer_id, start_time)
        print("Created appointment:", json.dumps(appointment, indent=2))
        appointment_id = appointment['id']
        
        # 7. Provider reschedules the appointment (1 hour later)
        new_start_dt = start_datetime + timedelta(hours=1)
        updated_appointment = update_appointment(appointment_id, new_start_dt)
        print("Provider rescheduled appointment:", json.dumps(updated_appointment, indent=2))
        
        # 8. Customer reschedules the appointment (another hour later)
        customer_new_start_dt = new_start_dt + timedelta(hours=1)
        final_appointment = update_appointment(appointment_id, customer_new_start_dt)
        print("Customer rescheduled appointment:", json.dumps(final_appointment, indent=2))
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

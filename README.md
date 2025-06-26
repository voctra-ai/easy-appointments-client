# Easy Appointments Async Python Client

An async Python client for the Easy Appointments API.

## Features

- Fully async API using `httpx`
- Type-hinted with Pydantic models
- Automatic retry with exponential backoff
- Comprehensive error handling

## Quick Start (Setting Easy Appointments server locally)

1. Start the Easy Appointments server:
   ```bash
   docker compose up -d
   ```
   Access it at http://localhost

2. Create an admin account at http://localhost/

3. Generate an API key:
   - Go to Profile > Settings > Integrations > API
   - Create and copy your API key

## Documentation

- [Easy Appointments REST API](https://easyappointments.org/docs.html#1.5.1/rest-api.md)
- Local Swagger UI: http://localhost:8000/#/
- Sample CURL requests: `docs/sample-curls.txt`
- OpenAPI specs: `docs/openapi.yml`

## Installation

```bash
# Install from the repository
pip install git+https://github.com/voctra-ai/easy-appointments-client.git

# Or using Poetry
poetry add git+https://github.com/voctra-ai/easy-appointments-client.git
```

## Development

### Setting up the development environment

1. Clone the repository:
   ```bash
   git clone https://github.com/voctra-ai/easy-appointments-client.git
   cd easy-appointments-client
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

### Running tests

Run the test suite using pytest:

```bash
# Run all tests
pytest tests/

# Run tests with coverage report
pytest --cov=easyappointments tests/

# Generate HTML coverage report
pytest --cov=easyappointments --cov-report=html tests/

# Run a specific test file
pytest tests/test_e2e.py

# Run a specific test case
pytest -xvs tests/test_e2e.py::TestE2E::test_provider_workflow

# Run tests with verbose output
pytest -v tests/
```

### Pre-commit hooks

This project includes pre-commit hooks to automatically run code quality checks before each commit. To set up:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

Now the hooks will run automatically on each commit.


## Quick Start

```python
import asyncio
from easyappointments import EasyAppointmentsClient


async def main():
    # Initialize the client
    client = EasyAppointmentsClient(
        api_key="YOUR_API_KEY",
        base_url="http://localhost/index.php/api/v1"  # Adjust to your Easy Appointments URL
    )

    try:
        # List all admins
        admins = await client.admins.list_admins()
        print(f"Found {len(admins.results)} admins:")
        for admin in admins.results:
            print(f"- {admin.first_name} {admin.last_name} ({admin.email})")

    finally:
        # Close the client
        await client.close()


# Run the async function
asyncio.run(main())
```



## API Reference

### Client Initialization

```python
from easyappointments import EasyAppointmentsClient

client = EasyAppointmentsClient(
    api_key="YOUR_API_KEY",
    base_url="http://localhost/index.php/api/v1",
    max_retries=3,  # Maximum number of retries for failed requests
    retry_delay=1.0,  # Base delay between retries in seconds
    timeout=30.0,  # Default timeout for requests in seconds
    logging_enabled=True  # Whether to enable logging
)
```

### Using with async context manager

```python
async with EasyAppointmentsClient(api_key="YOUR_API_KEY") as client:
    admins = await client.admins.list_admins()
    # Do something with admins
```

### Admins API

#### List all admins

```python
admins = await client.admins.list_admins()
for admin in admins.results:
    print(f"Admin: {admin.first_name} {admin.last_name} (ID: {admin.id})")
```

#### Get admin by ID

```python
admin = await client.admins.get_admin(1)
print(f"Admin: {admin.first_name} {admin.last_name}")
```

### Providers API

#### List all providers

```python
providers = await client.providers.list_providers()
for provider in providers.results:
    print(f"Provider: {provider.first_name} {provider.last_name} (ID: {provider.id})")
```

#### Get provider by ID

```python
provider = await client.providers.get_provider(1)
print(f"Provider: {provider.first_name} {provider.last_name}")
```

#### Create a new provider

```python
from easyappointments.models import Provider, ProviderSettings

# Create provider settings
settings = ProviderSettings(
    username="johndoe",
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
    email="john.doe@example.com",
    phone="123-456-7890",
    settings=settings,
    services=[1]
)

# Create the provider
created_provider = await client.providers.create_provider(new_provider)
print(f"Created provider with ID: {created_provider.id}")
```

#### Update an existing provider

```python
provider = await client.providers.get_provider(1)
provider.first_name = "Jane"
updated_provider = await client.providers.update_provider(1, provider)
print(f"Updated provider: {updated_provider.first_name} {updated_provider.last_name}")
```

#### Delete a provider

```python
await client.providers.delete_provider(1)
```

## Error Handling

The client provides specific exception classes for different types of errors:

```python
from easyappointments import (
    EasyAppointmentsError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)

try:
    await client.admins.list_admins()
except AuthenticationError:
    print("Authentication failed")
except ResourceNotFoundError:
    print("Resource not found")
except ValidationError as e:
    print(f"Validation error: {e}")
except RateLimitError:
    print("Rate limit exceeded")
except ServerError:
    print("Server error")
except EasyAppointmentsError as e:
    print(f"API error: {e}")
```

## Extending the Client

To add support for additional API endpoints, create a new API manager class that extends `BaseAPI`:

```python
from easyappointments.api.base import BaseAPI
from easyappointments.models import YourModel, PaginatedResponse


class YourAPI(BaseAPI):
    async def list_items(self):
        response = await self._get("/your-endpoint")
        return PaginatedResponse.from_dict(response, YourModel)

    async def create_item(self, item):
        response = await self._post("/your-endpoint", data=item.model_dump(by_alias=True))
        return YourModel.model_validate(response)


# Then add it to the client
client = EasyAppointmentsClient(api_key="YOUR_API_KEY")
client.your_api = YourAPI(
    client._api_key,
    client._base_url,
    http_client=client._http_client
)
```

## License

MIT

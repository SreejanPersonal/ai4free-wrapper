# AI4Free Wrapper - Testing Directory

**Comprehensive Testing Framework**

This directory provides a structured, modular testing framework for validating the AI4Free API wrapper. The tests are organized by functionality to make it easier to run specific tests and maintain the codebase.

## Directory Structure

```
testing/
├── api/                       # API endpoint tests
│   ├── test_api_endpoints.py  # Core API endpoint tests
│   └── test_api_usage.py      # Usage tracking tests
│
├── client/                    # OpenAI client compatibility tests
│   └── test_openai_client.py  # Client compatibility tests
│
├── providers/                 # Provider-specific tests
│   ├── test_provider_5.py     # Provider 5 tests
│   └── test_provider_7.py     # Provider 7 tests
│
├── image_generation/          # Image generation tests
│   ├── test_image_generation.py       # General image generation tests
│   └── test_provider_specific_image.py # Provider-specific image tests
│
├── utils/                     # Shared testing utilities
│   ├── image_utils.py         # Image handling utilities
│   └── test_helpers.py        # Common test helper functions
│
└── README.md                  # This documentation
```

## Test Categories

### API Tests
- **test_api_endpoints.py**: Tests core API endpoints including API key generation and authentication.
- **test_api_usage.py**: Tests API usage tracking and reporting.

### Client Tests
- **test_openai_client.py**: Tests compatibility with the OpenAI client library across various providers.

### Provider Tests
- **test_provider_5.py**: Tests Provider 5's chat completion capabilities.
- **test_provider_7.py**: Tests Provider 7's chat completion capabilities.

### Image Generation Tests
- **test_image_generation.py**: Tests general image generation functionality.
- **test_provider_specific_image.py**: Tests provider-specific image generation capabilities.

### Utilities
- **test_helpers.py**: Common helper functions for formatting test output.
- **image_utils.py**: Utilities for saving and managing generated images.

## Running Tests

### Running Individual Tests

To run a specific test module, navigate to the testing directory and run the Python file directly:

```bash
cd testing
python api/test_api_endpoints.py
```

### Running All Tests

To run all tests, you can use a simple script or run them individually:

```bash
# Example script to run all tests (create this if needed)
cd testing
python -m api.test_api_endpoints
python -m api.test_api_usage
python -m client.test_openai_client
python -m providers.test_provider_5
python -m providers.test_provider_7
python -m image_generation.test_image_generation
python -m image_generation.test_provider_specific_image
```

## Test Configuration

Most tests use environment variables for configuration. Ensure your `.env` file is properly set up with the following variables:

- `LOCAL_API_URL`: The URL of your local API server (default: "http://127.0.0.1:5000")
- `TEST_API_KEY`: Your test API key
- `SYSTEM_SECRET`: The system secret for API key generation tests

## Adding New Tests

When adding new tests:

1. Place them in the appropriate category directory
2. Import common utilities from `testing.utils`
3. Follow the existing pattern for consistent test output
4. Update this README if adding new test categories

## Best Practices

- Use the common utilities for consistent output formatting
- Create output directories for test artifacts (e.g., generated images)
- Handle exceptions properly and provide clear error messages
- Use descriptive test names and comments

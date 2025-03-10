# AI4Free Wrapper - Testing Directory

**Comprehensive Testing Scripts**

This directory provides a comprehensive suite of test scripts for validating the AI4Free API wrapper. These scripts are designed to test API endpoints, provider integrations, and usage tracking functionalities, ensuring the reliability, performance, and correctness of the application.

---

## Directory Overview

1. **Test Scripts**: Python Test Files.
   - **`API_Endpoint_Testing.py`**: API Endpoint Functionality Tests.
     - Tests the core functionality and responses of the API endpoints.
     - Includes tests for chat completion endpoints (`/v1/chat/completions`), model listing (`/v1/models`), API key generation (`/v1/api-keys`), usage details (`/v1/usage`), and uptime checks (`/v1/uptime/<model_id>`).
     - Validates request/response formats, status codes, and expected behaviors for different API operations.
     - See [`testing/API_Endpoint_Testing.py`](./API_Endpoint_Testing.py) for test implementations.

   - **`OpenAI_Client_Testing.py`**: OpenAI Client Compatibility Tests.
     - Validates the API wrapper's compatibility and integration with OpenAI's client API libraries and tools.
     - Ensures that the API wrapper behaves as expected when used with OpenAI-compatible clients.
     - Tests request/response compatibility, header handling, and adherence to OpenAI API standards.
     - See [`testing/OpenAI_Client_Testing.py`](./OpenAI_Client_Testing.py) for test implementations.

   - **`test_api_usage.py`**: API Usage Tracking and Rate Limit Tests.
     - Tests API usage tracking, rate limiting, and cost metrics functionalities.
     - Validates that token usage is correctly tracked, rate limits are enforced as configured, and cost calculations are accurate.
     - Includes tests for usage recording, reporting, and rate limit enforcement mechanisms.
     - See [`testing/test_api_usage.py`](./test_api_usage.py) for test implementations.

---

## Usage

Run the test scripts to thoroughly validate the AI4Free API wrapper's functionality before deployment or after making changes. These scripts are crucial for:

- **Debugging**: Identifying and fixing bugs or issues in the API implementation, provider integrations, or usage tracking logic.
- **Performance Analysis**: Evaluating the performance of API endpoints and identifying potential bottlenecks.
- **Regression Testing**: Ensuring that new changes do not introduce regressions or break existing functionalities.
- **Reliability Assurance**: Verifying the overall reliability and stability of the system before deploying it to production.
- **Continuous Integration/Continuous Deployment (CI/CD)**: Integrating tests into CI/CD pipelines to automate testing and ensure code quality.

---

### Running Tests

To execute the test scripts, navigate to the `testing` directory in your terminal and run the Python scripts directly using the python interpreter:

```bash
cd testing
python API_Endpoint_Testing.py
python OpenAI_Client_Testing.py
python test_api_usage.py
```

Alternatively, you can run all tests at once from the project root directory:

```bash
python -m unittest testing/API_Endpoint_Testing.py testing/OpenAI_Client_Testing.py testing/test_api_usage.py
```

Review the output of the test scripts to check for any test failures or errors. Ensure all tests pass before deploying the application to production.

By utilizing these comprehensive test scripts, you can ensure the AI4Free API wrapper is robust, reliable, and functions as expected across different scenarios and integrations.

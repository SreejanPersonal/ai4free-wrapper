# AI4Free Wrapper - Services Directory

**Business Logic and Services**

This directory is responsible for implementing the core business logic of the AI4Free API wrapper. It contains services for API key management, rate limiting, and usage tracking. Services encapsulate reusable functionalities that are utilized by API controllers and models, promoting modularity, scalability, and maintainability.

---

## Directory Overview

1. **`api_key_service.py`**: API Key Management Service.
   - Handles all operations related to API keys.
   - **Key Generation**: Implements logic for generating new API keys, including setting expiration dates and associating keys with users or projects.
   - **Key Validation**: Provides functions for validating API keys, checking if a key is active and not expired.
   - **Key Revocation**: Manages API key revocation or disabling.
   - **Key Retrieval**: Offers methods for retrieving API keys from the database based on various criteria.
   - Interacts with the `ApiKey` model defined in [`app/models/api_key.py`](../models/api_key.py) for database operations.
   - See [`app/services/api_key_service.py`](./api_key_service.py) for service implementation.

2. **`rate_limit_service.py`**: Rate Limiting Service.
   - Implements rate limiting logic to protect the API from abuse and ensure fair usage.
   - **Redis Integration**: Uses Redis as a backend for storing and managing rate limit counters.
   - **Lua Scripting**: Employs Lua scripts for atomic operations in Redis to ensure efficient and accurate rate limiting.
   - **Tiered Rate Limits**: Supports different rate limit tiers, allowing for varying levels of access based on API keys or user roles.
   - **Configuration**: Rate limit configurations (e.g., limits per minute, per hour) are likely defined in [`app/config.py`](../config.py) and used by this service.
   - See [`app/services/rate_limit_service.py`](./rate_limit_service.py) for service implementation.

3. **`usage_service.py`**: Usage Tracking Service.
   - Tracks API usage, including token consumption and cost calculation.
   - **Token Counting**: Integrates with token counting utilities (likely from [`app/utils/token_counter.py`](../utils/token_counter.py)) to count prompt and completion tokens.
   - **Usage Recording**: Records detailed usage data in the database using the `Usage` model defined in [`app/models/usage.py`](../models/usage.py).
   - **Cost Calculation**: Calculates API usage costs based on provider pricing models and token counts.
   - **Reporting**: May provide functionalities for generating usage reports or retrieving usage statistics for API keys or users.
   - See [`app/services/usage_service.py`](./usage_service.py) for service implementation.

---

## Usage

Services in this directory are crucial for:

- **Business Logic Encapsulation**: Centralizing business logic in reusable services, promoting separation of concerns and code organization.
- **Modularity and Scalability**: Services are designed to be modular and independent, making it easier to scale and maintain the application.
- **Reusability**: Services provide reusable functions that can be called from different parts of the application (e.g., API controllers, background tasks, etc.).
- **Testability**: Services can be tested independently, improving the overall testability of the application.

API controllers in [`app/api/controllers.py`](../api/controllers.py) typically delegate business logic operations to these services. For example, when an API request comes in for chat completions, the controller might use the `rate_limit_service` to check rate limits, the `api_key_service` to validate the API key, and the `usage_service` to record usage data.

By structuring business logic into services, the AI4Free API wrapper achieves a clean, organized, and maintainable architecture.

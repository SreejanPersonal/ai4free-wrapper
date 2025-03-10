# AI4Free Wrapper - App Directory

**Core Flask Application**

This directory houses the core Flask application for the AI4Free API wrapper. It includes application initialization, configurations, extensions, API routing, controllers, services, and database models. The application factory pattern is used for structuring the Flask app, promoting modularity and testability.

---

## Directory Structure

1. **`__init__.py`**: Application Factory and Initialization.
   - Initializes the Flask application using the application factory pattern.
   - Configures application settings, registers blueprints, and sets up extensions.
   - See [`app/__init__.py`](./__init__.py) for the implementation.

2. **`config.py`**: Configuration Management.
   - Manages application configurations using environment variables and default settings.
   - Defines settings for database connections (PostgreSQL, Redis), provider API keys, Flask secret key, and debug mode.
   - See [`app/config.py`](./config.py) for configuration details.

3. **`extensions.py`**: Flask Extension Initialization.
   - Initializes and registers Flask extensions such as Flask-SQLAlchemy for database integration, Flask-CORS for handling Cross-Origin Resource Sharing, and potentially others.
   - See [`app/extensions.py`](./extensions.py) for extension setup.

---

## Subdirectories

- **`api/`**: API Endpoints and Controllers.
   - Contains modules for defining API routes, request handling logic, and response formatting.
   - **`controllers.py`**: Implements route handlers for API endpoints, managing request processing and calling relevant services. See [`app/api/controllers.py`](./api/controllers.py).
   - **`routes.py`**: Defines API routes using Flask blueprints, mapping URLs to controller functions. See [`app/api/routes.py`](./api/routes.py).
   - **`schemas.py`**: Defines request and response schemas using Marshmallow for data validation and serialization. See [`app/api/schemas.py`](./api/schemas.py).
   - **`utils.py`**: Utility functions specific to the API layer, such as request parsing or response helpers. See [`app/api/utils.py`](./api/utils.py).
   - See [`app/api/Readme.md`](./api/Readme.md) for more details on the API directory.

- **`models/`**: SQLAlchemy Database Models.
   - Defines SQLAlchemy models representing database tables.
   - Includes models for API keys, usage tracking, and potentially other entities.
   - Base model class is defined in [`app/models/base.py`](./models/base.py).
   - API key model is defined in [`app/models/api_key.py`](./models/api_key.py).
   - Usage model is defined in [`app/models/usage.py`](./models/usage.py).
   - See [`app/models/Readme.md`](./models/Readme.md) for more details on the models directory.

- **`providers/`**: LLM Provider Integrations.
   - Contains implementations for integrating with different LLM providers.
   - Each provider has its own module (e.g., `provider_1.py`, `provider_2.py`, etc.) implementing the `BaseProvider` interface defined in [`app/providers/base_provider.py`](./providers/base_provider.py).
   - `provider_manager.py` handles provider selection and management. See [`app/providers/provider_manager.py`](./providers/provider_manager.py).
   - See [`app/providers/Readme.md`](./providers/Readme.md) for more details on the providers directory.

- **`services/`**: Business Logic and Services.
   - Implements business logic for various functionalities.
   - **`api_key_service.py`**: Manages API key generation, validation, and retrieval. See [`app/services/api_key_service.py`](./services/api_key_service.py).
   - **`rate_limit_service.py`**: Implements rate limiting logic using Redis. See [`app/services/rate_limit_service.py`](./services/rate_limit_service.py).
   - **`usage_service.py`**: Handles usage tracking and reporting. See [`app/services/usage_service.py`](./services/usage_service.py).
   - See [`app/services/Readme.md`](./services/Readme.md) for more details on the services directory.

- **`utils/`**: Utility Functions.
   - Contains helper functions and utilities used across the application.
   - **`db_utils.py`**: Database utility functions, such as database session management. See [`app/utils/db_utils.py`](./utils/db_utils.py).
   - **`helpers.py`**: General helper functions. See [`app/utils/helpers.py`](./utils/helpers.py).
   - **`streaming.py`**: Utilities for handling streaming responses. See [`app/utils/streaming.py`](./utils/streaming.py).
   - **`token_counter.py`**: Utilities for counting tokens in text. See [`app/utils/token_counter.py`](./utils/token_counter.py).
   - See [`app/utils/Readme.md`](./utils/Readme.md) for more details on the utils directory.

---

This `app` directory is structured to provide a clear separation of concerns, making the codebase modular, maintainable, and scalable. It follows Flask best practices and industry-standard patterns for building robust web applications.

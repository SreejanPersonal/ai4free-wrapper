# AI4Free Wrapper - App API Directory

**Flask API Implementation**

This directory contains all components related to the Flask API implementation for the AI4Free API wrapper. It serves as the backbone for defining API routes, handling requests through controllers, validating data using schemas, and providing utility functions specific to the API layer.

---

## Directory Overview

1. **`__init__.py`**: API Blueprint Initialization.
   - Initializes the API blueprint for the Flask application.
   - Creates a Flask Blueprint named `api_bp` and registers it.
   - See [`app/api/__init__.py`](./__init__.py) for blueprint setup.

2. **`controllers.py`**: API Route Handlers (Controllers).
   - Contains controller functions that handle the business logic for each API route.
   - Each function corresponds to a specific API endpoint (e.g., chat completions, list models, API key generation, usage details, uptime check).
   - Handles request processing, calls relevant services to perform actions, and formats API responses.
   - See [`app/api/controllers.py`](./controllers.py) for controller implementations.

3. **`routes.py`**: API Route Definitions.
   - Defines API routes using the Flask blueprint (`api_bp`) created in `__init__.py`.
   - Maps URL endpoints to their respective controller functions defined in `controllers.py`.
   - Uses decorators (e.g., `@api_bp.route`) to register routes and specify HTTP methods.
   - See [`app/api/routes.py`](./routes.py) for route definitions.

4. **`schemas.py`**: API Request and Response Schemas.
   - Defines schemas for validating API request payloads and formatting API responses.
   - Uses Marshmallow library to define schemas as classes with fields and validation rules.
   - Ensures data consistency and validation for API inputs and outputs.
   - Includes schemas for chat completion requests, API key requests, usage requests, and model listings.
   - See [`app/api/schemas.py`](./schemas.py) for schema definitions.

5. **`utils.py`**: API Utility Functions.
   - Includes helper functions and utilities specific to the API layer.
   - May contain functions for request parsing, response formatting, error handling, or other API-related tasks.
   - See [`app/api/utils.py`](./utils.py) for API utility functions.

---

## Usage

This directory is crucial for implementing and refining the API behavior of the AI4Free API wrapper. It provides a structured approach to:

- **Endpoint Definition**: Define new API endpoints in `routes.py` and map them to controller functions.
- **Request Handling**: Implement request handling logic, business logic calls, and response formatting in `controllers.py`.
- **Data Validation**: Define and use schemas in `schemas.py` to validate request payloads and ensure data integrity.
- **Utility Functions**: Add any API-specific utility functions in `utils.py` to keep controllers and routes clean and focused.

By organizing API components in this directory, the codebase maintains clarity, scalability, and ease of maintenance for the API layer of the AI4Free wrapper.

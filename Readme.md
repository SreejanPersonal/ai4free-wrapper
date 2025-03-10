# AI4Free API Wrapper

**An industry-grade, multi-provider API wrapper for chat completions.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)  
[![GitHub issues](https://img.shields.io/github/issues/SreejanPersonal/ai4free-wrapper)](https://github.com/SreejanPersonal/ai4free-wrapper/issues)  
[![GitHub stars](https://img.shields.io/github/stars/SreejanPersonal/ai4free-wrapper)](https://github.com/SreejanPersonal/ai4free-wrapper/stargazers)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture & Directory Structure](#architecture--directory-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Database Management](#database-management)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

The **AI4Free API Wrapper** is a robust and production-ready API wrapper designed to provide a unified interface to multiple Large Language Model (LLM) providers. It supports both streaming and non-streaming chat completions and includes built-in functionalities such as API key management, rate limiting, detailed usage tracking, and a comprehensive testing suite.

This repository, maintained by **SreejanPersonal**, serves as a backend service for applications requiring seamless integration with various LLMs through a single, consistent API. It leverages Flask for the REST API, SQLAlchemy with PostgreSQL for database management, and Redis for rate limiting, ensuring scalability and reliability.

---

## Features

- **Multi-Provider Support:** Seamlessly switch between diverse LLM providers including DeepSeek-R1, gpt-4o, o3-mini, DeepSeekV3, and more. Provider integrations are implemented in the [`app/providers`](./app/providers) directory, with each provider having a dedicated module (e.g., `provider_1.py`, `provider_2.py`). The `provider_manager.py` in the same directory orchestrates provider selection based on configuration.
- **Unified API Interface:** Enjoy consistent request and response schemas across different providers, adhering to OpenAI-compatible API standards. API routes are defined in [`app/api/routes.py`](./app/api/routes.py), and request/response schemas are validated using Marshmallow, defined in [`app/api/schemas.py`](./app/api/schemas.py).
- **Streaming & Non-Streaming:** Supports both streaming responses using Server-Sent Events (SSE) and standard, non-streaming completions. Streaming logic is handled in [`app/utils/streaming.py`](./app/utils/streaming.py), and the API endpoints in [`app/api/controllers.py`](./app/api/controllers.py) manage the response formatting based on client request headers.
- **Robust Rate Limiting:** Protect your services with configurable rate limiting implemented using Redis and Lua scripting. The rate limiting service, located in [`app/services/rate_limit_service.py`](./app/services/rate_limit_service.py), uses Redis for efficient counter management and Lua scripts for atomic operations, ensuring high performance and preventing race conditions.
- **API Key Management:** Securely generate, validate, and manage API keys. API key generation and validation logic is implemented in [`app/services/api_key_service.py`](./app/services/api_key_service.py). API keys are stored in the database using SQLAlchemy models defined in [`app/models/api_key.py`](./app/models/api_key.py).
- **Token Usage & Cost Tracking:** Detailed tracking of prompt tokens, completion tokens, and associated costs. Usage tracking is implemented in [`app/services/usage_service.py`](./app/services/usage_service.py), and usage data is stored using SQLAlchemy models defined in [`app/models/usage.py`](./app/models/usage.py). Token counting utilities are available in [`app/utils/token_counter.py`](./app/utils/token_counter.py).
- **Flask-based REST API:** Powered by Flask, a micro web framework, with CORS enabled for cross-origin requests. The Flask application is initialized in [`app/__init__.py`](./app/__init__.py), and CORS is configured using the Flask-CORS extension.
- **PostgreSQL & SQLAlchemy Integration:** Reliable data persistence and ORM support using PostgreSQL and SQLAlchemy. Database connection and SQLAlchemy setup are configured in [`app/extensions.py`](./app/extensions.py) and [`app/config.py`](./app/config.py). Database models are defined in the [`app/models`](./app/models) directory.
- **Comprehensive Testing Suite:** End-to-end testing scripts for API endpoints, provider integrations, and usage metrics are located in the [`Testing`](./Testing) directory. Tests are written using Python's `unittest` framework and `requests` library to simulate API calls.
- **Production-Ready Configuration:** Gunicorn with gevent for rapid asynchronous handling and optimal CPU resource utilization. Gunicorn configuration is in [`gunicorn.config.py`](./gunicorn.config.py), optimized for production deployment with asynchronous workers.

---

## Architecture & Directory Structure

The repository is organized following industry best practices using the application factory pattern. The key directories include:

- **`app/`**  
  Contains the core Flask application, initialized in [`app/__init__.py`](./app/__init__.py). It includes configuration files in [`app/config.py`](./app/config.py), Flask extensions setup in [`app/extensions.py`](./app/extensions.py), API routes defined in [`app/api/routes.py`](./app/api/routes.py), controllers in [`app/api/controllers.py`](./app/api/controllers.py), services in [`app/services/`](./app/services/), and database models in [`app/models/`](./app/models/).

- **`providers/`**  
  Integrates multiple LLM providers with alias-based mapping to ensure flexibility. Each provider has its own implementation module (e.g., `provider_1.py`, `provider_2.py`, etc.) within [`app/providers/`](./app/providers/). The `provider_manager.py` in this directory handles provider selection and management.

- **`services/`**  
  Implements business logic such as API key management (in [`app/services/api_key_service.py`](./app/services/api_key_service.py)), rate limiting (in [`app/services/rate_limit_service.py`](./app/services/rate_limit_service.py)), and usage recording (in [`app/services/usage_service.py`](./app/services/usage_service.py)).

- **`utils/`**  
  Contains utility functions for database context management (in [`app/utils/db_utils.py`](./app/utils/db_utils.py)), token counting (in [`app/utils/token_counter.py`](./app/utils/token_counter.py)), stream processing (in [`app/utils/streaming.py`](./app/utils/streaming.py)), and helper methods (in [`app/utils/helpers.py`](./app/utils/helpers.py)).

- **`data/`**  
  Contains centralized data files such as `models.json`, which includes provider-specific and versioned model metadata.

- **`Testing/`**  
  A set of testing scripts and clients to validate API endpoints. Includes `API_Endpoint_Testing.py`, `OpenAI_Client_Testing.py`, and `test_api_usage.py` for comprehensive API validation.

- **Additional Files:**  
  - `db_manager.py`: CLI tool for database management (creation, reset, etc.).
  - `run.py`: Script to run the Flask application in development mode.
  - `gunicorn.config.py`: Gunicorn configuration file for production deployment.
  - `requirements.txt`: List of Python dependencies.

---

## Installation

### Prerequisites

- **Python 3.10+**: Ensure you have Python 3.10 or higher installed. Check your version using `python --version`.
- **PostgreSQL**: Install and configure PostgreSQL database. Refer to the [PostgreSQL documentation](https://www.postgresql.org/docs/current/installation.html) for installation instructions specific to your operating system.
- **Redis**: Install and configure Redis server. Follow the [Redis installation guide](https://redis.io/docs/getting-started/installation/) for your system.

### Clone the Repository

```bash
git clone https://github.com/SreejanPersonal/ai4free-wrapper.git
cd ai4free-wrapper
```

### Create a Virtual Environment

Using `venv` (recommended for isolating project dependencies):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

Install required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Configuration

1. **Environment Variables:**  
   Create a `.env` file in the project root. Refer to `.env.example` for a template and descriptions of all environment variables. Key configurations include:

   - **Provider Base URLs & API Keys:**  
     Set API endpoints and keys for each LLM provider you intend to use. These variables are typically prefixed with the provider alias (e.g., `PROVIDER_1_API_KEY`, `PROVIDER_2_BASE_URL`).
   - **Local API URL:**  
     `LOCAL_API_URL=http://127.0.0.1:5000` (default for local development)
   - **Database Settings:**  
     Configure PostgreSQL connection details using variables such as `DATABASE_URL`. Ensure the database is running and accessible.
   - **Redis Settings:**  
     Configure Redis connection details, typically using `REDIS_URL`. Ensure Redis server is running.
   - **Flask Settings:**  
     Set `FLASK_SECRET_KEY` for session management and CSRF protection. Toggle `FLASK_DEBUG=1` for debug mode during development (set to `0` in production).
   - **System Secret:**  
     `SYSTEM_SECRET` environment variable is crucial for secure API key generation and management. This secret should be a strong, randomly generated string.

2. **Model Configuration:**  
   Models and provider mappings are defined in `data/models.json`. This JSON file specifies available models, their providers, and configurations. `app/config.py` further refines model configurations and mappings, loading data from `models.json` and environment variables.

---

## Running the Application

### Development Server

Start the Flask development server. This is suitable for local development and testing.

```bash
python run.py
```

The API will be accessible at [http://127.0.0.1:5000](http://127.0.0.1:5000). Flask's debug mode (if enabled via `FLASK_DEBUG=1`) provides hot-reloading and detailed error messages.

### Production Server

For production deployments, use Gunicorn, a Python WSGI HTTP server, with the provided configuration. Gunicorn is configured in `gunicorn.config.py` for optimal performance.

```bash
gunicorn -c gunicorn.config.py run:app
```

This command starts Gunicorn with settings defined in `gunicorn.config.py`, using `run:app` to specify the Flask application instance. Gunicorn is configured to use gevent workers for asynchronous request handling, maximizing CPU utilization and throughput.

---

## API Endpoints

The API is designed to be OpenAI-compatible, making it easy to integrate with existing OpenAI clients and tools. Key endpoints include:

- **Health Check**
  - **GET** `/health`  
    _Returns a simple JSON `{"status": "ok"}` indicating the service is running. Useful for monitoring and health checks._

- **Chat Completions**
  - **POST** `/v1/chat/completions`  
    _Handles both streaming and non-streaming chat completions. Requires a valid API key passed in the `Authorization` header as a Bearer token. The request body should follow the OpenAI chat completions API format. See [`app/api/controllers.py`](./app/api/controllers.py) for request handling and response formatting._

- **List Models**
  - **GET/POST** `/v1/models`  
    _Returns a JSON list of available models and their configurations as defined in `data/models.json` and `app/config.py`. Useful for clients to discover available models. See [`app/api/controllers.py`](./app/api/controllers.py) for implementation details._

- **API Key Generation**
  - **POST** `/v1/api-keys`  
    _Generates a new API key. Requires system secret verification via the `X-System-Secret` header for security. See [`app/api/controllers.py`](./app/api/controllers.py) and [`app/services/api_key_service.py`](./app/services/api_key_service.py) for API key generation logic._

- **Usage Details**
  - **POST** `/v1/usage`  
    _Returns usage details for a given API key. Requires the API key in the `Authorization` header. Returns token counts, request statistics, and cost metrics. See [`app/api/controllers.py`](./app/api/controllers.py) and [`app/services/usage_service.py`](./app/services/usage_service.py) for usage data retrieval._

- **Uptime Check**
  - **GET** `/v1/uptime/<model_id>`  
    _Performs a minimal streaming check to verify that a specific model is up and responding. Initiates a lightweight streaming request to the specified model. See [`app/api/controllers.py`](./app/api/controllers.py) for the uptime check implementation._

> **Note:** Ensure your requests include the appropriate JSON payloads and headers as specified in the code comments and schema validations in [`app/api/schemas.py`](./app/api/schemas.py). API key authentication is enforced using Bearer tokens in the `Authorization` header for most endpoints.

---

## Testing

A comprehensive suite of test scripts is located in the [`Testing/`](./Testing) directory. These scripts use Python's `unittest` framework and `requests` library to validate API functionality.

- **Chat Completion Testing:**  
  - `API_Endpoint_Testing.py`: Tests API endpoints for chat completions, including streaming and non-streaming modes.
  - `OpenAI_Client_Testing.py`: Simulates OpenAI client interactions to test API compatibility.
  - Run tests using: 
    ```bash
    python Testing/API_Endpoint_Testing.py
    python Testing/OpenAI_Client_Testing.py
    ```

- **API Usage Testing:**  
  - `test_api_usage.py`: Tests API usage tracking and reporting endpoints.
  - Run tests using:
    ```bash
    python Testing/test_api_usage.py
    ```

These tests verify provider integration, streaming behavior, non-streaming behavior, rate limiting, and API key authentication. Review test scripts in [`Testing/`](./Testing) for detailed test cases and setup.

---

## Database Management

The `db_manager.py` script provides a CLI tool for managing the PostgreSQL database. It uses SQLAlchemy for database interactions and Flask's application context for configuration.

### Commands

- **Create Database & Tables:**

  ```bash
  python db_manager.py create-db
  ```
  _Creates the PostgreSQL database and SQLAlchemy tables as defined in [`app/models/`](./app/models/)._

- **Clean (Drop) Database Tables:**

  ```bash
  python db_manager.py clean-db
  ```
  _Drops all tables from the database. Useful for starting with a clean schema._

- **Reset Database (Drop & Recreate Tables):**

  ```bash
  python db_manager.py reset-db
  ```
  _Drops and recreates all database tables. Effectively resets the database schema and data._

- **List All Tables:**

  ```bash
  python db_manager.py list-tables
  ```
  _Lists all tables in the connected PostgreSQL database. Useful for verifying database schema._

> **Warning:** Database management commands in `db_manager.py` modify your database schema and data. **Always ensure you have backups** before running these commands, especially in production environments. Refer to [`db_manager.py`](./db_manager.py) for command implementation details.

---

## Contributing

Contributions are welcome and encouraged! Follow these guidelines to contribute to the project:

1. **Fork the Repository:**  
   Fork the [AI4Free API Wrapper repository](https://github.com/SreejanPersonal/ai4free-wrapper) to your GitHub account. Create a new branch from the `main` branch for your contributions.

2. **Code Standards:**  
   Adhere to PEP 8 standards for Python code. Use linters and formatters (e.g., `flake8`, `black`) to ensure code quality and consistency. Ensure proper logging using the `logging` module, implement robust error handling using try-except blocks, and follow the application architecture and design patterns used in the project.

3. **Commit Messages:**  
   Write clear, descriptive commit messages. Follow conventional commit message format, detailing the changes made and the reasoning behind them.

4. **Pull Request:**  
   Submit a pull request to the `main` branch of the main repository. Include a clear description of your changes, any relevant context, and testing instructions. Ensure your pull request addresses a specific issue or feature request.

5. **Testing:**  
   Include tests for new features and changes. Ensure existing tests pass after your changes. Refer to the [`Testing/`](./Testing) directory for existing test scripts and examples.

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for the full license text and details.

---

## Contact

For questions, suggestions, or issues, please use the following channels:

- **GitHub Issues:** [GitHub Issues Tracker](https://github.com/SreejanPersonal/ai4free-wrapper/issues) - Report bugs, suggest enhancements, and ask questions.
- **GitHub Profile:** [SreejanPersonal](https://github.com/SreejanPersonal) - For direct inquiries and contributions.

---

_Thank you for using the AI4Free API Wrapper. Happy coding!_

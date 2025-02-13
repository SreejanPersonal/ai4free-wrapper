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

This repository is maintained by **SreejanPersonal** and is intended to serve as a backend service for applications requiring integration with various LLMs using a single, consistent API.

---

## Features

- **Multi-Provider Support:** Seamlessly switch between providers such as DeepSeek-R1, gpt-4o, o3-mini, DeepSeekV3, and more.
- **Unified API Interface:** Consistent request and response schemas across different providers.
- **Streaming & Non-Streaming:** Supports both streaming responses and standard completions.
- **Robust Rate Limiting:** Protect your services with configurable rate limiting using Redis and Lua scripting.
- **API Key Management:** Generate, validate, and manage API keys securely.
- **Token Usage & Cost Tracking:** Detailed tracking of prompt, completion tokens, and associated costs.
- **Flask-based REST API:** Powered by Flask with CORS enabled for cross-origin requests.
- **PostgreSQL & SQLAlchemy Integration:** Reliable data persistence and ORM support.
- **Comprehensive Testing Suite:** End-to-end testing scripts for API endpoints, provider integrations, and usage metrics.
- **Production-Ready Configuration:** Gunicorn with gevent for rapid asynchronous handling and optimal CPU resource utilization.

---

## Architecture & Directory Structure

The repository is organized following industry best practices using the application factory pattern. The key directories include:

- **`app/`**  
  Contains the core Flask application, configuration files, extensions, API routes, controllers, services, and models.

- **`providers/`**  
  Integrates multiple LLM providers with alias-based mapping to ensure flexibility. Each provider has its own implementation module.

- **`services/`**  
  Implements business logic such as API key management, rate limiting, and detailed usage recording.

- **`utils/`**  
  Utility functions for database context management, token counting, stream processing, and helper methods.

- **`data/`**  
  Contains centralized data files such as `models.json` with provider-specific and versioned model metadata.

- **`Testing/`**  
  A set of testing scripts and clients to validate API endpoints, including chat completions and usage statistics.

- **Additional Files:**  
  - `db_manager.py` for database creation, reset, and management.  
  - `run.py` for running the Flask application.  
  - `gunicorn.config.py` for production deployment configuration.  
  - `requirements.txt` listing all dependencies.

---

## Installation

### Prerequisites

- **Python 3.10+**
- **PostgreSQL**
- **Redis**

### Clone the Repository

```bash
git clone https://github.com/SreejanPersonal/ai4free-wrapper.git
cd ai4free-wrapper
```

### Create a Virtual Environment

Using `venv`:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

1. **Environment Variables:**  
   Create a `.env` file in the project root. You may refer to `.env.example` for the complete set of environment variables. The default settings include:

   - **Provider Base URLs & API Keys:**  
     Set your provider endpoints and API keys accordingly.
   - **Local API URL:**  
     `LOCAL_API_URL=http://127.0.0.1:5000`
   - **Database Settings:**  
     Configure PostgreSQL connection details.
   - **Redis Settings:**  
     Configure your Redis instance.
   - **Flask Settings:**  
     Set `FLASK_SECRET_KEY` and toggle `FLASK_DEBUG` as needed.
   - **System Secret:** For secure API key generation and management.

2. **Model Configuration:**  
   Models and provider mappings are defined in `data/models.json` and further refined in `app/config.py`.

---

## Running the Application

### Development Server

Start the Flask development server using:

```bash
python run.py
```

The API will be accessible at [http://127.0.0.1:5000](http://127.0.0.1:5000).

### Production Server

Use Gunicorn with the provided configuration:

```bash
gunicorn -c gunicorn.config.py run:app
```

---

## API Endpoints

The API is designed to be OpenAI-compatible. Some key endpoints include:

- **Health Check**
  - **GET** `/health`  
    _Returns a simple JSON indicating the service status._

- **Chat Completions**
  - **POST** `/v1/chat/completions`  
    _Handles both streaming and non-streaming chat completions. Requires a valid API key passed in the `Authorization` header (Bearer token)._

- **List Models**
  - **GET/POST** `/v1/models`  
    _Returns available models and their configurations._

- **API Key Generation**
  - **POST** `/v1/api-keys`  
    _Generates a new API key for a user. Requires system secret verification._

- **Usage Details**
  - **POST** `/v1/usage`  
    _Returns usage details for the provided API key, including token counts, request statistics, and cost metrics._

- **Uptime Check**
  - **GET** `/v1/uptime/<model_id>`  
    _Performs a minimal streaming check to verify that a model is up._

> **Note:** Ensure your requests include the appropriate JSON payloads and headers as specified in the code comments and schema validations.

---

## Testing

A comprehensive suite of test scripts is provided in the `Testing/` directory. These scripts cover:

- **Chat Completion Testing:**  
  - `API_Endpoint_Testing.py` and `OpenAI_Client_Testing.py`
- **API Usage Testing:**  
  - `test_api_usage.py`

To run the tests, execute the scripts directly, for example:

```bash
python Testing/API_Endpoint_Testing.py
python Testing/OpenAI_Client_Testing.py
python Testing/test_api_usage.py
```

These tests verify provider integration, streaming versus non-streaming behavior, and rate limiting.

---

## Database Management

The repository includes a CLI tool for managing your PostgreSQL database.

### Commands

- **Create Database & Tables:**

  ```bash
  python db_manager.py create-db
  ```

- **Clean (Drop) Database Tables:**

  ```bash
  python db_manager.py clean-db
  ```

- **Reset Database (Drop & Recreate Tables):**

  ```bash
  python db_manager.py reset-db
  ```

- **List All Tables:**

  ```bash
  python db_manager.py list-tables
  ```

> **Warning:** These commands modify your database schema. Ensure you have proper backups before running them in production.

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the Repository:**  
   Create your own branch from the `main` branch.

2. **Code Standards:**  
   Follow PEP 8 standards for Python code. Ensure proper logging, error handling, and adherence to the application architecture.

3. **Commit Messages:**  
   Use descriptive commit messages detailing your changes and reasoning.

4. **Pull Request:**  
   Submit a pull request with a clear description of your changes and any additional context or testing instructions.

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## Contact

For questions or suggestions, please reach out via GitHub:

- **GitHub:** [SreejanPersonal](https://github.com/SreejanPersonal)

---

_Thank you for using the AI4Free API Wrapper. Happy coding!_
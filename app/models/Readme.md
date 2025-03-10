# AI4Free Wrapper - Models Directory

**SQLAlchemy ORM Models**

This directory contains the SQLAlchemy ORM models used for database interactions in the AI4Free API wrapper. These models define the structure of database tables and provide an interface for interacting with the database using SQLAlchemy.

---

## Directory Overview

1. **`api_key.py`**: API Key Model.
   - Defines the `ApiKey` model, which represents the structure of the `api_keys` database table.
   - Handles attributes such as `api_key_id` (primary key), `user_id`, `api_key_secret`, `created_at`, `expires_at`, `is_active`, and `rate_limit_tier`.
   - Includes methods for API key creation, validation, and checking expiry status.
   - See [`app/models/api_key.py`](./api_key.py) for model definition.

2. **`base.py`**: Base Model and Database Initialization.
   - Contains shared model definitions and initializes the SQLAlchemy database instance (`db`).
   - Defines a base model class `Base` that other models inherit from, providing common functionalities and configurations.
   - Initializes the Flask-SQLAlchemy extension and provides the `db` instance for use in other models.
   - See [`app/models/base.py`](./base.py) for base model and database setup.

3. **`usage.py`**: Usage Tracking Model.
   - Defines the `Usage` model, which represents the structure of the `usage_records` database table.
   - Tracks detailed token usage, including attributes like `usage_id` (primary key), `api_key_id` (foreign key to `ApiKey`), `request_timestamp`, `model_requested`, `provider_used`, `prompt_tokens`, `completion_tokens`, `cost_in_usd`, and `request_status`.
   - Designed for detailed monitoring of token usage and cost tracking.
   - See [`app/models/usage.py`](./usage.py) for model definition.

---

## Usage

The models in this directory are integral to the AI4Free API wrapper's data persistence logic. They are used throughout the application, particularly in services and controllers, to interact with the database.

- **Data Persistence**: Models define how data is structured in the database and how the application interacts with it.
- **ORM Abstraction**: SQLAlchemy ORM provides an abstraction layer, allowing interaction with the database using Python objects rather than raw SQL queries.
- **Relationship Management**: Models define relationships between database tables (e.g., `Usage` model has a foreign key relationship with `ApiKey` model).
- **Data Validation**: SQLAlchemy models can include validation rules to ensure data integrity.

These models manage operations related to:

- **API Keys**: Storing, retrieving, and managing API keys using the `ApiKey` model.
- **Usage Metrics**: Recording and querying usage data using the `Usage` model for tracking token consumption and costs.
- **Database Interactions**: Providing a consistent and structured way to interact with the PostgreSQL database throughout the application.

By using SQLAlchemy ORM models, the application achieves robust data management, separation of concerns, and maintainability in its data layer.

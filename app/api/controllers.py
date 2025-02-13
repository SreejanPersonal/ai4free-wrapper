# app/api/controllers.py

from flask import jsonify, current_app
from marshmallow import ValidationError
import logging
from ..providers.provider_manager import ProviderManager
from .schemas import ChatCompletionRequestSchema, ModelListResponseSchema
from ..services.api_key_service import get_api_key_from_request, create_new_api_key, get_api_key_record
from ..services.usage_service import record_request, record_failed_request
from ..utils.token_counter import count_tokens
from ..config import Config
from ..utils.streaming import generate_stream

log = logging.getLogger(__name__)

def handle_chat_completion(data, request):
    """Handles a chat completion request."""
    # 1. Validate the request data
    schema = ChatCompletionRequestSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return {"error": err.messages, "status_code": 400}

    # 2. Get the API key and user
    api_key_record = get_api_key_from_request(request)
    if not api_key_record:
        return {"error": "Invalid API key", "status_code": 401}

    api_key = api_key_record.api_key
    user_id = api_key_record.user_id

    # 3. Select a provider
    model_id = validated_data['model']
    provider = current_app.provider_manager.select_provider(model_id)
    if not provider:
        record_failed_request(user_id, api_key, model_id)
        return {"error": f"Model '{model_id}' not supported or provider unavailable.", "status_code": 400}

    # Set the streaming flag and prepare data for provider call
    is_stream = validated_data.get("stream", False)
    data_for_provider = validated_data.copy()
    data_for_provider.pop("model", None)
    data_for_provider.pop("messages", None)
    data_for_provider.pop("stream", None)

    # 4. Check token limits using model-specific configuration
    messages = validated_data['messages']
    prompt_tokens = count_tokens(messages, model_id, current_app)
    model_config = Config.get_model_config(model_id)
    allowed_input_tokens = model_config.get("max_input_tokens")
    allowed_output_tokens = model_config.get("max_output_tokens")

    # Validate the prompt (input) tokens
    if prompt_tokens > allowed_input_tokens:
        record_failed_request(user_id, api_key, model_id)
        return {
            "error": f"Input tokens ({prompt_tokens}) exceed the model's allowed limit of {allowed_input_tokens} per request.",
            "status_code": 400
        }

    # Validate the requested max output tokens, if supplied.
    # If not supplied, default to the allowed maximum.
    requested_max_tokens = validated_data.get("max_tokens", allowed_output_tokens)
    if requested_max_tokens > allowed_output_tokens:
        record_failed_request(user_id, api_key, model_id)
        return {
            "error": f"Requested max output tokens ({requested_max_tokens}) exceed the model's allowed limit of {allowed_output_tokens} per request.",
            "status_code": 400
        }
    # Overwrite the value in the payload for consistency with provider calls.
    validated_data["max_tokens"] = requested_max_tokens

    # 5. Call the provider
    try:
        if is_stream:
            response_generator = provider.chat_completion(
                model_id=model_id,
                messages=messages,
                stream=is_stream,
                **data_for_provider
            )
            return generate_stream(response_generator, user_id, api_key, model_id, current_app._get_current_object(), messages)
        else:
            response = provider.chat_completion(
                model_id=model_id,
                messages=messages,
                stream=is_stream,
                **data_for_provider,
                app=current_app
            )
            completion_tokens = count_tokens(
                [{"role": "assistant", "content": response["choices"][0]["message"]["content"]}],
                model_id,
                current_app
            )
            record_request(user_id, api_key, model_id, prompt_tokens, completion_tokens, response)
            return response, 200
    except Exception as e:
        log.error(f"Provider error: {e}")
        record_failed_request(user_id, api_key, model_id)
        return {"error": str(e), "status_code": 500}

def list_models():
    """Lists available models in an OpenAI-compatible format."""
    try:
        provider_manager = current_app.provider_manager
        all_models = provider_manager.list_models()
        response_models = []
        for model in all_models:
            # Transform your internal model format into the OpenAI-type model object.
            response_models.append({
                "id": model.get("id"),
                "object": "model",
                "created": 1700000000,  # You can replace or generate a real timestamp if needed.
                "owned_by": "DevsDoCode",  # Adjust as appropriate or make this dynamic.
                "permission": [],
                "owner_cost_per_million_tokens": model.get("owner_cost_per_million_tokens", 0),
                "user_cost_per_million_tokens": 0
            })

        return {
            "data": response_models,
            "object": "list",
            "status_code": 200
        }
    except Exception as e:
        log.error(f"Error listing models: {e}")
        return {"error": "Failed to retrieve model list", "status_code": 500}

def create_api_key(data):
    from ..models.usage import User
    from ..models.api_key import APIKey
    system_secret = Config.SYSTEM_SECRET
    provided_secret = data.get('secret')
    if not system_secret or provided_secret != system_secret:
        return {"error": "Unauthorized", "status_code": 401}, 401

    user_id = data.get('user_id')
    telegram_user_link = data.get('telegram_user_link')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    username = data.get('username')
    if not user_id or not telegram_user_link:
        return {"error": "Missing required fields: user_id and telegram_user_link", "status_code": 400}, 400

    # First check if the user already exists and already has an API key.
    existing_user = User.query.filter_by(external_user_id=user_id).first()
    if existing_user:
        existing_key = APIKey.query.filter_by(user_id=existing_user.user_id, is_active=True).first()
        if existing_key:
            return {
                "error": "User already exists. Cannot create duplicate API key.",
                "existing_key": existing_key.api_key,
                "status_code": 409
            }, 409

    # No pre-existing user and API key? Proceed to create new API key.
    try:
        # create_new_api_key creates a user record if it does not exist so it is safe to call here.
        new_api_key = create_new_api_key(user_id, telegram_user_link, first_name, last_name, username)
        return {
            "api_key": new_api_key,
            "message": "Store this key securely - it cannot be retrieved later!",
            "status_code": 201
        }, 201
    except Exception as e:
        # Any other exception gets a 500.
        log.error(f"Error creating API key: {e}")
        return {"error": str(e), "status_code": 500}, 500
    
def get_usage(data):
    """
    Retrieves usage details for a user based on the provided API key.
    The returned details include:
      1. Total input tokens
      2. Total output tokens
      3. Success rate (successful_requests / total_requests × 100)
      4. Model‑wise token usage details (retrieved from the APIKey record)
      5. Telegram full name (concatenation of first & last name)
      6. Telegram username (if available)
      7. API key
      8. Telegram Id (stored in external_user_id)
      9. The API key creation time
      10. The total cost incurred by the user
    """
    api_key = data.get('api_key')
    if not api_key:
        return {"error": "API key is required in payload", "status_code": 400}

    # Get the APIKey record from the database
    from ..services.api_key_service import get_api_key_record
    api_key_record = get_api_key_record(api_key)
    if not api_key_record:
        return {"error": "Invalid API key", "status_code": 401}

    # Get the associated user (via relationship)
    user = api_key_record.user
    if not user:
        return {"error": "User associated with the API key not found", "status_code": 404}

    # Instead of dummy data, retrieve the original model usage data
    model_usage = api_key_record.model_usage if api_key_record.model_usage is not None else {}

    # Calculate success rate (avoid division by zero)
    if user.total_requests and user.total_requests > 0:
        success_rate = (user.successful_requests / user.total_requests) * 100
    else:
        success_rate = 0.0

    # Construct Telegram full name by concatenating first and last name
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

    usage_data = {
        "input_tokens": user.total_input_tokens,
        "output_tokens": user.total_output_tokens,
        "successful_requests": user.successful_requests,
        "total_requests": user.total_requests,
        "success_rate": success_rate,
        "model_usage": model_usage,
        "telegram_full_name": full_name,
        "telegram_username": user.username,
        "api_key": api_key_record.api_key,
        "telegram_id": user.external_user_id,
        "api_key_created_at": api_key_record.created_at.isoformat() if api_key_record.created_at else None,
        "total_cost": str(user.total_cost)
    }
    return usage_data, 200
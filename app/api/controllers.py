# app/api/controllers.py

from flask import jsonify, current_app
from marshmallow import ValidationError
import logging
from ..providers.provider_manager import ProviderManager
from .schemas import ChatCompletionRequestSchema, ModelListResponseSchema, ImageGenerationRequestSchema
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

def handle_image_generation(data, request):
    """Handles an image generation request."""
    # 1. Validate the request data
    schema = ImageGenerationRequestSchema()
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

    # 3. Determine which provider to use based on the model
    model_id = validated_data.get('model', 'Provider-5/flux-pro')
    
    # Get the appropriate provider directly using the model ID
    provider = current_app.provider_manager.select_provider(model_id)
    if not provider:
        return {"error": f"Image generation provider for model '{model_id}' not available", "status_code": 503}

    # 4. Call the provider's image_generation method
    try:
        response = provider.image_generation(
            prompt=validated_data['prompt'],
            size=validated_data.get('size', "1024x1024"),
            n=validated_data.get('n', 1),
            response_format=validated_data.get('response_format', "url"),
            model=model_id
        )
        return response, 200
    except Exception as e:
        log.error(f"Image generation error: {e}")
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
    """
    Creates a new API key for a user.
    
    This function integrates with Firebase and Supabase for authentication:
    1. Validates the system secret
    2. Checks required fields including email (mandatory for Firebase/Supabase validation)
    3. Calls the create_new_api_key service which handles:
       - Firebase authentication (user must exist in Firebase)
       - Supabase integration (user must exist or will be created in Supabase)
       - Local PostgreSQL database updates
    4. Returns appropriate response based on the result
    
    Args:
        data (dict): The request data containing user information
        
    Returns:
        tuple: (response_data, status_code) - The response data and HTTP status code
    """
    from ..models.usage import User
    from ..models.api_key import APIKey
    
    # Validate system secret
    system_secret = Config.SYSTEM_SECRET
    provided_secret = data.get('secret')
    if not system_secret or provided_secret != system_secret:
        return {"error": "Unauthorized", "status_code": 401}, 401

    # Get user data from request
    user_id = data.get('user_id')
    telegram_user_link = data.get('telegram_user_link')
    email = data.get('email')  # Required field for Firebase/Supabase validation
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    username = data.get('username')
    
    # Validate required fields
    if not user_id or not telegram_user_link:
        return {"error": "Missing required fields: user_id and telegram_user_link", "status_code": 400}, 400
    
    # Email is now required for Firebase/Supabase validation
    if not email:
        return {"error": "Missing required field: email is required for authentication", "status_code": 400}, 400
    
    # Get ID if provided (optional)
    id = data.get('id')
    
    # If ID is not provided, partial API key is required
    partial_api_key = data.get('partial_api_key')
    if not id and not partial_api_key:
        return {"error": "Missing required field: partial_api_key is required for authentication when id is not provided", "status_code": 400}, 400

    # Attempt to create or retrieve API key
    try:
        # The updated create_new_api_key function now handles Firebase and Supabase integration
        api_key, status_code, message = create_new_api_key(
            user_id, 
            telegram_user_link, 
            email=email,
            first_name=first_name, 
            last_name=last_name, 
            username=username,
            partial_api_key=partial_api_key,  # Pass partial API key
            id=id  # Pass ID if provided
        )
        
        # Handle different status codes
        if status_code == 200:  # API key already exists
            return {
                "api_key": api_key,
                "message": message,
                "status_code": status_code
            }, status_code
        elif status_code == 201:  # New API key created
            return {
                "api_key": api_key,
                "message": "Store this key securely - it cannot be retrieved later!",
                "status_code": status_code
            }, status_code
        else:  # Other status codes (e.g., 400, 404, 500)
            return {
                "error": message,
                "status_code": status_code
            }, status_code
            
    except Exception as e:
        # Any other exception gets a 500
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

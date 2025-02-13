from flask import Blueprint, request, jsonify, Response, current_app
from .controllers import (
    handle_chat_completion,
    list_models,
    create_api_key,
    get_usage,
)
from ..services.rate_limit_service import rate_limit
from ..services.api_key_service import validate_api_key_header
from functools import wraps

api_blueprint = Blueprint('api', __name__)

def requires_api_key(f):
    """Decorator to validate API key in the Authorization header."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not validate_api_key_header(request):
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_blueprint.route('/chat/completions', methods=['POST'])
@requires_api_key
@rate_limit  # Apply rate limiting
def chat_completions():
    """Handles chat completion requests."""
    data = request.get_json()
    result = handle_chat_completion(data, request)
    if isinstance(result, Response):
        return result
    if isinstance(result, tuple):
        response_data, status = result
        return jsonify(response_data), status
    else:
        return jsonify(result), result.get("status_code", 200)

@api_blueprint.route('/models', methods=['GET', 'POST'])
def models_list():
    """Lists available models."""
    result = list_models()
    if isinstance(result, tuple):
        response_data, status = result
        return jsonify(response_data), status
    return jsonify(result), result.get("status_code", 200)

@api_blueprint.route('/api-keys', methods=['POST'])
def api_keys_create():
    data = request.get_json() or {}
    result = create_api_key(data)
    if isinstance(result, tuple):
        response_data, status_code = result
    else:
        response_data = result
        status_code = result.get("status_code", 200)
    return jsonify(response_data), status_code

@api_blueprint.route('/usage', methods=['POST'])
def usage_details():
    """
    Returns the usage details for a user based on the API key provided in the payload.
    Expected JSON payload:
    {
      "api_key": "your_api_key_here"
    }
    """
    data = request.get_json() or {}
    result = get_usage(data)
    if isinstance(result, tuple):
        response_data, status = result
        return jsonify(response_data), status
    else:
        return jsonify(result), result.get("status_code", 200)

@api_blueprint.route('/uptime/<path:model_id>', methods=['GET'])
def uptime(model_id):
    """
    Checks if the given model is up by sending a minimal streaming chat request.
    
    Example:
      GET /uptime/o3-mini
      GET /uptime/deepseek-ai/DeepSeek-R1
      
    If the model exists (i.e. is supported), the route sends a basic "ping" message
    using chat streaming. If the provider returns a chunk (which implies status 200),
    then the uptime check passes and a 200 response is returned.
    Otherwise, if an error occurs or if no response chunk is found, the error status
    and message are returned.
    """
    # Check if a provider for the model exists
    provider = current_app.provider_manager.select_provider(model_id)
    if not provider:
        return jsonify({"error": f"Model '{model_id}' not supported."}), 404

    # Define a very basic payload for the uptime test.
    test_message = [{"role": "system", "content": "ping"}]

    try:
        # Trigger a chat completion call in streaming mode.
        # Some providers (like Provider3) require the 'app' parameter.
        stream_response = provider.chat_completion(
            model_id,
            test_message,
            stream=True,
            app=current_app  # Only needed if the provider requires this.
        )

        # Attempt to get the first chunk from the streaming generator.
        first_chunk = next(stream_response, None)
        if first_chunk is None:
            return jsonify({"error": "No response received from provider."}), 503

        # If a chunk is received without exception, the model should be up.
        return jsonify({"status": "200 OK"}), 200

    except Exception as e:
        # If the exception has a response attribute (like some requests exceptions),
        # use its status_code; otherwise, default to 500.
        status_code = 500
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
        return jsonify({"error": str(e), "status": status_code}), status_code
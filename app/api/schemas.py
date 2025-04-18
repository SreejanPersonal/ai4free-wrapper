# app/api/schemas.py
from marshmallow import Schema, fields, validate, ValidationError


class AudioSchema(Schema):
    """Schema for audio generation parameters."""
    voice = fields.Str(required=False, validate=validate.OneOf(["alloy", "echo", "fable", "onyx", "nova", "shimmer"]), default="alloy")
    format = fields.Str(required=False, validate=validate.OneOf(["mp3", "opus", "aac", "flac", "wav"]), default="mp3")


class MessageSchema(Schema):
    """Schema for a single chat message."""
    role = fields.Str(required=True, validate=validate.OneOf(["system", "user", "assistant","developer"]))
    content = fields.Str(required=True)

class ChatCompletionRequestSchema(Schema):
    """Schema for chat completion requests."""
    model = fields.Str(required=True)
    messages = fields.List(fields.Nested(MessageSchema), required=True)
    max_tokens = fields.Int(required=False, validate=validate.Range(min=1))
    stream = fields.Bool(required=False, default=False)
    temperature = fields.Float(required=False, validate=validate.Range(min=0.0, max=2.0)) # Added
    top_p = fields.Float(required=False, validate=validate.Range(min=0.0, max=1.0))  # Added
    presence_penalty = fields.Float(required=False, validate=validate.Range(min=-2.0, max=2.0))  # Added
    frequency_penalty = fields.Float(required=False, validate=validate.Range(min=-2.0, max=2.0))  # Added
    modalities = fields.List(fields.Str(validate=validate.OneOf(["text", "audio"])), required=False)
    audio = fields.Nested(AudioSchema, required=False)

class ImageGenerationRequestSchema(Schema):
    """Schema for image generation requests."""
    prompt = fields.Str(required=True)
    n = fields.Int(required=False, validate=validate.Range(min=1, max=10), default=1)
    size = fields.Str(required=False, validate=validate.OneOf(["256x256", "512x512", "1024x1024"]), default="1024x1024")
    response_format = fields.Str(required=False, validate=validate.OneOf(["url", "b64_json"]), default="url")
    
    # Dynamic validation of model based on models.json
    def _get_image_models():
        from ..config import Config
        image_models = []
        for model in Config.ALLOWED_MODELS:
            if model.get("type") == "image":
                image_models.append(model["id"])
        return image_models
    
    model = fields.Str(required=False, validate=validate.OneOf(_get_image_models()), default="Provider-5/flux-pro")

class ModelSchema(Schema):
    """Schema for a single model."""
    id = fields.Str(required=True)
    description = fields.Str(required=False) # Added Description
    provider = fields.Str(required=True)
    max_tokens = fields.Int(required=True)  # Added Max Tokens
    owner_cost_per_million_tokens = fields.Float(required=False)  # Added Cost

class ModelListResponseSchema(Schema):
    """Schema for the model list response."""
    data = fields.List(fields.Nested(ModelSchema))

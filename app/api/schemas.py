# app/api/schemas.py
from marshmallow import Schema, fields, validate, ValidationError


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

class ImageGenerationRequestSchema(Schema):
    """Schema for image generation requests."""
    prompt = fields.Str(required=True)
    n = fields.Int(required=False, validate=validate.Range(min=1, max=10), default=1)
    size = fields.Str(required=False, validate=validate.OneOf(["256x256", "512x512", "1024x1024"]), default="1024x1024")
    response_format = fields.Str(required=False, validate=validate.OneOf(["url", "b64_json"]), default="url")
    model = fields.Str(required=False, validate=validate.OneOf(["flux-pro", "flux-schnell"]), default="flux-pro")

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
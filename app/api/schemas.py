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
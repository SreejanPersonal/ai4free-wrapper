# app/api/utils.py

# This file can contain utility functions specific to the API,
# such as request formatting, header manipulation, etc.
# For now, it's relatively empty, but it's a good place to
# put such functions as your API grows.

def format_model_list(models):
    """
    Formats a list of models into the desired API response format.

    Args:
        models: A list of model dictionaries (as returned by ProviderManager).

    Returns:
        A list of dictionaries in the API response format.
    """
    formatted_models = []
    for model in models:
        formatted_models.append({
            "id": model["id"],
            "description": model.get("description",""), #Added Description
            "provider": model["provider"],
            "max_tokens": model["max_tokens"], #Added Max Tokens
            "owner_cost_per_million_tokens": model.get("owner_cost_per_million_tokens",0)
        })
    return formatted_models
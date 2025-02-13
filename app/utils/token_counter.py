# app/utils/token_counter.py
import tiktoken
import logging
from ..config import Config
from flask import current_app  # Import current_app

log = logging.getLogger(__name__)

def count_tokens(messages, model_id, app):
    """
    Counts the number of tokens in a list of messages.
    """
    with app.app_context(): # Put the context here
        try:

            encoding = tiktoken.get_encoding(Config.TOKEN_ENCODING)
            num_tokens = 0
            for message in messages:
                if isinstance(message, dict):
                    num_tokens += 3
                    for key, value in message.items():
                        if value is None:
                            continue
                        if not isinstance(value, str):
                            value = str(value)
                        try:
                            num_tokens += len(encoding.encode(value))
                        except Exception as e:
                            log.warning(f"Error during token encoding: {e}, Key: {key}, Value: {value}")
                            continue
                        if key == "name":
                            num_tokens -= 1
                elif isinstance(message, str):
                    num_tokens += len(encoding.encode(message))
                else:
                    log.warning(f"Unsupported message type: {type(message)}. Skipping.")
            num_tokens += 3
            return num_tokens
        except Exception as e:
            log.error(f"Token counting error: {e}")
            return 0
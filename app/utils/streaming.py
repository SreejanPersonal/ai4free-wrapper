# app/utils/streaming.py

from flask import Response, current_app
import json
import logging
from ..services.usage_service import record_request
from ..utils.token_counter import count_tokens

log = logging.getLogger(__name__)

def generate_stream(response_generator, user_id, api_key, model_id, app, messages):
    """
    Handles streaming responses with a single application context,
    accumulates the assistant's text to count tokens once after the stream,
    and records usage only at the end.
    """
    # Get initial token count for the prompt messages
    prompt_tokens = count_tokens(messages, model_id, app)
    
    def event_stream():
        accumulated_text = ""
        try:
            # Open a single app context for the entire stream processing.
            with app.app_context():
                for chunk in response_generator:
                    try:
                        # Determine chunk_data from various possible types.
                        if hasattr(chunk, 'model_dump'):
                            chunk_data = chunk.model_dump()
                        elif isinstance(chunk, (str, bytes, bytearray)):
                            try:
                                chunk_data = json.loads(chunk)
                            except json.JSONDecodeError as e:
                                log.error(f"JSON parsing error in chunk: {e}")
                                yield f"data: {json.dumps({'error': 'Invalid JSON in chunk.'})}\n\n"
                                break
                        elif isinstance(chunk, dict):
                            chunk_data = chunk
                        else:
                            log.error(f"Unexpected chunk type: {type(chunk)}. Skipping.")
                            continue

                        # Check if chunk_data is a termination signal.
                        if isinstance(chunk_data, str) and chunk_data.strip() == "[DONE]":
                            break
                        
                        # Remove any 'usage' key to avoid premature usage logging.
                        if isinstance(chunk_data, dict) and "usage" in chunk_data:
                            chunk_data.pop("usage", None)

                        # If there is content in the delta field, accumulate it.
                        if isinstance(chunk_data, dict) and 'choices' in chunk_data:
                            choices = chunk_data.get('choices', [])
                            if choices and isinstance(choices, list) and len(choices) > 0:
                                delta = choices[0].get("delta", {})
                                if isinstance(delta, dict):
                                    content = delta.get("content", "")
                                    if content:
                                        accumulated_text += content
                                        
                        # Yield the processed chunk to the client.
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                        
                    except Exception as e:
                        log.error(f"Error processing chunk: {e}", exc_info=True)
                        yield f"data: {json.dumps({'error': 'Error processing chunk.'})}\n\n"
                        break

                # Once all chunks are processed, count tokens on the final accumulated text.
                final_completion_tokens = count_tokens(
                    [{"role": "assistant", "content": accumulated_text}],
                    model_id,
                    app
                )
                # Record the complete request usage only once.
                record_request(
                    user_id,
                    api_key,
                    model_id,
                    prompt_tokens,
                    final_completion_tokens,
                    {"choices": [{"message": {"content": accumulated_text}}]}
                )
                # Signal the end of streaming.
                yield "data: [DONE]\n\n"
                
        except Exception as e:
            log.error(f"Error in stream generation: {e}", exc_info=True)
            with app.app_context():
                # In case of error, record usage with what we have so far.
                current_token_count = count_tokens(
                    [{"role": "assistant", "content": accumulated_text}],
                    model_id,
                    app
                )
                record_request(
                    user_id,
                    api_key,
                    model_id,
                    prompt_tokens,
                    current_token_count,
                    {"choices": [{"message": {"content": accumulated_text}}]}
                )
            yield f"data: {json.dumps({'error': 'An error occurred during streaming.'})}\n\n"
    
    return Response(event_stream(), mimetype='text/event-stream')
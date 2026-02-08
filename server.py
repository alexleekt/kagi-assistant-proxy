import json
import os
import sys
import time
import uuid

from flask import Flask, Response, jsonify, request, stream_with_context
from lib.auth import KagiSessionManager
from lib.query.query import stream_query

app = Flask(__name__)

kagi_session_key = os.environ.get("KAGI_SESSION_KEY")
if not kagi_session_key:
    print(
        "Need to define your Kagi session key using the environment variable KAGI_SESSION_KEY. See README.md for more info."
    )
    sys.exit(1)
kagi_session_manager = KagiSessionManager()
kagi_session_manager.set_session_key(kagi_session_key)

# Model mapping from OpenAI models to Kagi models
MODEL_MAPPING = {
    "openai/gpt-5-mini": "gpt-5-mini",
    "openai/gpt-oss-120b": "gpt-oss-120b",
    "moonshotai/kimi-k2.5": "kimi-k2-5",
}

# Default model, set to the first listed in MODEL_MAPPING
DEFAULT_MODEL = list(MODEL_MAPPING.keys())[0]


def create_chat_completion_chunk(content, finish_reason=None):
    """Create a chat completion chunk in OpenAI format"""
    chunk = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": request.json.get("model", MODEL_MAPPING.get(DEFAULT_MODEL)),
        "choices": [{"index": 0, "delta": {}, "finish_reason": finish_reason}],
    }

    if content is not None:
        chunk["choices"][0]["delta"]["content"] = content

    return chunk


def create_chat_completion(content, model):
    """Create a non-streaming chat completion response in OpenAI format"""
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": -1,  # We don't have token counts from Kagi
            "completion_tokens": -1,
            "total_tokens": -1,
        },
    }


def convert_messages_to_prompt(messages):
    """Convert OpenAI messages format to a single prompt string"""
    prompt_parts = []

    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")

        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")

    return "\n\n".join(prompt_parts)


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    try:
        # Get request data
        data = request.get_json()

        # Validate required fields
        messages = data.get("messages", [])
        if not messages:
            return jsonify(
                {
                    "error": {
                        "message": "messages is required",
                        "type": "invalid_request_error",
                        "code": "missing_required_parameter",
                    }
                }
            ), 400

        # Get model and map it to Kagi model
        requested_model = data.get("model", DEFAULT_MODEL)
        kagi_model = MODEL_MAPPING.get(requested_model, DEFAULT_MODEL)

        # Convert messages to prompt
        prompt = convert_messages_to_prompt(messages)

        # Check if streaming is requested
        stream = data.get("stream", False)

        if stream:

            def generate():
                try:
                    # Send initial chunk with role
                    initial_chunk = create_chat_completion_chunk("")
                    initial_chunk["choices"][0]["delta"]["role"] = "assistant"
                    yield f"data: {json.dumps(initial_chunk)}\n\n"

                    # Stream content from Kagi
                    full_content = ""
                    for chunk in stream_query(prompt, kagi_model):
                        # Parse the SSE data
                        if chunk.startswith("data: "):
                            chunk_data = json.loads(chunk[6:])

                            if chunk_data.get("type") == "token":
                                content = chunk_data.get("content", "")
                                full_content += content
                                response_chunk = create_chat_completion_chunk(content)
                                yield f"data: {json.dumps(response_chunk)}\n\n"

                            elif chunk_data.get("type") == "done":
                                # Send final chunk
                                final_chunk = create_chat_completion_chunk(None, "stop")
                                yield f"data: {json.dumps(final_chunk)}\n\n"
                                yield "data: [DONE]\n\n"
                                break

                            elif chunk_data.get("error"):
                                error_response = {
                                    "error": {
                                        "message": chunk_data.get("error"),
                                        "type": "api_error",
                                        "code": "internal_error",
                                    }
                                }
                                yield f"data: {json.dumps(error_response)}\n\n"
                                break

                except Exception as e:
                    raise
                    # error_response = {
                    #     'error': {
                    #         'message': str(e),
                    #         'type': 'api_error',
                    #         'code': 'internal_error'
                    #     }
                    # }
                    # yield f"data: {json.dumps(error_response)}\n\n"

            return Response(
                stream_with_context(generate()),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )

        else:
            # Non-streaming response
            full_content = ""
            for chunk in stream_query(prompt, kagi_model):
                if chunk.startswith("data: "):
                    chunk_data = json.loads(chunk[6:])

                    if chunk_data.get("type") == "token":
                        full_content += chunk_data.get("content", "")

                    elif chunk_data.get("type") == "final":
                        full_content = chunk_data.get("content", "")

                    elif chunk_data.get("error"):
                        print(chunk_data)
                        # return jsonify({
                        #     'error': {
                        #         'message': chunk_data.get('error'),
                        #         'type': 'api_error',
                        #         'code': 'internal_error'
                        #     }
                        # }), 500

            return jsonify(create_chat_completion(full_content, requested_model))

    except Exception as e:
        raise
        # return jsonify({
        #     'error': {
        #         'message': str(e),
        #         'type': 'api_error',
        #         'code': 'internal_error'
        #     }
        # }), 500


@app.route("/v1/models", methods=["GET"])
def list_models():
    """List available models in OpenAI format"""
    models = [
        {
            "id": model_id,
            "object": "model",
            "created": 1677532384,
            "owned_by": "kagi-proxy",
        }
        for model_id in MODEL_MAPPING.keys()
    ]
    models = sorted(models, key=lambda m: m["id"])
    return jsonify({"object": "list", "data": models})


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

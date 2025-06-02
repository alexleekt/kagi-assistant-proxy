import json
import logging

import requests

from lib.auth import KagiSessionManager
from lib.headers import DEFAULT_HEADERS
from lib.query.parse import parse_kagi_sse_stream

_logger = logging.getLogger('SERVER').getChild('STREAM')

_kagi_session_manager = KagiSessionManager()


def stream_query(prompt: str, model: str):
    print(prompt)

    headers = DEFAULT_HEADERS.copy()
    headers['accept'] = 'application/vnd.kagi.stream'

    data = {
        "focus": {
            "thread_id": None,
            "branch_id": "00000000-0000-4000-0000-000000000000",
            "prompt": prompt,
        },
        "profile": {
            "id": None,
            "personalizations": True,
            "internet_access": True,
            "model": model,
            "lens_id": None
        }
    }

    cookies = {
        'kagi_session': _kagi_session_manager.get_session_key(),
    }

    thread_id = None
    try:
        response = requests.post('https://kagi.com/assistant/prompt', cookies=cookies, headers=headers, json=data, stream=True)

        if response.status_code == 404:
            yield f"data: {json.dumps({'error': f'Error: invalid session key', 'details': None})}\n\n"
            return
        elif response.status_code != 200:
            yield f"data: {json.dumps({'error': f'Error: {response.status_code}', 'details': response.text})}\n\n"
            return

        # The session key appears to rotate so we need to update it on each request
        set_cookie_header = response.headers.get('set-cookie')
        if set_cookie_header and 'kagi_session' in set_cookie_header:
            p1 = set_cookie_header.split('kagi_session=')
            if len(p1) == 2:
                p2 = p1[1].split(';')
                if len(p2) > 2:
                    new_session_key = p2[0]
                    _kagi_session_manager.set_session_key(new_session_key)

        for line in response.iter_lines():
            message = parse_kagi_sse_stream(line)
            if not message:
                continue

            if message['type'] == 'new_message_json' and message['state'] == 'done':
                # Send the final message
                yield f"data: {json.dumps({'type': 'final', 'content': message['reply']})}\n\n"

            if message['type'] == 'tokens_json':
                # Stream the tokens as they come
                yield f"data: {json.dumps({'type': 'token', 'content': message['text']})}\n\n"
            elif message['type'] == 'thread_json':
                # Save the thread ID
                thread_id = message['data']['id']

        # Delete the thread
        if thread_id:
            try:
                requests.post('https://kagi.com/assistant/thread_delete', headers=DEFAULT_HEADERS, cookies=cookies, json={"focus": {"thread_id": thread_id}})
            except Exception as e:
                # Log the error but don't fail the request
                _logger.error(f"Failed to delete thread {thread_id}: {e}")

            # Send a completion signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

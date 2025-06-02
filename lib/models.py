import json
from typing import List, Dict

import requests

from lib.headers import DEFAULT_HEADERS


def get_models(session_key: str) -> List[Dict[str, str]]:
    headers = DEFAULT_HEADERS.copy()
    headers['Accept'] = 'application/vnd.kagi.stream'
    response = requests.post('https://kagi.com/assistant/profile_list', headers=headers,
                             cookies={'kagi_session': session_key}, json={})
    response.raise_for_status()
    models = json.loads(response.text.split('profiles.json:')[1].strip('\x00\n'))['profiles']
    return models

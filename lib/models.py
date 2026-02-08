# kagi-assistant-proxy - A proxy that exposes Kagi's LLM platform
# Copyright (C) 2024-2025  Cyberes, Alex Lee
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
from typing import Dict, List

import requests

from lib.headers import DEFAULT_HEADERS


def get_models(session_key: str) -> List[Dict[str, str]]:
    headers = DEFAULT_HEADERS.copy()
    headers["Accept"] = "application/vnd.kagi.stream"
    response = requests.post(
        "https://kagi.com/assistant/profile_list",
        headers=headers,
        cookies={"kagi_session": session_key},
        json={},
    )
    response.raise_for_status()
    models = json.loads(response.text.split("profiles.json:")[1].strip("\x00\n"))[
        "profiles"
    ]
    return models

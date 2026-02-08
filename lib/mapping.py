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

import html
import json
import logging
from typing import Any

import requests
from bs4 import BeautifulSoup

from lib.auth import KagiSessionManager
from lib.headers import DEFAULT_HEADERS

_logger = logging.getLogger("MAPPING")

# Provider mapping from Kagi's internal names to OpenAI-compatible format
PROVIDER_MAPPING = {
    "openai": "openai",
    "moonshot": "moonshotai",
    "zai": "zai",
    "kagi": "kagi",
    "anthropic": "anthropic",
    "qwen": "qwen",
    "deepseek": "deepseek",
    "google": "google",
    "meta": "meta",
    "xai": "xai",
    "mistral": "mistral",
    "nousresearch": "nousresearch",
}

# Model name sanitization mapping
MODEL_NAME_OVERRIDES = {
    "moonshot/kimi-k2.5": "moonshotai/kimi-k2.5",
}


def get_latest_model_mapping() -> dict[str, str]:
    """
    Fetch the latest model mapping from Kagi's assistant page.

    Scrapes https://kagi.com/assistant/ and extracts model information
    from the json-profile-list div.

    Returns:
        dict[str, str]: Mapping of OpenAI-compatible model IDs to Kagi model IDs.

    Raises:
        Exception: If the request fails or parsing fails.
    """
    session_manager = KagiSessionManager()
    session_key = session_manager.get_session_key()

    if not session_key:
        raise ValueError("No KAGI_SESSION_KEY set. Cannot fetch model mapping.")

    headers = {
        **DEFAULT_HEADERS,
        "cookie": f"kagi_session={session_key}",
    }

    try:
        response = requests.get(
            "https://kagi.com/assistant/",
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
    except Exception as e:
        _logger.error(f"Failed to fetch Kagi assistant page: {e}")
        raise

    soup = BeautifulSoup(response.text, "html.parser")
    profile_list_div = soup.find("div", {"id": "json-profile-list"})

    if not profile_list_div:
        raise ValueError("Could not find json-profile-list div in response")

    # Decode HTML entities and parse JSON
    json_str = html.unescape(profile_list_div.get_text())
    data: dict[str, Any] = json.loads(json_str)

    profiles = data.get("profiles", [])
    mapping: dict[str, str] = {}

    for profile in profiles:
        # Skip models the user doesn't have access to
        if not profile.get("accessible", False):
            continue

        kagi_model_id = profile.get("model")
        provider = profile.get("model_provider")
        model_name = profile.get("model_name", "").lower().replace(" ", "-")

        if not kagi_model_id or not provider:
            continue

        # Map provider to OpenAI-compatible format
        openai_provider = PROVIDER_MAPPING.get(provider, provider)

        # Build OpenAI-compatible model ID
        openai_model_id = f"{openai_provider}/{model_name}"

        # Apply any name overrides
        openai_model_id = MODEL_NAME_OVERRIDES.get(openai_model_id, openai_model_id)

        mapping[openai_model_id] = kagi_model_id

    _logger.info(f"Fetched {len(mapping)} models from Kagi")
    return mapping


# Default model to use when fetching fails
DEFAULT_MODEL = "openai/gpt-5-mini"

# Initialize MODEL_MAPPING by fetching from Kagi
# Falls back to empty dict if fetching fails (will be retried at runtime)
try:
    MODEL_MAPPING = get_latest_model_mapping()
except Exception:
    MODEL_MAPPING = {}

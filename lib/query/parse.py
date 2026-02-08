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

# Whitelist of known valid tags from Kagi SSE stream
VALID_TAGS = {
    "hi",
    "thread_list.html",
    "thread.html",
    "thread_list.json",
    "thread.json",
    "messages.json",
    "new_message.json",
    "tokens.json",
}


def parse_kagi_sse_stream(line: bytes):
    """Parse a single line from Kagi SSE stream response."""
    if not line:
        return None

    # Decode the line and remove null terminator
    line_str = line.decode("utf-8").rstrip("\x00")

    if not line_str:
        return None

    # Split on first colon to separate tag from payload
    parts = line_str.split(":", 1)
    if len(parts) != 2:
        # Non-JSON data such as the threads list HTML
        return None

    tag, payload = parts

    # Only process whitelisted tags - everything else is ignored
    if tag not in VALID_TAGS:
        return None

    try:
        if tag == "hi":
            # hi payload is already JSON
            data = json.loads(payload)
            return {"type": "hi", "data": data, "trace": data.get("trace")}

        elif tag == "thread_list.html":
            # HTML content is raw, not JSON
            return {"type": "thread_list_html", "data": payload}

        elif tag == "thread.html":
            # HTML content is raw, not JSON
            return {"type": "thread_html", "data": payload}

        elif tag == "thread_list.json":
            return {"type": "thread_list_json", "data": json.loads(payload)}

        elif tag == "thread.json":
            return {"type": "thread_json", "data": json.loads(payload)}

        elif tag == "messages.json":
            return {"type": "messages_json", "data": json.loads(payload)}

        elif tag == "new_message.json":
            message_data = json.loads(payload)
            return {
                "type": "new_message_json",
                "data": message_data,
                "state": message_data.get("state"),
                "reply": message_data.get("reply"),
                "md": message_data.get("md"),
            }

        elif tag == "tokens.json":
            token_data = json.loads(payload)
            return {
                "type": "tokens_json",
                "data": token_data,
                "text": token_data.get("text"),
                "id": token_data.get("id"),
            }
        else:
            raise Exception(f"Unknown tag: {tag}\n{line_str}")

    except json.JSONDecodeError as e:
        raise Exception(
            f"Failed to parse JSON for tag '{tag}': {e}\nRaw payload: {payload}"
        )

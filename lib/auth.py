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

import threading
from datetime import datetime
from typing import Any, Optional


class KagiSessionManager:
    """
    Thread-safe session manager for Kagi session keys.
    Ensures consistent session data across all threads.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern to ensure single instance across threads."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the session manager (only once)."""
        if self._initialized:
            return

        with self._lock:
            if not self._initialized:
                self._session_key: Optional[str] = None
                self._session_data: dict[str, Any] = {}
                self._last_updated: Optional[datetime] = None
                self._session_lock = (
                    threading.RLock()
                )  # Reentrant lock for session operations
                self._initialized = True

    def get_session_key(self) -> Optional[str]:
        """
        Get the current session key.
        Thread-safe getter for session key.

        Returns:
            Optional[str]: The current session key or None if not set
        """
        with self._session_lock:
            return self._session_key

    def set_session_key(self, key: str) -> None:
        """
        Set the session key.
        Thread-safe setter for session key.

        Args:
            key (str): The new session key
        """
        with self._session_lock:
            self._session_key = key
            self._last_updated = datetime.now()

    def get_last_updated(self) -> Optional[datetime]:
        """
        Get the timestamp of last session key update.

        Returns:
            Optional[datetime]: Last update timestamp or None
        """
        with self._session_lock:
            return self._last_updated

    def __repr__(self) -> str:
        """String representation of the session manager."""
        with self._session_lock:
            return (
                f"KagiSessionManager(has_key={self._session_key is not None}, "
                f"last_updated={self._last_updated})"
            )

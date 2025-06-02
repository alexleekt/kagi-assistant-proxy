import threading
from datetime import datetime
from typing import Optional, Any


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
                self._session_lock = threading.RLock()  # Reentrant lock for session operations
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
            return (f"KagiSessionManager(has_key={self._session_key is not None}, "
                    f"last_updated={self._last_updated})")

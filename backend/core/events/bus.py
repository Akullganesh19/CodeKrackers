import asyncio
import logging
from typing import Callable, Any, Dict, List

logger = logging.getLogger("vas.event_bus")

class EventBus:
    """
    In-memory event bus for loosely coupled cross-system communication.
    Synapse: Facilitates emergent intelligence by letting isolated systems share data.
    """
    _instance = None
    _listeners: Dict[str, List[Callable]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._listeners = {}
        return cls._instance

    def on(self, event_name: str, callback: Callable):
        """Register a listener for an event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def emit(self, event_name: str, payload: Any):
        """Emit an event to all registered listeners asynchronously."""
        if event_name in self._listeners:
            logger.info(f"EventBus Emitting: {event_name} to {len(self._listeners[event_name])} listeners")
            for callback in self._listeners[event_name]:
                asyncio.create_task(self._execute_callback(callback, payload, event_name))

    async def _execute_callback(self, callback: Callable, payload: Any, event_name: str):
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(payload)
            else:
                callback(payload)
        except Exception as e:
            logger.error(f"Error in EventBus listener for {event_name}: {e}")

event_bus = EventBus()

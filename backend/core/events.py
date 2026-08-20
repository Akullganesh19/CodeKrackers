from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger("vas.events")

class EventEmitter:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event_name: str, callback: Callable) -> None:
        """Register a listener for an event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def emit(self, event_name: str, **kwargs: Any) -> None:
        """Emit an event to all registered listeners."""
        if event_name in self._listeners:
            logger.info(f"Event emitted: {event_name} (Firing {len(self._listeners[event_name])} listeners)")
            for callback in self._listeners[event_name]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_name}: {e}")
        else:
            logger.debug(f"Event emitted: {event_name} (No listeners)")

# Global event bus
event_bus = EventEmitter()

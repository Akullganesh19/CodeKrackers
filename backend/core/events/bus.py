"""
In-memory Event Bus for loosely coupled inter-system communication.
Allows components to emit and listen for events without tight coupling.
"""
import asyncio
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger("vas.events")

class EventBus:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Register a callback for an event type."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}. Total listeners: {len(self.listeners[event_type])}")

    def publish(self, event_type: str, **kwargs: Any) -> None:
        """Emit an event, executing all registered callbacks as background tasks."""
        if event_type not in self.listeners:
            logger.debug(f"Event {event_type} published but has no listeners.")
            return

        logger.debug(f"Publishing event {event_type} to {len(self.listeners[event_type])} listeners.")
        for callback in self.listeners[event_type]:
            # Execute async callbacks in the background
            if asyncio.iscoroutinefunction(callback):
                asyncio.create_task(callback(event_type, **kwargs))
            else:
                # Still handle sync callbacks if any, though async is preferred
                try:
                    callback(event_type, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing sync callback for {event_type}: {e}")

event_bus = EventBus()

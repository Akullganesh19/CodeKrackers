import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger("vas.events")

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def publish(self, event_name: str, payload: Any):
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(payload))
                    else:
                        callback(payload)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_name}: {e}")

event_bus = EventBus()

from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger("vas.events")

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed to {event_type}")

    def emit(self, event_type: str, payload: Any = None):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(payload)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_type}: {e}")
        else:
            logger.debug(f"No subscribers for {event_type}")

event_bus = EventBus()

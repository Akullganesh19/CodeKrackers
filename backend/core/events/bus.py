import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger("vas.events")


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable) -> None:
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)
        logger.debug(f"Subscribed to {event_name}")

    def publish(self, event_name: str, **kwargs: Any) -> None:
        if event_name not in self._subscribers:
            return

        for callback in self._subscribers[event_name]:
            try:
                callback(**kwargs)
            except Exception as e:
                logger.error(f"Error in event listener for {event_name}: {e}")


bus = EventBus()

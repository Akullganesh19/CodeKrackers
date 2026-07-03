import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger("vas.events")

class EventBus:
    _listeners: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: str, listener: Callable):
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        cls._listeners[event_type].append(listener)
        logger.info(f"Subscribed to {event_type}")

    @classmethod
    def publish(cls, event_type: str, **kwargs):
        if event_type in cls._listeners:
            logger.info(f"Publishing event {event_type} to {len(cls._listeners[event_type])} listeners")
            for listener in cls._listeners[event_type]:
                try:
                    listener(**kwargs)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_type}: {str(e)}")

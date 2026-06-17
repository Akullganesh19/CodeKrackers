import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger("vas.event_bus")

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[..., Any]]] = {}

    def subscribe(self, event_type: str, callback: Callable[..., Any]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscribed to {event_type}: {callback.__name__}")

    def publish(self, event_type: str, *args, **kwargs):
        logger.info(f"EventBus publishing: {event_type}")
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(*args, **kwargs))
                else:
                    try:
                        callback(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Event handler error in {callback.__name__}: {e}")

event_bus = EventBus()

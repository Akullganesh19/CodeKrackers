import collections
from typing import Callable, Any

class EventBus:
    def __init__(self):
        self._subscribers = collections.defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable[..., Any]):
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, *args, **kwargs):
        import asyncio
        for callback in self._subscribers[event_type]:
            if asyncio.iscoroutinefunction(callback):
                asyncio.create_task(callback(*args, **kwargs))
            else:
                callback(*args, **kwargs)

# Global instance
event_bus = EventBus()

import asyncio
import logging
from typing import Callable, Dict, List

logger = logging.getLogger("vas.events")


class EventBus:
    _instance = None
    _background_tasks = set()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.subscribers: Dict[str, List[Callable]] = {}
        return cls._instance

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")

    def publish(self, event_type: str, **kwargs):
        if event_type not in self.subscribers:
            return

        for callback in self.subscribers[event_type]:
            if asyncio.iscoroutinefunction(callback):
                try:
                    loop = asyncio.get_running_loop()
                    task = loop.create_task(callback(**kwargs))
                    self._background_tasks.add(task)
                    task.add_done_callback(self._background_tasks.discard)
                except RuntimeError:
                    # No running event loop, execute sync
                    asyncio.run(callback(**kwargs))
            else:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(
                        f"Error in sync event handler for {event_type}: {e}",
                        exc_info=True,
                    )


bus = EventBus()

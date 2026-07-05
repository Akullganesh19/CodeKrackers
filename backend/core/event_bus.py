import asyncio
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger("vas.event_bus")


class EventBus:
    _instance = None
    _subscribers: Dict[str, List[Callable]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._subscribers = {}
        return cls._instance

    @classmethod
    def subscribe(cls, event_type: str, callback: Callable):
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")

    @classmethod
    def publish(cls, event_type: str, **kwargs):
        if event_type not in cls._subscribers:
            return

        for callback in cls._subscribers[event_type]:
            try:
                # Run the callback gracefully
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(cls._run_async(callback, **kwargs))
                else:
                    callback(**kwargs)
            except Exception as e:
                logger.error(
                    f"Error in event listener for {event_type}: {e}", exc_info=True
                )

    @staticmethod
    async def _run_async(callback: Callable, **kwargs):
        try:
            await callback(**kwargs)
        except Exception as e:
            logger.error(f"Error in async event listener: {e}", exc_info=True)


event_bus = EventBus()

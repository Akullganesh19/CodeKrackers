"""
Central EventBus for loose coupling between backend systems.
"""
import asyncio
import logging

logger = logging.getLogger("vas.events")

class EventBus:
    def __init__(self):
        self._listeners = {}

    def on(self, event_type: str, listener):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
        logger.debug("Registered listener for event %s", event_type)

    async def emit(self, event_type: str, *args, **kwargs):
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(*args, **kwargs)
                    else:
                        listener(*args, **kwargs)
                except Exception as e:
                    logger.error("Error in event listener for %s: %s", event_type, e)

event_bus = EventBus()

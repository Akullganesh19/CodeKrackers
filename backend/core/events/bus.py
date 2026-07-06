import logging

logger = logging.getLogger("vas.events")

class EventBus:
    _listeners = {}

    @classmethod
    def subscribe(cls, event_type: str, listener):
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        cls._listeners[event_type].append(listener)

    @classmethod
    def publish(cls, event_type: str, data: dict):
        for listener in cls._listeners.get(event_type, []):
            try:
                listener(data)
            except Exception as e:
                logger.error(f"EventBus listener failed for {event_type}: {e}")

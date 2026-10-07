from abc import ABC

from app.application.entities.event import NewEventEntity


class IEventRepository(ABC):
    async def create(self, new_event: NewEventEntity):
        pass

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.entities.event import NewEventEntity
from app.application.interfaces.event_repository import IEventRepository
from app.infrastructure.db.models.outbox_event import OutboxEvent
from app.repositories.common.err import translate_db_exceptions


class EventRepository(IEventRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    @translate_db_exceptions
    async def create(
            self,
            new_event: NewEventEntity
    ):
        query = (
            insert(OutboxEvent)
            .values({
                OutboxEvent.id: new_event.id,
                OutboxEvent.event_type: new_event.event_type,
                OutboxEvent.payload: new_event.payload.serialize(),
                OutboxEvent.created_at: new_event.created_at
            })
        )
        await self._db_session.execute(query)

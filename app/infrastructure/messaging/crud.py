from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.enums import PaymentStatusEnum, EventTypeEnum
from app.infrastructure.db.models.outbox_event import OutboxEvent
from app.infrastructure.db.models.payment import Payment


async def get_events_batch(db_session: AsyncSession,
                           event_type: EventTypeEnum,
                           limit: int) -> list[OutboxEvent]:
    query = (
        select(OutboxEvent)
        .where(OutboxEvent.processed_at.is_(None) &
               (OutboxEvent.event_type == event_type))
        .order_by(OutboxEvent.created_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    )
    messages = (await db_session.execute(query)).scalars().all()
    return list(messages)


async def mark_published(db_session: AsyncSession,
                         msg_ids: list[UUID],
                         dt: datetime | None = None):
    if dt is None:
        dt = datetime.now(UTC)
    query = (
        update(OutboxEvent)
        .values({
            OutboxEvent.processed_at: dt
        })
        .where(OutboxEvent.id.in_(msg_ids))
    )
    await db_session.execute(query)


async def update_payment_status(db_session: AsyncSession,
                                payment_id: UUID,
                                new_status: PaymentStatusEnum,
                                dt: datetime | None = None) -> Payment | None:
    if dt is None:
        dt = datetime.now(UTC)
    query = (
        update(Payment)
        .values({
            Payment.status: new_status,
            Payment.processed_at: dt
        })
        .where((Payment.id == payment_id) & Payment.processed_at.is_(None))
        .returning(Payment)
    )
    return (await db_session.execute(query)).scalar_one_or_none()


async def get_payment(
        db_session: AsyncSession,
        payment_id: UUID
) -> Payment | None:
    query = (
        select(Payment)
        .where(Payment.id == payment_id)
    )
    return (await db_session.execute(query)).scalar_one_or_none()

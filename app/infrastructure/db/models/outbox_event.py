from datetime import datetime
from uuid import UUID

from sqlalchemy import func, CheckConstraint, Index, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.application.enums import EventTypeEnum
from app.infrastructure.db.core.base import Base
from app.infrastructure.db.core.custom_types import EnumString
from app.infrastructure.db.tools import get_enum_values_string


class OutboxEvent(Base):
    __tablename__ = 'outbox_events'

    id: Mapped[UUID] = \
        mapped_column(primary_key=True, server_default=func.uuidv7())

    event_type: Mapped[EventTypeEnum] = mapped_column(EnumString(EventTypeEnum))
    payload: Mapped[dict] = mapped_column(JSONB())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            f'event_type IN ({get_enum_values_string(EventTypeEnum)})',
            'ck_outbox_events_event_type'
        ),
        Index('ix_outbox_events_processed_at_event_type_created_at',
              processed_at,
              event_type,
              created_at,
              postgresql_where=processed_at.is_(None))
    )

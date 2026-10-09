from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID, uuid7 # type: ignore

from app.application.enums import EventTypeEnum


class IEventPayload(ABC):
    @abstractmethod
    def serialize(self) -> Any:
        pass


@dataclass(kw_only=True)
class PaymentCreatedEventPayload(IEventPayload):
    event_type: EventTypeEnum
    payment_id: UUID
    event_id: UUID

    def serialize(self) -> dict:
        return {
            'event_type': self.event_type.value,
            'event_id': str(self.event_id),
            'payment_id': str(self.payment_id)
        }


@dataclass(slots=True, kw_only=True)
class NewEventEntity:
    id: UUID
    event_type: EventTypeEnum
    payload: IEventPayload
    created_at: datetime

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.application.entities.payment import PaymentEntity
from app.application.enums import PaymentStatusEnum


class CreatedPaymentResponseSchemaV1(BaseModel):
    payment_id: UUID
    status: PaymentStatusEnum
    created_at: datetime

    @classmethod
    def from_entity(cls, entity: PaymentEntity):
        return cls(
            payment_id=entity.id,
            status=entity.status,
            created_at=entity.created_at
        )

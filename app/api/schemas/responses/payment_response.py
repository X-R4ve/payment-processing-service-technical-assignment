from datetime import datetime
from decimal import Decimal
from typing import Self, Any
from uuid import UUID

from pydantic import BaseModel

from app.application.entities.payment import PaymentEntity
from app.application.enums import CurrencyEnum, PaymentStatusEnum


class PaymentResponseSchemaV1(BaseModel):
    payment_id: UUID
    amount: Decimal
    currency: CurrencyEnum
    description: str | None
    metadata: dict[str, Any]
    webhook_url: str
    status: PaymentStatusEnum
    created_at: datetime
    processed_at: datetime | None

    @classmethod
    def from_entity(cls, entity: PaymentEntity) -> Self:
        return cls(
            payment_id=entity.id,
            amount=entity.amount,
            currency=entity.currency,
            description=entity.description,
            metadata=entity.metadata,
            webhook_url=entity.webhook_url,
            status=entity.status,
            created_at=entity.created_at,
            processed_at=entity.processed_at
        )

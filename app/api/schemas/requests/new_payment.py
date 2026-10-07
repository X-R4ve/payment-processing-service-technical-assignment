from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from app.application.entities.payment import NewPaymentEntity
from app.application.enums import CurrencyEnum


class NewPaymentRequestSchemaV1(BaseModel):
    amount: Decimal = Field(..., ge=0)
    currency: CurrencyEnum
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    webhook_url: HttpUrl

    def to_entity(self) -> NewPaymentEntity:
        return NewPaymentEntity(
            amount=self.amount,
            currency=self.currency,
            description=self.description,
            metadata=self.metadata,
            webhook_url=str(self.webhook_url)
        )

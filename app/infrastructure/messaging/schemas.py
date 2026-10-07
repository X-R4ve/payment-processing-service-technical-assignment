from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, HttpUrl

from app.application.enums import CurrencyEnum, EventTypeEnum, PaymentStatusEnum


class PaymentCreatedMessageSchema(BaseModel):
    event_type: EventTypeEnum
    event_id: UUID
    payment_id: UUID


class WebhookBodySchema(BaseModel):
    event_type: EventTypeEnum
    event_id: UUID
    payment_id: UUID
    amount: Decimal
    currency: CurrencyEnum
    status: PaymentStatusEnum
    processed_at: datetime

from dataclasses import dataclass, field
from datetime import datetime, UTC
from decimal import Decimal
from hashlib import sha256
from uuid import UUID

from ..enums import CurrencyEnum, PaymentStatusEnum


@dataclass(slots=True, kw_only=True)
class NewPaymentEntity:
    amount: Decimal
    currency: CurrencyEnum
    description: str
    metadata: dict
    webhook_url: str
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def compute_hash(self) -> str:
        payload_string = (f'{self.amount}:'
                          f'{self.currency.value}:'
                          f'{self.description}:'
                          f'{str(self.metadata)}:'
                          f'{self.webhook_url}')
        return sha256(payload_string.encode()).hexdigest()


@dataclass(slots=True, kw_only=True)
class PaymentEntity:
    id: UUID
    amount: Decimal
    currency: CurrencyEnum
    description: str | None
    metadata: dict
    webhook_url: str
    status: PaymentStatusEnum
    created_at: datetime
    processed_at: datetime | None

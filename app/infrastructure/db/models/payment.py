from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import JSON, CheckConstraint, func, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.application.entities.payment import PaymentEntity
from app.application.enums import CurrencyEnum, PaymentStatusEnum
from app.infrastructure.db.core.base import Base
from app.infrastructure.db.core.custom_types import EnumString
from app.infrastructure.db.tools import get_enum_values_string


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[UUID] = \
        mapped_column(primary_key=True, server_default=func.uuidv7())

    amount: Mapped[Decimal] = mapped_column()
    currency: Mapped[CurrencyEnum] = mapped_column(EnumString(CurrencyEnum))
    description: Mapped[str | None] = mapped_column()
    payment_metadata: Mapped[dict] = mapped_column(JSON())
    status: Mapped[PaymentStatusEnum] = mapped_column(EnumString(PaymentStatusEnum))
    idempotency_key: Mapped[str] = mapped_column()
    webhook_url: Mapped[str] = mapped_column()
    hash: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            f'currency IN ({get_enum_values_string(CurrencyEnum)})',
            'ck_payments_currency'
        ),
        CheckConstraint(
            f'status IN ({get_enum_values_string(PaymentStatusEnum)})',
            'ck_payments_status'
        ),
        Index('ix_payments_idempotency_key',
              idempotency_key,
              unique=True),
    )

    def to_entity(self) -> PaymentEntity:
        return PaymentEntity(
            id=self.id,
            amount=self.amount,
            currency=self.currency,
            description=self.description,
            metadata=self.payment_metadata,
            status=self.status,
            webhook_url=self.webhook_url,
            created_at=self.created_at,
            processed_at=self.processed_at
        )

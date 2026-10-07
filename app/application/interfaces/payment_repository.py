from abc import ABC, abstractmethod
from uuid import UUID

from ..entities.payment import NewPaymentEntity, PaymentEntity


class IPaymentRepository(ABC):
    @abstractmethod
    async def create_payment(
            self,
            new_payment: NewPaymentEntity,
            idempotency_key: str,
            hash_: str
    ) -> tuple[PaymentEntity, bool]:
        pass

    @abstractmethod
    async def get_payment_by_id(
            self,
            payment_id: UUID
    ) -> PaymentEntity:
        pass

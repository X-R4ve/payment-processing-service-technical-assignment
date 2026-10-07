from uuid import UUID

from ..entities.payment import PaymentEntity
from ..interfaces.payment_repository import IPaymentRepository


class GetPaymentInfoUseCase:
    def __init__(self, payment_repository: IPaymentRepository):
        self._payment_repo = payment_repository

    async def execute(self, payment_id: UUID) -> PaymentEntity:
        return await self._payment_repo.get_payment_by_id(payment_id=payment_id)

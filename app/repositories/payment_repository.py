from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.entities.payment import PaymentEntity, NewPaymentEntity
from app.application.err import BaseError
from app.application.interfaces.payment_repository import IPaymentRepository
from app.infrastructure.db.models.payment import Payment
from app.repositories.common.err import translate_db_exceptions


class PaymentRepository(IPaymentRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    @translate_db_exceptions
    async def create_payment(
            self,
            new_payment: NewPaymentEntity,
            idempotency_key: str,
            hash_: str
    ) -> tuple[PaymentEntity, bool]:
        query = (
            insert(Payment)
            .on_conflict_do_nothing(index_elements=[Payment.idempotency_key])
            .values({
                Payment.amount: new_payment.amount,
                Payment.currency: new_payment.currency,
                Payment.description: new_payment.description,
                Payment.payment_metadata: new_payment.metadata,
                Payment.status: new_payment.status,
                Payment.idempotency_key: idempotency_key,
                Payment.created_at: new_payment.created_at,
                Payment.webhook_url: new_payment.webhook_url,
                Payment.hash: hash_
            })
            .returning(Payment)
        )
        created_payment: Payment | None = (
            await self._db_session.execute(query)
        ).scalar_one_or_none()

        if created_payment is None:
            is_new = False
            payment_orm = await self._get_payment_orm_by_idempotency_key(
                idempotency_key=idempotency_key
            )
            if payment_orm.hash != hash_:
                raise BaseError(code=409,
                                err='conflict',
                                reason='existing payment hash mismatch')
            payment = payment_orm.to_entity()
        else:
            is_new = True
            payment = created_payment.to_entity()
        return payment, is_new

    async def _get_payment_orm_by_idempotency_key(
            self, idempotency_key: str
    ) -> Payment:
        query = (
            select(Payment)
            .where(Payment.idempotency_key == idempotency_key)
        )
        payment: Payment = (await self._db_session.execute(query)).scalar_one()
        return payment

    @translate_db_exceptions
    async def get_payment_by_id(
            self,
            payment_id: UUID
    ) -> PaymentEntity:
        query = select(Payment).where(Payment.id == payment_id)
        payment: Payment = (await self._db_session.execute(query)).scalar_one()
        return payment.to_entity()

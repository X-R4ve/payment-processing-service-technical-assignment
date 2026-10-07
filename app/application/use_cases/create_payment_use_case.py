from uuid import uuid7 # type: ignore

from ..entities.event import NewEventEntity, \
    PaymentCreatedEventPayload
from ..entities.payment import NewPaymentEntity, PaymentEntity
from ..enums import EventTypeEnum
from ..interfaces.event_repository import IEventRepository
from ..interfaces.payment_repository import IPaymentRepository


class CreatePaymentUseCase:
    def __init__(self,
                 payment_repository: IPaymentRepository,
                 event_repository: IEventRepository):
        self._payment_repository = payment_repository
        self._event_repository = event_repository

    async def execute(
            self,
            new_payment: NewPaymentEntity,
            idempotency_key: str
    ) -> PaymentEntity:
        payment, is_new = await self._payment_repository.create_payment(
            new_payment=new_payment,
            idempotency_key=idempotency_key,
            hash_=new_payment.compute_hash()
        )
        if is_new:
            event_id = uuid7()
            new_event = NewEventEntity(
                id=event_id,
                event_type=EventTypeEnum.PAYMENT_CREATED,
                payload=PaymentCreatedEventPayload(
                    event_type=EventTypeEnum.PAYMENT_CREATED,
                    event_id=event_id,
                    payment_id=payment.id,
                ),
                created_at=payment.created_at
            )
            await self._event_repository.create(new_event=new_event)
        return payment

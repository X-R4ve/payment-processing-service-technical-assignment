from typing import Annotated

from fastapi.params import Header
from fastapi import Depends

from app.api.dependencies import get_create_payment_use_case
from app.api.schemas.requests import NewPaymentRequestSchemaV1
from app.api.schemas.responses import CreatedPaymentResponseSchemaV1
from app.application.use_cases.create_payment_use_case import \
CreatePaymentUseCase


async def create_payment_v1(
        idempotency_key: Annotated[str, Header(alias='Idempotency-Key')],
        create_payment_uc: Annotated[
            CreatePaymentUseCase,
            Depends(get_create_payment_use_case)
        ],
        new_payment: NewPaymentRequestSchemaV1
) -> CreatedPaymentResponseSchemaV1:
    new_payment_entity = new_payment.to_entity()
    created_payment = \
        await create_payment_uc.execute(new_payment=new_payment_entity,
                                        idempotency_key=idempotency_key)
    return CreatedPaymentResponseSchemaV1.from_entity(entity=created_payment)

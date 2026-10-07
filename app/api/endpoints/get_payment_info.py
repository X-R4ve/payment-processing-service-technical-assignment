from typing import Annotated
from uuid import UUID

from fastapi import Depends

from app.api.dependencies import get_get_payment_info_use_case
from app.api.schemas.responses import PaymentResponseSchemaV1
from app.application.use_cases.get_payment_use_case import GetPaymentInfoUseCase


async def get_payment_info_v1(
        get_payment_info_uc: Annotated[
            GetPaymentInfoUseCase,
            Depends(get_get_payment_info_use_case)
        ],
        payment_id: UUID
) -> PaymentResponseSchemaV1:
    payment_entity = await get_payment_info_uc.execute(payment_id=payment_id)
    return PaymentResponseSchemaV1.from_entity(entity=payment_entity)

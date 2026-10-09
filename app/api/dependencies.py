from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Request, Depends
from fastapi.params import Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.err import BaseError
from app.application.use_cases.create_payment_use_case import \
    CreatePaymentUseCase
from app.application.use_cases.get_payment_use_case import GetPaymentInfoUseCase
from app.infrastructure.settings import get_settings
from app.repositories.event_repository import EventRepository
from app.repositories.payment_repository import PaymentRepository


async def get_db_session(
        request: Request
) -> AsyncGenerator[AsyncSession, None]:
    async with request.state.db_connection.new_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_payment_repository(
        db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> PaymentRepository:
    return PaymentRepository(db_session=db_session)


def get_event_repository(
        db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> EventRepository:
    return EventRepository(db_session=db_session)


def get_create_payment_use_case(
        payment_repository: Annotated[
            PaymentRepository,
            Depends(get_payment_repository)
        ],
        event_repository: Annotated[
            EventRepository,
            Depends(get_event_repository)
        ]
) -> CreatePaymentUseCase:
    return CreatePaymentUseCase(payment_repository=payment_repository,
                                event_repository=event_repository)


def get_get_payment_info_use_case(
        payment_repository: Annotated[
            PaymentRepository,
            Depends(get_payment_repository)
        ]
) -> GetPaymentInfoUseCase:
    return GetPaymentInfoUseCase(payment_repository=payment_repository)


api_key_scheme = APIKeyHeader(name='X-API-Key', auto_error=False)


@lru_cache
def get_api_key():
    return get_settings().api_key


async def validate_api_key(
        api_key: Annotated[str, Depends(get_api_key)],
        api_key_from_client: Annotated[str | None, Security(api_key_scheme)]
) -> str:
    if api_key_from_client is None:
        raise BaseError(code=401, err='unauthorized', reason='API key required')

    if api_key_from_client != api_key:
        raise BaseError(code=401, err='unauthorized', reason='Invalid API key')

    return api_key_from_client

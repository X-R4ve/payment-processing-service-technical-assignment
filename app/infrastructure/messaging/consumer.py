from asyncio import sleep, Semaphore
from contextlib import asynccontextmanager
from datetime import datetime, UTC
from logging import getLogger, basicConfig, INFO
from random import uniform, choices
from typing import Annotated, Any

from faststream import FastStream, AckPolicy, ContextRepo, Context
from faststream.rabbit.message import RabbitMessage
from httpx import AsyncClient

from app.application.enums import PaymentStatusEnum
from app.infrastructure.db.core.connection import DatabaseConnection
from app.infrastructure.db.models import Payment
from app.infrastructure.messaging.crud import update_payment_status, \
    get_payment
from app.infrastructure.messaging.retries import retry_webhook
from app.infrastructure.messaging.schemas import \
    PaymentCreatedMessageSchema, WebhookBodySchema
from app.infrastructure.messaging.broker import (
    broker,
    payments_new_messages_queue, declare_topology
)
from app.infrastructure.settings import get_settings


logger = getLogger(__name__)
basicConfig(level=INFO)


@asynccontextmanager
async def lifespan(context: ContextRepo):
    db_connection = DatabaseConnection(db_url=get_settings().db.url)
    context.set_global('db_connection', db_connection)
    try:
        async with AsyncClient() as httpx_client:
            context.set_global('httpx_client', httpx_client)
            yield
    finally:
        await db_connection.close()


consumer_app = FastStream(broker, lifespan=lifespan)


@consumer_app.after_startup
async def declare_topology_after_startup():
    await declare_topology()


async def emulate_payment_processing(
        payment: Payment
):
    await sleep(2 + uniform(0, 3))
    is_success = choices(population=[True, False], weights=[0.9, 0.1], k=1)[0]
    if not is_success:
        raise RuntimeError('Payment processing failed')


@retry_webhook
async def send_webhook(
        url: str,
        message: dict[str, Any],
        httpx_client: AsyncClient,
        timeout: int | float = 5
):
    response = await httpx_client.post(url, json=message, timeout=timeout)
    response.raise_for_status()


@broker.subscriber(
    payments_new_messages_queue,
    ack_policy=AckPolicy.MANUAL
)
async def handle_payment_created_event(
        message: PaymentCreatedMessageSchema,
        db_connection: Annotated[DatabaseConnection, Context()],
        httpx_client: Annotated[AsyncClient, Context()],
        msg: Annotated[RabbitMessage, Context('message')]
):
    logger.info(f'Received new payment event with payment_id {message.payment_id}')

    async with db_connection.new_session() as session:
        payment = await get_payment(
            db_session=session,
            payment_id=message.payment_id
        )
    if not payment:
        await msg.ack()
        return
    if payment.status != PaymentStatusEnum.PENDING:
        logger.info(f'Payment {payment.id} already '
                    f'processed. Status: {payment.status}')
        await msg.ack()
        return

    try:
        await emulate_payment_processing(payment=payment)
        is_success = True
    except Exception as e:
        logger.error(f'Failed to process payment {payment.id}', exc_info=e)
        attempt_num = msg.headers.get('x-delivery-count', 0) + 1
        if attempt_num < 3:
            await msg.reject(requeue=True)
            return
        is_success = False

    if is_success:
        new_status = PaymentStatusEnum.SUCCEEDED
        logger.info(f'Payment {message.payment_id} succeeded')
    else:
        new_status = PaymentStatusEnum.FAILED
        logger.error(f'Payment {message.payment_id} failed')

    async with db_connection.new_session() as session:
        payment = await update_payment_status(
            db_session=session,
            payment_id=message.payment_id,
            new_status=new_status,
            dt=datetime.now(UTC)
        )
        if payment is None:
            await msg.ack()
            return
        await session.commit()

    webhook_body = WebhookBodySchema(
        event_type=message.event_type,
        event_id=message.event_id,
        payment_id=payment.id,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
        processed_at=payment.processed_at
    )

    try:
        await send_webhook(url=str(payment.webhook_url),
                           message=webhook_body.model_dump(mode='json'),
                           httpx_client=httpx_client)
    except Exception as e:
        logger.error(
            'Failed to send webhook for payment '
            f'{message.payment_id} on url {payment.webhook_url}',
            exc_info=e
        )
    if is_success:
        await msg.ack()
    else:
        await msg.reject(requeue=True)

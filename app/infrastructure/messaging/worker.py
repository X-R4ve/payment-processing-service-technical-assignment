from asyncio import gather, sleep, create_task
from datetime import UTC, datetime
from logging import getLogger, basicConfig, INFO

from faststream import FastStream
from faststream.rabbit.publisher import RabbitPublisher
from pamqp.commands import Basic

from app.application.enums import EventTypeEnum
from app.infrastructure.db.core.connection import DatabaseConnection
from app.infrastructure.messaging.crud import (get_events_batch,
                                               mark_published)
from app.infrastructure.messaging.broker import \
    broker, events_exchange, payments_new_messages_queue, declare_topology
from app.infrastructure.settings import get_settings


logger = getLogger(__name__)
basicConfig(level=INFO)


async def run_cycle(
        db_connection: DatabaseConnection,
        publisher: RabbitPublisher
) -> bool:
    need_sleep = False
    async with db_connection.new_session() as session:
        messages = await get_events_batch(
            db_session=session,
            event_type=EventTypeEnum.PAYMENT_CREATED,
            limit=20
        )
        if not messages:
            logger.debug('No new events. Sleeping...')
            return True

        results = await gather(
            *(publisher.publish(msg.payload) for msg in messages),
            return_exceptions=True
        )
        success_ids = [
            messages[i].id
            for i in range(len(messages))
            if not isinstance(results[i], BaseException)
        ]
        logger.info(f'{len(success_ids)} new events have been published')
        errors_num = len(messages) - len(success_ids)
        if errors_num > 0:
            need_sleep = True
            logger.error(f'Some new events were not published: {errors_num}')

        await mark_published(db_session=session,
                             msg_ids=success_ids,
                             dt=datetime.now(UTC))
        await session.commit()

    return need_sleep


async def outbox_worker(
        db_connection: DatabaseConnection,
        publisher: RabbitPublisher
):
    need_sleep = False
    while True:
        try:
            need_sleep = await run_cycle(db_connection=db_connection,
                                         publisher=publisher)
        except Exception as e:
            logger.error('Failed to publish new events', exc_info=e)
            need_sleep = True
        if need_sleep:
            await sleep(1)
            need_sleep = False


worker_app = FastStream(broker)


@worker_app.after_startup
async def start_worker():
    await declare_topology()
    publisher = broker.publisher(
        queue=payments_new_messages_queue,
        exchange=events_exchange,
        persist=True,
        mandatory=True
    )
    db_connection = DatabaseConnection(db_url=get_settings().db.url)

    create_task(outbox_worker(db_connection=db_connection,
                              publisher=publisher))

from faststream.rabbit import RabbitBroker, Channel, RabbitExchange, \
    ExchangeType, RabbitQueue, QueueType

from app.infrastructure.settings import get_settings

broker = RabbitBroker(
    url=get_settings().rabbitmq.url,
    default_channel=Channel(
        publisher_confirms=True,
        on_return_raises=True
    )
)

events_dlx_name = 'events.dead'
events_dlx = RabbitExchange(
    name=events_dlx_name,
    type=ExchangeType.DIRECT,
    durable=True
)
payments_dlq_name = 'payments.new.dead'
payments_dlq = RabbitQueue(
    name=payments_dlq_name,
    durable=True
)
events_exchange = RabbitExchange(
    name='events',
    type=ExchangeType.DIRECT,
    durable=True
)
payments_new_messages_queue = RabbitQueue(
    name='payments.new',
    queue_type=QueueType.QUORUM,
    durable=True,
    arguments={
        'x-dead-letter-exchange': events_dlx_name,
        'x-dead-letter-routing-key': payments_dlq_name,
        'x-delivery-limit': 3
    }
)

async def declare_topology():
    exchange = await broker.declare_exchange(events_exchange)
    queue = await broker.declare_queue(payments_new_messages_queue)
    await queue.bind(exchange)

    exchange = await broker.declare_exchange(events_dlx)
    queue = await broker.declare_queue(payments_dlq)
    await queue.bind(exchange)

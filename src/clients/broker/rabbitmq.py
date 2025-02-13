from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractRobustExchange, AbstractRobustQueue
import json

from clients.broker.abstract_broker import AbstractBroker
from common.settings import settings


class RabbitMQClient(AbstractBroker):
    _self: "RabbitMQClient" = None
    _connection: AbstractRobustConnection | None = None
    _channel: AbstractRobustChannel | None = None
    _exchange: AbstractRobustExchange | None = None
    _notification_queue: AbstractRobustQueue | None = None

    def __new__(cls, *args, **kwargs):
        if not cls._self:
            cls._self = super().__new__(cls, *args, **kwargs)
        return cls._self

    async def connect(self) -> None:
        try:
            self._connection = await connect_robust(settings.get_rmq_url())
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                name=settings.RABBITMQ_EXCHANGE_NAME, auto_delete=True
            )
            self._notification_queue = await self._channel.declare_queue(
                name=settings.RABBITMQ_NOTIFICATION_QUEUE_NAME, auto_delete=True
            )
            await self._notification_queue.bind(self._exchange, settings.RABBITMQ_NOTIFICATION_ROUTING_KEY)

        except Exception:
            await self.disconnect()


    async def disconnect(self) -> None:
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        self._channel = self._connection = None


    async def send_to_notification(self, message: dict) -> None:
        await self._exchange.publish(
            message=Message(body=json.dumps(message).encode()),
            routing_key=settings.RABBITMQ_NOTIFICATION_ROUTING_KEY,
        )


rmq_client = RabbitMQClient()

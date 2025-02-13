from datetime import datetime

from src.clients.broker.rabbitmq import rmq_client
from src.common.settings import settings
from utils.enums import LogLevel


async def send_log(level: LogLevel, msg: str):
    message = f"{str(datetime.now())} - {settings.SERVICE_NAME} - {level} - {msg}"
    await rmq_client.send_log(message)

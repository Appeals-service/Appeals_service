from fastapi import APIRouter, status
import pika
import json

router = APIRouter(tags=["Sending"])

spam = {"key_1": "value_1", "key_2": "value_2"}
queue_name = "task_queue"
exchange_name = "logs"


@router.post("/",status_code=status.HTTP_201_CREATED, summary="Send a request")
async def send_request(msg: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name, exchange_type="fanout")

    channel.basic_publish(
        exchange=exchange_name,
        routing_key='',
        body=msg.encode(),
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
    )
    print(f" [x] Sent {msg}")
    connection.close()

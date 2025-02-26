import asyncio
import json
from functools import wraps
from hashlib import sha256
from typing import Any

from fastapi import Request
from sqlalchemy.engine.row import Row

from clients.cache.redis_client import redis_client
from common.settings import settings


def cache(expire: int = settings.DEFAULT_CACHE_EXPIRATION):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = create_cache_key(func.__name__, *args, **kwargs)

            if cached_data := await redis_client.get(key):
                return json.loads(cached_data)

            data =  await func(*args, **kwargs)
            data = transform_data(data)
            asyncio.create_task(redis_client.set(key, json.dumps(data), expire))
            return data

        return wrapper
    return decorator


def create_cache_key(func_name: str, *args, **kwargs) -> str:
    for key, value in kwargs.items():
        if isinstance(value, Request):
            kwargs[key] = value.get("headers")
            break

    data = f"{func_name}_{args}_{kwargs}"
    return sha256(data.encode()).hexdigest()


def transform_data(data: Any) -> Any:
    def convert_row_to_dict(row: Row) -> dict:
        dict_data = row._asdict()
        if created_at := dict_data.get("created_at"):
            dict_data["created_at"] = created_at.strftime("%Y-%m-%d %H:%M:%S")
        return dict_data

    if isinstance(data, list) and all([isinstance(item, Row) for item in data]):
        output_data = [convert_row_to_dict(row) for row in data]
    elif isinstance(data, Row):
        output_data = convert_row_to_dict(data)
    else:
        output_data = data
    return output_data

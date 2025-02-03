# pylint: disable=too-many-arguments

import asyncio
import logging
from abc import ABC
from contextlib import asynccontextmanager

from aiohttp import ClientConnectionError, ClientSession, ServerDisconnectedError

from common.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(format=settings.LOGGING_FORMAT)
logger.setLevel(logging.DEBUG)


class BaseAsyncClient(ABC):
    base_url: str
    timeout: int

    def __init__(self, base_url: str, timeout: int):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @asynccontextmanager
    async def _request(
        self,
        method: str,
        path: str,
        params: dict = None,
        data: dict = None,
        json: dict = None,
        headers: dict = None,
        timeout: int = None,
        retry: int = 2,
        retry_delay: int = 0.5,
    ):
        logger.debug(f"Start _request({method}, {path})")
        retry = retry if retry is not None else 0
        retry_delay = retry_delay if retry_delay is not None else 0.5
        assert retry >= 0, "Retry must be greater than or equal to 0"
        assert retry_delay >= 0, "Retry delay must be greater than or equal to 0"

        request_url = (self.base_url + "/" + path.lstrip("/")).strip("/")

        log_json = json.copy()
        if log_json.get("pwd"):
            log_json["pwd"] = "***"
        logger.info(
            f"\nSending request: {method} {request_url}"
            f"\nparams: {params}\ndata: {data}\njson: {log_json}\nheaders: {headers}",
        )

        while retry >= 0:
            retry -= 1

            try:
                async with ClientSession() as session:
                    async with session.request(
                        method,
                        request_url.lstrip("/"),
                        params=params,
                        data=data,
                        json=json,
                        headers=headers,
                        timeout=timeout or self.timeout,
                    ) as response:
                        await self._logging_after_response(response, method, request_url)
                        yield response
                        logger.debug(f"Finish _request({method}, {path})")
                        return

            except asyncio.TimeoutError:
                logger.warning(f"Timeout error. Retry in {retry_delay} s...")
            except ServerDisconnectedError:
                logger.warning(f"Server disconnected. Retry in {retry_delay} s...")
            except ClientConnectionError:
                logger.warning(f"Connection error. Retry in {retry_delay} s...")

            await asyncio.sleep(retry_delay)

        raise ConnectionError(f"Connection error after {retry} retries. {method} {request_url}")

    @staticmethod
    async def _logging_after_response(response, method, request_url):
        if response.ok:
            logger.info(f"Request successful: {method} {request_url}. Status code: {response.status}")
        else:
            await response.read()
            logger.warning(f"Request failed: {method} {request_url}. Status code: {response.status}")

    def _get(self, path, params=None, headers=None, timeout=None, retry=None, retry_delay=None):
        return self._request(
            "GET",
            path,
            params,
            headers=headers,
            timeout=timeout,
            retry=retry,
            retry_delay=retry_delay,
        )

    def _post(
        self,
        path,
        data=None,
        params=None,
        json=None,
        headers=None,
        timeout=None,
        retry=None,
        retry_delay=None,
    ):
        return self._request(
            "POST",
            path,
            data=data,
            params=params,
            json=json,
            headers=headers,
            timeout=timeout,
            retry=retry,
            retry_delay=retry_delay,
        )

    def _put(self, path, data=None, json=None, headers=None, timeout=None, retry=None, retry_delay=None):
        return self._request(
            "PUT",
            path,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout,
            retry=retry,
            retry_delay=retry_delay,
        )

    def _patch(self, path, data=None, json=None, headers=None, timeout=None, retry=None, retry_delay=None):
        return self._request(
            "PATCH",
            path,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout,
            retry=retry,
            retry_delay=retry_delay,
        )

    def _delete(self, path, data=None, json=None, headers=None, timeout=None, retry=None, retry_delay=None):
        return self._request(
            "DELETE",
            path,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout,
            retry=retry,
            retry_delay=retry_delay,
        )

    def _head(self, path, data=None, json=None, headers=None, timeout=None, retry=None, retry_delay=None):
        return self._request(
            "HEAD",
            path,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout,
            retry=retry,
            retry_delay=retry_delay,
        )

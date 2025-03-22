from typing import AsyncGenerator, Optional
import logging
import httpx
from contextlib import asynccontextmanager
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# class ModelSpecs(BaseModel):
#     id: str
#     name: str
#     description: str
#     operation: Operation
#     response: Optional[Response]
#     components: Components


class ServiceApi(BaseModel):
    url: str

    @asynccontextmanager
    async def _client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        client = httpx.AsyncClient()
        yield client

    async def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        async with self._client() as client:
            res = await client.request(method, self.url + endpoint, **kwargs)
        return res

    async def model_specs(self):
        res = await self._request("GET", "modelspecs")
        data = res.json()
        logger.debug(f"modelspecs response: {data}")
        return data

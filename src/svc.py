import pprint
import fastapi
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse
import time
from typing import AsyncGenerator, Optional, List, Dict
import logging
import httpx
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ModelRequestField(BaseModel):
    key: str
    title: str
    dtype: str
    label: str
    description: str
    default: Optional[str]
    required: bool

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    gt: Optional[float] = None
    ge: Optional[float] = None
    lt: Optional[float] = None
    le: Optional[float] = None


class ModelEndpoint(BaseModel):
    endpoint: str
    label: str
    description: str
    http_method: str
    request_schema: List[ModelRequestField]


class ModelSpec(BaseModel):
    id: str
    name: str
    description: str
    endpoints: List[ModelEndpoint]


class ServiceApi(BaseModel):
    url: str

    @asynccontextmanager
    async def _client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        client = httpx.AsyncClient(base_url=self.url, timeout=60)
        yield client

    async def proxy(self, path: str, req: fastapi.Request) -> httpx.Response:
        url = httpx.URL(path=path, query=req.url.query.encode("utf-8"))
        async with self._client() as client:
            request = client.build_request(
                req.method, url, headers=req.headers.raw, content=req.stream()
            )
            res = await client.send(request)
        return res

    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        async with self._client() as client:
            res = await client.request(method, self.url + endpoint, **kwargs)
        return res

    async def model_specs(self) -> Dict[str, ModelSpec]:
        res = await self.request("GET", "modelspecs")
        resdata = res.json()
        logger.debug(f"modelspecs response: {resdata}")
        return {k: ModelSpec.model_validate(v) for k, v in resdata.items()}


class ModelSpecs:
    _svc: ServiceApi
    _cachetime: int
    _loadtime: float
    _specs: Dict[str, ModelSpec]

    def __init__(self, svc: ServiceApi, cache_time: int = 3600):
        self._svc = svc
        self._cachetime = cache_time
        self._loadtime = 0
        self._specs = {}

    async def _reload_specs(self):
        logger.info("Reloading ModelSpecs...")
        self._specs = await self._svc.model_specs()
        self._loadtime = time.time()

    async def get_all_specs(self) -> Dict[str, ModelSpec]:
        if len(self._specs) == 0 or self._loadtime - time.time() >= self._cachetime:
            await self._reload_specs()

        assert self._specs is not None
        return self._specs

    async def get_model_specs(self, mdl_name: str) -> ModelSpec:
        specs = await self.get_all_specs()
        return specs[mdl_name]


class ServiceApiResponse(BaseModel):
    status_code: int
    time_taken: str
    text: str

    @classmethod
    def from_response(cls, r: httpx.Response, t: float):
        text = pprint.pformat(r.json(), width=50)
        if t < 60:
            time_taken = f"{t:.2f} seconds"
        else:
            time_taken = f"{(t / 60):.2f} minutes"

        return cls(status_code=r.status_code, text=text, time_taken=time_taken)

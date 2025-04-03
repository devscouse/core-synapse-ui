from time import time
from typing import Annotated
import httpx
import logging
from fastapi import FastAPI, Header
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from src.log import logging_config
from src.config import cfg
from src.svc import ModelSpecs, ServiceApi, ServiceApiResponse

logging_config()
logger = logging.getLogger(__name__)
app = FastAPI(title="core-synapse-ui-backend")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

svc = ServiceApi(url=cfg.svc_api_url)
specs = ModelSpecs(svc)


@app.get("/")
async def serve_ui(request: Request):
    models = await specs.get_all_specs()
    return templates.TemplateResponse(
        "index.html", {"request": request, "models": list(models.values())}
    )


@app.get("/model/{model_key}")
async def model_key_page(request: Request, model_key: str):
    mdl_specs = await specs.get_model_specs(model_key)
    logger.info(mdl_specs)
    return templates.TemplateResponse(
        "model.html", {"model": mdl_specs, "request": request}
    )


@app.api_route(
    "/svcproxy/{path_name:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def service_api_proxy(
    request: Request, path_name: str, model_key: Annotated[str, Header()]
):
    t1 = time()
    res = await svc.proxy(f"/service/{path_name}", request)
    svcres = ServiceApiResponse.from_response(res, time() - t1)

    logger.info(svcres)

    return templates.TemplateResponse(
        "api_response.html", {"response": svcres, "request": request}
    )

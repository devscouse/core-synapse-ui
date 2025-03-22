import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from src.log import logging_config
from src.config import cfg
from src.svc import ServiceApi

logging_config()
logger = logging.getLogger(__name__)
app = FastAPI(title="core-synapse-ui-backend")

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

svc = ServiceApi(url=cfg.svc_api_url)

@app.get("/")
async def serve_ui(request: Request):

    models = await svc.model_specs()
    return templates.TemplateResponse(
        "index.html", {"request": request, "models": list(models.values())}
    )


@app.get("/model/{model_key}")
def model_key_page(request: Request):
    pass

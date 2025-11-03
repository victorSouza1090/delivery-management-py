from fastapi import FastAPI
from app.api.routes import orders
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.middlewares.logging_middleware import log_requests
from app.core.exceptions.exceptions import register_exception_handlers

logger = setup_logging(name="api")
logger.info("API inicializada")

app = FastAPI(title="Delivery Service API", version=settings.app_version)

app.middleware("http")(log_requests)

register_exception_handlers(app)

app.include_router(orders.router, prefix="/orders", tags=["Orders"])

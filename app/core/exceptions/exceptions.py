import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from .orders.orderNotFoundError import OrderNotFoundError

logger = logging.getLogger("api")




def register_exception_handlers(app: FastAPI):

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_server_error", "detail": "Internal server error."},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        formatted_errors = []

        for err in exc.errors():
            loc = ".".join(str(l) for l in err["loc"]) 
            msg = err["msg"]

            if err["type"] == "uuid_parsing":
                msg = "Invalid UUID format"

            formatted_errors.append(f"{loc}: {msg}")

        logger.warning(f"Validation error: {formatted_errors}")

        return JSONResponse(
            status_code=422,
            content={"error": "validation_error", "messages": formatted_errors},
        )

    @app.exception_handler(OrderNotFoundError)
    async def order_not_found_handler(request: Request, exc: OrderNotFoundError):
        logger.warning(f"{exc}")
        return JSONResponse(
            status_code=404,
            content={"error": "order_not_found", "detail": str(exc)},
        )
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.application.err import BaseError


def base_error_handler(request: Request, error: BaseError):
    return JSONResponse(
        content={'message': error.text},
        status_code=error.code
    )


def unexpected_error_handler(request: Request, error: Exception):
    return JSONResponse(
        content={'message': 'unexpected error'},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
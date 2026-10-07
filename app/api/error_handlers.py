from fastapi import Request
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
        status_code=500
    )
from fastapi import FastAPI, status, Depends

from app.api.dependencies import validate_api_key
from app.api.endpoints.create_payment import create_payment_v1
from app.api.endpoints.get_payment_info import get_payment_info_v1
from app.api.error_handlers import base_error_handler, unexpected_error_handler
from app.application.err import BaseError

payment_processing_service_app_v1 = FastAPI(
    dependencies=[Depends(validate_api_key)],
    version='v1'
)

payment_processing_service_app_v1.add_api_route(
    '/payments',
    create_payment_v1,
    methods=['POST'],
    status_code=status.HTTP_202_ACCEPTED
)
payment_processing_service_app_v1.add_api_route(
    '/payments/{payment_id}',
    get_payment_info_v1,
    methods=['GET'],
    status_code=status.HTTP_200_OK
)

payment_processing_service_app_v1.add_exception_handler(
    BaseError,
    base_error_handler # type: ignore
)
payment_processing_service_app_v1.add_exception_handler(
    Exception,
    unexpected_error_handler
)

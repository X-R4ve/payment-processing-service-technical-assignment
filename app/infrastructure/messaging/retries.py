from httpx import RequestError, InvalidURL, UnsupportedProtocol, HTTPStatusError
from tenacity import retry, retry_if_exception, stop_after_attempt, \
    wait_exponential


RETRIABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}

def is_retriable_webhook(err: BaseException) -> bool:
    if isinstance(err, RequestError):
        return not isinstance(err, (InvalidURL, UnsupportedProtocol))
    if isinstance(err, HTTPStatusError):
        return err.response.status_code in RETRIABLE_STATUS_CODES
    return False

retry_webhook = retry(
    retry=retry_if_exception(predicate=is_retriable_webhook),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=3, min=3, max=9, exp_base=3),
    reraise=True
)

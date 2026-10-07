

class BaseError(Exception):
    def __init__(self, code: int, err: str, reason: str):
        self._code = code
        self._err = err
        self._reason = reason

    @property
    def code(self):
        return self._code

    @property
    def text(self):
        return f'{self._err}: {self._reason}'

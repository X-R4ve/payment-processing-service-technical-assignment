from functools import wraps

from sqlalchemy.exc import IntegrityError, NoResultFound, OperationalError, \
    ProgrammingError, DBAPIError, SQLAlchemyError

from app.application.err import BaseError


def translate_db_exceptions(async_method):
    @wraps(async_method)
    async def wrapper(*args, **kwargs):
        try:
            return await async_method(*args, **kwargs)
        except IntegrityError as e:
            raise BaseError(code=409,
                            err='database error',
                            reason='data conflict') from e
        except NoResultFound as e:
            raise BaseError(code=404,
                            err='database error',
                            reason='data not found') from e
        except OperationalError as e:
            raise BaseError(code=503,
                            err='database error',
                            reason='error connecting to database') from e
        except (ProgrammingError, DBAPIError, SQLAlchemyError) as e:
            raise BaseError(code=500,
                            err='database error',
                            reason='something went wrong') from e
    return wrapper
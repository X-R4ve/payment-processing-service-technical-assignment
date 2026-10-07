from enum import Enum


class CurrencyEnum(str, Enum):
    RUB = 'RUB'
    USD = 'USD'
    EUR = 'EUR'


class PaymentStatusEnum(str, Enum):
    PENDING = 'pending'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


class EventTypeEnum(str, Enum):
    PAYMENT_CREATED = 'payment.created'

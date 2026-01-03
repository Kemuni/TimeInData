import random
import string
from contextlib import contextmanager
from datetime import datetime, timedelta, UTC
from typing import Optional, Generator
from unittest.mock import patch


def get_random_lower_string(length: int = 32) -> str:
    """ Get random string with length `length`. """
    return "".join(random.choices(string.ascii_lowercase, k=length))


def get_random_number(min_num: int = 1, max_num: int = 999_999_999) -> int:
    """
    Get random number in range [`min_num`, `max_num`].
    :param min_num: The minimum number. By default, 1.
    :param max_num: The maximum number. By default, 999_999_999.
    :return: The random number in range [`min_num`, `max_num`].
    """
    if min_num > max_num:
        raise ValueError("`min_num` must be less than `max_num`")
    return random.randint(min_num, max_num)


def get_random_datetime(from_date: Optional[datetime] = None, to_date: Optional[datetime] = None) -> datetime:
    """
    Get random datetime from `from_date` to `to_date` inclusive in UTC.
    :param from_date: The start datetime. If none, then `to_date` - 30 days.
    :param to_date: The end datetime. If none, then datetime from UTC.
    :return: The random datetime from `from_date` to `to_date` inclusive in UTC.
    """
    if to_date is None:
        to_date = datetime.now(UTC).replace(tzinfo=None)
    if from_date is None:
        from_date = to_date - timedelta(days=30)
    return datetime.fromtimestamp(random.uniform(from_date.timestamp(), to_date.timestamp()))


def datetime_to_clear_format(custom_datetime: datetime) -> datetime:
    """
    Clear datetime to have only year, month, day and hour.
    :param custom_datetime: Any datetime object.
    :return: Clear datetime.
    """
    return datetime(
        custom_datetime.year,
        custom_datetime.month,
        custom_datetime.day,
        custom_datetime.hour,
    ).replace(tzinfo=None)


@contextmanager
def patch_utcnow(module_name: str, return_value: datetime) -> Generator[None, None, None]:
    """
    Patch `utcnow` from `utils` in module `module_name` to return `return_value`.
    :param module_name: The module name, for example `routers.users`.
    :param return_value: The value to return.
    """
    with patch(f'{module_name}.utcnow') as mock_utcnow:
        mock_utcnow.return_value = return_value
        yield

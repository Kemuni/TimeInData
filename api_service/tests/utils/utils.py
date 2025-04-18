import random
import string
from datetime import datetime, timedelta
from typing import Optional


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
    :param to_date: The end datetime. If none, then `datetime.utcnow()`.
    :return: The random datetime from `from_date` to `to_date` inclusive in UTC.
    """
    if to_date is None:
        to_date = datetime.utcnow()
    if from_date is None:
        from_date = to_date - timedelta(days=30)
    return datetime.fromtimestamp(random.uniform(from_date.timestamp(), to_date.timestamp()))

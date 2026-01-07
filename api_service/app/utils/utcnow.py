from datetime import datetime, UTC


def utcnow() -> datetime:
    """ Return current UTC datetime without timezone info. """
    return datetime.now(UTC).replace(tzinfo=None)
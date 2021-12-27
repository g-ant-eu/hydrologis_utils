"""
Utilities to work with time.
"""

import datetime

PATTERN_WITH_SECONDS = "%Y-%m-%d %H:%M:%S"

def new_datetime(string = None):
    """Create a new datetime object.

    :param string: if supplied, it is used to build the datetime, else now is returned.
    :return: the datetime object.
    """
    if string:
        return datetime.datetime.strptime(string, PATTERN_WITH_SECONDS)
    else:
        return datetime.datetime.now()

def new_datetime_utc(string = None):
    """Create a new UTC datetime object.

    :param string: if supplied, it is used to build the datetime, else now is returned.
    :return: the datetime object.
    """
    if string:
        return datetime.datetime.strptime(string, PATTERN_WITH_SECONDS).replace(tzinfo=datetime.timezone.utc)
    else:
        return datetime.datetime.utcnow()

def to_string_with_seconds( dt ):
    """Get String of format: YYYY-MM-DD HH:MM:SS from a datetime object.

    :param dt: the datetime object to format.
    :return: the formatted string.
    """
    return dt.strftime(PATTERN_WITH_SECONDS)

def to_string_with_minutes( dt ):
    """Get String of format: YYYY-MM-DD HH:MM from a datetime object.

    :param dt: the datetime object to format.
    :return: the formatted string.
    """
    return dt.strftime("%Y-%m-%d %H:%M")

def quick_utc_to_string( unixEpoch ):
    """Quick long to timestamp string formatter, UTC.

    :param unixEpoch: the unix epoch to convert.
    :return: the timestamp string as yyyy-MM-dd HH:mm:ss
    """
    dt = datetime.datetime.fromtimestamp(unixEpoch, datetime.timezone.utc)

    return dt.strftime(PATTERN_WITH_SECONDS)

def quick_to_string( unixEpoch ):
    """Quick long to timestamp string formatter.

    :param unixEpoch: the unix epoch to convert.
    :return: the timestamp string as yyyy-MM-dd HH:mm:ss
    """
    dt = datetime.datetime.fromtimestamp(unixEpoch)

    return dt.strftime(PATTERN_WITH_SECONDS)

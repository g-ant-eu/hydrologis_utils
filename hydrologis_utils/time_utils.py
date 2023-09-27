"""
Utilities to work with time.
"""

from datetime import datetime, timezone

PATTERN_WITH_SECONDS = "%Y-%m-%d %H:%M:%S"
PATTERN_COMPACT = "%Y%m%d_%H%M%S"

def newDatetime(string:str = None) -> datetime:
    """Create a new datetime object.

    :param string: if supplied, it is used to build the datetime, else now is returned.
    :return: the datetime object.
    """
    if string:
        return datetime.strptime(string, PATTERN_WITH_SECONDS)
    else:
        return datetime.now()

def newDatetimeUtc(string:str = None) -> datetime:
    """Create a new UTC datetime object.

    :param string: if supplied, it is used to build the datetime, else now is returned.
    :return: the datetime object.
    """
    if string:
        return datetime.strptime(string, PATTERN_WITH_SECONDS).replace(tzinfo=timezone.utc)
    else:
        return datetime.utcnow()

def toStringWithSeconds( dt:datetime ) -> str:
    """Get String of format: YYYY-MM-DD HH:MM:SS from a datetime object.

    :param dt: the datetime object to format.
    :return: the formatted string.
    """
    return dt.strftime(PATTERN_WITH_SECONDS)

def toStringWithMinutes( dt:datetime ) -> str:
    """Get String of format: YYYY-MM-DD HH:MM from a datetime object.

    :param dt: the datetime object to format.
    :return: the formatted string.
    """
    return dt.strftime("%Y-%m-%d %H:%M")

def toStringCompact( dt:datetime ) -> str:
    """Get String of format: YYYYMMDD_HHMMSS from a datetime object.

    :param dt: the datetime object to format.
    :return: the formatted string.
    """
    return dt.strftime(PATTERN_COMPACT)

def quickUtcToString( unixEpoch:int ) -> str:
    """Quick long to timestamp string formatter, UTC.

    :param unixEpoch: the unix epoch to convert.
    :return: the timestamp string as yyyy-MM-dd HH:mm:ss
    """
    dt = datetime.fromtimestamp(unixEpoch, timezone.utc)

    return dt.strftime(PATTERN_WITH_SECONDS)

def quickToString( unixEpoch:int ) -> str:
    """Quick long to timestamp string formatter.

    :param unixEpoch: the unix epoch to convert.
    :return: the timestamp string as yyyy-MM-dd HH:mm:ss
    """
    dt = datetime.fromtimestamp(unixEpoch)

    return dt.strftime(PATTERN_WITH_SECONDS)

def toEpochInMillis( dt:datetime ) -> int:
    """Get millis since epoch from date object.
    
    :param dt: the datetime object.
    :return: the millis since epoch.
    """
    return dt.timestamp() * 1000
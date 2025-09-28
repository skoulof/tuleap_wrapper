import re
from datetime import datetime, timezone, timedelta

def iso_to_datetime(iso_string: str) -> datetime:
    """
    Manually parses an ISO 8601 formatted string and converts it to a datetime object.

    :param iso_string: ISO 8601 formatted string (e.g., "2025-01-27T10:47:28+02:00" or "2025-01-27T10:47:28Z")
    :return: A timezone-aware datetime object
    """

    # Handle empty strings
    if not iso_string:
        return iso_string

    # Regex pattern to match ISO 8601 strings
    iso_pattern = r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(Z|[+-]\d{2}:\d{2})?"
    match = re.match(iso_pattern, iso_string)

    if not match:
        raise ValueError(f"Invalid ISO 8601 format: {iso_string}")

    # Extract components
    year, month, day, hour, minute, second, tzinfo = match.groups()

    # Convert to integers
    year, month, day = int(year), int(month), int(day)
    hour, minute, second = int(hour), int(minute), int(second)

    # Handle timezone information
    if tzinfo == "Z":  # UTC
        tz = timezone.utc
    elif tzinfo:  # Offset like +02:00 or -05:00
        sign = 1 if tzinfo[0] == "+" else -1
        tz_hours, tz_minutes = map(int, tzinfo[1:].split(":"))
        tz_offset = timedelta(hours=tz_hours, minutes=tz_minutes) * sign
        tz = timezone(tz_offset)
    else:  # No timezone provided (naive datetime)
        tz = None

    # Create and return the datetime object
    return datetime(year, month, day, hour, minute, second, tzinfo=tz)


def datetime_to_iso(dt: datetime, use_z: bool = False) -> str:
    """
    Manually converts a datetime object to an ISO 8601 formatted string.

    :param dt: A datetime object (timezone-aware or naive)
    :param use_z: If True, replaces "+00:00" with "Z" for UTC
    :return: ISO 8601 formatted string
    """

    # Handle None value
    if not dt:
        return dt

    # Extract date and time components
    date_part = f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}"
    time_part = f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"

    # Handle timezone information
    if dt.tzinfo:
        offset = dt.tzinfo.utcoffset(dt)
        if offset == timedelta(0) and use_z:  # UTC timezone with 'Z'
            tz_part = "Z"
        else:
            # Calculate hours and minutes of the offset
            total_seconds = offset.total_seconds()
            sign = "+" if total_seconds >= 0 else "-"
            offset_hours = int(abs(total_seconds) // 3600)
            offset_minutes = int((abs(total_seconds) % 3600) // 60)
            tz_part = f"{sign}{offset_hours:02d}:{offset_minutes:02d}"
    else:
        tz_part = ""  # Naive datetime, no timezone info

    # Combine into final ISO string
    return f"{date_part}T{time_part}{tz_part}"

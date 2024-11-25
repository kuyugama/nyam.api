from datetime import datetime, UTC


def now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def utc_timestamp(date: datetime) -> float:
    return date.replace(tzinfo=UTC).timestamp()


def from_utc_timestamp(timestamp: str | float) -> datetime:
    return datetime.fromtimestamp(timestamp, UTC).replace(tzinfo=None)

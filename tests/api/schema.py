"""Response shape checks.

Hand-written rather than pulled from a schema library: the point is to say in
plain terms what a booking is supposed to look like, and to fail with a message
that names the offending field.
"""
from __future__ import annotations

from typing import Any

BOOKING_FIELDS: dict[str, type | tuple[type, ...]] = {
    "firstname": str,
    "lastname": str,
    "totalprice": int,
    "depositpaid": bool,
    "bookingdates": dict,
}

BOOKING_DATE_FIELDS = ("checkin", "checkout")


def assert_booking_shape(booking: dict[str, Any]) -> None:
    """Fail unless the payload has every booking field, with the right type."""
    for field, expected_type in BOOKING_FIELDS.items():
        assert field in booking, f"booking is missing the field {field!r}: {booking}"
        assert isinstance(booking[field], expected_type), (
            f"field {field!r} should be {expected_type} "
            f"but was {type(booking[field])} ({booking[field]!r})"
        )

    dates = booking["bookingdates"]
    for field in BOOKING_DATE_FIELDS:
        assert field in dates, f"bookingdates is missing {field!r}: {dates}"
        assert_is_iso_date(dates[field], field)

    # Nothing unexpected should appear either; a new field is a change worth
    # noticing rather than silently accepting.
    unexpected = set(booking) - set(BOOKING_FIELDS) - {"additionalneeds"}
    assert not unexpected, f"unexpected fields in booking response: {sorted(unexpected)}"


def assert_is_iso_date(value: Any, field_name: str) -> None:
    from datetime import date

    assert isinstance(value, str), f"{field_name} should be a string, got {value!r}"
    try:
        date.fromisoformat(value)
    except ValueError:  # pragma: no cover - the assert carries the message
        raise AssertionError(f"{field_name} is not an ISO date: {value!r}") from None

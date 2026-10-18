"""Negative cases: what the API does with input it should not accept.

Two of these are written as expected failures. They are real defects in the
application under test, not flaws in the tests — each one is written up in
docs/BUG_REPORTS.md with steps to reproduce. They are marked xfail(strict=True)
so that the suite stays green while the defect stands, and turns red the moment
it is fixed and the write-up goes stale.
"""
from __future__ import annotations

import pytest

from .client import BookerClient


@pytest.mark.api
@pytest.mark.booking
def test_unknown_booking_id_returns_not_found(anon_client: BookerClient) -> None:
    """API-20: reading an id that does not exist returns 404."""
    response = anon_client.get_booking(99_999_999)
    assert response.status_code == 404, (
        f"an unknown id returned {response.status_code}: {response.text}"
    )


@pytest.mark.api
@pytest.mark.booking
def test_deleting_an_unknown_booking_is_not_reported_as_success(
    client: BookerClient,
) -> None:
    """API-21: deleting an id that does not exist does not report success."""
    response = client.delete_booking(99_999_999)
    assert response.status_code != 201, (
        "deleting a booking that does not exist reported 201 Created"
    )


@pytest.mark.api
@pytest.mark.booking
def test_booking_without_required_fields_is_rejected(
    client: BookerClient, booking_payload: dict
) -> None:
    """API-22: a booking missing a required field is not stored."""
    incomplete = {k: v for k, v in booking_payload.items() if k != "firstname"}
    response = client.create_booking(incomplete)
    assert response.status_code >= 400, (
        "a booking with no firstname was accepted with "
        f"{response.status_code}: {response.text}"
    )


@pytest.mark.api
@pytest.mark.booking
@pytest.mark.xfail(
    strict=True,
    reason="BUG-01: a missing required field answers 500 rather than 400",
)
def test_missing_field_is_a_client_error_not_a_server_error(
    client: BookerClient, booking_payload: dict
) -> None:
    """API-25: bad input should be a 4xx with a reason, not a 500.

    The request is rejected, which is correct, but it is rejected as an
    internal server error with an HTML body. A caller cannot tell a bad payload
    apart from an outage. See docs/BUG_REPORTS.md, BUG-01.
    """
    incomplete = {k: v for k, v in booking_payload.items() if k != "firstname"}
    response = client.create_booking(incomplete)
    assert 400 <= response.status_code < 500, (
        "invalid input was reported as "
        f"{response.status_code}, which is not a client error"
    )


@pytest.mark.api
@pytest.mark.booking
@pytest.mark.xfail(
    strict=True,
    reason="BUG-02: checkout dates before checkin are accepted",
)
def test_checkout_before_checkin_is_rejected(
    client: BookerClient, booking_payload: dict
) -> None:
    """API-23: a stay that ends before it starts should be rejected.

    See docs/BUG_REPORTS.md, BUG-02.
    """
    backwards = dict(
        booking_payload,
        bookingdates={
            "checkin": booking_payload["bookingdates"]["checkout"],
            "checkout": booking_payload["bookingdates"]["checkin"],
        },
    )
    response = client.create_booking(backwards)
    assert response.status_code >= 400, (
        "a booking whose checkout precedes its checkin was accepted with "
        f"{response.status_code}: {response.text}"
    )


@pytest.mark.api
@pytest.mark.booking
def test_price_is_stored_as_a_number(
    client: BookerClient, anon_client: BookerClient, booking_payload: dict
) -> None:
    """API-24: totalprice comes back as a number, whatever was sent."""
    booking_id = client.create_booking(booking_payload).json()["bookingid"]
    try:
        stored = anon_client.get_booking(booking_id).json()
        assert isinstance(stored["totalprice"], int), (
            f"totalprice came back as {type(stored['totalprice'])}: "
            f"{stored['totalprice']!r}"
        )
    finally:
        client.delete_booking(booking_id)

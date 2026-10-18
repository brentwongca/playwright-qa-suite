"""The booking lifecycle: create, read, list, update, delete.

Each case checks the response the endpoint gives back *and* re-reads the record
afterwards, because an API that answers 200 and stores nothing is the failure
worth catching.
"""
from __future__ import annotations

import pytest

from .client import BookerClient
from .schema import assert_booking_shape


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.booking
def test_create_returns_an_id_and_echoes_the_booking(
    client: BookerClient, created_booking: dict
) -> None:
    """API-10: a created booking comes back with an id and the sent values."""
    assert isinstance(created_booking["id"], int), (
        f"bookingid should be an integer, got {created_booking['id']!r}"
    )
    assert created_booking["created"] == created_booking["payload"], (
        "the echoed booking does not match what was sent:\n"
        f"sent:     {created_booking['payload']}\n"
        f"returned: {created_booking['created']}"
    )


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.booking
def test_created_booking_can_be_read_back(
    anon_client: BookerClient, created_booking: dict
) -> None:
    """API-11: GET /booking/{id} returns the stored record in the right shape."""
    response = anon_client.get_booking(created_booking["id"])
    assert response.status_code == 200, (
        f"reading the booking returned {response.status_code}: {response.text}"
    )
    booking = response.json()
    assert_booking_shape(booking)
    assert booking["firstname"] == created_booking["payload"]["firstname"]
    assert booking["totalprice"] == created_booking["payload"]["totalprice"]


@pytest.mark.api
@pytest.mark.booking
def test_new_booking_appears_in_the_list(
    anon_client: BookerClient, created_booking: dict
) -> None:
    """API-12: the id of a new booking is present in GET /booking."""
    response = anon_client.list_bookings()
    assert response.status_code == 200, (
        f"listing bookings returned {response.status_code}: {response.text}"
    )
    ids = [row["bookingid"] for row in response.json()]
    assert created_booking["id"] in ids, (
        f"booking {created_booking['id']} is missing from the list of {len(ids)} ids"
    )


@pytest.mark.api
@pytest.mark.booking
def test_list_can_be_filtered_by_name(
    anon_client: BookerClient, created_booking: dict
) -> None:
    """API-13: filtering by firstname and lastname returns the matching id."""
    payload = created_booking["payload"]
    response = anon_client.list_bookings(
        firstname=payload["firstname"], lastname=payload["lastname"]
    )
    assert response.status_code == 200, (
        f"filtered list returned {response.status_code}: {response.text}"
    )
    ids = [row["bookingid"] for row in response.json()]
    assert created_booking["id"] in ids, (
        "filtering by the booking's own name did not return it; "
        f"got {len(ids)} other ids instead"
    )


@pytest.mark.api
@pytest.mark.booking
def test_full_update_replaces_every_field(
    client: BookerClient, anon_client: BookerClient, created_booking: dict
) -> None:
    """API-14: PUT with a complete payload replaces the record."""
    booking_id = created_booking["id"]
    replacement = dict(
        created_booking["payload"],
        firstname="Replaced",
        lastname="Record",
        totalprice=999,
        depositpaid=False,
        additionalneeds="Quiet room",
    )

    response = client.update_booking(booking_id, replacement)
    assert response.status_code == 200, (
        f"update returned {response.status_code}: {response.text}"
    )

    stored = anon_client.get_booking(booking_id).json()
    assert_booking_shape(stored)
    assert stored == replacement, (
        "the stored record does not match the replacement:\n"
        f"sent:   {replacement}\nstored: {stored}"
    )


@pytest.mark.api
@pytest.mark.booking
def test_partial_update_changes_only_the_named_fields(
    client: BookerClient, anon_client: BookerClient, created_booking: dict
) -> None:
    """API-15: PATCH changes the fields it names and leaves the rest alone."""
    booking_id = created_booking["id"]
    original = created_booking["payload"]

    response = client.patch_booking(booking_id, {"firstname": "Patched"})
    assert response.status_code == 200, (
        f"patch returned {response.status_code}: {response.text}"
    )

    stored = anon_client.get_booking(booking_id).json()
    assert stored["firstname"] == "Patched", "the patched field was not applied"
    assert stored["lastname"] == original["lastname"], (
        "a field that was not in the patch changed anyway: "
        f"lastname is {stored['lastname']!r}"
    )
    assert stored["totalprice"] == original["totalprice"], (
        "a field that was not in the patch changed anyway: "
        f"totalprice is {stored['totalprice']!r}"
    )


@pytest.mark.api
@pytest.mark.booking
def test_deleted_booking_is_gone(
    client: BookerClient, anon_client: BookerClient, booking_payload: dict
) -> None:
    """API-16: a deleted booking can no longer be read.

    This case creates its own booking rather than using the fixture, because it
    deliberately leaves nothing to clean up.
    """
    booking_id = client.create_booking(booking_payload).json()["bookingid"]

    deleted = client.delete_booking(booking_id)
    assert deleted.status_code == 201, (
        f"delete returned {deleted.status_code}: {deleted.text}"
    )

    gone = anon_client.get_booking(booking_id)
    assert gone.status_code == 404, (
        f"a deleted booking still reads back with {gone.status_code}: {gone.text}"
    )

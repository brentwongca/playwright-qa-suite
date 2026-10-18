"""Fixtures for the API layer.

The API under test is Restful Booker (https://restful-booker.herokuapp.com), a
public practice API. The admin credentials below are the ones its own
documentation publishes; they are not anyone's personal credentials. Override
them with BOOKER_USER / BOOKER_PASSWORD for another environment.
"""
from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any, Iterator

import pytest

from .client import BookerClient

DEFAULT_BASE_URL = "https://restful-booker.herokuapp.com"
BOOKER_USER = os.getenv("BOOKER_USER", "admin")
BOOKER_PASSWORD = os.getenv("BOOKER_PASSWORD", "password123")


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return os.getenv("BOOKER_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def anon_client(api_base_url: str) -> BookerClient:
    """A client with no token, for the endpoints that do not need one."""
    return BookerClient(api_base_url)


@pytest.fixture(scope="session")
def auth_token(anon_client: BookerClient) -> str:
    response = anon_client.create_token(BOOKER_USER, BOOKER_PASSWORD)
    assert response.status_code == 200, (
        f"could not obtain a token: {response.status_code} {response.text}"
    )
    token = response.json().get("token")
    assert token, f"auth responded 200 but returned no token: {response.text}"
    return token


@pytest.fixture()
def client(api_base_url: str, auth_token: str) -> BookerClient:
    return BookerClient(api_base_url, token=auth_token)


@pytest.fixture()
def booking_payload() -> dict[str, Any]:
    """A valid booking, dated relative to today so it never goes stale."""
    checkin = date.today() + timedelta(days=7)
    checkout = checkin + timedelta(days=3)
    return {
        "firstname": "Kai",
        "lastname": "Tester",
        "totalprice": 275,
        "depositpaid": True,
        "bookingdates": {
            "checkin": checkin.isoformat(),
            "checkout": checkout.isoformat(),
        },
        "additionalneeds": "Late checkout",
    }


@pytest.fixture()
def created_booking(
    client: BookerClient, booking_payload: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    """Create a booking for the test to work on, then clean it up afterwards."""
    response = client.create_booking(booking_payload)
    assert response.status_code == 200, (
        f"setup failed to create a booking: {response.status_code} {response.text}"
    )
    body = response.json()
    booking_id = body["bookingid"]

    yield {"id": booking_id, "payload": booking_payload, "created": body["booking"]}

    # Teardown runs even when the test fails, so a red run leaves nothing behind.
    client.delete_booking(booking_id)

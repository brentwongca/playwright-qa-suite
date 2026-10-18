"""Authentication: who is allowed to change a booking, and who is not.

The API issues a token from valid credentials and expects it back as a cookie
on every write. These cases cover both halves of that: getting a usable token,
and what happens to a write that arrives without one.
"""
from __future__ import annotations

import pytest

from .client import BookerClient


@pytest.mark.api
@pytest.mark.smoke
def test_health_endpoint_reports_the_service_is_up(anon_client: BookerClient) -> None:
    """API-01: /ping answers 201 when the service is running."""
    response = anon_client.health()
    assert response.status_code == 201, (
        f"health check returned {response.status_code}: {response.text}"
    )


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.auth
def test_valid_credentials_return_a_token(auth_token: str) -> None:
    """API-02: valid credentials produce a non-empty token."""
    assert isinstance(auth_token, str) and auth_token.strip(), (
        f"expected a usable token string, got {auth_token!r}"
    )


@pytest.mark.api
@pytest.mark.auth
@pytest.mark.parametrize(
    ("username", "password", "case"),
    [
        ("admin", "wrong-password", "right user, wrong password"),
        ("not-a-user", "password123", "unknown user, right password"),
        ("", "", "both fields empty"),
    ],
)
def test_bad_credentials_do_not_return_a_token(
    anon_client: BookerClient, username: str, password: str, case: str
) -> None:
    """API-03: bad credentials are refused rather than issued a token."""
    response = anon_client.create_token(username, password)
    body = response.json()
    assert "token" not in body, f"{case}: a token was issued anyway: {body}"
    assert body.get("reason") == "Bad credentials", (
        f"{case}: expected a 'Bad credentials' reason, got {body}"
    )


@pytest.mark.api
@pytest.mark.auth
def test_update_without_a_token_is_rejected(
    anon_client: BookerClient, created_booking: dict, booking_payload: dict
) -> None:
    """API-04: a PUT with no token is refused with 403, and changes nothing."""
    booking_id = created_booking["id"]
    tampered = dict(booking_payload, firstname="Unauthorised")

    response = anon_client.update_booking(booking_id, tampered, authed=False)
    assert response.status_code == 403, (
        f"an unauthenticated update returned {response.status_code}, expected 403"
    )

    unchanged = anon_client.get_booking(booking_id).json()
    assert unchanged["firstname"] == booking_payload["firstname"], (
        "the refused request still modified the record: "
        f"{unchanged['firstname']!r}"
    )


@pytest.mark.api
@pytest.mark.auth
def test_delete_without_a_token_is_rejected(
    anon_client: BookerClient, created_booking: dict
) -> None:
    """API-05: a DELETE with no token is refused, and the booking survives."""
    booking_id = created_booking["id"]

    response = anon_client.delete_booking(booking_id, authed=False)
    assert response.status_code == 403, (
        f"an unauthenticated delete returned {response.status_code}, expected 403"
    )

    survivor = anon_client.get_booking(booking_id)
    assert survivor.status_code == 200, (
        "the booking disappeared after a refused delete"
    )

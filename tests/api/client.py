"""A thin client for the Restful Booker API.

One place that knows the endpoints, the headers and the auth cookie, so the
tests read as behaviour rather than as plumbing. Every method returns the raw
``requests.Response`` — assertions about status codes belong in the tests, not
in here.
"""
from __future__ import annotations

from typing import Any

import requests

DEFAULT_TIMEOUT = 15


class BookerClient:
    def __init__(self, base_url: str, token: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    # --- plumbing ---------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _headers(self, *, authed: bool, accept: str = "application/json") -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": accept}
        if authed:
            # The API takes the token as a cookie, not as a bearer header.
            headers["Cookie"] = f"token={self.token}"
        return headers

    # --- endpoints --------------------------------------------------------

    def health(self) -> requests.Response:
        return requests.get(self._url("/ping"), timeout=DEFAULT_TIMEOUT)

    def create_token(self, username: str, password: str) -> requests.Response:
        return requests.post(
            self._url("/auth"),
            json={"username": username, "password": password},
            headers=self._headers(authed=False),
            timeout=DEFAULT_TIMEOUT,
        )

    def list_bookings(self, **filters: Any) -> requests.Response:
        return requests.get(
            self._url("/booking"),
            params=filters or None,
            headers=self._headers(authed=False),
            timeout=DEFAULT_TIMEOUT,
        )

    def get_booking(self, booking_id: int) -> requests.Response:
        return requests.get(
            self._url(f"/booking/{booking_id}"),
            headers=self._headers(authed=False),
            timeout=DEFAULT_TIMEOUT,
        )

    def create_booking(self, payload: dict[str, Any]) -> requests.Response:
        return requests.post(
            self._url("/booking"),
            json=payload,
            headers=self._headers(authed=False),
            timeout=DEFAULT_TIMEOUT,
        )

    def update_booking(
        self, booking_id: int, payload: dict[str, Any], *, authed: bool = True
    ) -> requests.Response:
        return requests.put(
            self._url(f"/booking/{booking_id}"),
            json=payload,
            headers=self._headers(authed=authed),
            timeout=DEFAULT_TIMEOUT,
        )

    def patch_booking(
        self, booking_id: int, payload: dict[str, Any], *, authed: bool = True
    ) -> requests.Response:
        return requests.patch(
            self._url(f"/booking/{booking_id}"),
            json=payload,
            headers=self._headers(authed=authed),
            timeout=DEFAULT_TIMEOUT,
        )

    def delete_booking(self, booking_id: int, *, authed: bool = True) -> requests.Response:
        return requests.delete(
            self._url(f"/booking/{booking_id}"),
            headers=self._headers(authed=authed),
            timeout=DEFAULT_TIMEOUT,
        )

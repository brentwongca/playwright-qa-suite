"""Shared behaviour for every page object.

Keeping waits and navigation here means a test never calls Playwright's
low-level API directly, so a change in the application only has to be fixed in
one place.
"""
from __future__ import annotations

from playwright.sync_api import Page, expect


class BasePage:
    #: Every subclass sets this to the path it owns, e.g. "/inventory.html".
    path: str = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    # --- navigation -----------------------------------------------------
    def open(self) -> "BasePage":
        self.page.goto(f"{self.base_url}{self.path}", wait_until="domcontentloaded")
        return self

    def expect_loaded(self) -> "BasePage":
        expect(self.page).to_have_url(f"{self.base_url}{self.path}")
        return self

    # --- helpers --------------------------------------------------------
    @property
    def title_text(self) -> str:
        return self.page.title()

    def screenshot(self, name: str) -> bytes:
        return self.page.screenshot(full_page=True, path=f"reports/{name}.png")

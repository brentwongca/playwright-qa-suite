"""Login page: the only entry point into the application under test."""
from __future__ import annotations

from playwright.sync_api import Locator, expect

from .base_page import BasePage
from .inventory_page import InventoryPage


class LoginPage(BasePage):
    path = "/"

    # --- locators -------------------------------------------------------
    @property
    def username(self) -> Locator:
        return self.page.get_by_placeholder("Username")

    @property
    def password(self) -> Locator:
        return self.page.get_by_placeholder("Password")

    @property
    def submit(self) -> Locator:
        return self.page.get_by_role("button", name="Login")

    @property
    def error(self) -> Locator:
        return self.page.locator('[data-test="error"]')

    # --- actions --------------------------------------------------------
    def login(self, user: str, secret: str) -> "LoginPage":
        self.username.fill(user)
        self.password.fill(secret)
        self.submit.click()
        return self

    def login_expecting_success(self, user: str, secret: str) -> InventoryPage:
        self.login(user, secret)
        inventory = InventoryPage(self.page, self.base_url)
        inventory.expect_loaded()
        return inventory

    # --- assertions -----------------------------------------------------
    def expect_error(self, message: str) -> "LoginPage":
        expect(self.error).to_be_visible()
        expect(self.error).to_contain_text(message)
        return self

    def expect_no_error(self) -> "LoginPage":
        expect(self.error).to_have_count(0)
        return self

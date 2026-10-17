"""Checkout: the two-step form, the totals, and the confirmation."""
from __future__ import annotations

from playwright.sync_api import Locator, expect

from .base_page import BasePage


class CheckoutPage(BasePage):
    path = "/checkout-step-one.html"

    # --- step one: customer information ---------------------------------
    @property
    def first_name(self) -> Locator:
        return self.page.locator('[data-test="firstName"]')

    @property
    def last_name(self) -> Locator:
        return self.page.locator('[data-test="lastName"]')

    @property
    def postal_code(self) -> Locator:
        return self.page.locator('[data-test="postalCode"]')

    @property
    def error(self) -> Locator:
        return self.page.locator('[data-test="error"]')

    def fill_customer(self, first: str, last: str, postcode: str) -> "CheckoutPage":
        self.first_name.fill(first)
        self.last_name.fill(last)
        self.postal_code.fill(postcode)
        return self

    def continue_to_overview(self) -> "CheckoutPage":
        self.page.locator('[data-test="continue"]').click()
        return self

    def expect_error(self, message: str) -> "CheckoutPage":
        expect(self.error).to_be_visible()
        expect(self.error).to_contain_text(message)
        return self

    # --- step two: overview and totals ----------------------------------
    @property
    def item_total(self) -> float:
        raw = self.page.locator(".summary_subtotal_label").inner_text()
        return float(raw.split("$")[1])

    @property
    def tax(self) -> float:
        raw = self.page.locator(".summary_tax_label").inner_text()
        return float(raw.split("$")[1])

    @property
    def total(self) -> float:
        raw = self.page.locator(".summary_total_label").inner_text()
        return float(raw.split("$")[1])

    def expect_on_overview(self) -> "CheckoutPage":
        expect(self.page).to_have_url(f"{self.base_url}/checkout-step-two.html")
        return self

    def finish(self) -> "CheckoutPage":
        self.page.locator('[data-test="finish"]').click()
        return self

    def expect_order_complete(self) -> "CheckoutPage":
        expect(self.page).to_have_url(f"{self.base_url}/checkout-complete.html")
        expect(self.page.locator(".complete-header")).to_contain_text(
            "Thank you for your order!"
        )
        return self

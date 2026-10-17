"""Cart: what was added, what it costs, and the way on to checkout."""
from __future__ import annotations

from playwright.sync_api import Locator, expect

from .base_page import BasePage


class CartPage(BasePage):
    path = "/cart.html"

    @property
    def rows(self) -> Locator:
        return self.page.locator(".cart_item")

    @property
    def item_names(self) -> list[str]:
        return self.page.locator(".inventory_item_name").all_text_contents()

    def quantity_of(self, product: str) -> str:
        row = self.page.locator(".cart_item").filter(has_text=product)
        return row.locator(".cart_quantity").inner_text()

    def remove(self, product: str) -> "CartPage":
        row = self.page.locator(".cart_item").filter(has_text=product)
        row.get_by_role("button", name="Remove").click()
        return self

    def continue_shopping(self):
        self.page.locator('[data-test="continue-shopping"]').click()
        from .inventory_page import InventoryPage

        inventory = InventoryPage(self.page, self.base_url)
        inventory.expect_loaded()
        return inventory

    def checkout(self):
        self.page.locator('[data-test="checkout"]').click()
        from .checkout_page import CheckoutPage

        checkout = CheckoutPage(self.page, self.base_url)
        checkout.expect_loaded()
        return checkout

    def expect_rows(self, count: int) -> "CartPage":
        expect(self.rows).to_have_count(count)
        return self

    def expect_contains(self, product: str) -> "CartPage":
        expect(self.page.locator(".cart_item").filter(has_text=product)).to_have_count(1)
        return self

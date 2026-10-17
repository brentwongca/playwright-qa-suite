"""Product listing: sorting, adding to cart, and the cart badge."""
from __future__ import annotations

from playwright.sync_api import Locator, expect

from .base_page import BasePage


class InventoryPage(BasePage):
    path = "/inventory.html"

    SORT_OPTIONS = {
        "name_asc": "az",
        "name_desc": "za",
        "price_asc": "lohi",
        "price_desc": "hilo",
    }

    # --- locators -------------------------------------------------------
    @property
    def items(self) -> Locator:
        return self.page.locator(".inventory_item")

    @property
    def item_names(self) -> list[str]:
        return self.page.locator(".inventory_item_name").all_text_contents()

    @property
    def item_prices(self) -> list[float]:
        raw = self.page.locator(".inventory_item_price").all_text_contents()
        return [float(value.replace("$", "")) for value in raw]

    @property
    def sort_dropdown(self) -> Locator:
        return self.page.locator('[data-test="product-sort-container"]')

    @property
    def cart_badge(self) -> Locator:
        return self.page.locator(".shopping_cart_badge")

    def add_button(self, product: str) -> Locator:
        slug = product.lower().replace(" ", "-").replace("(", "").replace(")", "")
        return self.page.locator(f'[data-test="add-to-cart-{slug}"]')

    def remove_button(self, product: str) -> Locator:
        slug = product.lower().replace(" ", "-").replace("(", "").replace(")", "")
        return self.page.locator(f'[data-test="remove-{slug}"]')

    # --- actions --------------------------------------------------------
    def sort_by(self, key: str) -> "InventoryPage":
        self.sort_dropdown.select_option(self.SORT_OPTIONS[key])
        return self

    def add_to_cart(self, product: str) -> "InventoryPage":
        self.add_button(product).click()
        return self

    def remove_from_cart(self, product: str) -> "InventoryPage":
        self.remove_button(product).click()
        return self

    def open_cart(self):
        self.page.locator(".shopping_cart_link").click()
        from .cart_page import CartPage

        cart = CartPage(self.page, self.base_url)
        cart.expect_loaded()
        return cart

    # --- assertions -----------------------------------------------------
    def expect_item_count(self, count: int) -> "InventoryPage":
        expect(self.items).to_have_count(count)
        return self

    def expect_cart_count(self, count: int) -> "InventoryPage":
        if count == 0:
            expect(self.cart_badge).to_have_count(0)
        else:
            expect(self.cart_badge).to_have_text(str(count))
        return self

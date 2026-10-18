"""Cart contents survive navigation, and removal works from inside the cart."""
import pytest

from pages import InventoryPage


@pytest.mark.smoke
@pytest.mark.cart
def test_added_product_appears_in_the_cart(inventory_page: InventoryPage):
    cart = inventory_page.add_to_cart("Sauce Labs Backpack").open_cart()
    cart.expect_rows(1).expect_contains("Sauce Labs Backpack")
    assert cart.quantity_of("Sauce Labs Backpack") == "1"


@pytest.mark.cart
def test_cart_keeps_its_contents_when_shopping_continues(inventory_page: InventoryPage):
    cart = inventory_page.add_to_cart("Sauce Labs Bike Light").open_cart()
    inventory = cart.continue_shopping()
    inventory.expect_cart_count(1)
    cart = inventory.open_cart()
    cart.expect_contains("Sauce Labs Bike Light")


@pytest.mark.cart
def test_product_can_be_removed_from_inside_the_cart(inventory_page: InventoryPage):
    cart = (
        inventory_page.add_to_cart("Sauce Labs Backpack")
        .add_to_cart("Sauce Labs Bike Light")
        .open_cart()
    )
    cart.expect_rows(2)
    cart.remove("Sauce Labs Backpack").expect_rows(1)
    cart.expect_contains("Sauce Labs Bike Light")


@pytest.mark.cart
def test_empty_cart_has_no_rows(inventory_page: InventoryPage):
    inventory_page.open_cart().expect_rows(0)

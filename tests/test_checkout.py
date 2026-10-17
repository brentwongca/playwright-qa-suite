"""Checkout form validation, the arithmetic of the totals, and order completion."""
import pytest

from pages import InventoryPage

TAX_RATE = 0.08


@pytest.mark.checkout
@pytest.mark.parametrize(
    "first,last,postcode,message",
    [
        ("", "Wong", "V6Y0E8", "First Name is required"),
        ("Kai Chit", "", "V6Y0E8", "Last Name is required"),
        ("Kai Chit", "Wong", "", "Postal Code is required"),
    ],
    ids=["no-first-name", "no-last-name", "no-postcode"],
)
def test_checkout_requires_every_field(inventory_page: InventoryPage, first, last, postcode, message):
    checkout = inventory_page.add_to_cart("Sauce Labs Backpack").open_cart().checkout()
    checkout.fill_customer(first, last, postcode).continue_to_overview()
    checkout.expect_error(message)


@pytest.mark.smoke
@pytest.mark.checkout
def test_single_item_order_completes(inventory_page: InventoryPage):
    checkout = inventory_page.add_to_cart("Sauce Labs Backpack").open_cart().checkout()
    checkout.fill_customer("Kai Chit", "Wong", "V6Y 0E8").continue_to_overview()
    checkout.expect_on_overview()
    checkout.finish().expect_order_complete()


@pytest.mark.checkout
def test_overview_totals_add_up(inventory_page: InventoryPage):
    checkout = (
        inventory_page.add_to_cart("Sauce Labs Backpack")
        .add_to_cart("Sauce Labs Bike Light")
        .open_cart()
        .checkout()
    )
    checkout.fill_customer("Kai Chit", "Wong", "V6Y 0E8").continue_to_overview()
    checkout.expect_on_overview()

    expected_tax = round(checkout.item_total * TAX_RATE, 2)
    assert checkout.tax == pytest.approx(expected_tax, abs=0.01), (
        f"Tax {checkout.tax} is not {TAX_RATE:.0%} of subtotal {checkout.item_total}"
    )
    assert checkout.total == pytest.approx(checkout.item_total + checkout.tax, abs=0.01), (
        f"Total {checkout.total} is not subtotal {checkout.item_total} plus tax {checkout.tax}"
    )


@pytest.mark.checkout
def test_order_can_be_placed_for_the_whole_catalogue(inventory_page: InventoryPage):
    for product in [
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
        "Sauce Labs Bolt T-Shirt",
        "Sauce Labs Fleece Jacket",
        "Sauce Labs Onesie",
    ]:
        inventory_page.add_to_cart(product)
    inventory_page.expect_cart_count(5)
    checkout = inventory_page.open_cart().checkout()
    checkout.fill_customer("Kai Chit", "Wong", "V6Y 0E8").continue_to_overview()
    checkout.finish().expect_order_complete()

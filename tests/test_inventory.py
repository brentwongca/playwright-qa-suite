"""Product listing: how many items, how they sort, and the cart badge."""
import pytest

from pages import InventoryPage


@pytest.mark.smoke
@pytest.mark.inventory
def test_six_products_are_listed(inventory_page: InventoryPage):
    inventory_page.expect_item_count(6)


@pytest.mark.inventory
def test_sort_by_name_ascending(inventory_page: InventoryPage):
    names = inventory_page.sort_by("name_asc").item_names
    assert names == sorted(names), "Product names are not in A-Z order"


@pytest.mark.inventory
def test_sort_by_name_descending(inventory_page: InventoryPage):
    names = inventory_page.sort_by("name_desc").item_names
    assert names == sorted(names, reverse=True), "Product names are not in Z-A order"


@pytest.mark.inventory
def test_sort_by_price_low_to_high(inventory_page: InventoryPage):
    prices = inventory_page.sort_by("price_asc").item_prices
    assert prices == sorted(prices), f"Prices are not ascending: {prices}"


@pytest.mark.inventory
def test_sort_by_price_high_to_low(inventory_page: InventoryPage):
    prices = inventory_page.sort_by("price_desc").item_prices
    assert prices == sorted(prices, reverse=True), f"Prices are not descending: {prices}"


@pytest.mark.inventory
def test_cart_badge_counts_each_product_added(inventory_page: InventoryPage):
    inventory_page.expect_cart_count(0)
    inventory_page.add_to_cart("Sauce Labs Backpack").expect_cart_count(1)
    inventory_page.add_to_cart("Sauce Labs Bike Light").expect_cart_count(2)


@pytest.mark.inventory
def test_removing_a_product_lowers_the_badge(inventory_page: InventoryPage):
    inventory_page.add_to_cart("Sauce Labs Backpack").expect_cart_count(1)
    inventory_page.remove_from_cart("Sauce Labs Backpack").expect_cart_count(0)


@pytest.mark.inventory
def test_every_product_shows_a_price(inventory_page: InventoryPage):
    prices = inventory_page.item_prices
    assert len(prices) == 6
    assert all(price > 0 for price in prices), f"A product has no price: {prices}"

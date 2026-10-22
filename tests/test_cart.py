from unittest.mock import Mock

import pytest

from shop.cart import Cart

# --- add ---


def test_add_single_item(empty_cart: Cart) -> None:
    empty_cart.add("book", price=200.0)
    assert empty_cart.items_count() == 1


def test_add_increases_qty_for_existing_item(empty_cart: Cart) -> None:
    empty_cart.add("book", price=200.0, qty=2)
    empty_cart.add("book", price=200.0, qty=3)
    assert empty_cart.items_count() == 5


def test_add_negative_price_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="price"):
        empty_cart.add("book", price=-1.0)


def test_add_zero_qty_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="qty"):
        empty_cart.add("book", price=10.0, qty=0)


def test_add_negative_qty_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="qty"):
        empty_cart.add("book", price=10.0, qty=-2)


# --- remove ---


def test_remove_existing_item(cart_with_items: Cart) -> None:
    cart_with_items.remove("book")
    assert cart_with_items.items_count() == 4


def test_remove_missing_item_raises(empty_cart: Cart) -> None:
    with pytest.raises(KeyError):
        empty_cart.remove("ghost")


# --- items_count ---


def test_items_count_empty_cart(empty_cart: Cart) -> None:
    assert empty_cart.items_count() == 0


def test_items_count_with_items(cart_with_items: Cart) -> None:
    assert cart_with_items.items_count() == 6


# --- total / discount (параметризація + граничні значення) ---


@pytest.mark.parametrize(
    ("discount", "expected"),
    [(0, 460.0), (10, 414.0), (50, 230.0), (100, 0.0)],
)
def test_total_with_various_discounts(
    cart_with_items: Cart, discount: float, expected: float
) -> None:
    assert cart_with_items.total(discount_percent=discount) == pytest.approx(expected)


def test_total_without_discount_default(cart_with_items: Cart) -> None:
    assert cart_with_items.total() == pytest.approx(460.0)


def test_total_discount_below_zero_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="discount_percent"):
        empty_cart.total(discount_percent=-1)


def test_total_discount_above_100_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="discount_percent"):
        empty_cart.total(discount_percent=101)


def test_total_empty_cart_is_zero(empty_cart: Cart) -> None:
    assert empty_cart.total() == 0.0


# --- total_in (mock, без реальних мережевих запитів) ---


def test_total_in_usd_uses_rate_provider() -> None:
    rates = Mock()
    rates.get_rate.return_value = 40.0

    cart = Cart()
    cart.add("book", price=400.0)

    assert cart.total_in("USD", rates) == pytest.approx(10.0)
    rates.get_rate.assert_called_once_with("USD")


def test_total_in_zero_rate_raises() -> None:
    rates = Mock()
    rates.get_rate.return_value = 0.0

    cart = Cart()
    cart.add("book", price=100.0)

    with pytest.raises(ValueError, match="rate"):
        cart.total_in("USD", rates)


def test_total_in_negative_rate_raises() -> None:
    rates = Mock()
    rates.get_rate.return_value = -5.0

    cart = Cart()
    cart.add("book", price=100.0)

    with pytest.raises(ValueError, match="rate"):
        cart.total_in("USD", rates)


# --- TDD: most_expensive ---


def test_most_expensive_returns_none_for_empty_cart(empty_cart: Cart) -> None:
    assert empty_cart.most_expensive() is None


def test_most_expensive_returns_item_with_highest_unit_price(cart_with_items: Cart) -> None:
    result = cart_with_items.most_expensive()
    assert result is not None
    assert result.name == "book"


def test_most_expensive_with_single_item(empty_cart: Cart) -> None:
    empty_cart.add("pen", price=15.0, qty=10)
    result = empty_cart.most_expensive()
    assert result is not None
    assert result.name == "pen"

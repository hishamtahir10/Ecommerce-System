"""pricing.py - subtotal, discount and shipping rules (all money is Decimal)."""

from helpers import add_up, round_money, to_decimal
from config import SETTINGS


def calculate_order_subtotal(order, products):
    """price x quantity for every item, then add them all up.
    (Call this only for a VALID order - validate_order() checks the ids.)"""
    line_totals = [
        to_decimal(products[item["product_id"]]["price"]) * item["quantity"]
        for item in order["items"]
    ]
    return add_up(*line_totals)


def make_discount_calculator(tiers):
    """LEGB demo (the 'E' = Enclosing scope): returns a function that remembers `tiers`.
    The inner calculate() uses `tiers_high_first` from this enclosing function,
    so no global variable is needed. tiers = ((minimum_subtotal, rate), ...)"""
    tiers_high_first = sorted(tiers, key=lambda tier: tier[0], reverse=True)

    def calculate(subtotal):
        """Discount amount for this subtotal, rounded half up to cents."""
        subtotal = to_decimal(subtotal)
        for minimum, rate in tiers_high_first:
            if subtotal >= minimum:
                return round_money(subtotal * rate)
        return round_money(0)

    return calculate


def calculate_discount(subtotal):
    """Discount amount in dollars (tiers come from config.SETTINGS)."""
    return make_discount_calculator(SETTINGS["discount_tiers"])(subtotal)


def calculate_shipping(subtotal):
    """Free shipping from the configured subtotal (BEFORE discount), otherwise the fixed cost."""
    if to_decimal(subtotal) >= SETTINGS["free_shipping_from"]:
        return round_money(0)
    return round_money(SETTINGS["shipping_cost"])

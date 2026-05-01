"""
Input validation for trading bot CLI arguments.
All public functions raise ValueError with a human-readable message on failure.
"""

from decimal import Decimal, InvalidOperation

SUPPORTED_SYMBOLS = None          # None → skip static whitelist check
SUPPORTED_SIDES = {"BUY", "SELL"}
SUPPORTED_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    """Normalise and sanity-check a trading pair symbol."""
    symbol = symbol.strip().upper()
    if not symbol.isalnum():
        raise ValueError(f"Invalid symbol '{symbol}': must be alphanumeric (e.g. BTCUSDT).")
    if SUPPORTED_SYMBOLS and symbol not in SUPPORTED_SYMBOLS:
        raise ValueError(
            f"Unknown symbol '{symbol}'. Supported: {', '.join(sorted(SUPPORTED_SYMBOLS))}."
        )
    return symbol


def validate_side(side: str) -> str:
    """Ensure side is BUY or SELL."""
    side = side.strip().upper()
    if side not in SUPPORTED_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of: {', '.join(SUPPORTED_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    """Ensure order type is one of the supported types."""
    order_type = order_type.strip().upper()
    if order_type not in SUPPORTED_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(SUPPORTED_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity: str) -> str:
    """Ensure quantity is a positive decimal number."""
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation:
        raise ValueError(f"Invalid quantity '{quantity}': must be a positive number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than zero, got {qty}.")
    # Return as plain string (Binance expects string params)
    return str(qty)


def validate_price(price: str) -> str:
    """Ensure price is a positive decimal number (required for LIMIT orders)."""
    try:
        p = Decimal(str(price))
    except InvalidOperation:
        raise ValueError(f"Invalid price '{price}': must be a positive number.")
    if p <= 0:
        raise ValueError(f"Price must be greater than zero, got {p}.")
    return str(p)


def validate_stop_price(stop_price: str) -> str:
    """Ensure stop price is a positive decimal number (for STOP_MARKET orders)."""
    return validate_price(stop_price)  # same rules


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
) -> dict:
    """
    Validate and normalise all order inputs in one call.

    Returns a dict of cleaned values ready to be passed to the API layer.
    Raises ValueError for any invalid input.
    """
    cleaned = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
    }

    order_type_clean = cleaned["type"]

    if order_type_clean == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders.")
        cleaned["price"] = validate_price(price)
        cleaned["timeInForce"] = "GTC"   # Good-Till-Cancel default

    elif order_type_clean == "MARKET":
        if price is not None:
            raise ValueError("Price must not be supplied for MARKET orders.")

    elif order_type_clean == "STOP_MARKET":
        if stop_price is None:
            raise ValueError("--stop-price is required for STOP_MARKET orders.")
        cleaned["stopPrice"] = validate_stop_price(stop_price)

    return cleaned

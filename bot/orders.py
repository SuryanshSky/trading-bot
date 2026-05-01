"""
High-level order placement logic.
Sits between the CLI layer and the raw Binance client.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

from bot.client import BinanceFuturesClient, BinanceClientError, NetworkError
from bot.validators import validate_order_inputs

logger = logging.getLogger(__name__)


@dataclass
class OrderResult:
    """Structured representation of a completed order response."""

    success: bool
    order_id: Optional[int] = None
    client_order_id: Optional[str] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    order_type: Optional[str] = None
    status: Optional[str] = None
    executed_qty: Optional[str] = None
    avg_price: Optional[str] = None
    orig_qty: Optional[str] = None
    price: Optional[str] = None
    error: Optional[str] = None
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, response: dict) -> "OrderResult":
        return cls(
            success=True,
            order_id=response.get("orderId"),
            client_order_id=response.get("clientOrderId"),
            symbol=response.get("symbol"),
            side=response.get("side"),
            order_type=response.get("type"),
            status=response.get("status"),
            executed_qty=response.get("executedQty"),
            avg_price=response.get("avgPrice"),
            orig_qty=response.get("origQty"),
            price=response.get("price"),
            raw=response,
        )

    @classmethod
    def from_error(cls, error_message: str) -> "OrderResult":
        return cls(success=False, error=error_message)


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> OrderResult:
    """
    Validate inputs, build the order payload, submit it, and return an OrderResult.

    Args:
        client:      Authenticated BinanceFuturesClient instance
        symbol:      Trading pair, e.g. "BTCUSDT"
        side:        "BUY" or "SELL"
        order_type:  "MARKET", "LIMIT", or "STOP_MARKET"
        quantity:    Order quantity as a string
        price:       Limit price (required for LIMIT orders)
        stop_price:  Stop trigger price (required for STOP_MARKET)

    Returns:
        OrderResult with success=True and order details, or success=False with an error message.
    """
    # --- Validate -----------------------------------------------------------
    try:
        params = validate_order_inputs(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except ValueError as exc:
        logger.warning("Input validation failed: %s", exc)
        return OrderResult.from_error(str(exc))

    logger.info(
        "Placing %s %s %s | qty=%s price=%s stopPrice=%s",
        params["type"], params["side"], params["symbol"],
        params["quantity"], params.get("price", "–"),
        params.get("stopPrice", "–"),
    )

    # --- Submit -------------------------------------------------------------
    try:
        response = client.place_order(**params)
        logger.info("Order accepted: orderId=%s status=%s", response.get("orderId"), response.get("status"))
        return OrderResult.from_api_response(response)

    except BinanceClientError as exc:
        logger.error("Binance API error [%s]: %s", exc.error_code, exc.message)
        return OrderResult.from_error(f"API error {exc.error_code}: {exc.message}")

    except NetworkError as exc:
        logger.error("Network error: %s", exc)
        return OrderResult.from_error(f"Network error: {exc}")

    except Exception as exc:
        logger.exception("Unexpected error while placing order")
        return OrderResult.from_error(f"Unexpected error: {exc}")

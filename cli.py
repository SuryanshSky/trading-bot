#!/usr/bin/env python3
"""
Trading Bot CLI — Binance Futures Testnet

Usage examples:
    # Market BUY
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

    # Limit SELL
    python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3200

    # Stop-Market SELL (bonus order type)
    python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 60000
"""

import argparse
import os
import sys
import logging
from dotenv import load_dotenv

from bot.client import BinanceFuturesClient
from bot.orders import place_order, OrderResult
from bot.logging_config import setup_logging

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Output helpers                                                               #
# --------------------------------------------------------------------------- #

def _separator(char: str = "─", width: int = 60) -> str:
    return char * width


def print_request_summary(args: argparse.Namespace) -> None:
    print(_separator())
    print("  ORDER REQUEST SUMMARY")
    print(_separator())
    print(f"  Symbol     : {args.symbol.upper()}")
    print(f"  Side       : {args.side.upper()}")
    print(f"  Type       : {args.type.upper()}")
    print(f"  Quantity   : {args.quantity}")
    if args.price:
        print(f"  Price      : {args.price}")
    if args.stop_price:
        print(f"  Stop Price : {args.stop_price}")
    print(_separator())


def print_order_result(result: OrderResult) -> None:
    if result.success:
        print(_separator())
        print("  ORDER RESPONSE")
        print(_separator())
        print(f"  Order ID       : {result.order_id}")
        print(f"  Client OID     : {result.client_order_id}")
        print(f"  Symbol         : {result.symbol}")
        print(f"  Side           : {result.side}")
        print(f"  Type           : {result.order_type}")
        print(f"  Status         : {result.status}")
        print(f"  Orig Qty       : {result.orig_qty}")
        print(f"  Executed Qty   : {result.executed_qty}")
        avg = result.avg_price or result.price or "–"
        print(f"  Avg / Set Price: {avg}")
        print(_separator())
        print("  ✅  Order placed successfully!")
    else:
        print(_separator())
        print("  ❌  Order FAILED")
        print(_separator())
        print(f"  Reason: {result.error}")
    print(_separator())


# --------------------------------------------------------------------------- #
# Argument parsing                                                             #
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--symbol", required=True,
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL", "buy", "sell"],
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type", required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET", "market", "limit", "stop_market"],
        dest="type",
        help="Order type: MARKET | LIMIT | STOP_MARKET",
    )
    parser.add_argument(
        "--quantity", required=True,
        help="Order quantity (base asset units)",
    )
    parser.add_argument(
        "--price", default=None,
        help="Limit price — required for LIMIT orders",
    )
    parser.add_argument(
        "--stop-price", default=None, dest="stop_price",
        help="Stop trigger price — required for STOP_MARKET orders",
    )
    parser.add_argument(
        "--api-key", default=None,
        help="Binance API key (overrides BINANCE_API_KEY env var)",
    )
    parser.add_argument(
        "--api-secret", default=None,
        help="Binance API secret (overrides BINANCE_API_SECRET env var)",
    )
    parser.add_argument(
        "--testnet-url", default="https://testnet.binancefuture.com",
        help="Testnet base URL (default: https://testnet.binancefuture.com)",
    )

    return parser


# --------------------------------------------------------------------------- #
# Entry point                                                                  #
# --------------------------------------------------------------------------- #

def main() -> int:
    """
    Main entry point.  Returns 0 on success, 1 on failure.
    """
    setup_logging()

    load_dotenv()

    parser = build_parser()
    args = parser.parse_args()

    # Resolve credentials (CLI flag > env var)
    api_key = args.api_key or os.getenv("BINANCE_API_KEY", "")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET", "")

    if not api_key or not api_secret:
        parser.error(
            "API credentials are required.\n"
            "Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables, "
            "or use --api-key / --api-secret flags."
        )

    # Print what the user asked for
    print_request_summary(args)

    # Build the client and submit the order
    client = BinanceFuturesClient(
        api_key=api_key,
        api_secret=api_secret,
        base_url=args.testnet_url,
    )

    result = place_order(
        client=client,
        symbol=args.symbol,
        side=args.side,
        order_type=args.type,
        quantity=args.quantity,
        price=args.price,
        stop_price=args.stop_price,
    )

    print_order_result(result)

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())

"""
Binance Futures Testnet REST API client.
Handles authentication, request signing, and raw HTTP communication.
"""

import hashlib
import hmac
import time
import logging
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised when Binance API returns an error response."""

    def __init__(self, status_code: int, error_code: int, message: str):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(f"Binance API error {error_code}: {message} (HTTP {status_code})")


class NetworkError(Exception):
    """Raised on connectivity or timeout failures."""


class BinanceFuturesClient:
    """
    Thin wrapper around the Binance Futures Testnet REST API.

    Responsibilities:
    - Sign every private request with HMAC-SHA256
    - Attach the API key header
    - Handle HTTP-level errors and surface them as typed exceptions
    - Log every outgoing request and incoming response
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str = TESTNET_BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _sign(self, params: dict) -> dict:
        """Append a HMAC-SHA256 signature to a params dict (mutates + returns it)."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, endpoint: str, signed: bool = False, **kwargs) -> dict:
        """
        Execute an HTTP request and return the parsed JSON body.

        Args:
            method:   HTTP verb ("GET", "POST", …)
            endpoint: API path, e.g. "/fapi/v1/order"
            signed:   Whether to attach timestamp + signature
            **kwargs: Passed directly to requests.Session.request
                      (use `params` for query-string, `data` for POST body)
        """
        url = f"{self.base_url}{endpoint}"

        # Merge params/data dicts so we can sign them uniformly
        payload = kwargs.pop("params", None) or kwargs.pop("data", None) or {}
        if signed:
            payload = self._sign(payload)

        # For POST requests Binance expects the payload in the request body
        req_kwargs = {"data": payload} if method.upper() == "POST" else {"params": payload}

        logger.info("→ %s %s | payload: %s", method.upper(), endpoint, payload)

        try:
            response = self.session.request(method, url, timeout=10, **req_kwargs)
        except requests.exceptions.ConnectionError as exc:
            raise NetworkError(f"Connection failed: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            raise NetworkError(f"Request timed out: {exc}") from exc

        logger.info("← %s %s | status: %s | body: %s",
                    method.upper(), endpoint, response.status_code, response.text[:500])

        try:
            body = response.json()
        except ValueError:
            body = {"raw": response.text}

        if not response.ok:
            raise BinanceClientError(
                status_code=response.status_code,
                error_code=body.get("code", -1),
                message=body.get("msg", response.text),
            )

        return body

    # ------------------------------------------------------------------ #
    # Public API methods                                                   #
    # ------------------------------------------------------------------ #

    def get_exchange_info(self) -> dict:
        """Fetch exchange metadata (symbols, filters, etc.)."""
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def get_account(self) -> dict:
        """Fetch account balances and positions (requires auth)."""
        return self._request("GET", "/fapi/v2/account", signed=True)

    def place_order(self, **order_params) -> dict:
        """
        Place a new order on Futures Testnet.

        Expected keys in order_params (per Binance docs):
            symbol, side, type, quantity,
            price (LIMIT only), timeInForce (LIMIT only),
            stopPrice (STOP_LIMIT only), etc.
        """
        return self._request("POST", "/fapi/v1/order", signed=True, params=order_params)

    def get_order(self, symbol: str, order_id: int) -> dict:
        """Query a single order by ID."""
        return self._request(
            "GET", "/fapi/v1/order", signed=True,
            params={"symbol": symbol, "orderId": order_id},
        )

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an open order."""
        return self._request(
            "DELETE", "/fapi/v1/order", signed=True,
            params={"symbol": symbol, "orderId": order_id},
        )

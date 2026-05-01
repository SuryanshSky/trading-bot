# Trading Bot — Binance Futures Testnet

A clean, minimal Python CLI that places **Market**, **Limit**, and **Stop-Market** orders on the Binance Futures Testnet (USDT-M).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST client (auth, signing, HTTP)
│   ├── orders.py          # Order placement logic + OrderResult dataclass
│   ├── validators.py      # Input validation (raises ValueError on bad input)
│   └── logging_config.py  # File + coloured-console logging setup
├── cli.py                 # CLI entry point (argparse)
├── logs/
│   └── trading_bot.log    # Auto-created at runtime
├── .env.example           # Template for credentials
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet Credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account
3. Under **API Key**, generate a new key pair
4. Copy the API Key and Secret

### 2. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/trading-bot.git
cd trading-bot

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
cp .env.example .env
# Edit .env and paste your testnet API key and secret
```

`.env` contents:
```
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

---

## How to Run

### Market Order (BUY)
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Market Order (SELL)
```bash
python cli.py --symbol ETHUSDT --side SELL --type MARKET --quantity 0.01
```

### Limit Order (BUY)
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 60000
```

### Limit Order (SELL)
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 68000
```

### Stop-Market Order *(bonus)*
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 59000
```

### Pass credentials inline (no .env)
```bash
python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET \
    --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

---

## Example Output

```
────────────────────────────────────────────────────────────
  ORDER REQUEST SUMMARY
────────────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
────────────────────────────────────────────────────────────
  ORDER RESPONSE
────────────────────────────────────────────────────────────
  Order ID       : 3147483648
  Client OID     : web_abc123
  Symbol         : BTCUSDT
  Side           : BUY
  Type           : MARKET
  Status         : FILLED
  Orig Qty       : 0.001
  Executed Qty   : 0.001
  Avg / Set Price: 65432.10
────────────────────────────────────────────────────────────
  ✅  Order placed successfully!
────────────────────────────────────────────────────────────
```

---

## Logging

All logs are written to `logs/trading_bot.log` (auto-created).

- **DEBUG** level: full request payloads and response bodies (file only)
- **INFO** level: order lifecycle events (file + console in green)
- **WARNING**: validation failures
- **ERROR**: API errors, network failures

Log rotation: 5 MB per file, 3 backups kept.

---

## Validation & Error Handling

| Scenario | Behaviour |
|---|---|
| Missing `--price` for LIMIT | Clear `ValueError` message, no API call made |
| `--price` supplied for MARKET | Rejected before API call |
| Invalid symbol characters | Caught by validator |
| Non-positive quantity/price | Rejected with descriptive message |
| Binance API error (e.g. -1121) | Logged + shown to user; exit code 1 |
| Network timeout / DNS failure | Caught as `NetworkError`; exit code 1 |

---

## Assumptions

- Testnet only — no real funds are used.
- Position mode: one-way (default). `positionSide` is not set.
- `timeInForce` defaults to `GTC` for LIMIT orders.
- Quantity precision is not automatically adjusted; ensure your quantity matches the symbol's `stepSize` filter on the testnet exchange.

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP client |
| `python-dotenv` | Load `.env` credentials |

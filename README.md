# Trading Bot — Binance Futures Testnet

A lightweight Python CLI application to place orders on Binance Futures Testnet (USDT-M).
Built as part of a Python Developer application task to demonstrate API integration, clean architecture, and robust CLI design.

---

## What this does

You run a command in the terminal, it places a real order on the Binance Futures Testnet and shows you the result. That's it. No UI, no unnecessary complexity — just a clean CLI tool that does exactly what it's supposed to do.

Supported order types:
- Market order (BUY / SELL)
- Limit order (BUY / SELL)
- Stop-Market order (bonus)

---

## Project structure

```
trading_bot/
├── bot/
│   ├── client.py          # handles all API communication with Binance
│   ├── orders.py          # order logic, builds and submits the order
│   ├── validators.py      # validates user input before touching the API
│   └── logging_config.py  # sets up file logging + coloured console output
├── cli.py                 # entry point, handles all CLI arguments
├── logs/
│   └── trading_bot.log    # created automatically when you run the bot
├── .env.example           # copy this to .env and add your keys
├── requirements.txt
└── README.md
```

The idea was to keep things separated — the CLI layer doesn't talk to Binance directly, and the API client doesn't know anything about user input. Each file has one job.

---

## Setup

### Step 1 — Get your testnet API keys

Go to [testnet.binancefuture.com](https://testnet.binancefuture.com) and log in with GitHub. Head to the API Management section and generate a new key pair. Copy both the API Key and the Secret Key somewhere safe — the secret is only shown once.

### Step 2 — Clone the repo and install dependencies

```bash
git clone https://github.com/SuryanshSky/trading-bot.git
cd trading-bot
pip install -r requirements.txt
```

### Step 3 — Add your credentials

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_secret_key_here
```

Note: API keys are not included in this repository for security reasons. Use the provided .env.example file to configure your credentials.

That's all the setup needed.

---

## How to run

**Place a market BUY order:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Place a market SELL order:**
```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

**Place a limit BUY order:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 60000
```

**Place a limit SELL order:**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 75000
```

**Place a stop-market order:**
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 70000
```

One thing to note with limit orders — the price has to be within a reasonable range of the current market price or Binance will reject it. If you get a price-related error, just check the current BTC price and adjust.

---

## What the output looks like

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
  Order ID       : 13096948937
  Symbol         : BTCUSDT
  Side           : BUY
  Type           : MARKET
  Status         : NEW
  Orig Qty       : 0.001
  Executed Qty   : 0.001
  Avg / Set Price: 74500.00
────────────────────────────────────────────────────────────
  ✅  Order placed successfully!
────────────────────────────────────────────────────────────
```

---

## Logging

Every run writes to `logs/trading_bot.log`. The log captures the full request payload, the response from Binance, and any errors that occur. On the console you only see INFO level and above — the file gets everything including DEBUG.

Logs rotate automatically at 5 MB so they don't pile up.

---

## Error handling

A few things I made sure to handle properly:

- If you forget `--price` on a limit order, it tells you before making any API call
- If you pass `--price` on a market order, same thing — caught early
- Invalid symbols, negative quantities, and non-numeric values are all caught by the validator
- Binance API errors come back with the error code and message clearly shown
- Network timeouts and connection failures are caught separately so you get a useful message instead of a raw exception

---
## Tech Stack
- Python 3
- requests
- argparse
- python-dotenv

---
## Assumptions

- This runs against the Binance Futures Testnet only — no real money involved
- Position mode is one-way (the default on testnet)
- Limit orders use GTC (Good Till Cancelled) by default
- Quantity precision isn't auto-adjusted — use values that match the symbol's step size (0.001 works fine for BTCUSDT on testnet)

---

## Dependencies

Only two external libraries used:

- `requests` — for making HTTP calls to the Binance API
- `python-dotenv` — for loading credentials from the `.env` file

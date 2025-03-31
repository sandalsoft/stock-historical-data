# Stock Historical Data Fetcher

A Python utility for downloading historical stock price data from Yahoo Finance and storing it in a PostgreSQL database.

## Overview

This tool fetches historical stock data for specified ticker symbols over a one-year period and stores the information in a relational database for further analysis, visualization, or integration with other financial applications.

## Features

- Downloads stock price history for the past year
- Processes multiple stock symbols specified via an environment variable
- Efficient database connection handling (connects once per run)
- Stores comprehensive price data (open, high, low, close, volume, dividends, stock splits)
- Handles duplicate entries with conflict resolution (ON CONFLICT DO NOTHING)
- Uses environment variables for secure database configuration and symbol list

## Requirements

- Python 3.12 or higher
- PostgreSQL database
- Dependencies listed in `pyproject.toml`

## Installation

1. Clone this repository
2. Set up a Python virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the required dependencies
   ```bash
   pip install -e .
   ```

## Database Setup

Create a database table with the following schema:

```sql
CREATE TABLE IF NOT EXISTS stock_prices (
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    dividends DECIMAL(10,6) NOT NULL,
    stock_splits DECIMAL(10,6) NOT NULL,
    PRIMARY KEY (symbol, date)
);
```

## Configuration

Create a `.env` file in the project root by copying `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file and provide your database credentials and the list of stock symbols:

```dotenv
# .env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Comma-separated list of stock symbols to process
# Example: STOCK_SYMBOLS=AAPL,MSFT,GOOG,NVDA
STOCK_SYMBOLS=AAPL, JEF, AMZN, NVDA
```

**Important:** Ensure there are no extra spaces unless intended, although the script now trims whitespace around commas.

## Usage

Ensure your `.env` file is correctly configured with database details and the `STOCK_SYMBOLS` variable.

Run the program from the project root:

```bash
python src/main.py
```

The application will:

1. Read configuration from the `.env` file.
2. Connect to the configured PostgreSQL database once.
3. Download historical stock data for each symbol listed in `STOCK_SYMBOLS`.
4. Insert the data into the `stock_prices` table, avoiding duplicates.
5. Report on the number of records inserted/skipped/errored for each symbol.
6. Close the database connection.

## Project Structure

- `src/main.py` - Main script for data fetching and database operations
- `pyproject.toml` - Project dependencies and metadata
- `.env` - Database configuration and symbol list (not version controlled)
- `.env.example` - Example environment configuration
- `README.md` - This file

## License

[License information here]

## Contributing

[Contribution guidelines here]

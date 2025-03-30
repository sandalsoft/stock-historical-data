# Stock Historical Data Fetcher

A Python utility for downloading historical stock price data from Yahoo Finance and storing it in a PostgreSQL database.

## Overview

This tool fetches historical stock data for specified ticker symbols over a one-year period and stores the information in a relational database for further analysis, visualization, or integration with other financial applications.

## Features

- Downloads stock price history for the past year
- Processes multiple stock symbols in a single run
- Stores comprehensive price data (open, high, low, close, volume, dividends, stock splits)
- Handles duplicate entries with conflict resolution
- Uses environment variables for secure database configuration

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

Create a `.env` file in the project root with the following environment variables:

```
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## Usage

Run the program with one or more stock symbols as arguments:

```bash
python main.py AAPL MSFT GOOGL
```

The application will:

1. Connect to the configured PostgreSQL database
2. Download historical stock data for each symbol
3. Insert the data into the database, avoiding duplicates
4. Report on the number of records inserted/skipped

## Project Structure

- `main.py` - Main script for data fetching and database operations
- `pyproject.toml` - Project dependencies and metadata
- `.env` - Database configuration (not version controlled)
- `.env.example` - Example environment configuration

## License

[License information here]

## Contributing

[Contribution guidelines here]

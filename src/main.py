import os
import sys
import yfinance as yf
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file at the start
load_dotenv()


def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    if not all([db_name, db_user, db_password, db_host, db_port]):
        print("Error: Database environment variables DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT must be set.")
        sys.exit(1)

    print(f"Connecting to database {db_name}...")
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        print("Database connection successful.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)


def download_and_insert(symbol, conn):
    """
    Download historical stock prices for the past year and insert into PostgreSQL
    using the provided database connection.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL')
        conn: Active psycopg2 database connection.
    """
    print(f"Processing symbol: {symbol}")

    try:
        cur = conn.cursor()

        # Download historical data for the past year
        print(f"Downloading historical data for {symbol}...")
        stock = yf.Ticker(symbol)
        hist = stock.history(period='1y')  # '1y' gets data for the past year
        if hist.empty:
            print(f"No historical data found for {symbol}. Skipping.")
            cur.close()
            return
        print(f"Downloaded {len(hist)} data points for {symbol}.")

        # Insert each row into the stock_prices table
        print(f"Inserting data for {symbol} into the database...")
        inserted_count = 0
        skipped_count = 0
        error_count = 0
        for index, row in hist.iterrows():
            # Skip rows with NaN values in critical columns to prevent insertion errors
            if row[['Open', 'High', 'Low', 'Close', 'Volume']].isnull().any():
                print(
                    f"Skipping row for {symbol} on {index.date()} due to NaN values.")
                skipped_count += 1
                continue
            try:
                cur.execute("""
                    INSERT INTO stock_prices (symbol, date, open, high, low, close, volume, dividends, stock_splits)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, date) DO NOTHING
                """, (
                    symbol,
                    index.date(),           # Convert datetime to date
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume']),
                    float(row['Dividends']),
                    float(row['Stock Splits'])
                ))
                if cur.rowcount > 0:
                    inserted_count += 1
                else:
                    skipped_count += 1
            except (Exception, psycopg2.Error) as e:
                print(
                    f"Error inserting row for {symbol} on {index.date()}: {e}")
                conn.rollback()  # Rollback the single failed insert
                error_count += 1
                # It might be prudent to reconnect or handle specific errors differently
                # For now, we just count the error and continue with the next row

        # Commit the transaction for this symbol
        conn.commit()
        cur.close()
        print(
            f"Data insertion for {symbol} complete. Inserted: {inserted_count}, Skipped (conflict/NaN): {skipped_count}, Errors: {error_count}.")

    except Exception as e:
        print(f"An error occurred processing symbol {symbol}: {e}")
        # Rollback any changes for this symbol if an error occurred outside the row loop
        conn.rollback()


if __name__ == '__main__':
    # Get symbols from environment variable
    symbols_str = os.getenv('STOCK_SYMBOLS')
    if not symbols_str:
        print("Error: STOCK_SYMBOLS environment variable not set or empty.")
        print("Please set it with a comma-separated list of stock symbols (e.g., 'AAPL,MSFT,GOOG').")
        sys.exit(1)

    # Split the string by commas and trim whitespace from each symbol
    symbols = [symbol.strip().upper()
               for symbol in symbols_str.split(',') if symbol.strip()]
    print(f"Processing symbols from env var: {', '.join(symbols)}")

    if not symbols:
        print("No valid symbols found in STOCK_SYMBOLS environment variable.")
        sys.exit(1)

    db_connection = None
    try:
        db_connection = get_db_connection()
        for symbol in symbols:
            try:
                download_and_insert(symbol, db_connection)
            except Exception as e:
                # Catching exceptions during the processing of a single symbol
                print(f"Failed to process symbol {symbol}: {e}")
                # Ensure connection is rolled back if a symbol fails mid-processing
                if db_connection:
                    db_connection.rollback()
                # Decide whether to continue with the next symbol or exit
                # For now, let's continue
                continue
    finally:
        # Ensure the database connection is closed
        if db_connection:
            db_connection.close()
            print("Database connection closed.")

    print("All symbols processed.")

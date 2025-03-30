import os
import sys
import yfinance as yf
import psycopg2
from dotenv import load_dotenv


def download_and_insert(symbol):
    """
    Download historical stock prices for the past month and insert into PostgreSQL.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL')
    """
    print(f"Processing symbol: {symbol}")
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve database credentials
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    # Connect to PostgreSQL database
    print(f"Connecting to database {db_name}...")
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    cur = conn.cursor()
    print("Database connection successful.")

    # Download historical data for the past year
    print(f"Downloading historical data for {symbol}...")
    stock = yf.Ticker(symbol)
    # '1y' gets data for the past year
    hist = stock.history(period='1y')
    print(f"Downloaded {len(hist)} data points for {symbol}.")

    # Insert each row into the stock_prices table
    print(f"Inserting data for {symbol} into the database...")
    inserted_count = 0
    skipped_count = 0
    for index, row in hist.iterrows():
        try:
            cur.execute("""
                INSERT INTO stock_prices (symbol, date, open, high, low, close, volume, dividends, stock_splits)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, date) DO NOTHING
            """, (
                symbol,
                index.date(),           # Convert datetime to date
                # Convert NumPy types to Python native types
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
        except Exception as e:
            print(f"Error inserting row for {symbol} on {index.date()}: {e}")
            conn.rollback()  # Rollback the single failed insert if needed, or handle differently

    # Commit the transaction and clean up
    conn.commit()
    cur.close()
    conn.close()
    print(
        f"Data insertion for {symbol} complete. Inserted: {inserted_count}, Skipped (due to conflict): {skipped_count}.")
    print(f"Database connection closed for {symbol}.")


if __name__ == '__main__':
    # Check for command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <symbol1> [symbol2] ...")
        sys.exit(1)

    symbols = sys.argv[1:]  # Get all arguments after the script name
    print(f"Received symbols: {', '.join(symbols)}")

    for symbol in symbols:
        try:
            # Convert symbol to uppercase for consistency
            download_and_insert(symbol.upper())
        except Exception as e:
            print(f"Failed to process symbol {symbol}: {e}")

    print("All symbols processed.")

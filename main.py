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
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve database credentials
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    cur = conn.cursor()

    # Download historical data for the past month
    stock = yf.Ticker(symbol)
    # '1mo' gets approximately the past month
    hist = stock.history(period='1y')

    # Insert each row into the stock_prices table
    for index, row in hist.iterrows():
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

    # Commit the transaction and clean up
    conn.commit()
    cur.close()
    conn.close()
    print(f"Data for {symbol} inserted successfully.")


if __name__ == '__main__':
    # Check for command-line argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <symbol>")
        sys.exit(1)

    symbol = sys.argv[1]
    download_and_insert(symbol)

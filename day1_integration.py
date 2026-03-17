"""
Day 1 Integration - Fetch real data and store it!
"""

from stock_fetcher import StockFetcher
from stock_database import StockTable

print("="*70)
print("DAY 1 INTEGRATION - FETCH AND STORE")
print("="*70)

# Create fetcher and database
fetcher = StockFetcher()
db = StockTable("stocks.db")

# Fetch real stock data
print("\n--- Fetching real stock data ---")
symbols = ['AAPL', 'GOOGL', 'MSFT']
all_data = fetcher.get_multiple_stocks(symbols, days=30)

# Store in database
print("\n--- Storing in database ---")
for symbol, data in all_data.items():
    count = db.insert_dataframe(data, symbol)
    print(f"  {symbol}: {count} rows inserted")

print(f"\nTotal rows in database: {db.num_rows}")

# Query back
print("\n--- Querying AAPL data ---")
aapl_rows = list(db.select_by_symbol("AAPL"))
print(f"Found {len(aapl_rows)} AAPL rows")

# Show latest 5
print("\nLatest 5 AAPL prices:")
for row in aapl_rows[-5:]:
    print(f"  {row.date}: ${row.close:.2f}")

# Close
db.close()

print("\n" + "="*70)
print("✓ DAY 1 COMPLETE!")
print("✓ You fetched real stock data!")
print("✓ You stored it in your database!")
print("✓ You can query it back!")
print("="*70)
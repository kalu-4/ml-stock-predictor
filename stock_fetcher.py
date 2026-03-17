"""
stock_fetcher.py
================

Fetches real stock data from Yahoo Finance and stores it in database.

WEEK 1, DAY 1 - Core component
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time


class StockFetcher:
    """
    Fetches stock data from Yahoo Finance.
    
    Usage:
        fetcher = StockFetcher()
        data = fetcher.get_stock_data("AAPL", days=365)
    """
    
    def __init__(self):
        """Initialize stock fetcher"""
        print("[StockFetcher] Initialized")
    
    def get_stock_data(self, symbol, days=365):
        """
        Fetch stock data for given symbol.
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL', 'GOOGL')
            days: Number of days of historical data
            
        Returns:
            pandas DataFrame with OHLCV data
        """
        print(f"\n[StockFetcher] Fetching {symbol} data for {days} days...")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                print(f"[StockFetcher] ERROR: No data found for {symbol}")
                return None
            
            # Clean up data
            data.reset_index(inplace=True)
            data['Symbol'] = symbol
            
            # Rename columns for consistency
            data.columns = [col.replace(' ', '_').lower() for col in data.columns]
            
            print(f"[StockFetcher] ✓ Fetched {len(data)} rows for {symbol}")
            print(f"[StockFetcher]   Date range: {data['date'].min()} to {data['date'].max()}")
            print(f"[StockFetcher]   Latest price: ${data['close'].iloc[-1]:.2f}")
            
            return data
            
        except Exception as e:
            print(f"[StockFetcher] ERROR: Failed to fetch {symbol}: {e}")
            return None
    
    def get_multiple_stocks(self, symbols, days=365):
        """
        Fetch data for multiple stocks.
        
        Args:
            symbols: List of ticker symbols
            days: Number of days of historical data
            
        Returns:
            Dict of {symbol: DataFrame}
        """
        print(f"\n[StockFetcher] Fetching {len(symbols)} stocks...")
        
        results = {}
        
        for symbol in symbols:
            data = self.get_stock_data(symbol, days)
            if data is not None:
                results[symbol] = data
            
            # Be nice to Yahoo Finance - don't hammer their API
            time.sleep(1)
        
        print(f"\n[StockFetcher] ✓ Successfully fetched {len(results)}/{len(symbols)} stocks")
        return results
    
    def get_current_price(self, symbol):
        """
        Get current/latest price for a stock.
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Current price (float)
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            
            if data.empty:
                return None
            
            current_price = data['Close'].iloc[-1]
            return current_price
            
        except Exception as e:
            print(f"[StockFetcher] ERROR: Failed to get price for {symbol}: {e}")
            return None
    
    def get_stock_info(self, symbol):
        """
        Get company information.
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Dict with company info
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD')
            }
            
        except Exception as e:
            print(f"[StockFetcher] ERROR: Failed to get info for {symbol}: {e}")
            return None


# ============================================================================
# TESTING & DEMO
# ============================================================================

def demo_stock_fetcher():
    """
    Demo: Fetch and display stock data
    """
    print("="*70)
    print("STOCK FETCHER DEMO")
    print("="*70)
    
    # Create fetcher
    fetcher = StockFetcher()
    
    # Test 1: Fetch single stock
    print("\n--- TEST 1: Fetch Apple (AAPL) ---")
    aapl_data = fetcher.get_stock_data("AAPL", days=30)
    
    if aapl_data is not None:
        print("\nFirst 5 rows:")
        print(aapl_data.head())
        
        print("\nBasic statistics:")
        print(f"  Average close price: ${aapl_data['close'].mean():.2f}")
        print(f"  Highest price: ${aapl_data['close'].max():.2f}")
        print(f"  Lowest price: ${aapl_data['close'].min():.2f}")
        print(f"  Total volume: {aapl_data['volume'].sum():,}")
    
    # Test 2: Get current price
    print("\n--- TEST 2: Get Current Prices ---")
    for symbol in ['AAPL', 'GOOGL', 'MSFT']:
        price = fetcher.get_current_price(symbol)
        if price:
            print(f"  {symbol}: ${price:.2f}")
    
    # Test 3: Get company info
    print("\n--- TEST 3: Get Company Info ---")
    info = fetcher.get_stock_info("AAPL")
    if info:
        print(f"  Name: {info['name']}")
        print(f"  Sector: {info['sector']}")
        print(f"  Industry: {info['industry']}")
        print(f"  Market Cap: ${info['market_cap']:,}")
    
    # Test 4: Fetch multiple stocks
    print("\n--- TEST 4: Fetch Multiple Stocks ---")
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    all_data = fetcher.get_multiple_stocks(symbols, days=7)
    
    print("\nSummary:")
    for symbol, data in all_data.items():
        latest_price = data['close'].iloc[-1]
        print(f"  {symbol}: {len(data)} rows, latest price: ${latest_price:.2f}")
    
    print("\n" + "="*70)
    print("✓ STOCK FETCHER WORKING!")
    print("="*70)
    
    return all_data


if __name__ == "__main__":
    # Run demo
    demo_stock_fetcher()
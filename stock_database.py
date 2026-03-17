"""
stock_database.py
=================

Integrates stock data with your database from Project 1.

This shows how to adapt your database for a new use case!
"""

import struct
import os
from datetime import datetime


# ============================================================================
# STOCK ROW (Adapted from your Project 1 Row class)
# ============================================================================

class StockRow:
    """
    One row of stock data.
    
    Fields:
    - id: integer (auto-increment)
    - symbol: string (8 chars, e.g., "AAPL")
    - date: string (10 chars, "YYYY-MM-DD")
    - open: float (opening price)
    - high: float (highest price)
    - low: float (lowest price)
    - close: float (closing price)
    - volume: integer (trading volume)
    
    Total size: 4 + 8 + 10 + 4 + 4 + 4 + 4 + 4 = 42 bytes
    """
    
    def __init__(self, id, symbol, date, open_price, high, low, close, volume):
        """Create stock row"""
        self.id = id
        self.symbol = symbol[:8]  # Max 8 chars
        self.date = date[:10]  # YYYY-MM-DD
        self.open = float(open_price)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.volume = int(volume)
    
    @staticmethod
    def size():
        """Size of one row in bytes"""
        return 42  # 4 + 8 + 10 + 4 + 4 + 4 + 4 + 4
    
    def serialize(self):
        """Convert to bytes for storage"""
        # Pack all fields
        id_bytes = struct.pack('I', self.id)  # 4 bytes
        symbol_bytes = self.symbol.encode('utf-8').ljust(8, b'\x00')  # 8 bytes
        date_bytes = self.date.encode('utf-8').ljust(10, b'\x00')  # 10 bytes
        open_bytes = struct.pack('f', self.open)  # 4 bytes
        high_bytes = struct.pack('f', self.high)  # 4 bytes
        low_bytes = struct.pack('f', self.low)  # 4 bytes
        close_bytes = struct.pack('f', self.close)  # 4 bytes
        volume_bytes = struct.pack('I', self.volume)  # 4 bytes
        
        return (id_bytes + symbol_bytes + date_bytes + 
                open_bytes + high_bytes + low_bytes + 
                close_bytes + volume_bytes)
    
    @staticmethod
    def deserialize(data):
        """Convert bytes back to StockRow"""
        # Unpack all fields
        id_value = struct.unpack('I', data[0:4])[0]
        symbol = data[4:12].decode('utf-8').rstrip('\x00')
        date = data[12:22].decode('utf-8').rstrip('\x00')
        open_price = struct.unpack('f', data[22:26])[0]
        high = struct.unpack('f', data[26:30])[0]
        low = struct.unpack('f', data[30:34])[0]
        close = struct.unpack('f', data[34:38])[0]
        volume = struct.unpack('I', data[38:42])[0]
        
        return StockRow(id_value, symbol, date, open_price, 
                       high, low, close, volume)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'date': self.date,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }
    
    def __repr__(self):
        return (f"StockRow({self.id}, {self.symbol}, {self.date}, "
                f"O:{self.open:.2f}, H:{self.high:.2f}, "
                f"L:{self.low:.2f}, C:{self.close:.2f}, V:{self.volume})")


# ============================================================================
# STOCK PAGE (Adapted from your Project 1 Page class)
# ============================================================================

class StockPage:
    """
    One page holding multiple stock rows.
    
    Page size: 4096 bytes
    Row size: 42 bytes
    Rows per page: 4096 / 42 = 97 rows
    """
    
    PAGE_SIZE = 4096
    ROWS_PER_PAGE = PAGE_SIZE // StockRow.size()  # 97 rows
    
    def __init__(self):
        """Create empty page"""
        self.rows = []
        self.num_rows = 0
    
    def is_full(self):
        """Check if page is full"""
        return self.num_rows >= self.ROWS_PER_PAGE
    
    def insert_row(self, row):
        """Insert row into page"""
        if self.is_full():
            return False
        
        self.rows.append(row)
        self.num_rows += 1
        return True
    
    def get_row(self, row_num):
        """Get row by index"""
        if row_num >= self.num_rows:
            return None
        return self.rows[row_num]
    
    def serialize(self):
        """Convert page to bytes"""
        # Pack number of rows
        data = struct.pack('I', self.num_rows)
        
        # Pack each row
        for row in self.rows:
            data += row.serialize()
        
        # Pad to PAGE_SIZE
        data = data.ljust(self.PAGE_SIZE, b'\x00')
        
        return data
    
    @staticmethod
    def deserialize(data):
        """Convert bytes back to page"""
        page = StockPage()
        
        # Unpack number of rows
        num_rows = struct.unpack('I', data[0:4])[0]
        
        # Unpack each row
        offset = 4
        for i in range(num_rows):
            row_data = data[offset:offset + StockRow.size()]
            row = StockRow.deserialize(row_data)
            page.rows.append(row)
            offset += StockRow.size()
        
        page.num_rows = num_rows
        return page
    
    def __repr__(self):
        return f"StockPage(rows={self.num_rows}/{self.ROWS_PER_PAGE})"


# ============================================================================
# STOCK PAGER (Reuse logic from your Project 1)
# ============================================================================

class StockPager:
    """Manages pages in memory and on disk"""
    
    def __init__(self, filename):
        """Open/create database file"""
        self.filename = filename
        self.pages = {}  # Cache
        self.num_pages = 0
        
        if os.path.exists(filename):
            self.file = open(filename, 'r+b')
            file_size = os.path.getsize(filename)
            self.num_pages = file_size // StockPage.PAGE_SIZE
        else:
            self.file = open(filename, 'w+b')
            self.num_pages = 0
    
    def get_page(self, page_num):
        """Get page (from cache or disk)"""
        # Check cache
        if page_num in self.pages:
            return self.pages[page_num]
        
        # Load from disk or create new
        page = StockPage()
        
        if page_num < self.num_pages:
            self.file.seek(page_num * StockPage.PAGE_SIZE)
            data = self.file.read(StockPage.PAGE_SIZE)
            page = StockPage.deserialize(data)
        
        # Add to cache
        self.pages[page_num] = page
        return page
    
    def flush(self, page_num):
        """Write page to disk"""
        if page_num not in self.pages:
            return
        
        page = self.pages[page_num]
        data = page.serialize()
        
        self.file.seek(page_num * StockPage.PAGE_SIZE)
        self.file.write(data)
        self.file.flush()
        
        if page_num >= self.num_pages:
            self.num_pages = page_num + 1
    
    def close(self):
        """Close database"""
        for page_num in self.pages:
            self.flush(page_num)
        self.file.close()


# ============================================================================
# STOCK TABLE (High-level interface)
# ============================================================================

class StockTable:
    """
    Stock data table.
    
    Stores stock price history with efficient page-based storage.
    """
    
    def __init__(self, filename="stocks.db"):
        """Create/open stock table"""
        self.pager = StockPager(filename)
        self.num_rows = 0
        self.next_id = 1
        
        # Count existing rows
        for page_num in range(self.pager.num_pages):
            page = self.pager.get_page(page_num)
            self.num_rows += page.num_rows
            
            # Update next_id
            for row in page.rows:
                if row.id >= self.next_id:
                    self.next_id = row.id + 1
    
    def insert(self, symbol, date, open_price, high, low, close, volume):
        """Insert stock data"""
        # Calculate page number
        page_num = self.num_rows // StockPage.ROWS_PER_PAGE
        
        # Get page
        page = self.pager.get_page(page_num)
        
        # Create row
        row = StockRow(self.next_id, symbol, date, open_price, 
                      high, low, close, volume)
        
        # Insert
        if not page.insert_row(row):
            return False
        
        # Save to disk
        self.pager.flush(page_num)
        
        # Update counters
        self.num_rows += 1
        self.next_id += 1
        
        return True
    
    def insert_dataframe(self, df, symbol):
        """
        Insert pandas DataFrame of stock data.
        
        Args:
            df: DataFrame with columns: date, open, high, low, close, volume
            symbol: Stock symbol (e.g., 'AAPL')
        """
        print(f"[StockTable] Inserting {len(df)} rows for {symbol}...")
        
        count = 0
        for idx, row in df.iterrows():
            # Convert date to string
            if isinstance(row['date'], datetime):
                date_str = row['date'].strftime('%Y-%m-%d')
            else:
                date_str = str(row['date'])[:10]
            
            # Insert row
            success = self.insert(
                symbol=symbol,
                date=date_str,
                open_price=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=int(row['volume'])
            )
            
            if success:
                count += 1
        
        print(f"[StockTable] ✓ Inserted {count} rows")
        return count
    
    def select_all(self):
        """Get all rows"""
        for page_num in range(self.pager.num_pages):
            page = self.pager.get_page(page_num)
            for row in page.rows:
                yield row
    
    def select_by_symbol(self, symbol):
        """Get all rows for a symbol"""
        for row in self.select_all():
            if row.symbol == symbol:
                yield row
    
    def get_latest(self, symbol, n=10):
        """Get latest N rows for a symbol"""
        rows = list(self.select_by_symbol(symbol))
        return rows[-n:] if len(rows) >= n else rows
    
    def close(self):
        """Close table"""
        self.pager.close()
    
    def __repr__(self):
        return f"StockTable(rows={self.num_rows}, pages={self.pager.num_pages})"


# ============================================================================
# DEMO
# ============================================================================

def demo_stock_database():
    """Demo: Store and retrieve stock data"""
    print("="*70)
    print("STOCK DATABASE DEMO")
    print("="*70)
    
    # Create table
    print("\n--- Creating stock table ---")
    table = StockTable("demo_stocks.db")
    print(f"Table: {table}")
    
    # Insert test data
    print("\n--- Inserting test data ---")
    table.insert("AAPL", "2024-01-01", 180.50, 182.30, 179.80, 181.20, 50000000)
    table.insert("AAPL", "2024-01-02", 181.20, 183.50, 181.00, 182.90, 52000000)
    table.insert("AAPL", "2024-01-03", 182.90, 184.20, 182.50, 183.40, 48000000)
    
    table.insert("GOOGL", "2024-01-01", 140.20, 141.50, 139.80, 140.90, 25000000)
    table.insert("GOOGL", "2024-01-02", 140.90, 142.30, 140.50, 141.80, 26000000)
    
    print(f"Total rows: {table.num_rows}")
    
    # Query all data
    print("\n--- All stock data ---")
    for row in table.select_all():
        print(f"  {row}")
    
    # Query by symbol
    print("\n--- AAPL data only ---")
    for row in table.select_by_symbol("AAPL"):
        print(f"  {row}")
    
    # Get latest
    print("\n--- Latest 2 AAPL rows ---")
    latest = table.get_latest("AAPL", n=2)
    for row in latest:
        print(f"  {row}")
    
    # Close
    table.close()
    
    # Reopen and verify persistence
    print("\n--- Reopening database ---")
    table2 = StockTable("demo_stocks.db")
    print(f"Table after restart: {table2}")
    print(f"Data still there: {table2.num_rows} rows")
    table2.close()
    
    print("\n" + "="*70)
    print("✓ STOCK DATABASE WORKING!")
    print("="*70)


if __name__ == "__main__":
    demo_stock_database()
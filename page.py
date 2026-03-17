"""
page.py
=======

Page class - represents one 4KB page that holds multiple rows
"""

import struct
from constants import PAGE_SIZE  # Import PAGE_SIZE
from row import Row


class Page:
    """
    One page = 4KB chunk of data.
    
    Can hold up to 14 rows (Row.size() = 291 bytes each).
    """
    
    # Calculate rows per page
    ROWS_PER_PAGE = PAGE_SIZE // Row.size()  # 4096 // 291 = 14
    
    def __init__(self):
        """Create empty page"""
        self.rows = []
        self.num_rows = 0
    
    def is_full(self):
        """Check if page is full"""
        return self.num_rows >= self.ROWS_PER_PAGE
    
    def insert_row(self, row):
        """
        Insert row into page.
        
        Args:
            row: Row object to insert
            
        Returns:
            True if inserted, False if page full
        """
        if self.is_full():
            return False
        
        self.rows.append(row)
        self.num_rows += 1
        return True
    
    def get_row(self, row_num):
        """
        Get row by index within page.
        
        Args:
            row_num: Row index (0-13)
            
        Returns:
            Row object or None
        """
        if row_num >= self.num_rows:
            return None
        return self.rows[row_num]
    
    def serialize(self):
        """
        Convert page to bytes for disk storage.
        
        Format:
        [num_rows: 4 bytes][row1: 291 bytes][row2: 291 bytes]...
        
        Returns:
            bytes (exactly PAGE_SIZE = 4096 bytes)
        """
        # Pack number of rows (4 bytes)
        data = struct.pack('I', self.num_rows)
        
        # Serialize each row
        for row in self.rows:
            data += row.serialize()
        
        # Pad to PAGE_SIZE with zeros
        data = data.ljust(PAGE_SIZE, b'\x00')
        
        return data
    
    @staticmethod
    def deserialize(data):
        """
        Convert bytes back to Page object.
        
        Args:
            data: bytes (PAGE_SIZE = 4096 bytes)
            
        Returns:
            Page object
        """
        page = Page()
        
        # Read number of rows (first 4 bytes)
        num_rows = struct.unpack('I', data[0:4])[0]
        
        # Read each row
        offset = 4  # Start after num_rows
        for i in range(num_rows):
            row_data = data[offset:offset + Row.size()]
            row = Row.deserialize(row_data)
            page.rows.append(row)
            offset += Row.size()
        
        page.num_rows = num_rows
        return page
    
    def __repr__(self):
        return f"Page(rows={self.num_rows}/{self.ROWS_PER_PAGE})"
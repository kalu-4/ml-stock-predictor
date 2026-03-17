"""
table.py
========

Table class - manages collection of pages and rows
"""

from page import Page
from pager import Pager


class Table:
    """
    Database table with persistence.
    
    A table is a collection of pages stored in a file.
    """
    
    def __init__(self, filename):
        """
        Create/open table.
        
        Args:
            filename: Database file (e.g., 'users.db')
        """
        self.pager = Pager(filename)
        self.num_rows = 0
        
        # Count existing rows from all pages
        for page_num in range(self.pager.num_pages):
            page = self.pager.get_page(page_num)
            self.num_rows += page.num_rows
    
    def insert(self, row):
        """
        Insert row into table.
        
        Args:
            row: Row object to insert
            
        Returns:
            True if successful, False if failed
        """
        # Calculate which page to use
        page_num = self.num_rows // Page.ROWS_PER_PAGE
        
        # Get the page
        page = self.pager.get_page(page_num)
        
        # Try to insert
        if not page.insert_row(row):
            return False
        
        # Flush to disk
        self.pager.flush(page_num)
        
        # Increment counter
        self.num_rows += 1
        
        return True
    
    def select_all(self):
        """
        Get all rows in table.
        
        Yields rows one at a time (generator).
        """
        for page_num in range(self.pager.num_pages):
            page = self.pager.get_page(page_num)
            
            for row_num in range(page.num_rows):
                yield page.get_row(row_num)
    
    def get_row(self, row_id):
        """
        Get specific row by row number (0-indexed).
        
        Args:
            row_id: Row number (not the id field, but position)
            
        Returns:
            Row object or None
        """
        if row_id >= self.num_rows:
            return None
        
        # Calculate page and row within page
        page_num = row_id // Page.ROWS_PER_PAGE
        row_in_page = row_id % Page.ROWS_PER_PAGE
        
        # Get page
        page = self.pager.get_page(page_num)
        
        # Get row from page
        return page.get_row(row_in_page)
    
    def get_row_by_id(self, id_value):
        """
        Get row by its id field (linear search).
        
        Args:
            id_value: The value of the id field to search for
            
        Returns:
            Row object or None
        """
        # Search through all rows
        for row in self.select_all():
            if row.id == id_value:
                return row
        
        return None
    
    def close(self):
        """Close table and flush all changes to disk"""
        self.pager.close()
    
    def __repr__(self):
        return f"Table(rows={self.num_rows}, pages={self.pager.num_pages})"
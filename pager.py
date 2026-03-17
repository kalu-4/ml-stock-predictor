"""
pager.py
========

Pager class - manages pages in memory (cache) and on disk
"""

import os
from constants import PAGE_SIZE
from page import Page


class Pager:
    """
    Manages page cache and disk I/O.
    
    Keeps frequently used pages in memory (fast).
    Loads from disk only when needed (slow).
    """
    
    def __init__(self, filename):
        """
        Open database file (or create if doesn't exist).
        
        Args:
            filename: Database file path (e.g., 'users.db')
        """
        self.filename = filename
        self.pages = {}  # Cache: {page_num: Page}
        self.num_pages = 0
        
        # Check if file exists
        if os.path.exists(filename):
            # Open existing file for reading and writing
            self.file = open(filename, 'r+b')
            
            # Calculate number of pages
            file_size = os.path.getsize(filename)
            self.num_pages = file_size // PAGE_SIZE
        else:
            # Create new file
            self.file = open(filename, 'w+b')
            self.num_pages = 0
    
    def get_page(self, page_num):
        """
        Get page by number.
        
        Returns from cache if available, otherwise loads from disk.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            Page object
        """
        # Check cache first
        if page_num in self.pages:
            # Cache hit!
            return self.pages[page_num]
        
        # Cache miss - need to load from disk
        page = Page()
        
        if page_num < self.num_pages:
            # Page exists on disk - load it
            self.file.seek(page_num * PAGE_SIZE)
            data = self.file.read(PAGE_SIZE)
            page = Page.deserialize(data)
        
        # Add to cache
        self.pages[page_num] = page
        return page
    
    def flush(self, page_num):
        """
        Write page from cache to disk.
        
        IMPORTANT: Changes only become permanent after flush!
        
        Args:
            page_num: Page number to flush
        """
        if page_num not in self.pages:
            return
        
        page = self.pages[page_num]
        
        # Serialize page to bytes
        data = page.serialize()
        
        # Write to file
        self.file.seek(page_num * PAGE_SIZE)
        self.file.write(data)
        self.file.flush()  # Force OS to write to disk
        
        # Update num_pages if needed
        if page_num >= self.num_pages:
            self.num_pages = page_num + 1
    
    def close(self):
        """
        Close database file.
        
        Flushes all cached pages before closing.
        """
        # Flush all pages in cache
        for page_num in self.pages:
            self.flush(page_num)
        
        # Close file
        self.file.close()
    
    def __repr__(self):
        return f"Pager(file={self.filename}, pages={self.num_pages})"
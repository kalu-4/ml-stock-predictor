"""
row.py
======

Row class - represents one row in the database
"""

import struct
from constants import COLUMN_NAME_SIZE, COLUMN_EMAIL_SIZE


class Row:
    """
    One row in the database.
    
    Fields:
    - id: integer (4 bytes)
    - name: string (32 bytes max)
    - email: string (255 bytes max)
    """
    
    def __init__(self, id, name, email):
        """
        Create row.
        
        Args:
            id: integer ID
            name: string name (max 32 chars)
            email: string email (max 255 chars)
        """
        self.id = id
        self.name = name[:COLUMN_NAME_SIZE]  # Truncate if too long
        self.email = email[:COLUMN_EMAIL_SIZE]
    
    @staticmethod
    def size():
        """
        Calculate size of one row in bytes.
        
        Returns:
            291 bytes (4 + 32 + 255)
        """
        return 4 + COLUMN_NAME_SIZE + COLUMN_EMAIL_SIZE
    
    def serialize(self):
        """
        Convert row to bytes for disk storage.
        
        Returns:
            bytes (exactly 291 bytes)
        """
        # Pack id as unsigned integer (4 bytes)
        id_bytes = struct.pack('I', self.id)
        
        # Encode and pad name to 32 bytes
        name_bytes = self.name.encode('utf-8').ljust(COLUMN_NAME_SIZE, b'\x00')
        
        # Encode and pad email to 255 bytes
        email_bytes = self.email.encode('utf-8').ljust(COLUMN_EMAIL_SIZE, b'\x00')
        
        # Combine all bytes
        return id_bytes + name_bytes + email_bytes
    
    @staticmethod
    def deserialize(data):
        """
        Convert bytes back to Row object.
        
        Args:
            data: bytes (291 bytes)
            
        Returns:
            Row object
        """
        # Extract id (first 4 bytes)
        id_value = struct.unpack('I', data[0:4])[0]
        
        # Extract name (next 32 bytes)
        name_bytes = data[4:4 + COLUMN_NAME_SIZE]
        name = name_bytes.decode('utf-8').rstrip('\x00')
        
        # Extract email (next 255 bytes)
        email_bytes = data[4 + COLUMN_NAME_SIZE:4 + COLUMN_NAME_SIZE + COLUMN_EMAIL_SIZE]
        email = email_bytes.decode('utf-8').rstrip('\x00')
        
        return Row(id_value, name, email)
    
    def to_dict(self):
        """
        Convert row to dictionary.
        
        Returns:
            dict with id, name, email keys
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }
    
    def __repr__(self):
        """String representation for printing"""
        return f"({self.id}, {self.name}, {self.email})"
    
    def __eq__(self, other):
        """Check if two rows are equal"""
        if not isinstance(other, Row):
            return False
        return (self.id == other.id and 
                self.name == other.name and 
                self.email == other.email)
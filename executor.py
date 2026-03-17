"""
executor.py
===========

Query Executor - Runs SQL queries using all components
"""


class QueryExecutor:
    """
    Executes parsed SQL queries.
    
    Connects storage, indexes, and parser together.
    """
    
    def __init__(self, database):
        """
        Initialize executor.
        
        Args:
            database: Database instance
        """
        self.database = database
    
    def execute(self, query):
        """
        Execute any query type.
        
        Args:
            query: Parsed query object
            
        Returns:
            Query results
        """
        # Import query classes
        from parser_implementation import (
            SelectQuery,
            InsertQuery, 
            CreateTableQuery
        )
        
        if isinstance(query, SelectQuery):
            return self.execute_select(query)
        elif isinstance(query, InsertQuery):
            return self.execute_insert(query)
        elif isinstance(query, CreateTableQuery):
            return self.execute_create_table(query)
        else:
            raise Exception(f"Unknown query type: {type(query)}")
    
    def execute_select(self, query):
        """
        Execute SELECT query.
        
        Returns list of rows or dictionaries.
        """
        table_name = query.table_name
        
        # Check table exists
        if table_name not in self.database.tables:
            raise Exception(f"Table '{table_name}' does not exist")
        
        table = self.database.tables[table_name]
        results = []
        
        # Check if we can use index
        can_use_index = (
            query.where and 
            query.where.column == 'id' and 
            query.where.operator == '=' and
            table_name in self.database.indexes
        )
        
        if can_use_index:
            # INDEX SCAN
            print(f"[Executor] Using index on id")
            
            index = self.database.indexes[table_name]
            
            # Search index
            if isinstance(index, dict):
                # Simple dict index
                row_position = index.get(query.where.value)
                if row_position is not None:
                    row = table.get_row(row_position)
                    if row:
                        results.append(row)
            else:
                # B+ tree index
                row_position = index.search(query.where.value)
                if row_position is not None:
                    row = table.get_row(row_position)
                    if row:
                        results.append(row)
        else:
            # FULL TABLE SCAN
            print(f"[Executor] Full table scan on {table_name}")
            
            for row in table.select_all():
                # Apply WHERE filter if exists
                if query.where:
                    if not query.where.matches(row):
                        continue
                
                results.append(row)
        
        # Project columns
        if query.columns == ['*']:
            # Return all columns
            return results
        else:
            # Return only requested columns
            projected = []
            for row in results:
                # Get row as dictionary
                if hasattr(row, 'to_dict'):
                    row_dict = row.to_dict()
                else:
                    row_dict = {
                        'id': row.id,
                        'name': row.name,
                        'email': row.email
                    }
                
                # Project columns
                projected_row = {col: row_dict[col] for col in query.columns}
                projected.append(projected_row)
            
            return projected
    
    def execute_insert(self, query):
        """
        Execute INSERT query.
        
        Returns success message.
        """
        from row import Row
        
        table_name = query.table_name
        
        # Check table exists
        if table_name not in self.database.tables:
            raise Exception(f"Table '{table_name}' does not exist")
        
        table = self.database.tables[table_name]
        
        # Validate values
        if len(query.values) != 3:
            raise Exception("Expected 3 values (id, name, email)")
        
        # Create row
        id_val, name_val, email_val = query.values
        row = Row(id_val, name_val, email_val)
        
        # Insert into table
        success = table.insert(row)
        
        if not success:
            raise Exception("Failed to insert row")
        
        # Update index
        if table_name in self.database.indexes:
            index = self.database.indexes[table_name]
            row_position = table.num_rows - 1
            
            if isinstance(index, dict):
                # Simple dict index
                index[id_val] = row_position
            else:
                # B+ tree index
                index.insert(id_val, row_position)
            
            print(f"[Executor] Updated index: {id_val} -> row {row_position}")
        
        return f"Inserted 1 row into {table_name}"
    
    def execute_create_table(self, query):
        """
        Execute CREATE TABLE query.
        
        Returns success message.
        """
        from table import Table
        
        table_name = query.table_name
        
        # Check if table already exists
        if table_name in self.database.tables:
            raise Exception(f"Table '{table_name}' already exists")
        
        # Create table file
        filename = f"{table_name}.db"
        table = Table(filename)
        
        # Store in database
        self.database.tables[table_name] = table
        self.database.schemas[table_name] = query.columns
        
        # Create index on PRIMARY KEY
        for column in query.columns:
            if column.primary_key:
                print(f"[Executor] Creating B+ tree index on {column.name}")
                # Use simple dict for now (can upgrade to B+ tree later)
                self.database.indexes[table_name] = {}
        
        return f"Created table '{table_name}'"


class Database:
    """
    Main database class.
    
    Manages tables, indexes, schemas, and query execution.
    """
    
    def __init__(self, name="mydb"):
        """Initialize database"""
        self.name = name
        self.tables = {}       # {table_name: Table}
        self.indexes = {}      # {table_name: dict or BTree}
        self.schemas = {}      # {table_name: [Column, ...]}
        self.executor = QueryExecutor(self)
    
    def execute(self, query):
        """
        Execute parsed query.
        
        Args:
            query: Query object from Parser
            
        Returns:
            Query results
        """
        return self.executor.execute(query)
    
    def close(self):
        """Close all tables"""
        for table in self.tables.values():
            table.close()
    
    def __repr__(self):
        tables = list(self.tables.keys())
        return f"Database(name={self.name}, tables={tables})"


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("TESTING EXECUTOR")
    print("="*70)
    
    from parser_implementation import Lexer, Parser
    
    db = Database("testdb")
    
    # Test CREATE TABLE
    print("\n[TEST] CREATE TABLE")
    sql = "CREATE TABLE users (id INT PRIMARY KEY, name TEXT, email TEXT)"
    query = Parser(Lexer(sql).tokenize()).parse()
    result = db.execute(query)
    print(f"✓ {result}")
    
    # Test INSERT
    print("\n[TEST] INSERT")
    sql = "INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')"
    query = Parser(Lexer(sql).tokenize()).parse()
    result = db.execute(query)
    print(f"✓ {result}")
    
    # Test SELECT
    print("\n[TEST] SELECT")
    sql = "SELECT * FROM users"
    query = Parser(Lexer(sql).tokenize()).parse()
    results = db.execute(query)
    print(f"✓ Results: {results}")
    
    db.close()
    print("\n✓ Tests passed!")
import os
import sqlite3
import time
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.database_type = os.getenv('DATABASE_TYPE', 'sqlite')
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///./data/sample.db')
        self.engine: Engine  # type: ignore
        self.SessionLocal: sessionmaker  # type: ignore
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection"""
        try:
            self.engine = create_engine(self.database_url)
            self.SessionLocal = sessionmaker(bind=self.engine)
            assert self.engine is not None, "Database engine is not initialized."
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print(f"✅ Connected to {self.database_type} database")
            
            # Create sample data if using SQLite
            if self.database_type == 'sqlite':
                self._create_sample_data()
                
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def _create_sample_data(self):
        """Create sample database with test data"""
        try:
            assert self.engine is not None, "Database engine is not initialized."
            with self.engine.connect() as conn:
                # Create customers table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        city TEXT,
                        state TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create orders table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY,
                        customer_id INTEGER,
                        product_name TEXT NOT NULL,
                        quantity INTEGER DEFAULT 1,
                        price DECIMAL(10,2),
                        order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES customers (id)
                    )
                """))
                
                # Create products table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        category TEXT,
                        price DECIMAL(10,2),
                        stock_quantity INTEGER DEFAULT 0,
                        description TEXT
                    )
                """))
                
                # Insert sample customers
                conn.execute(text("""
                    INSERT OR IGNORE INTO customers (id, name, email, city, state) VALUES
                    (1, 'John Smith', 'john.smith@email.com', 'New York', 'NY'),
                    (2, 'Jane Doe', 'jane.doe@email.com', 'Los Angeles', 'CA'),
                    (3, 'Bob Johnson', 'bob.johnson@email.com', 'Chicago', 'IL'),
                    (4, 'Alice Brown', 'alice.brown@email.com', 'Houston', 'TX'),
                    (5, 'Charlie Wilson', 'charlie.wilson@email.com', 'Phoenix', 'AZ')
                """))
                
                # Insert sample products
                conn.execute(text("""
                    INSERT OR IGNORE INTO products (id, name, category, price, stock_quantity, description) VALUES
                    (1, 'Laptop', 'Electronics', 999.99, 50, 'High-performance laptop'),
                    (2, 'Smartphone', 'Electronics', 599.99, 100, 'Latest smartphone model'),
                    (3, 'Coffee Mug', 'Kitchen', 12.99, 200, 'Ceramic coffee mug'),
                    (4, 'Desk Chair', 'Furniture', 249.99, 25, 'Ergonomic office chair'),
                    (5, 'Book', 'Education', 19.99, 75, 'Programming guide')
                """))
                
                # Insert sample orders
                conn.execute(text("""
                    INSERT OR IGNORE INTO orders (id, customer_id, product_name, quantity, price, order_date) VALUES
                    (1, 1, 'Laptop', 1, 999.99, '2024-01-15'),
                    (2, 2, 'Smartphone', 2, 599.99, '2024-01-20'),
                    (3, 3, 'Coffee Mug', 3, 12.99, '2024-02-01'),
                    (4, 1, 'Desk Chair', 1, 249.99, '2024-02-15'),
                    (5, 4, 'Book', 2, 19.99, '2024-03-01'),
                    (6, 5, 'Smartphone', 1, 599.99, '2024-03-10'),
                    (7, 2, 'Coffee Mug', 5, 12.99, '2024-03-15')
                """))
                
                conn.commit()
                print("✅ Sample data created successfully")
                
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information"""
        try:
            assert self.engine is not None, "Database engine is not initialized."
            inspector = inspect(self.engine)
            schema_info = {
                "tables": [],
                "total_tables": 0
            }
            
            for table_name in inspector.get_table_names():
                columns = []
                for column in inspector.get_columns(table_name):
                    columns.append({
                        "name": column['name'],
                        "type": str(column['type']),
                        "nullable": column.get('nullable', True),
                        "primary_key": column.get('primary_key', False)
                    })
                
                # Get sample data
                sample_data = self._get_sample_data(table_name, limit=3)
                
                schema_info["tables"].append({
                    "table_name": table_name,
                    "columns": columns,
                    "sample_data": sample_data
                })
            
            schema_info["total_tables"] = len(schema_info["tables"])
            return schema_info
            
        except Exception as e:
            print(f"❌ Error getting schema info: {e}")
            return {"tables": [], "total_tables": 0}
    
    def _get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get sample data from a table"""
        try:
            assert self.engine is not None, "Database engine is not initialized."
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
                columns = result.keys()
                rows = result.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            print(f"❌ Error getting sample data for {table_name}: {e}")
            return []
    
    def execute_query(self, sql_query: str, limit: int = 100) -> Dict[str, Any]:
        """Execute a SQL query and return results"""
        start_time = time.time()
        
        try:
            assert self.engine is not None, "Database engine is not initialized."
            with self.engine.connect() as conn:
                # Add LIMIT if not present in SELECT queries
                if sql_query.strip().upper().startswith('SELECT') and 'LIMIT' not in sql_query.upper():
                    sql_query += f" LIMIT {limit}"
                
                result = conn.execute(text(sql_query))
                
                if result.returns_rows:
                    columns = result.keys()
                    rows = result.fetchall()
                    results = [dict(zip(columns, row)) for row in rows]
                    row_count = len(results)
                else:
                    results = []
                    row_count = result.rowcount if result.rowcount else 0
                
                execution_time = time.time() - start_time
                
                return {
                    "results": results,
                    "row_count": row_count,
                    "execution_time": execution_time,
                    "success": True,
                    "error": None
                }
                
        except SQLAlchemyError as e:
            execution_time = time.time() - start_time
            return {
                "results": [],
                "row_count": 0,
                "execution_time": execution_time,
                "success": False,
                "error": str(e)
            }
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            assert self.engine is not None, "Database engine is not initialized."
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def get_schema_context(self) -> str:
        """Get schema context for LLM prompt"""
        schema_info = self.get_schema_info()
        context = "Database Schema:\n\n"
        
        for table in schema_info["tables"]:
            context += f"Table: {table['table_name']}\n"
            context += "Columns:\n"
            
            for column in table['columns']:
                context += f"  - {column['name']} ({column['type']})"
                if column.get('primary_key'):
                    context += " [PRIMARY KEY]"
                if not column.get('nullable'):
                    context += " [NOT NULL]"
                context += "\n"
            
            if table.get('sample_data'):
                context += "\nSample Data:\n"
                for i, row in enumerate(table['sample_data'][:2], 1):
                    context += f"  Row {i}: {row}\n"
            
            context += "\n"
        
        return context


# Global database manager instance
db_manager = DatabaseManager()

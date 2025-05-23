"""
Database initialization script for NL2SQL Tool

This script manually initializes the database schema and populates it with sample data.
Normally this happens automatically when the application starts, but this script can be
used to reset the database or set up a custom schema.

Usage:
    python initialize_db.py [--reset]

Options:
    --reset    Delete existing database file and create a new one (SQLite only)
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Check if we need to modify the path to find app module
if not os.path.exists('app'):
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.database import DatabaseManager
except ImportError:
    print("❌ Error: Could not import DatabaseManager")
    print("💡 Make sure you're running this script from the project root directory")
    sys.exit(1)


def initialize_database(reset=False):
    """Initialize the database schema and sample data"""
    print("\n🔄 Initializing database...")
    
    # Handle SQLite reset option
    database_type = os.getenv('DATABASE_TYPE', 'sqlite')
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./data/sample.db')
    
    if reset and database_type == 'sqlite':
        # Extract file path from SQLite URL
        if database_url.startswith('sqlite:///'):
            db_path = database_url.replace('sqlite:///', '')
            
            # Handle both absolute and relative paths
            if not os.path.isabs(db_path):
                db_path = os.path.join(os.path.dirname(__file__), db_path)
            
            # Delete existing database file
            db_file = Path(db_path)
            if db_file.exists():
                print(f"🗑️ Deleting existing database file: {db_path}")
                try:
                    db_file.unlink()
                    
                    # Make sure parent directory exists
                    db_file.parent.mkdir(parents=True, exist_ok=True)
                    print("✅ Database file deleted successfully")
                except Exception as e:
                    print(f"❌ Error deleting database file: {e}")
                    return
    
    try:
        # Initialize database manager (this creates tables and sample data)
        start_time = time.time()
        db_manager = DatabaseManager()
        
        # Get schema info to verify tables were created
        schema = db_manager.get_schema_info()
        
        print(f"✅ Database initialized in {time.time() - start_time:.2f} seconds")
        print(f"📊 Created {schema['total_tables']} tables:")
        
        for table in schema["tables"]:
            print(f"   - {table['table_name']} ({len(table['columns'])} columns)")
            
            # Show sample data count
            if table.get('sample_data'):
                try:
                    count_result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table['table_name']}")
                    if count_result['success'] and count_result['results']:
                        count = count_result['results'][0]['count']
                        print(f"     ({count} rows)")
                except Exception:
                    pass
                
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Initialize database for NL2SQL Tool")
    parser.add_argument("--reset", action="store_true", help="Reset database (SQLite only)")
    args = parser.parse_args()
    
    print("\n🧠 NL2SQL Tool - Database Initialization")
    print("=" * 50)
    
    # Check environment setup
    if not os.path.exists('.env'):
        print("⚠️ Warning: .env file not found, using default settings")
        
        # Try to create .env from example
        if os.path.exists('.env.example'):
            print("📝 Creating .env file from .env.example...")
            with open('.env.example', 'r') as example_file:
                with open('.env', 'w') as env_file:
                    env_file.write(example_file.read())
            print("✅ Created .env file")
    
    # Initialize database
    initialize_database(args.reset)
    
    print("\n✨ Database initialization complete!")


if __name__ == "__main__":
    main()

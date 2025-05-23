import pytest
from app.database import DatabaseManager
from app.utils import validate_sql_syntax, format_sql_query


class TestDatabase:
    """Test database functionality"""
    
    def test_database_connection(self):
        """Test database connection"""
        db = DatabaseManager()
        assert db.test_connection() == True
    
    def test_get_schema_info(self):
        """Test schema information retrieval"""
        db = DatabaseManager()
        schema = db.get_schema_info()
        
        assert "tables" in schema
        assert "total_tables" in schema
        assert isinstance(schema["tables"], list)
        assert schema["total_tables"] >= 0
    
    def test_execute_simple_query(self):
        """Test simple query execution"""
        db = DatabaseManager()
        result = db.execute_query("SELECT 1 as test_column")
        
        assert result["success"] == True
        assert result["row_count"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["test_column"] == 1


class TestUtils:
    """Test utility functions"""
    
    def test_validate_sql_syntax_valid(self):
        """Test SQL validation with valid query"""
        sql = "SELECT * FROM customers WHERE city = 'New York'"
        result = validate_sql_syntax(sql)
        
        assert result["is_valid"] == True
        assert len(result["errors"]) == 0
    
    def test_validate_sql_syntax_invalid(self):
        """Test SQL validation with invalid query"""
        sql = "INVALID SQL QUERY"
        result = validate_sql_syntax(sql)
        
        assert result["is_valid"] == False
        assert len(result["errors"]) > 0
    
    def test_format_sql_query(self):
        """Test SQL formatting"""
        sql = "select * from customers where city='New York'"
        formatted = format_sql_query(sql)
        
        assert "SELECT" in formatted
        assert "FROM" in formatted
        assert "WHERE" in formatted


if __name__ == "__main__":
    pytest.main([__file__])

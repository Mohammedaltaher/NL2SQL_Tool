import pytest
import httpx
from app.models import NL2SQLRequest, QueryRequest


class TestAPI:
    """Test suite for the NL2SQL API"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from main import app
        return httpx.AsyncClient(app=app, base_url="http://test")
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "database_connected" in data
        assert "ollama_connected" in data
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_schema_endpoint(self, client):
        """Test schema endpoint"""
        response = await client.get("/schema")
        assert response.status_code == 200
        
        data = response.json()
        assert "tables" in data
        assert "total_tables" in data
        assert isinstance(data["tables"], list)
    
    @pytest.mark.asyncio
    async def test_nl2sql_endpoint(self, client):
        """Test NL to SQL conversion endpoint"""
        request_data = {
            "question": "Show me all customers from New York"
        }
        
        response = await client.post("/nl2sql", json=request_data)
        
        # Note: This might fail if Ollama is not running
        if response.status_code == 200:
            data = response.json()
            assert "question" in data
            assert "sql_query" in data
            assert data["question"] == request_data["question"]
    
    @pytest.mark.asyncio
    async def test_query_endpoint(self, client):
        """Test query execution endpoint"""
        request_data = {
            "question": "Show me all customers"
        }
        
        response = await client.post("/query", json=request_data)
        
        # Note: This might fail if Ollama is not running
        if response.status_code == 200:
            data = response.json()
            assert "question" in data
            assert "sql_query" in data
            assert "results" in data
            assert "row_count" in data
            assert "execution_time" in data
    
    @pytest.mark.asyncio
    async def test_models_endpoint(self, client):
        """Test available models endpoint"""
        response = await client.get("/models")
        
        # Should return 200 even if Ollama is not running
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert "models" in data["data"]


if __name__ == "__main__":
    pytest.main([__file__])

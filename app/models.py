from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class NL2SQLRequest(BaseModel):
    """Request model for natural language to SQL conversion"""
    question: str
    schema_context: Optional[str] = None


class NL2SQLResponse(BaseModel):
    """Response model for natural language to SQL conversion"""
    question: str
    sql_query: str
    explanation: Optional[str] = None
    confidence: Optional[float] = None


class QueryRequest(BaseModel):
    """Request model for executing queries"""
    question: str
    schema_context: Optional[str] = None
    limit: Optional[int] = 100


class QueryResponse(BaseModel):
    """Response model for query execution"""
    question: str
    sql_query: str
    results: List[Dict[str, Any]]
    row_count: int
    execution_time: float
    explanation: Optional[str] = None


class SchemaInfo(BaseModel):
    """Model for database schema information"""
    table_name: str
    columns: List[Dict[str, str]]
    sample_data: Optional[List[Dict[str, Any]]] = None


class DatabaseSchema(BaseModel):
    """Complete database schema model"""
    tables: List[SchemaInfo]
    total_tables: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database_connected: bool
    ollama_connected: bool
    timestamp: str

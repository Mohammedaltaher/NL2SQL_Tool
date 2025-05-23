"""
NL2SQL Tool - Natural Language to SQL conversion with LangChain and Ollama

This package contains the core functionality for the NL2SQL Tool,
including the database connection, LLM service, API models, and utilities.
"""

__version__ = "1.0.0"
__author__ = "NL2SQL Tool Team"

# Import core components for easy access
from app.database import db_manager
from app.llm_service import nl2sql_service
from app.models import NL2SQLRequest, NL2SQLResponse, QueryRequest, QueryResponse
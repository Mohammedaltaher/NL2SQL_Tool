import os
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.models import (
    NL2SQLRequest, NL2SQLResponse, QueryRequest, QueryResponse,
    DatabaseSchema, HealthResponse
)
from app.database import db_manager
from app.llm_service import nl2sql_service
from app.utils import (
    format_sql_query, validate_sql_syntax, format_query_results,
    generate_result_summary, create_error_response, create_success_response
)

# Initialize FastAPI app
app = FastAPI(
    title="NL2SQL Tool",
    description="Convert natural language to SQL queries using LangChain and Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    db_connected = db_manager.test_connection()
    ollama_connected = nl2sql_service.test_connection()
    
    status = "healthy" if db_connected and ollama_connected else "unhealthy"
    
    return HealthResponse(
        status=status,
        database_connected=db_connected,
        ollama_connected=ollama_connected,
        timestamp=datetime.now().isoformat()
    )


@app.get("/schema", response_model=DatabaseSchema)
async def get_database_schema():
    """Get database schema information"""
    try:
        schema_info = db_manager.get_schema_info()
        return DatabaseSchema(
            tables=schema_info["tables"],
            total_tables=schema_info["total_tables"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")


@app.post("/nl2sql", response_model=NL2SQLResponse)
async def convert_nl_to_sql(request: NL2SQLRequest):
    """Convert natural language to SQL query"""
    try:
        # Get schema context if not provided
        schema_context = request.schema_context
        if not schema_context:
            schema_context = db_manager.get_schema_context()
        
        # Generate SQL using LLM
        result = nl2sql_service.generate_sql(request.question, schema_context)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Format the SQL query
        formatted_sql = format_sql_query(result["sql_query"])
        
        # Validate SQL syntax
        validation = validate_sql_syntax(formatted_sql)
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Generated SQL has syntax errors: {', '.join(validation['errors'])}"
            )
        
        return NL2SQLResponse(
            question=request.question,
            sql_query=formatted_sql,
            explanation=result["explanation"],
            confidence=result["confidence"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert NL to SQL: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """Execute natural language query and return results"""
    try:
        # Get schema context if not provided
        schema_context = request.schema_context
        if not schema_context:
            schema_context = db_manager.get_schema_context()
        
        # Generate SQL using LLM
        nl2sql_result = nl2sql_service.generate_sql(request.question, schema_context)
        
        if not nl2sql_result["success"]:
            raise HTTPException(status_code=500, detail=nl2sql_result["error"])
        
        # Format and validate SQL
        formatted_sql = format_sql_query(nl2sql_result["sql_query"])
        validation = validate_sql_syntax(formatted_sql)
        
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Generated SQL has syntax errors: {', '.join(validation['errors'])}"
            )
        
        # Execute the query
        query_result = db_manager.execute_query(formatted_sql, limit=request.limit or 100)
        
        if not query_result["success"]:
            raise HTTPException(status_code=400, detail=f"Query execution failed: {query_result['error']}")
        
        # Format results
        formatted_results = format_query_results(query_result["results"])
        
        return QueryResponse(
            question=request.question,
            sql_query=formatted_sql,
            results=formatted_results,
            row_count=query_result["row_count"],
            execution_time=query_result["execution_time"],
            explanation=nl2sql_result["explanation"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute query: {str(e)}")


@app.post("/execute-sql")
async def execute_sql_directly(sql_query: str, limit: int = 100):
    """Execute SQL query directly (for advanced users)"""
    try:
        # Validate SQL syntax
        validation = validate_sql_syntax(sql_query)
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"SQL syntax errors: {', '.join(validation['errors'])}"
            )
        
        # Execute the query
        result = db_manager.execute_query(sql_query, limit=limit)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=f"Query execution failed: {result['error']}")
        
        # Format results
        formatted_results = format_query_results(result["results"])
        summary = generate_result_summary(formatted_results, result["execution_time"])
        
        return create_success_response({
            "sql_query": sql_query,
            "results": formatted_results,
            "row_count": result["row_count"],
            "execution_time": result["execution_time"],
            "summary": summary
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute SQL: {str(e)}")


@app.get("/models")
async def get_available_models():
    """Get available Ollama models"""
    try:
        models = nl2sql_service.get_available_models()
        return create_success_response({"models": models})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content=create_error_response("Endpoint not found", "not_found")
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content=create_error_response("Internal server error", "server_error")
    )


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    
    print("🚀 Starting NL2SQL Tool...")
    print(f"📊 Database: {db_manager.database_type}")
    print(f"🤖 LLM Model: {nl2sql_service.llm.model}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

import os
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.logger import logger
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
    logger.info("Serving main web interface")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("Performing health check")
    db_connected = db_manager.test_connection()
    ollama_connected = nl2sql_service.test_connection()
    
    status = "healthy" if db_connected and ollama_connected else "unhealthy"
    logger.info(f"Health check result: {status} (DB: {db_connected}, Ollama: {ollama_connected})")
    
    return HealthResponse(
        status=status,
        database_connected=db_connected,
        ollama_connected=ollama_connected,
        timestamp=datetime.now().isoformat()
    )


@app.get("/schema", response_model=DatabaseSchema)
async def get_database_schema():
    """Get database schema information"""
    logger.info("Fetching database schema")
    try:
        schema_info = db_manager.get_schema_info()
        logger.info(f"Successfully retrieved schema with {schema_info['total_tables']} tables")
        return DatabaseSchema(
            tables=schema_info["tables"],
            total_tables=schema_info["total_tables"]
        )
    except Exception as e:
        logger.error(f"Failed to get schema: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")


@app.post("/nl2sql", response_model=NL2SQLResponse)
async def convert_nl_to_sql(request: NL2SQLRequest):
    """Convert natural language to SQL query"""
    logger.info(f"Processing NL2SQL request: {request.question}")
    try:
        # Get schema context if not provided
        schema_context = request.schema_context
        if not schema_context:
            logger.debug("No schema context provided, fetching from database")
            schema_context = db_manager.get_schema_context()
        
        # Generate SQL using LLM
        logger.info("Generating SQL query using LLM")
        result = nl2sql_service.generate_sql(request.question, schema_context)
        
        if not result["success"]:
            logger.error(f"Failed to generate SQL: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Format the SQL query
        logger.debug("Formatting SQL query")
        formatted_sql = format_sql_query(result["sql_query"])
        
        # Validate SQL syntax
        logger.debug("Validating SQL syntax")
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
        logger.error(f"Error processing NL2SQL request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to convert NL to SQL: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """Execute natural language query and return results"""
    logger.info(f"Executing query: {request.question} with limit {request.limit}")
    try:
        # Get schema context if not provided
        schema_context = request.schema_context
        if not schema_context:
            logger.debug("No schema context provided, fetching from database")
            schema_context = db_manager.get_schema_context()
        
        # Generate SQL using LLM
        logger.info("Generating SQL query using LLM")
        nl2sql_result = nl2sql_service.generate_sql(request.question, schema_context)
        
        if not nl2sql_result["success"]:
            logger.error(f"Failed to generate SQL: {nl2sql_result['error']}")
            raise HTTPException(status_code=500, detail=nl2sql_result["error"])
        
        # Format and validate SQL
        logger.debug("Formatting SQL query")
        formatted_sql = format_sql_query(nl2sql_result["sql_query"])
        logger.debug("Validating SQL syntax")
        validation = validate_sql_syntax(formatted_sql)
        
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Generated SQL has syntax errors: {', '.join(validation['errors'])}"
            )
        
        # Execute the query
        logger.info("Executing SQL query")
        query_result = db_manager.execute_query(formatted_sql, limit=request.limit or 100)
        
        if not query_result["success"]:
            raise HTTPException(status_code=400, detail=f"Query execution failed: {query_result['error']}")
        
        # Format results
        logger.info(f"Query executed successfully, {query_result['row_count']} rows found")
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
        logger.error(f"Error executing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to execute query: {str(e)}")


@app.post("/execute-sql")
async def execute_sql_directly(sql_query: str, limit: int = 100):
    """Execute SQL query directly (for advanced users)"""
    logger.info(f"Executing SQL directly: {sql_query[:50]}... with limit {limit}")
    try:
        # Validate SQL syntax
        logger.debug("Validating SQL syntax")
        validation = validate_sql_syntax(sql_query)
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"SQL syntax errors: {', '.join(validation['errors'])}"
            )
        
        # Execute the query
        logger.info("Executing SQL query")
        result = db_manager.execute_query(sql_query, limit=limit)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=f"Query execution failed: {result['error']}")
        
        # Format results
        logger.info(f"SQL query executed successfully, {result['row_count']} rows found")
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
        logger.error(f"Error executing SQL directly: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to execute SQL: {str(e)}")


@app.get("/models")
async def get_available_models():
    """Get available Ollama models"""
    logger.info("Fetching available Ollama models")
    try:
        models = nl2sql_service.get_available_models()
        logger.info(f"Retrieved {len(models)} models")
        return create_success_response({"models": models})
    except Exception as e:
        logger.error(f"Failed to get models: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    logger.warning(f"404 Error: {request.url} not found")
    return JSONResponse(
        status_code=404,
        content=create_error_response("Endpoint not found", "not_found")
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"500 Error: Internal server error at {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=create_error_response("Internal server error", "server_error")
    )


@app.on_event("startup")
async def startup_event():
    """Handle application startup events"""
    logger.info("Starting NL2SQL Tool application")
    try:
        if db_manager.test_connection():
            logger.info("Successfully connected to database")
        else:
            logger.warning("Failed to connect to database")
        
        if nl2sql_service.test_connection():
            logger.info("Successfully connected to Ollama service")
        else:
            logger.warning("Failed to connect to Ollama service")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Handle application shutdown events"""
    logger.info("Shutting down NL2SQL Tool application")
    try:
        # Add any cleanup code here
        pass
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


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

import re
import json
from datetime import datetime
from typing import Dict, Any, List


def format_sql_query(sql_query: str) -> str:
    """Format SQL query for better readability"""
    # Basic SQL formatting
    sql_query = sql_query.strip()
    
    # Add line breaks for major SQL keywords
    keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY', 'HAVING']
    for keyword in keywords:
        sql_query = re.sub(f'\\b{keyword}\\b', f'\n{keyword}', sql_query, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    sql_query = re.sub(r'\n\s+', '\n', sql_query)
    sql_query = re.sub(r'\n+', '\n', sql_query)
    
    return sql_query.strip()


def validate_sql_syntax(sql_query: str) -> Dict[str, Any]:
    """Basic SQL syntax validation"""
    errors = []
    warnings = []
    
    # Check for basic SQL structure
    if not re.search(r'\bSELECT\b', sql_query, re.IGNORECASE):
        errors.append("Query must contain SELECT statement")
    
    if not re.search(r'\bFROM\b', sql_query, re.IGNORECASE):
        errors.append("Query must contain FROM clause")
    
    # Check for balanced parentheses
    if sql_query.count('(') != sql_query.count(')'):
        errors.append("Unbalanced parentheses in query")
    
    # Check for potential SQL injection patterns (basic)
    dangerous_patterns = [
        r';\s*DROP\s+TABLE',
        r';\s*DELETE\s+FROM',
        r';\s*UPDATE\s+.*\s+SET',
        r'UNION\s+.*\s+SELECT.*--'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, sql_query, re.IGNORECASE):
            errors.append("Potentially dangerous SQL pattern detected")
    
    # Performance warnings
    if not re.search(r'\bLIMIT\b', sql_query, re.IGNORECASE):
        warnings.append("Consider adding LIMIT clause for large datasets")
    
    if re.search(r'SELECT\s+\*', sql_query, re.IGNORECASE):
        warnings.append("Consider selecting specific columns instead of *")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def format_query_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format query results for display"""
    formatted_results = []
    
    for row in results:
        formatted_row = {}
        for key, value in row.items():
            # Format different data types
            if value is None:
                formatted_row[key] = "NULL"
            elif isinstance(value, datetime):
                formatted_row[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, (int, float)):
                formatted_row[key] = value
            else:
                formatted_row[key] = str(value)
        
        formatted_results.append(formatted_row)
    
    return formatted_results


def generate_result_summary(results: List[Dict[str, Any]], execution_time: float) -> str:
    """Generate a summary of query results"""
    if not results:
        return f"Query executed successfully in {execution_time:.3f}s but returned no results."
    
    row_count = len(results)
    column_count = len(results[0].keys()) if results else 0
    
    summary = f"Retrieved {row_count} row{'s' if row_count != 1 else ''} "
    summary += f"with {column_count} column{'s' if column_count != 1 else ''} "
    summary += f"in {execution_time:.3f} seconds."
    
    return summary


def sanitize_table_name(table_name: str) -> str:
    """Sanitize table name to prevent SQL injection"""
    # Only allow alphanumeric characters and underscores
    return re.sub(r'[^a-zA-Z0-9_]', '', table_name)


def extract_table_names(sql_query: str) -> List[str]:
    """Extract table names from SQL query"""
    # Simple regex to find table names after FROM and JOIN
    pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
    matches = re.findall(pattern, sql_query, re.IGNORECASE)
    
    # Remove duplicates and return
    return list(set(matches))


def convert_to_json_serializable(obj: Any) -> Any:
    """Convert objects to JSON serializable format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    else:
        return obj


def estimate_query_complexity(sql_query: str) -> str:
    """Estimate the complexity of a SQL query"""
    complexity_score = 0
    
    # Count various SQL constructs
    constructs = {
        'JOIN': 2,
        'SUBQUERY': 3,
        'UNION': 2,
        'GROUP BY': 1,
        'ORDER BY': 1,
        'HAVING': 2,
        'CASE': 1,
        'DISTINCT': 1
    }
    
    for construct, weight in constructs.items():
        count = len(re.findall(construct, sql_query, re.IGNORECASE))
        complexity_score += count * weight
    
    # Count subqueries
    subquery_count = sql_query.count('(') - sql_query.count(')')
    complexity_score += abs(subquery_count) * 3
    
    if complexity_score <= 2:
        return "Simple"
    elif complexity_score <= 5:
        return "Moderate"
    else:
        return "Complex"


def create_error_response(error_message: str, error_type: str = "general") -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "success": False,
        "error": {
            "message": error_message,
            "type": error_type,
            "timestamp": datetime.now().isoformat()
        }
    }


def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

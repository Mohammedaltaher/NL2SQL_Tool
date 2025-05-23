"""
Demo script for NL2SQL Tool

This script demonstrates how to use the NL2SQL Tool programmatically.
It sends a natural language question to the API and retrieves the SQL query and results.

Usage:
    python demo_query.py "your natural language question"

Example:
    python demo_query.py "Show me all customers from New York"
"""

import argparse
import json
import requests
import sys
import time
from datetime import datetime


# Configuration
API_BASE_URL = "http://localhost:8000"
DEFAULT_QUERY = "Show me customers who placed orders in the last 30 days"


def format_output(data, title):
    """Format output for display"""
    separator = "=" * 80
    print(f"\n{separator}")
    print(f"{title}")
    print(f"{separator}\n")
    
    # Pretty format json output
    return json.dumps(data, indent=2)


def run_query(question):
    """Send question to API and get SQL and results"""
    print(f"\n🔍 Sending query: '{question}'")
    
    try:
        # First, get the SQL query
        print("📝 Generating SQL query...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/nl2sql",
            json={"question": question}
        )
        response.raise_for_status()
        nl2sql_result = response.json()
        
        sql_time = time.time() - start_time
        print(f"✅ SQL generated in {sql_time:.2f} seconds")
        
        # Then, execute the query
        print("🔄 Executing SQL query...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question}
        )
        response.raise_for_status()
        query_result = response.json()
        
        execution_time = time.time() - start_time
        print(f"✅ Query executed in {execution_time:.2f} seconds")
        
        # Return results
        return {
            "sql": nl2sql_result["sql_query"],
            "explanation": nl2sql_result.get("explanation", ""),
            "confidence": nl2sql_result.get("confidence", 0),
            "results": query_result["results"],
            "row_count": query_result["row_count"],
            "execution_time": query_result["execution_time"],
        }
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API")
        print("💡 Make sure the NL2SQL Tool is running on http://localhost:8000")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error: {e}")
        print("💡 Check API response for more details")
        sys.exit(1)


def check_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            if health_data["status"] == "healthy":
                print("✅ API is running and healthy")
            else:
                print("⚠️ API is running but reporting issues:")
                if not health_data.get("database_connected", True):
                    print("   - Database connection problem")
                if not health_data.get("ollama_connected", True):
                    print("   - Ollama connection problem")
        else:
            print("⚠️ API health check returned unexpected status code")
    except:
        print("❌ API is not running or cannot be reached")
        print("💡 Start the API with: python main.py")
        sys.exit(1)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Demo script for NL2SQL Tool")
    parser.add_argument(
        "question", 
        nargs="?", 
        default=DEFAULT_QUERY,
        help="Natural language question to convert to SQL"
    )
    args = parser.parse_args()
    
    # Print header
    print("\n🧠 NL2SQL Tool Demo")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check API health
    check_health()
    
    # Run query
    result = run_query(args.question)
    
    # Display SQL query
    print(format_output({
        "sql_query": result["sql"],
        "explanation": result["explanation"],
        "confidence": f"{result['confidence'] * 100:.2f}%"
    }, "🔍 Generated SQL"))
    
    # Display results
    print(format_output({
        "row_count": result["row_count"],
        "execution_time": f"{result['execution_time']:.3f} seconds",
        "results": result["results"][:5],  # Show first 5 results
        "result_note": "Showing first 5 results..." if len(result["results"]) > 5 else ""
    }, "📊 Query Results"))
    
    print("\n✨ Demo completed successfully!")


if __name__ == "__main__":
    main()

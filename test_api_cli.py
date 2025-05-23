#!/usr/bin/env python
"""
Test script for NL2SQL Tool API

This script provides a simple way to test the API endpoints from the command line.
It includes commands for health check, schema retrieval, and natural language to SQL conversion.

Usage:
    python test_api.py [command] [arguments...]

Commands:
    health              Check API health
    schema              Get database schema
    nl2sql <question>   Convert natural language to SQL
    query <question>    Execute natural language query
    models              List available Ollama models

Example:
    python test_api.py nl2sql "Show me all customers from New York"
"""

import argparse
import json
import requests
import sys


# Configuration
API_BASE_URL = "http://localhost:8000"


def pretty_print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))


def check_health():
    """Check API health"""
    print("Checking API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        
        print("\nHealth Status:")
        pretty_print_json(data)
        
        # Check specific statuses
        if data["status"] == "healthy":
            print("\n✅ API is healthy")
        else:
            print("\n⚠️ API is reporting issues")
            
        return True
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API")
        print("💡 Make sure the NL2SQL Tool is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def get_schema():
    """Get database schema"""
    print("Getting database schema...")
    try:
        response = requests.get(f"{API_BASE_URL}/schema")
        response.raise_for_status()
        data = response.json()
        
        print(f"\nDatabase Schema ({data['total_tables']} tables):")
        
        # Print summary
        for table in data["tables"]:
            print(f"\n📊 Table: {table['table_name']}")
            print(f"   Columns: {len(table['columns'])}")
            if table.get('sample_data'):
                print(f"   Sample Rows: {len(table['sample_data'])}")
        
        # Ask if user wants detailed schema
        detailed = input("\nShow detailed schema? (y/n): ").lower() == "y"
        if detailed:
            pretty_print_json(data)
            
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def convert_nl_to_sql(question):
    """Convert natural language to SQL"""
    print(f"Converting natural language to SQL: '{question}'")
    try:
        response = requests.post(
            f"{API_BASE_URL}/nl2sql",
            json={"question": question}
        )
        response.raise_for_status()
        data = response.json()
        
        print("\nGenerated SQL:")
        print("=" * 80)
        print(data["sql_query"])
        print("=" * 80)
        
        if data.get("explanation"):
            print(f"\nExplanation: {data['explanation']}")
            
        if data.get("confidence") is not None:
            print(f"\nConfidence: {data['confidence'] * 100:.2f}%")
            
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def execute_query(question):
    """Execute natural language query"""
    print(f"Executing query: '{question}'")
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question}
        )
        response.raise_for_status()
        data = response.json()
        
        print("\nGenerated SQL:")
        print("=" * 80)
        print(data["sql_query"])
        print("=" * 80)
        
        print(f"\nResults: {data['row_count']} rows returned in {data['execution_time']:.3f}s")
        
        if data["results"]:
            print("\nData:")
            pretty_print_json(data["results"])
        else:
            print("\nNo results found")
            
        if data.get("explanation"):
            print(f"\nExplanation: {data['explanation']}")
            
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def list_models():
    """List available Ollama models"""
    print("Getting available Ollama models...")
    try:
        response = requests.get(f"{API_BASE_URL}/models")
        response.raise_for_status()
        data = response.json()
        
        if data.get("data", {}).get("models"):
            models = data["data"]["models"]
            print(f"\nAvailable models ({len(models)}):")
            for model in models:
                print(f"- {model}")
        else:
            print("\nNo models found or Ollama not connected")
            
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test script for NL2SQL Tool API")
    
    # Add commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Health check command
    subparsers.add_parser("health", help="Check API health")
    
    # Schema command
    subparsers.add_parser("schema", help="Get database schema")
    
    # NL2SQL command
    nl2sql_parser = subparsers.add_parser("nl2sql", help="Convert natural language to SQL")
    nl2sql_parser.add_argument("question", help="Natural language question")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Execute natural language query")
    query_parser.add_argument("question", help="Natural language question")
    
    # Models command
    subparsers.add_parser("models", help="List available Ollama models")
    
    args = parser.parse_args()
    
    # Print header
    print("\n🧠 NL2SQL Tool API Test Script")
    print("=" * 50)
    
    # Handle commands
    if args.command == "health":
        check_health()
    elif args.command == "schema":
        get_schema()
    elif args.command == "nl2sql":
        convert_nl_to_sql(args.question)
    elif args.command == "query":
        execute_query(args.question)
    elif args.command == "models":
        list_models()
    else:
        parser.print_help()
        
    print("\n✨ Test complete")


if __name__ == "__main__":
    main()

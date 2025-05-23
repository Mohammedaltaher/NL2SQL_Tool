import os
import requests
from typing import Optional, Dict, Any
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from .logger import logger  # Import logger

load_dotenv()


class OllamaLLM(LLM):
    """Custom Ollama LLM wrapper for LangChain"""
    
    base_url: str = "http://localhost:11434"
    model: str = "llama2"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama2')
        logger.info(f"OllamaLLM initialized with base_url={self.base_url}, model={self.model}")

    def _call(self, prompt: str, stop: Optional[list] = None, run_manager=None, **kwargs) -> str:
        """Call Ollama API"""
        logger.debug(f"Calling Ollama API with prompt: {prompt}")
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "stop": stop or []
                    }
                },
                timeout=120
            )
            logger.debug(f"Ollama API response status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"Ollama API result: {result}")
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.exception(f"Failed to call Ollama: {e}")
            raise Exception(f"Failed to call Ollama: {e}")

    @property
    def _llm_type(self) -> str:
        return "ollama"


class NL2SQLService:
    """Service for converting natural language to SQL using LangChain and Ollama"""
    
    def __init__(self):
        self.llm = OllamaLLM()
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup prompt templates for different tasks"""
        
        # SQL generation prompt
        self.sql_prompt = PromptTemplate(
            input_variables=["schema", "question"],
            template="""You are a SQL expert. Given the database schema and a natural language question, generate a precise SQL query.

Database Schema:
{schema}

Rules:
1. Generate ONLY the SQL query, no explanations or markdown
2. Use proper SQL syntax for the given schema
3. Include appropriate WHERE clauses, JOINs, and aggregate functions as needed
4. Use table and column names exactly as shown in the schema
5. For date queries, use appropriate date functions
6. Limit results to reasonable numbers (use LIMIT)
7. Do not include semicolon at the end

Question: {question}

SQL Query:"""
        )
        
        # Query explanation prompt
        self.explanation_prompt = PromptTemplate(
            input_variables=["sql_query", "question"],
            template="""Explain this SQL query in simple terms.

Original Question: {question}
SQL Query: {sql_query}

Provide a brief, clear explanation of what this query does:"""
        )
        
        # Setup chains
        self.sql_chain = LLMChain(llm=self.llm, prompt=self.sql_prompt)
        self.explanation_chain = LLMChain(llm=self.llm, prompt=self.explanation_prompt)
    
    def generate_sql(self, question: str, schema_context: str) -> Dict[str, Any]:
        """Generate SQL from natural language question"""
        logger.info(f"Generating SQL for question: {question}")
        try:
            # Generate SQL query
            sql_query = self.sql_chain.run(
                schema=schema_context,
                question=question
            )
            logger.debug(f"Raw SQL query generated: {sql_query}")
            # Clean up the SQL query
            sql_query = self._clean_sql_query(sql_query)
            logger.debug(f"Cleaned SQL query: {sql_query}")
            # Generate explanation
            explanation = self.explanation_chain.run(
                sql_query=sql_query,
                question=question
            )
            logger.debug(f"Explanation generated: {explanation}")
            # Calculate confidence based on query complexity and schema match
            confidence = self._calculate_confidence(sql_query, schema_context)
            logger.info(f"SQL generation successful. Confidence: {confidence}")
            return {
                "sql_query": sql_query,
                "explanation": explanation.strip(),
                "confidence": confidence,
                "success": True,
                "error": None
            }
        except Exception as e:
            logger.exception(f"Error generating SQL: {e}")
            return {
                "sql_query": "",
                "explanation": "",
                "confidence": 0.0,
                "success": False,
                "error": str(e)
            }
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """Clean and validate SQL query"""
        # Remove common prefixes/suffixes
        sql_query = sql_query.strip()
        
        # Remove markdown code blocks if present
        if sql_query.startswith('```'):
            lines = sql_query.split('\n')
            sql_query = '\n'.join(lines[1:-1]) if len(lines) > 2 else sql_query
        
        # Remove sql prefix if present
        if sql_query.lower().startswith('sql'):
            sql_query = sql_query[3:].strip()
        
        # Remove trailing semicolon
        if sql_query.endswith(';'):
            sql_query = sql_query[:-1]
        
        return sql_query.strip()
    
    def _calculate_confidence(self, sql_query: str, schema_context: str) -> float:
        """Calculate confidence score for the generated SQL"""
        confidence = 0.5  # Base confidence
        
        # Check if query contains SQL keywords
        sql_keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY']
        for keyword in sql_keywords:
            if keyword in sql_query.upper():
                confidence += 0.1
        
        # Check if table names from schema are used
        tables_in_schema = []
        for line in schema_context.split('\n'):
            if line.startswith('Table:'):
                table_name = line.split(':')[1].strip()
                tables_in_schema.append(table_name)
        
        for table in tables_in_schema:
            if table in sql_query:
                confidence += 0.1
        
        # Cap confidence at 1.0
        return min(confidence, 1.0)
    
    def test_connection(self) -> bool:
        """Test connection to Ollama"""
        logger.info("Testing connection to Ollama API...")
        try:
            response = requests.get(f"{self.llm.base_url}/api/tags", timeout=5)
            logger.debug(f"Ollama test connection status: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logger.exception(f"Ollama test connection failed: {e}")
            return False
    
    def get_available_models(self) -> list:
        """Get list of available models from Ollama"""
        logger.info("Fetching available models from Ollama API...")
        try:
            response = requests.get(f"{self.llm.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                logger.debug(f"Available models: {models}")
                return models
            logger.error(f"Failed to fetch models: {response.status_code}")
            return []
        except Exception as e:
            logger.exception(f"Error fetching models: {e}")
            return []


# Global service instance
nl2sql_service = NL2SQLService()

# 📋 NL2SQL Tool - Complete Step-by-Step Setup Guide

This guide will walk you through setting up and running the NL2SQL Tool from scratch.

---

## 🎯 Overview

The NL2SQL Tool converts natural language questions into SQL queries using:
- **LangChain** for LLM orchestration
- **Ollama** for local AI model hosting
- **FastAPI** for the web API
- **SQLAlchemy** for database operations

---

## ⚡ Quick Start (Automated Setup)

### Option 1: Run the Setup Script

1. **Open PowerShell as Administrator** (Windows) or Terminal (Mac/Linux)

2. **Navigate to the project directory:**
   ```powershell
   cd c:\Users\DMA\source\repos\NL2SQL_Tool
   ```

3. **Run the automated setup:**
   ```powershell
   python setup.py
   ```

4. **Start the application:**
   ```powershell
   .\start.bat    # Windows
   # or
   ./start.sh     # Mac/Linux
   ```

5. **Open your browser:**
   - Main Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

---

## 🔧 Manual Setup (Step-by-Step)

### Step 1: Install Prerequisites

#### 1.1 Install Python 3.8+
- Download from [python.org](https://python.org)
- Verify installation: `python --version`

#### 1.2 Install Ollama
1. Visit [ollama.ai](https://ollama.ai)
2. Download installer for your OS
3. Run the installer
4. Verify: `ollama --version`

### Step 2: Set Up the Environment

#### 2.1 Create Virtual Environment
```powershell
# Navigate to project directory
cd c:\Users\DMA\source\repos\NL2SQL_Tool

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1    # Windows PowerShell
# or
venv\Scripts\activate.bat      # Windows Command Prompt
# or
source venv/bin/activate       # Mac/Linux
```

#### 2.2 Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Configure the Database

#### 3.1 Using SQLite (Default - Recommended for Testing)
- No additional setup required
- Sample database is created automatically

#### 3.2 Using PostgreSQL (Optional)
1. Install PostgreSQL
2. Create a database
3. Update `.env` file:
   ```env
   DATABASE_TYPE=postgresql
   DATABASE_URL=postgresql://username:password@localhost:5432/dbname
   ```

#### 3.3 Using MySQL (Optional)
1. Install MySQL
2. Create a database
3. Install driver: `pip install pymysql`
4. Update `.env` file:
   ```env
   DATABASE_TYPE=mysql
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/dbname
   ```

### Step 4: Set Up Ollama AI Model

#### 4.1 Start Ollama Service
```powershell
ollama serve
```
Keep this terminal open.

#### 4.2 Download AI Model (in a new terminal)
```powershell
# Basic model (faster, less capable)
ollama pull llama2

# More capable models (larger, slower)
ollama pull codellama
ollama pull llama2:13b
```

#### 4.3 Verify Model Installation
```powershell
ollama list
```

### Step 5: Configure Environment Variables

#### 5.1 Copy Environment File
```powershell
copy .env.example .env    # Windows
# or
cp .env.example .env      # Mac/Linux
```

#### 5.2 Edit Configuration (Optional)
Open `.env` file and modify if needed:
```env
# Database settings
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./data/sample.db

# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# API settings
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 6: Start the Application

#### 6.1 Start the API Server
```powershell
python main.py
```

#### 6.2 Verify Everything is Working
Open these URLs in your browser:
- **Main Interface:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🎮 Using the Application

### Web Interface Usage

1. **Open** http://localhost:8000 in your browser

2. **Check Status Indicators:**
   - Green = Connected
   - Red = Disconnected

3. **Ask Questions:**
   - Enter natural language questions in the text area
   - Example: "Show me all customers from New York"

4. **Choose Action:**
   - **Generate SQL Only:** Creates SQL without executing
   - **Generate & Execute:** Creates and runs SQL query
   - **View Schema:** Shows database structure

### API Usage Examples

#### Convert Natural Language to SQL
```powershell
curl -X POST "http://localhost:8000/nl2sql" -H "Content-Type: application/json" -d "{\"question\": \"Show me all customers from New York\"}"
```

#### Execute Query and Get Results
```powershell
curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d "{\"question\": \"How many orders were placed last month?\"}"
```

#### Get Database Schema
```powershell
curl "http://localhost:8000/schema"
```

---

## 🧪 Testing the Setup

### Test 1: Health Check
```powershell
curl http://localhost:8000/health
```
Should return status information.

### Test 2: Schema Access
```powershell
curl http://localhost:8000/schema
```
Should return database table information.

### Test 3: Simple Query
1. Go to http://localhost:8000
2. Enter: "Show me all customers"
3. Click "Generate & Execute"
4. Should see SQL query and results

---

## 🐛 Troubleshooting

### Problem: Ollama Connection Error

**Symptoms:** "Ollama not connected" in status bar

**Solutions:**
1. Check if Ollama is running: `ollama list`
2. Start Ollama service: `ollama serve`
3. Verify model is installed: `ollama pull llama2`
4. Check Ollama URL in `.env` file

### Problem: Database Connection Error

**Symptoms:** "Database not connected" in status bar

**Solutions:**
1. Check database credentials in `.env`
2. Ensure database server is running
3. For SQLite, check if `data` directory exists
4. Try resetting: delete `data/sample.db` and restart

### Problem: Python Import Errors

**Symptoms:** Module not found errors

**Solutions:**
1. Activate virtual environment: `.\venv\Scripts\Activate.ps1`
2. Install requirements: `pip install -r requirements.txt`
3. Check Python version: `python --version` (needs 3.8+)

### Problem: PowerShell Execution Policy (Windows)

**Symptoms:** Cannot run scripts

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: Port Already in Use

**Symptoms:** "Port 8000 is already in use"

**Solutions:**
1. Kill existing process using port 8000
2. Change port in `.env`: `API_PORT=8001`
3. On Windows: `netstat -ano | findstr :8000`

---

## 🚀 Advanced Usage

### Using Different AI Models

1. **List available models:**
   ```powershell
   ollama list
   ```

2. **Download more capable models:**
   ```powershell
   ollama pull codellama:13b
   ollama pull llama2:70b
   ```

3. **Update model in `.env`:**
   ```env
   OLLAMA_MODEL=codellama:13b
   ```

### Running with Docker

1. **Build and run with Docker Compose:**
   ```powershell
   docker-compose up -d
   ```

2. **Access application:**
   - http://localhost:8000

### Adding Custom Database Schemas

1. **Update database connection in `.env`**
2. **Restart the application**
3. **Schema will be auto-discovered**

---

## 📊 Sample Queries to Try

Once the application is running, try these example questions:

### Basic Queries
- "Show me all customers"
- "How many products do we have?"
- "List all orders from today"

### Filtered Queries
- "Show me customers from New York"
- "Find products with price greater than 100"
- "Orders placed in the last 30 days"

### Aggregate Queries
- "What's the total sales amount?"
- "How many customers are from each state?"
- "Top 5 most expensive products"

### Join Queries
- "Show customers and their orders"
- "Products that have never been ordered"
- "Customer order history with totals"

---

## 🔒 Security Considerations

1. **Never use in production without:**
   - Proper authentication
   - Input validation
   - SQL injection protection
   - Rate limiting

2. **For development only:**
   - Default setup is for testing/demo purposes
   - No authentication required
   - Direct database access enabled

---

## 🤝 Getting Help

1. **Check the logs** for error messages
2. **Review the API documentation** at http://localhost:8000/docs
3. **Test individual components:**
   - Database: `python -c "from app.database import db_manager; print(db_manager.test_connection())"`
   - Ollama: `ollama list`

---

## 🎯 Next Steps

Once you have the basic setup working:

1. **Explore the API documentation** at `/docs`
2. **Try different AI models** for better performance
3. **Connect your own database** by updating `.env`
4. **Customize the prompts** in `app/llm_service.py`
5. **Add authentication** for production use

---

**🎉 Congratulations! You now have a fully functional NL2SQL Tool running locally.**

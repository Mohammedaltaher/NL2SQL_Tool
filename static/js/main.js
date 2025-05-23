// API Configuration
const API_BASE_URL = window.location.origin;

// DOM Elements
const questionInput = document.getElementById('question');
const generateSqlBtn = document.getElementById('generate-sql-btn');
const executeQueryBtn = document.getElementById('execute-query-btn');
const viewSchemaBtn = document.getElementById('view-schema-btn');
const loading = document.getElementById('loading');
const sqlResult = document.getElementById('sql-result');
const queryResult = document.getElementById('query-result');
const schemaResult = document.getElementById('schema-result');
const errorResult = document.getElementById('error-result');
const copySqlBtn = document.getElementById('copy-sql-btn');

// Status elements
const dbStatus = document.getElementById('db-status');
const ollamaStatus = document.getElementById('ollama-status');
const dbStatusText = document.getElementById('db-status-text');
const ollamaStatusText = document.getElementById('ollama-status-text');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    checkHealthStatus();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    generateSqlBtn.addEventListener('click', handleGenerateSQL);
    executeQueryBtn.addEventListener('click', handleExecuteQuery);
    viewSchemaBtn.addEventListener('click', handleViewSchema);
    copySqlBtn.addEventListener('click', handleCopySQL);
    
    // Example card clicks
    document.querySelectorAll('.example-card').forEach(card => {
        card.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            questionInput.value = question;
            questionInput.focus();
        });
    });
    
    // Enter key in textarea
    questionInput.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            handleExecuteQuery();
        }
    });
}

// Health Status Check
async function checkHealthStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        updateStatusIndicator(dbStatus, dbStatusText, data.database_connected, 'Connected', 'Disconnected');
        updateStatusIndicator(ollamaStatus, ollamaStatusText, data.ollama_connected, 'Connected', 'Disconnected');
        
    } catch (error) {
        console.error('Health check failed:', error);
        updateStatusIndicator(dbStatus, dbStatusText, false, 'Connected', 'Error');
        updateStatusIndicator(ollamaStatus, ollamaStatusText, false, 'Connected', 'Error');
    }
}

function updateStatusIndicator(statusElement, textElement, isConnected, connectedText, disconnectedText) {
    statusElement.classList.remove('connected', 'disconnected');
    statusElement.classList.add(isConnected ? 'connected' : 'disconnected');
    textElement.textContent = isConnected ? connectedText : disconnectedText;
}

// Generate SQL Only
async function handleGenerateSQL() {
    const question = questionInput.value.trim();
    if (!question) {
        showError('Please enter a question');
        return;
    }
    
    showLoading();
    hideResults();
    
    try {
        const response = await fetch(`${API_BASE_URL}/nl2sql`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate SQL');
        }
        
        const data = await response.json();
        displaySQLResult(data);
        
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Execute Query
async function handleExecuteQuery() {
    const question = questionInput.value.trim();
    if (!question) {
        showError('Please enter a question');
        return;
    }
    
    showLoading();
    hideResults();
    
    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to execute query');
        }
        
        const data = await response.json();
        displaySQLResult(data);
        displayQueryResult(data);
        
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// View Schema
async function handleViewSchema() {
    showLoading();
    hideResults();
    
    try {
        const response = await fetch(`${API_BASE_URL}/schema`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch schema');
        }
        
        const data = await response.json();
        displaySchemaResult(data);
        
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Copy SQL to clipboard
async function handleCopySQL() {
    const sqlCode = document.getElementById('sql-code');
    if (sqlCode) {
        try {
            await navigator.clipboard.writeText(sqlCode.textContent);
            
            // Visual feedback
            const originalText = copySqlBtn.textContent;
            copySqlBtn.textContent = 'Copied!';
            copySqlBtn.style.background = '#27ae60';
            
            setTimeout(() => {
                copySqlBtn.textContent = originalText;
                copySqlBtn.style.background = '';
            }, 2000);
            
        } catch (error) {
            console.error('Failed to copy SQL:', error);
            showError('Failed to copy SQL to clipboard');
        }
    }
}

// Display Functions
function displaySQLResult(data) {
    const sqlCode = document.getElementById('sql-code');
    const sqlExplanation = document.getElementById('sql-explanation');
    const sqlConfidence = document.getElementById('sql-confidence');
    
    sqlCode.textContent = data.sql_query;
    
    if (data.explanation) {
        sqlExplanation.innerHTML = `<strong>Explanation:</strong> ${data.explanation}`;
        sqlExplanation.style.display = 'block';
    } else {
        sqlExplanation.style.display = 'none';
    }
    
    if (data.confidence !== undefined) {
        displayConfidence(sqlConfidence, data.confidence);
    } else {
        sqlConfidence.style.display = 'none';
    }
    
    // Highlight syntax
    if (window.Prism) {
        Prism.highlightElement(sqlCode);
    }
    
    sqlResult.classList.remove('hidden');
}

function displayQueryResult(data) {
    const resultSummary = document.getElementById('result-summary');
    const resultTable = document.getElementById('result-table');
    const thead = resultTable.querySelector('thead');
    const tbody = resultTable.querySelector('tbody');
    
    // Display summary
    const executionTime = data.execution_time ? `${data.execution_time.toFixed(3)}s` : 'N/A';
    resultSummary.innerHTML = `
        <strong>Results:</strong> ${data.row_count} row${data.row_count !== 1 ? 's' : ''} 
        returned in ${executionTime}
    `;
    
    // Clear previous results
    thead.innerHTML = '';
    tbody.innerHTML = '';
    
    if (data.results && data.results.length > 0) {
        // Create table headers
        const headerRow = document.createElement('tr');
        Object.keys(data.results[0]).forEach(column => {
            const th = document.createElement('th');
            th.textContent = column;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        
        // Create table rows
        data.results.forEach(row => {
            const tr = document.createElement('tr');
            Object.values(row).forEach(value => {
                const td = document.createElement('td');
                td.textContent = value !== null ? value : 'NULL';
                if (value === null) {
                    td.style.fontStyle = 'italic';
                    td.style.color = '#999';
                }
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
    } else {
        tbody.innerHTML = '<tr><td colspan="100%" style="text-align: center; font-style: italic;">No results found</td></tr>';
    }
    
    queryResult.classList.remove('hidden');
}

function displaySchemaResult(data) {
    const schemaContent = document.getElementById('schema-content');
    
    let html = '';
    data.tables.forEach(table => {
        html += `
            <div class="schema-table">
                <div class="schema-table-header">
                    📊 Table: <strong>${table.table_name}</strong>
                </div>
                <div class="schema-columns">
                    ${table.columns.map(column => `
                        <div class="schema-column">
                            <span><strong>${column.name}</strong></span>
                            <span>${column.type}${column.primary_key ? ' 🔑' : ''}${!column.nullable ? ' ⚠️' : ''}</span>
                        </div>
                    `).join('')}
                </div>
                ${table.sample_data && table.sample_data.length > 0 ? `
                    <div style="padding: 1rem; background: #f8f9fa; border-top: 1px solid #e9ecef;">
                        <strong>Sample Data:</strong>
                        <pre style="margin-top: 0.5rem; font-size: 0.9rem;">${JSON.stringify(table.sample_data, null, 2)}</pre>
                    </div>
                ` : ''}
            </div>
        `;
    });
    
    if (html) {
        schemaContent.innerHTML = html;
    } else {
        schemaContent.innerHTML = '<p>No tables found in the database.</p>';
    }
    
    schemaResult.classList.remove('hidden');
}

function displayConfidence(element, confidence) {
    const percentage = Math.round(confidence * 100);
    const color = confidence < 0.5 ? '#e74c3c' : confidence < 0.8 ? '#f39c12' : '#27ae60';
    
    element.innerHTML = `
        <span><strong>Confidence:</strong> ${percentage}%</span>
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${percentage}%; background-color: ${color};"></div>
        </div>
    `;
    element.style.display = 'flex';
}

// Utility Functions
function showLoading() {
    loading.classList.remove('hidden');
    generateSqlBtn.disabled = true;
    executeQueryBtn.disabled = true;
    viewSchemaBtn.disabled = true;
}

function hideLoading() {
    loading.classList.add('hidden');
    generateSqlBtn.disabled = false;
    executeQueryBtn.disabled = false;
    viewSchemaBtn.disabled = false;
}

function hideResults() {
    sqlResult.classList.add('hidden');
    queryResult.classList.add('hidden');
    schemaResult.classList.add('hidden');
    errorResult.classList.add('hidden');
}

function showError(message) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    errorResult.classList.remove('hidden');
}

// Auto-refresh health status
setInterval(checkHealthStatus, 30000); // Check every 30 seconds

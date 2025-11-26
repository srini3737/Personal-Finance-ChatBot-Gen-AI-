// Personal Finance Chatbot - Frontend JavaScript

// API Base URL
const API_BASE = window.location.origin;

// Utility: Show loading state
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading"></div>';
    }
}

// Utility: Show error message
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div class="alert alert-error">${message}</div>`;
    }
}

// Utility: Fetch API wrapper
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Budget Summary Functions
async function submitBudget(event) {
    event.preventDefault();
    
    const incomeInput = document.getElementById('incomeData').value;
    const expensesInput = document.getElementById('expensesData').value;
    
    try {
        const income = JSON.parse(incomeInput);
        const expenses = JSON.parse(expensesInput);
        
        showLoading('budgetResult');
        
        const data = await fetchAPI('/api/budget-summary', {
            method: 'POST',
            body: JSON.stringify({ income, expenses })
        });
        
        displayBudgetSummary(data);
        
    } catch (error) {
        showError('budgetResult', `Error: ${error.message}`);
    }
}

function displayBudgetSummary(data) {
    const resultDiv = document.getElementById('budgetResult');
    
    const savingsColor = data.savings_rate >= 20 ? 'success' : 
                        data.savings_rate >= 10 ? 'warning' : 'danger';
    
    let html = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Budget Summary</h3>
            </div>
            
            <div class="grid grid-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <div class="stat-label">Total Income</div>
                    <div class="stat-value">$${data.total_income.toFixed(2)}</div>
                </div>
                
                <div class="stat-card" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">
                    <div class="stat-label">Total Expenses</div>
                    <div class="stat-value">$${data.total_expenses.toFixed(2)}</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Savings Rate</div>
                    <div class="stat-value">${data.savings_rate.toFixed(1)}%</div>
                </div>
            </div>
            
            <div class="mt-2">
                <h4>Category Breakdown</h4>
                <div class="chart-container">
                    <canvas id="categoryChart"></canvas>
                </div>
            </div>
            
            <div class="mt-2">
                <h4>Suggestions</h4>
                <ul class="suggestion-list">
                    ${data.suggestion_list.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
    
    resultDiv.innerHTML = html;
    
    // Create chart
    createCategoryChart(data.category_percentages);
}

function createCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    const labels = Object.keys(categories);
    const data = Object.values(categories);
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#4f46e5', '#10b981', '#f59e0b', '#ef4444', 
                    '#8b5cf6', '#06b6d4', '#ec4899', '#6366f1'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

// Spending Insights Functions
async function submitInsights(event) {
    event.preventDefault();
    
    const transactionsInput = document.getElementById('transactionsData').value;
    
    try {
        const transactions = JSON.parse(transactionsInput);
        
        showLoading('insightsResult');
        
        const data = await fetchAPI('/api/spending-insights', {
            method: 'POST',
            body: JSON.stringify({ transactions })
        });
        
        displayInsights(data);
        
    } catch (error) {
        showError('insightsResult', `Error: ${error.message}`);
    }
}

function displayInsights(data) {
    const resultDiv = document.getElementById('insightsResult');
    
    let html = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Spending Insights</h3>
            </div>
            
            <div class="mt-2">
                <h4>Top Spending Categories</h4>
                <div class="chart-container">
                    <canvas id="topCategoriesChart"></canvas>
                </div>
            </div>
            
            <div class="mt-2">
                <h4>Red Flags 🚩</h4>
                ${data.red_flags.length > 0 ? `
                    <ul class="suggestion-list">
                        ${data.red_flags.map(flag => `<li style="border-left-color: #ef4444;">${flag}</li>`).join('')}
                    </ul>
                ` : '<p>No red flags detected. Great job!</p>'}
            </div>
            
            <div class="mt-2">
                <h4>Recommendations 💡</h4>
                <ul class="suggestion-list">
                    ${data.recommendations.map(rec => `<li style="border-left-color: #10b981;">${rec}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
    
    resultDiv.innerHTML = html;
    
    // Create chart
    if (data.top_categories && data.top_categories.length > 0) {
        createTopCategoriesChart(data.top_categories);
    }
}

function createTopCategoriesChart(categories) {
    const ctx = document.getElementById('topCategoriesChart');
    if (!ctx) return;
    
    const labels = categories.map(c => c.category);
    const amounts = categories.map(c => c.amount);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Amount ($)',
                data: amounts,
                backgroundColor: '#4f46e5'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
}

// Chat Functions
let chatHistory = [];

async function sendMessage(event) {
    if (event) event.preventDefault();
    
    const input = document.getElementById('chatInput');
    const personaSelect = document.getElementById('personaSelect');
    const message = input.value.trim();
    
    if (!message) return;
    
    const persona = personaSelect ? personaSelect.value : null;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    chatHistory.push({ role: 'user', content: message });
    
    // Clear input
    input.value = '';
    
    // Show loading
    const loadingId = addMessageToChat('Thinking...', 'bot', true);
    
    try {
        const data = await fetchAPI('/api/generate', {
            method: 'POST',
            body: JSON.stringify({
                prompt: message,
                persona: persona,
                stream: false,
                max_tokens: 512
            })
        });
        
        // Remove loading message
        document.getElementById(loadingId).remove();
        
        // Add bot response
        addMessageToChat(data.answer, 'bot');
        chatHistory.push({ role: 'assistant', content: data.answer });
        
    } catch (error) {
        document.getElementById(loadingId).remove();
        addMessageToChat(`Error: ${error.message}`, 'bot');
    }
}

function addMessageToChat(text, sender, isLoading = false) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    const messageId = `msg-${Date.now()}`;
    
    messageDiv.id = messageId;
    messageDiv.className = `message message-${sender}`;
    messageDiv.textContent = text;
    
    if (isLoading) {
        messageDiv.innerHTML = '<div class="loading"></div>';
    }
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    return messageId;
}

// NLU Analysis
async function analyzeText(event) {
    event.preventDefault();
    
    const textInput = document.getElementById('nluText').value;
    const personaSelect = document.getElementById('nluPersona');
    const persona = personaSelect ? personaSelect.value : 'general';
    
    try {
        showLoading('nluResult');
        
        const data = await fetchAPI('/api/nlu', {
            method: 'POST',
            body: JSON.stringify({
                text: textInput,
                persona: persona
            })
        });
        
        displayNLUResult(data);
        
    } catch (error) {
        showError('nluResult', `Error: ${error.message}`);
    }
}

function displayNLUResult(data) {
    const resultDiv = document.getElementById('nluResult');
    
    const sentimentColor = data.sentiment === 'positive' ? 'success' : 
                          data.sentiment === 'negative' ? 'danger' : 'warning';
    
    let html = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Analysis Result</h3>
            </div>
            
            <div class="mb-2">
                <h4>Sentiment</h4>
                <span class="badge badge-${sentimentColor}">${data.sentiment.toUpperCase()}</span>
            </div>
            
            <div class="mb-2">
                <h4>Entities</h4>
                ${data.entities.length > 0 ? `
                    <div class="grid grid-2">
                        ${data.entities.map(e => `
                            <div class="card">
                                <strong>${e.type}:</strong> ${e.text} (${e.value})
                            </div>
                        `).join('')}
                    </div>
                ` : '<p>No entities detected</p>'}
            </div>
            
            <div>
                <h4>Keywords</h4>
                <div>
                    ${data.keywords.map(k => `<span class="badge badge-success">${k}</span>`).join(' ')}
                </div>
            </div>
        </div>
    `;
    
    resultDiv.innerHTML = html;
}

// Initialize page-specific functionality
document.addEventListener('DOMContentLoaded', function() {
    // Set active nav link
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('nav a').forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
    
    // Chat input enter key
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});

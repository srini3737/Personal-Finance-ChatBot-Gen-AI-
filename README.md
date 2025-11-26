# 💰 Personal Finance Chatbot Web App

A full-stack AI-powered personal finance assistant providing budget summaries, spending insights, and persona-aware financial advice.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │   Chat   │  │  Budget  │  │ Insights │   │
│  │(HTML/CSS)│  │   (JS)   │  │ (Chart.js│  │(Analysis)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
                 REST API (FastAPI)
                      │
        ┌─────────────┴─────────────┐
        │                           │
   ┌────▼────┐              ┌───────▼────────┐
   │ Routes  │              │   Services     │
   │ /api/*  │              │ Budget/Insights│
   └────┬────┘              └───────┬────────┘
        │                           │
        └───────────┬───────────────┘
                    │
            ┌───────▼────────┐
            │ Model Factory  │
            │ (DI Pattern)   │
            └───────┬────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
   ┌────▼────┐ ┌───▼────┐ ┌───▼────┐
   │  Groq   │ │ Ollama │ │  Mock  │
   │ Llama   │ │Granite │ │ Local  │
   │ 3.3 70B │ │  (IBM) │ │  Dev   │
   └─────────┘ └────────┘ └────────┘
    (Cloud)     (Local)    (No API)
```

## ✨ Features

- **🎯 Persona-Aware Advice**: Tailored financial guidance for students, salaried professionals, parents, freelancers, and retirees
- **📊 Budget Analysis**: Calculate savings rate, category breakdowns, and get actionable suggestions
- **🔍 Spending Insights**: Identify patterns, red flags, and optimization opportunities
- **💬 AI Chat Interface**: Ask financial questions and get intelligent responses
- **🤖 Multi-Model Support**: Groq (cloud), Ollama (local), or Mock (dev) LLM backends
- **📈 Visual Analytics**: Interactive charts powered by Chart.js
- **🔒 Environment-Based Config**: Separate local and production modes

## 🔀 Model Routing

The application uses **purpose-based LLM routing** to optimize performance and cost:

### Production Mode (`APP_ENV=prod`)

| Endpoint | Model | Purpose | Why? |
|----------|-------|---------|------|
| `/api/generate` (Chat/Q&A) | **IBM Granite** (via Ollama) | Conversational AI | Better for natural dialogue and persona-aware responses |
| `/api/budget-summary` | **Groq Llama 3.3 70B** | Financial analysis | Fast, accurate structured JSON output |
| `/api/spending-insights` | **Groq Llama 3.3 70B** | Pattern analysis | Excellent at identifying trends and anomalies |

### Local Mode (`APP_ENV=local`)

All endpoints use the **Mock Client** (deterministic responses, no API keys required) for lightweight development on 8GB laptops.

### Benefits

- **Optimized Performance**: Each model is used for what it does best
- **Cost Efficiency**: Groq's free tier for analysis, local Granite for chat
- **Flexibility**: Easy to switch models by changing environment variables
- **Privacy**: Chat data stays local with Ollama, analysis uses cloud API

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip
- (Optional) Groq API key for production
- (Optional) Ollama for local LLM

### Local Development Setup (Mock Mode - No API Keys)

```bash
# 1. Clone or navigate to the repository
cd finance-chatbot

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
copy .env.example .env

# 5. Set environment to local (uses mock LLM)
# Edit .env and set: APP_ENV=local

# 6. Run the application
uvicorn app.main:app --reload

# 7. Open browser
# Navigate to: http://localhost:8000
```

The application will start in **local mode** using the deterministic mock LLM client (no API keys required).

## 🔧 Production Setup

### Option 1: Groq Cloud API (Recommended for 8GB RAM)

```bash
# 1. Get Groq API key from: https://console.groq.com

# 2. Update .env file
APP_ENV=prod
GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# 3. Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Advantages**: 
- Minimal local memory usage (cloud-based)
- Fast inference
- No local GPU required

### Option 2: Ollama with IBM Granite (Local)

```bash
# 1. Install Ollama from: https://ollama.ai

# 2. Pull IBM Granite model (use quantized version for 8GB RAM)
ollama pull granite-code:8b

# 3. Update .env file
APP_ENV=prod
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=granite-code:8b

# 4. Ensure Ollama is running
ollama serve

# 5. Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Advantages**:
- Complete privacy (no data leaves your machine)
- No API costs
- Works offline

**Memory Tips for 8GB Laptop**:
- Use quantized models (4-bit or 8-bit)
- Close other applications
- Use Groq API instead for minimal memory footprint

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# http://localhost:8000

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📡 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Calls

#### 1. Budget Summary

```bash
curl -X POST http://localhost:8000/api/budget-summary \
  -H "Content-Type: application/json" \
  -d '{
    "income": {
      "Salary": 5000,
      "Freelance": 500
    },
    "expenses": {
      "Rent": 1200,
      "Groceries": 400,
      "Transportation": 200,
      "Entertainment": 150,
      "Utilities": 100
    }
  }'
```

**Response**:
```json
{
  "total_income": 5500.0,
  "total_expenses": 2050.0,
  "savings_rate": 62.73,
  "category_percentages": {
    "Rent": 58.54,
    "Groceries": 19.51,
    "Transportation": 9.76,
    "Entertainment": 7.32,
    "Utilities": 4.88
  },
  "suggestion_list": [
    "Excellent! Your savings rate of 62.7% is well above the recommended 20%.",
    "Rent takes up 58.5% of expenses - this is high but manageable with your income.",
    "Consider automating your savings to maintain this great rate."
  ]
}
```

#### 2. Generate Persona-Aware Advice

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How can I save money on a tight budget?",
    "persona": "student",
    "stream": false,
    "max_tokens": 512
  }'
```

**Response**:
```json
{
  "answer": "As a student, focus on building good financial habits early. Consider these tips: 1) Use student discounts whenever possible, 2) Cook meals instead of eating out, 3) Buy used textbooks or use library resources, 4) Start a small emergency fund even if it's just $20/month, 5) Avoid credit card debt - only spend what you have.",
  "model": "mock-local",
  "meta": {
    "persona": "student",
    "confidence": 0.95
  }
}
```

#### 3. Spending Insights

```bash
curl -X POST http://localhost:8000/api/spending-insights \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {
        "category": "Food",
        "amount": 450.00,
        "date": "2024-01-15",
        "merchant": "Grocery Store"
      },
      {
        "category": "Entertainment",
        "amount": 120.00,
        "date": "2024-01-20",
        "merchant": "Concert Venue"
      }
    ]
  }'
```

#### 4. NLU Analysis

```bash
curl -X POST http://localhost:8000/api/nlu \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I spent $500 on groceries last week",
    "persona": "student"
  }'
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_budget_summary.py -v

# Run linting
black app/ tests/
flake8 app/ tests/ --max-line-length=120
```

## 📁 Project Structure

```
finance-chatbot/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings & environment config
│   ├── models/
│   │   ├── base_model.py       # Abstract LLM interface
│   │   ├── groq_client.py      # Groq Llama 3.3 70B client
│   │   ├── ollama_granite.py   # IBM Granite via Ollama
│   │   ├── fallback_mock.py    # Mock client for dev
│   │   └── model_factory.py    # Dependency injection factory
│   ├── routes/
│   │   ├── budget.py           # Budget summary endpoint
│   │   ├── insights.py         # Spending insights endpoint
│   │   ├── nlu.py              # NLU analysis endpoint
│   │   └── generate.py         # Chat/advice endpoint
│   └── services/
│       ├── prompt_templates.py # Strict JSON prompts
│       ├── budget_service.py   # Budget logic
│       ├── insights_service.py # Insights logic
│       └── nlu_service.py      # NLU logic
├── frontend/
│   ├── index.html              # Dashboard
│   ├── chat.html               # Chat interface
│   ├── budget.html             # Budget summary page
│   ├── insights.html           # Spending insights page
│   ├── settings.html           # Settings & preferences
│   ├── styles.css              # Global styles
│   └── app.js                  # Frontend logic
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── test_budget_summary.py  # Budget tests
│   └── test_generate_integration.py # API tests
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── Dockerfile                  # Docker image
├── docker-compose.yml          # Docker Compose config
└── README.md                   # This file
```

## 💾 Memory Optimization Tips (8GB Laptop)

### Recommended Approach: Use Groq API
- **Memory Usage**: ~200MB (minimal)
- **Speed**: Fast (cloud inference)
- **Cost**: Free tier available
- **Setup**: Just add API key to `.env`

### Alternative: Quantized Local Models
If you prefer local inference:

```bash
# Use 4-bit quantized models
ollama pull granite-code:8b-q4_0

# Or 8-bit for better quality
ollama pull granite-code:8b-q8_0
```

### System Optimization
```bash
# Close unnecessary applications
# Disable browser extensions
# Use lightweight browser (Firefox/Edge)
# Monitor memory: Task Manager (Windows) or htop (Linux)
```

## 🔐 Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Use environment variables** for all secrets
3. **Rotate API keys** regularly
4. **Use HTTPS** in production
5. **Implement rate limiting** for public deployments
6. **Validate all inputs** (Pydantic handles this)

## 🚀 Deployment Strategies

### Cloud Platforms

#### Heroku
```bash
# Install Heroku CLI
heroku create finance-chatbot-app
heroku config:set APP_ENV=prod
heroku config:set GROQ_API_KEY=your_key
git push heroku main
```

#### Railway
```bash
# Connect GitHub repo
# Set environment variables in dashboard
# Deploy automatically on push
```

#### Google Cloud Run
```bash
gcloud run deploy finance-chatbot \
  --source . \
  --set-env-vars APP_ENV=prod,GROQ_API_KEY=your_key
```

## 🔄 Extendability

### Future Enhancements

#### 1. CSV Transaction Import
```python
# Add to app/routes/upload.py
@router.post("/api/upload-csv")
async def upload_transactions(file: UploadFile):
    df = pd.read_csv(file.file)
    transactions = df.to_dict('records')
    return await analyze_transactions(transactions)
```

#### 2. JWT Authentication
```python
# Add to app/routes/auth.py
from fastapi_jwt_auth import AuthJWT

@router.post("/api/login")
async def login(user: UserLogin, Authorize: AuthJWT = Depends()):
    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}
```

#### 3. Database Integration
```python
# Add SQLAlchemy models
from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    category = Column(String)
    amount = Column(Float)
```

#### 4. Real-time Notifications
```python
# Add WebSocket support
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Send real-time budget alerts
```

## 📊 Performance Benchmarks

| Model | Latency | Memory | Cost |
|-------|---------|--------|------|
| Groq Llama 3.3 70B | ~500ms | ~200MB | Free tier |
| Ollama Granite 8B | ~2-5s | ~4GB | Free |
| Mock Client | <10ms | ~50MB | Free |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Groq** for fast LLM inference
- **IBM** for Granite models
- **Ollama** for local LLM hosting
- **FastAPI** for the excellent web framework
- **Chart.js** for beautiful visualizations

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs`

---

**Built with ❤️ for better financial literacy**

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import ModelFactory


@pytest.fixture(autouse=True)
def reset_model_factory():
    """Reset model factory before each test."""
    ModelFactory.reset()
    yield
    ModelFactory.reset()


@pytest.fixture
def client():
    """Fixture for FastAPI test client."""
    return TestClient(app)


def test_generate_endpoint_basic(client):
    """Test basic generate endpoint functionality."""
    response = client.post(
        "/api/generate",
        json={
            "prompt": "How can I save money?",
            "persona": "student",
            "stream": False,
            "max_tokens": 256
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "answer" in data
    assert "model" in data
    assert "meta" in data
    assert len(data["answer"]) > 0


def test_generate_endpoint_personas(client):
    """Test different personas."""
    personas = ["student", "salaried", "parent", "freelancer", "retiree"]
    
    for persona in personas:
        response = client.post(
            "/api/generate",
            json={
                "prompt": "How should I budget my money?",
                "persona": persona,
                "stream": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["meta"]["persona"] == persona


def test_generate_endpoint_no_persona(client):
    """Test generate without specific persona."""
    response = client.post(
        "/api/generate",
        json={
            "prompt": "What is compound interest?",
            "stream": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data


def test_nlu_endpoint(client):
    """Test NLU analysis endpoint."""
    response = client.post(
        "/api/nlu",
        json={
            "text": "I spent $500 on groceries last week",
            "persona": "student"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "sentiment" in data
    assert "entities" in data
    assert "keywords" in data
    assert data["sentiment"] in ["positive", "negative", "neutral"]


def test_budget_summary_endpoint(client):
    """Test budget summary endpoint."""
    response = client.post(
        "/api/budget-summary",
        json={
            "income": {
                "Salary": 5000,
                "Freelance": 500
            },
            "expenses": {
                "Rent": 1200,
                "Food": 400,
                "Transport": 200
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total_income" in data
    assert "total_expenses" in data
    assert "savings_rate" in data
    assert "category_percentages" in data
    assert "suggestion_list" in data


def test_spending_insights_endpoint(client):
    """Test spending insights endpoint."""
    response = client.post(
        "/api/spending-insights",
        json={
            "transactions": [
                {
                    "category": "Food",
                    "amount": 45.50,
                    "date": "2024-01-15",
                    "merchant": "Grocery Store",
                    "description": "Weekly groceries"
                },
                {
                    "category": "Entertainment",
                    "amount": 60.00,
                    "date": "2024-01-16",
                    "merchant": "Movie Theater"
                }
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "top_categories" in data
    assert "red_flags" in data
    assert "recommendations" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "environment" in data
    assert "model" in data


def test_invalid_json_budget(client):
    """Test budget endpoint with invalid data."""
    response = client.post(
        "/api/budget-summary",
        json={
            "income": "not a dict",
            "expenses": {}
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_empty_transactions(client):
    """Test insights with empty transaction list."""
    response = client.post(
        "/api/spending-insights",
        json={
            "transactions": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "top_categories" in data


def test_model_name_in_response(client):
    """Test that model name is included in generate response."""
    response = client.post(
        "/api/generate",
        json={
            "prompt": "Test question",
            "stream": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "model" in data
    assert len(data["model"]) > 0

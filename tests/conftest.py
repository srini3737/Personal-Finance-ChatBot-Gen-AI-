import pytest


@pytest.fixture
def mock_llm_client():
    """Fixture that provides a mock LLM client for testing."""
    from app.models.fallback_mock import FallbackMockClient
    return FallbackMockClient()


@pytest.fixture
def sample_income():
    """Sample income data for testing."""
    return {
        "Salary": 5000,
        "Freelance": 500,
        "Investments": 200
    }


@pytest.fixture
def sample_expenses():
    """Sample expense data for testing."""
    return {
        "Rent": 1200,
        "Groceries": 400,
        "Transportation": 200,
        "Entertainment": 150,
        "Utilities": 100
    }


@pytest.fixture
def sample_transactions():
    """Sample transaction data for testing."""
    return [
        {
            "category": "Food",
            "amount": 450.00,
            "date": "2024-01-15",
            "merchant": "Grocery Store",
            "description": "Monthly groceries"
        },
        {
            "category": "Food",
            "amount": 85.00,
            "date": "2024-01-18",
            "merchant": "Restaurant"
        },
        {
            "category": "Entertainment",
            "amount": 120.00,
            "date": "2024-01-20",
            "merchant": "Concert Venue"
        },
        {
            "category": "Transportation",
            "amount": 200.00,
            "date": "2024-01-10",
            "merchant": "Gas Station"
        }
    ]

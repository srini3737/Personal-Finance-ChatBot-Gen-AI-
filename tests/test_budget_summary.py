import pytest
from app.services.budget_service import BudgetService
from app.models.fallback_mock import FallbackMockClient


@pytest.fixture
def mock_client():
    """Fixture for mock LLM client."""
    return FallbackMockClient()


@pytest.fixture
def budget_service(mock_client):
    """Fixture for budget service."""
    return BudgetService(mock_client)


@pytest.mark.asyncio
async def test_budget_summary_basic(budget_service):
    """Test basic budget summary generation."""
    income = {"Salary": 5000, "Freelance": 500}
    expenses = {"Rent": 1200, "Food": 400, "Transport": 200}
    
    result = await budget_service.generate_summary(income, expenses)
    
    assert "total_income" in result
    assert "total_expenses" in result
    assert "savings_rate" in result
    assert "category_percentages" in result
    assert "suggestion_list" in result
    
    assert result["total_income"] > 0
    assert result["total_expenses"] > 0
    assert isinstance(result["suggestion_list"], list)


@pytest.mark.asyncio
async def test_budget_summary_calculations(budget_service):
    """Test budget calculations are correct."""
    income = {"Salary": 5000}
    expenses = {"Rent": 1500, "Food": 500}
    
    result = await budget_service.generate_summary(income, expenses)
    
    # Verify totals
    assert result["total_income"] == 5000
    assert result["total_expenses"] == 2000
    
    # Verify savings rate: (5000 - 2000) / 5000 * 100 = 60%
    assert result["savings_rate"] == pytest.approx(60.0, rel=0.1)


@pytest.mark.asyncio
async def test_budget_summary_zero_income(budget_service):
    """Test handling of zero income edge case."""
    income = {}
    expenses = {"Rent": 1000}
    
    result = await budget_service.generate_summary(income, expenses)
    
    assert result["total_income"] == 0
    assert result["savings_rate"] == 0


@pytest.mark.asyncio
async def test_budget_summary_negative_savings(budget_service):
    """Test handling when expenses exceed income."""
    income = {"Salary": 2000}
    expenses = {"Rent": 1500, "Food": 800, "Other": 500}
    
    result = await budget_service.generate_summary(income, expenses)
    
    assert result["total_income"] == 2000
    assert result["total_expenses"] == 2800
    # Savings rate should be negative
    assert result["savings_rate"] < 0


@pytest.mark.asyncio
async def test_budget_category_percentages(budget_service):
    """Test category percentage calculations."""
    income = {"Salary": 5000}
    expenses = {
        "Rent": 1000,
        "Food": 500,
        "Transport": 250,
        "Entertainment": 250
    }
    
    result = await budget_service.generate_summary(income, expenses)
    
    # Category percentages should sum to approximately 100%
    total_percentage = sum(result["category_percentages"].values())
    assert total_percentage == pytest.approx(100.0, rel=0.1)


@pytest.mark.asyncio
async def test_budget_suggestions_present(budget_service):
    """Test that suggestions are provided."""
    income = {"Salary": 3000}
    expenses = {"Rent": 1200, "Food": 600, "Entertainment": 800}
    
    result = await budget_service.generate_summary(income, expenses)
    
    assert len(result["suggestion_list"]) > 0
    assert all(isinstance(s, str) for s in result["suggestion_list"])

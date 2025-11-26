"""
Prompt templates for strict JSON-only output from LLMs.
All prompts enforce valid JSON format with explicit schemas.
"""


def get_budget_summary_prompt(income_data: dict, expense_data: dict) -> str:
    """
    Generate prompt for budget summary analysis.
    
    Args:
        income_data: Dictionary with income sources and amounts
        expense_data: Dictionary with expense categories and amounts
    
    Returns:
        Prompt string enforcing strict JSON output
    """
    return f"""You are a financial analysis assistant. Analyze the following budget data and return ONLY valid JSON.

INPUT DATA:
Income: {income_data}
Expenses: {expense_data}

REQUIRED OUTPUT FORMAT (JSON ONLY, NO OTHER TEXT):
{{
  "total_income": <float>,
  "total_expenses": <float>,
  "savings_rate": <float percentage>,
  "category_percentages": {{
    "CategoryName": <float percentage>,
    ...
  }},
  "suggestion_list": [
    "<actionable suggestion 1>",
    "<actionable suggestion 2>",
    "<actionable suggestion 3>"
  ]
}}

EXAMPLE OUTPUT:
{{
  "total_income": 5000.0,
  "total_expenses": 3500.0,
  "savings_rate": 30.0,
  "category_percentages": {{
    "Housing": 35.0,
    "Food": 20.0,
    "Transportation": 15.0,
    "Entertainment": 10.0,
    "Utilities": 10.0,
    "Other": 10.0
  }},
  "suggestion_list": [
    "Your savings rate of 30% is excellent! Keep it up.",
    "Consider reducing entertainment expenses to increase savings.",
    "Housing takes up 35% of expenses - this is within recommended limits."
  ]
}}

CRITICAL RULES:
1. Return ONLY valid JSON
2. NO TEXT before or after the JSON
3. Calculate savings_rate as: ((total_income - total_expenses) / total_income) * 100
4. Category percentages should sum to 100%
5. Provide 3-5 actionable suggestions based on the data

OUTPUT (JSON ONLY):"""


def get_spending_insights_prompt(transactions: list) -> str:
    """
    Generate prompt for spending insights analysis.
    
    Args:
        transactions: List of transaction dictionaries
    
    Returns:
        Prompt string enforcing strict JSON output
    """
    return f"""You are a spending analysis assistant. Analyze the following transactions and return ONLY valid JSON.

INPUT TRANSACTIONS:
{transactions}

REQUIRED OUTPUT FORMAT (JSON ONLY, NO OTHER TEXT):
{{
  "top_categories": [
    {{
      "category": "<category name>",
      "amount": <float>,
      "percentage": <float>
    }},
    ...
  ],
  "red_flags": [
    "<concerning pattern 1>",
    "<concerning pattern 2>",
    ...
  ],
  "recommendations": [
    "<actionable recommendation 1>",
    "<actionable recommendation 2>",
    "<actionable recommendation 3>"
  ]
}}

EXAMPLE OUTPUT:
{{
  "top_categories": [
    {{
      "category": "Housing",
      "amount": 1225.0,
      "percentage": 35.0
    }},
    {{
      "category": "Food",
      "amount": 700.0,
      "percentage": 20.0
    }},
    {{
      "category": "Transportation",
      "amount": 525.0,
      "percentage": 15.0
    }}
  ],
  "red_flags": [
    "Entertainment spending increased 40% compared to average",
    "Multiple late-night food delivery charges detected",
    "Subscription services total $150/month - review for unused services"
  ],
  "recommendations": [
    "Set a monthly budget cap for entertainment at $300",
    "Meal prep on weekends to reduce food delivery costs",
    "Consider carpooling or public transit to reduce transportation costs"
  ]
}}

CRITICAL RULES:
1. Return ONLY valid JSON
2. NO TEXT before or after the JSON
3. Identify top 3-5 spending categories
4. Flag unusual patterns, overspending, or concerning trends
5. Provide 3-5 specific, actionable recommendations

OUTPUT (JSON ONLY):"""


def get_nlu_prompt(text: str) -> str:
    """
    Generate prompt for natural language understanding.
    
    Args:
        text: User input text to analyze
    
    Returns:
        Prompt string enforcing strict JSON output
    """
    return f"""You are a natural language understanding assistant for financial text. Analyze the following text and return ONLY valid JSON.

INPUT TEXT:
"{text}"

REQUIRED OUTPUT FORMAT (JSON ONLY, NO OTHER TEXT):
{{
  "sentiment": "<positive|negative|neutral>",
  "entities": [
    {{
      "type": "<MONEY|CATEGORY|DATE|MERCHANT|etc>",
      "value": "<normalized value>",
      "text": "<original text>"
    }},
    ...
  ],
  "keywords": ["<keyword1>", "<keyword2>", ...]
}}

EXAMPLE OUTPUT:
{{
  "sentiment": "neutral",
  "entities": [
    {{
      "type": "MONEY",
      "value": "500",
      "text": "$500"
    }},
    {{
      "type": "CATEGORY",
      "value": "groceries",
      "text": "groceries"
    }},
    {{
      "type": "DATE",
      "value": "2024-01-15",
      "text": "last week"
    }}
  ],
  "keywords": ["spent", "groceries", "money", "budget"]
}}

CRITICAL RULES:
1. Return ONLY valid JSON
2. NO TEXT before or after the JSON
3. Sentiment must be: positive, negative, or neutral
4. Extract all financial entities (amounts, categories, dates, merchants)
5. Include 3-7 relevant keywords

OUTPUT (JSON ONLY):"""


def get_persona_prompt(question: str, persona: str) -> str:
    """
    Generate persona-aware financial advice prompt.
    
    Args:
        question: User's financial question
        persona: User persona (student, salaried, parent, freelancer, retiree)
    
    Returns:
        Prompt string for persona-aware response
    """
    persona_contexts = {
        "student": "a college student with limited income, student loans, and learning to manage money",
        "salaried": "a salaried professional with steady income, employer benefits, and career growth",
        "parent": "a parent managing family finances, children's education, and long-term planning",
        "freelancer": "a freelancer with variable income, self-employment taxes, and irregular cash flow",
        "retiree": "a retiree living on fixed income, managing retirement savings, and healthcare costs"
    }
    
    context = persona_contexts.get(persona, "an individual seeking financial advice")
    
    return f"""You are a personal finance advisor. The user is {context}.

USER QUESTION:
"{question}"

Provide tailored financial advice considering their specific situation. Be practical, empathetic, and actionable.

REQUIRED OUTPUT FORMAT (JSON ONLY, NO OTHER TEXT):
{{
  "answer": "<detailed, persona-specific financial advice>",
  "persona_context": "{persona}",
  "confidence": <float between 0 and 1>
}}

EXAMPLE OUTPUT:
{{
  "answer": "As a student, focus on building good financial habits early. Consider these tips: 1) Use student discounts whenever possible, 2) Cook meals instead of eating out to save $200+/month, 3) Buy used textbooks or use library resources, 4) Start a small emergency fund even if it's just $20/month, 5) Avoid credit card debt - only spend what you have. Many students find success with the envelope budgeting method for discretionary spending.",
  "persona_context": "student",
  "confidence": 0.95
}}

CRITICAL RULES:
1. Return ONLY valid JSON
2. NO TEXT before or after the JSON
3. Tailor advice specifically to the {persona} persona
4. Provide 3-7 concrete, actionable tips
5. Be empathetic and understanding of their unique challenges

OUTPUT (JSON ONLY):"""


def get_general_prompt(question: str) -> str:
    """
    Generate general financial advice prompt.
    
    Args:
        question: User's financial question
    
    Returns:
        Prompt string for general advice
    """
    return f"""You are a helpful personal finance assistant. Answer the following question with accurate, actionable advice.

USER QUESTION:
"{question}"

Provide clear, practical financial guidance. Use specific examples and numbers when helpful.

REQUIRED OUTPUT FORMAT (JSON ONLY, NO OTHER TEXT):
{{
  "answer": "<detailed financial advice>",
  "confidence": <float between 0 and 1>
}}

EXAMPLE OUTPUT:
{{
  "answer": "Here are proven strategies to build an emergency fund: 1) Start small - aim for $500 first, then work toward 3-6 months of expenses, 2) Automate savings - set up automatic transfers on payday, 3) Use a high-yield savings account (currently 4-5% APY), 4) Save windfalls like tax refunds or bonuses, 5) Cut one discretionary expense and redirect that money to savings. Most people find success by treating savings as a non-negotiable 'bill' that gets paid first.",
  "confidence": 0.90
}}

CRITICAL RULES:
1. Return ONLY valid JSON
2. NO TEXT before or after the JSON
3. Provide specific, actionable advice
4. Use concrete examples and numbers
5. Be accurate and responsible with financial guidance

OUTPUT (JSON ONLY):"""

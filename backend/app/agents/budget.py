"""Fortuna — The Budget Tracker Agent.

Tracks event finances, analyzes spending patterns, and generates alerts.
Falls back to simple arithmetic if LLM is unavailable.
"""
from ..models.schemas import BudgetSummary, BudgetItem
from .llm_helper import call_llm_json
import json


async def get_budget_analysis(items: list[BudgetItem]) -> BudgetSummary:
    """Analyze budget items and generate financial summary with warnings.
    
    Args:
        items: List of BudgetItem objects from the database.
    
    Returns:
        BudgetSummary with totals, items, and AI-generated warnings.
    """
    total_revenue = sum(i.amount for i in items if i.type == "revenue")
    total_expenses = sum(i.amount for i in items if i.type == "expense")
    net_balance = total_revenue - total_expenses

    # Build expense breakdown for LLM
    expense_by_cat = {}
    for i in items:
        if i.type == "expense":
            expense_by_cat[i.category] = expense_by_cat.get(i.category, 0) + i.amount

    prompt = f"""You are Fortuna, the financial intelligence for TechSummit 2026.

Analyze this budget and provide warnings/recommendations:

Total Revenue: ₹{total_revenue:,.0f}
Total Expenses: ₹{total_expenses:,.0f}
Net Balance: ₹{net_balance:,.0f}

Expense Breakdown:
{json.dumps(expense_by_cat, indent=2)}

Revenue Sources:
{json.dumps([{"desc": i.description, "amount": i.amount} for i in items if i.type == "revenue"], indent=2)}

Provide warnings as a JSON array of strings. Focus on:
1. Budget utilization (% spent)
2. Category-level overspends
3. Revenue gaps
4. Cost optimization suggestions

Example: ["Venue costs represent 54% of total expenses. Consider negotiating a package deal.", "Only 3 sponsors confirmed. Target 1-2 more for safety margin."]"""

    # Fallback warnings based on simple rules
    fallback_warnings = []
    
    utilization = (total_expenses / max(total_revenue, 1)) * 100
    if utilization > 80:
        fallback_warnings.append(
            f"⚠️ Budget utilization at {utilization:.0f}%. Only ₹{net_balance:,.0f} remaining."
        )
    elif utilization > 60:
        fallback_warnings.append(
            f"Budget utilization at {utilization:.0f}%. ₹{net_balance:,.0f} remaining — on track."
        )

    if expense_by_cat.get("Venue", 0) > total_expenses * 0.4:
        venue_pct = expense_by_cat["Venue"] / total_expenses * 100
        fallback_warnings.append(
            f"Venue costs are {venue_pct:.0f}% of total expenses. Consider negotiating bulk rates."
        )

    if net_balance < 0:
        fallback_warnings.append(
            f"🚨 DEFICIT: Expenses exceed revenue by ₹{abs(net_balance):,.0f}. Immediate action needed."
        )

    if not fallback_warnings:
        fallback_warnings.append("Budget is healthy. All categories within expected ranges.")

    result = await call_llm_json(prompt, fallback_warnings)

    warnings = result if isinstance(result, list) else fallback_warnings

    return BudgetSummary(
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        net_balance=net_balance,
        items=items,
        warnings=[str(w) for w in warnings]
    )

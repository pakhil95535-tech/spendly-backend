from app.config import settings
from app.schemas.ai import InsightRequest

async def get_insights(data: InsightRequest) -> str:
    if not settings.ANTHROPIC_API_KEY:
        return "1. Set your ANTHROPIC_API_KEY in .env to enable AI insights.\n2. Track your expenses daily.\n3. Set a monthly budget to stay on track."

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        summary = ", ".join([f"{cat}: ₹{int(amt)}" for cat, amt in data.category_breakdown.items()])
        budget_info = f"Monthly budget: ₹{int(data.budget)}." if data.budget else "No budget set."

        prompt = f"""Indian user expense data:
- This month total: ₹{int(data.month_total)}
- Today's total: ₹{int(data.today_total)}
- {budget_info}
- Category breakdown: {summary or 'No categories yet'}

Give exactly 3 numbered practical money-saving tips.
Be friendly. Use Indian context (mention UPI, Swiggy, kirana shops, etc.).
No markdown formatting. Plain text only. Maximum 2 sentences per tip."""

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"1. Track your daily chai and auto expenses — small amounts add up fast!\n2. Consider cooking at home instead of ordering from Swiggy 2-3 days a week.\n3. Set a monthly budget to get a spending score and stay financially healthy."
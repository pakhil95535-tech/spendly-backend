from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.ai import InsightRequest, InsightResponse
from app.services.ai_service import get_insights

router = APIRouter(prefix="/ai", tags=["AI Insights"])

@router.post("/insights", response_model=InsightResponse)
async def ai_insights(
    data: InsightRequest,
    current_user: User = Depends(get_current_user)
):
    text = await get_insights(data)
    return InsightResponse(insights=text)
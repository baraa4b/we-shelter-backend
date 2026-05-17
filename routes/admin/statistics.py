from fastapi import APIRouter, Depends

from schemas.statistics import StatisticsResponse
from services import statistics_service
from utils.deps import require_admin


router = APIRouter(
    prefix="/admin",
    tags=["admin-statistics"],
    dependencies=[Depends(require_admin)],
)


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics() -> StatisticsResponse:
    return await statistics_service.get_statistics()

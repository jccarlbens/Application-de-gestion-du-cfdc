from fastapi import APIRouter, Depends

from app.api.v1.dto.dto_health import HealthResponse
from app.bll.bll_health import BllHealth

router = APIRouter(tags=["health"])


def get_bll_health() -> BllHealth:
    return BllHealth()


@router.get("/health", response_model=HealthResponse)
def read_health(bll: BllHealth = Depends(get_bll_health)) -> HealthResponse:
    health = bll.get_health()
    return HealthResponse(
        status="ok",
        database="reachable" if health.is_database_reachable else "unreachable",
    )

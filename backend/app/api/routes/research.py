from fastapi import APIRouter, HTTPException

from app.schemas.research import ResearchRequest, ResearchResponse
from app.services.research import execute_research

router = APIRouter(tags=["research"])


@router.post("/research", response_model=ResearchResponse)
def create_research(request: ResearchRequest) -> ResearchResponse:
    try:
        return execute_research(request)
    except Exception as exc:  # pragma: no cover - API boundary guard
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/research/{research_id}")
def get_research(research_id: str) -> dict[str, str]:
    return {"research_id": research_id, "status": "in_progress"}

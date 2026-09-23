from fastapi import APIRouter, HTTPException

from app.schemas.research import ResearchRequest, ResearchResponse
from app.services.research import execute_research

router = APIRouter(tags=["research"])


@router.post("/research", response_model=ResearchResponse)
def create_research(request: ResearchRequest) -> ResearchResponse:
    try:
        return execute_research(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Research workflow failed.") from exc


@router.get("/research/{research_id}")
def get_research(research_id: str) -> dict[str, str]:
    return {
        "research_id": research_id,
        "status": "not_persisted",
        "message": "Research results are returned by POST /research. Durable result storage is a future production milestone.",
    }

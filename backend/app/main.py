from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.research import router as research_router

app = FastAPI(title="Multi-Agent Research Assistant", version="0.1.0")
app.include_router(health_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Multi-Agent Research Assistant API"}

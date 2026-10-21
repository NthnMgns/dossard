from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.db import get_db_path, init_db
from app.errors import ApiError
from app.routers import athletes, competitions, registrations, results


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db(get_db_path())
    yield


app = FastAPI(title="Dossard", version="0.1.0", lifespan=lifespan)
app.include_router(competitions.router)
app.include_router(athletes.router)
app.include_router(registrations.router)
app.include_router(results.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(ApiError)
async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    """Toutes les erreurs métier sortent au format {"error": {"code", "message"}}."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )

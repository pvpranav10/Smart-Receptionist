from multiprocessing.connection import Client
import os

from fastapi import FastAPI
from supabase import create_client, Client
from app.api.appointments import router as appointments_router
from app.api.patients import router as patients_router
from app.api.search import router as search_router
from dotenv import load_dotenv

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Voice Register Cliniko API",
        version="0.1.0",
        description="FastAPI wrapper for Cliniko endpoints exposed as REST tool APIs.",
    )
    app.include_router(appointments_router, prefix="/appointments", tags=["appointments"])
    app.include_router(patients_router, prefix="/patients", tags=["patients"])
    app.include_router(search_router, tags=["search"])

    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()

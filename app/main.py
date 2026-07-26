import json
from multiprocessing.connection import Client
import os

from fastapi import FastAPI
from supabase import create_client, Client
from app.api.appointments import router as appointments_router
from app.api.patients import router as patients_router
from app.api.search import router as search_router
from app.clients.bolna_client import BolnaClient
from app.clients.cliniko_client import ClinikoClient
from app.config import settings
from dotenv import load_dotenv

# supabase: Client = create_client(
#     os.environ.get("SUPABASE_URL"),
#     os.environ.get("SUPABASE_KEY")
# )

def create_app() -> FastAPI:
    app = FastAPI(
        title="Voice Register Cliniko API",
        version="0.1.0",
        description="FastAPI wrapper for Cliniko endpoints exposed as REST tool APIs.",
    )
    app.include_router(appointments_router, prefix="/individual_appointments ", tags=["individual_appointments"])
    app.include_router(patients_router, prefix="/patients", tags=["patients"])
    app.include_router(search_router,prefix="/businesses", tags=["search"])

    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    @app.get("/intiated", tags=["intiated"])
    async def intiated(contact_number: str | None = None, agent_id: str | None = None, execution_id: str | None = None):
        if not contact_number:
            return {"status": "ok", "message": "No contact number provided"}

        phone_number = contact_number

        client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
        try:
            result = await client.list_patients()
        finally:
            await client.close()

        patients = result.get("patients", [])
        matched_patient = None
        for patient in patients:
            if not isinstance(patient, dict):
                continue
            if phone_number and any(str(phone_number) == str(pn.get("number")) for pn in patient.get("patient_phone_numbers", [])):
                matched_patient = patient
                break

        if matched_patient is None:
            return {"status": "ok", "message": "No matching patient found", "contact_number": contact_number}

        bolna_client = BolnaClient(settings.bolna_api_key or "", settings.bolna_base_url)
        try:
            customer_name = " ".join(
                part for part in [matched_patient.get("first_name"), matched_patient.get("last_name")] if part
            ).strip()
            response = {
                
                    "first_name": matched_patient.get("first_name"),
                    "last_name": matched_patient.get("last_name"),
            }
        finally:
            await bolna_client.close()

        return response

    return app


app = create_app()

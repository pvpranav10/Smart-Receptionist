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

    @app.post("/intiated", tags=["intiated"])
    async def intiated(payload: dict | None = None):
        if not payload:
            return {"status": "ok", "message": "No payload provided"}

        phone_number = None
        if isinstance(payload, dict):
            phone_number = payload.get("user_number") or payload.get("phone") or payload.get("mobile")

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
            return {"status": "ok", "message": "No matching patient found", "payload": payload}

        bolna_client = BolnaClient(settings.bolna_api_key or "", settings.bolna_base_url)
        try:
            customer_name = " ".join(
                part for part in [matched_patient.get("first_name"), matched_patient.get("last_name")] if part
            ).strip()
            bolna_payload = {
                "agent_id":settings.bolna_agent_id,
                "recipient_phone_number": phone_number,
                "from_phone_number": payload.get("from_phone_number") or settings.bolna_from_phone_number,
                "user_data": {
                    "first_name": matched_patient.get("first_name"),
                    "last_name": matched_patient.get("last_name"),
                },
            }
            await bolna_client.initiate_user_variables_bolna(bolna_payload)
        finally:
            await bolna_client.close()

        return {
            "status": "ok",
        }

    return app


app = create_app()

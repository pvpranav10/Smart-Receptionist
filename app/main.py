import json
from multiprocessing.connection import Client
import os
from datetime import datetime, timedelta

from fastapi import FastAPI
from app.api.appointments import router as appointments_router
from app.api.patients import router as patients_router
from app.api.search import router as search_router
from app.clients.bolna_client import BolnaClient
from app.clients.cliniko_client import ClinikoClient
from app.clients.supabase_client import SupabaseClient
from app.config import settings
from dotenv import load_dotenv



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
        db_client = SupabaseClient()

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
             response = {
                        "from_number":contact_number
                     }
             return response
        
        # Handle conversation state
        conversation_state = db_client.select("conversation_state", {"conversation_id": contact_number.lstrip('+')}, "partial")
        
        # If no conversation state exists or it's expired, create a new one
        if not conversation_state or (isinstance(conversation_state, list) and len(conversation_state) == 0):
            # Create new conversation state
            new_state = {
                "conversation_id": contact_number.lstrip('+'),
                "current_step": "START",
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat(),
                "patient_id": matched_patient.get("id"),
            }
            await db_client.insert("conversation_state", new_state)
            conversation_state = new_state
        else:
            # Handle list response from select
            if isinstance(conversation_state, list) and len(conversation_state) > 0:
                state_record = conversation_state[0]
                expires_at = datetime.fromisoformat(state_record.get("expires_at", ""))
                
                if expires_at < datetime.now():
                    # Expired, create new conversation state
                    new_state = {
                        "conversation_id": contact_number.lstrip('+'),
                        "current_step": "START",
                        "created_at": datetime.now().isoformat(),
                        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
                        "patient_id": matched_patient.get("id"),
                    }
                    await db_client.insert("conversation_state", new_state)
                    conversation_state = new_state
                else:
                    # Use existing state
                    conversation_state = state_record

            

        response = {
            "first_name": matched_patient.get("first_name"),
            "last_name": matched_patient.get("last_name"),
        }


        return response

    @app.post("/log_call_summary", tags=["log_call_summary  "])
    async def log_call_summary(payload:dict):
        call_summary = payload.get("summary")
        db_client = SupabaseClient()
        response = await db_client.update("conversation_state",{"conversation_summary":call_summary},{"conversation_id":payload.get("user_number")},"partial")


    return app


app = create_app()

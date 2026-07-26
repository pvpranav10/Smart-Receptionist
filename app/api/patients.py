from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException

from app.clients.cliniko_client import ClinikoClient
from app.config import settings
from app.helpers.conversation_helper import generate_conversation_id
from app.schemas.patients import PatientCreateRequest, PatientDetailResponse
from app.clients.supabase_client import SupabaseClient
from datetime import datetime, timedelta

router = APIRouter()


@router.get("", response_model=list[PatientDetailResponse])
async def list_patients() -> list[PatientDetailResponse]:
    client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
    try:
        result = await client.list_patients()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    finally:
        await client.close()

    patients = result.get("patients", [])
    return [
        PatientDetailResponse(
            patient_id=patient.get("id", 0),
            first_name=patient.get("first_name", ""),
            last_name=patient.get("last_name", ""),
            email=patient.get("email"),
            phone=patient.get("phone"),
            raw_data=patient,
        )
        for patient in patients
        if isinstance(patient, dict)
    ]


@router.post("", response_model=PatientDetailResponse)
async def create_patient(payload: PatientCreateRequest) -> PatientDetailResponse:
    try:
        client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
        db_client = SupabaseClient()
        request_payload = {
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "email": payload.email,
        }

        if payload.phone:
            request_payload["patient_phone_numbers"] = [
                {"number": payload.phone.lstrip('+'), "phone_type": "Mobile"}
            ]

            response = await client.create_patient(request_payload)
            conversation_id = generate_conversation_id(payload.phone)
            new_state = {
                            "conversation_id": conversation_id,
                            "current_step": "START",
                            "phone_number": payload.phone,
                           "expires_at": str((datetime.now() + timedelta(minutes=20)).isoformat()),
                            "patient_id": response.get("id"),
                            "updated_at":str(datetime.now())
                        }
            await db_client.insert("conversation_state", new_state)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    finally:
        await client.close()

    return PatientDetailResponse(
        patient_id=response.get("id", 0),
        first_name=response.get("first_name", payload.first_name or ""),
        last_name=response.get("last_name", payload.last_name or ""),
        email=response.get("email", payload.email),
        phone=response.get("phone"),
    )


@router.get("/{patient_id}", response_model=PatientDetailResponse)
async def get_patient(patient_id: int) -> PatientDetailResponse:
    client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
    try:
        result = await client.get_patient(patient_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Patient not found")
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    finally:
        await client.close()

    patient = result.get("patient", result)
    return PatientDetailResponse(
        patient_id=patient.get("id", patient_id),
        first_name=patient.get("first_name", ""),
        last_name=patient.get("last_name", ""),
        email=patient.get("email"),
        phone=patient.get("phone"),
        raw_data=patient,
    )

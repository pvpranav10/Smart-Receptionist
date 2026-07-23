from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException

from app.clients.cliniko_client import ClinikoClient
from app.config import settings
from app.schemas.patients import PatientDetailResponse

router = APIRouter()


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

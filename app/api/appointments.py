from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException

from app.clients.cliniko_client import ClinikoClient
from app.config import settings
from app.schemas.appointments import AppointmentBookingRequest, AppointmentBookingResponse

router = APIRouter()


@router.post("/book", response_model=AppointmentBookingResponse)
async def book_appointment(payload: AppointmentBookingRequest) -> AppointmentBookingResponse:
    location_id = settings.branch_location_map.get(payload.branch_name)
    if location_id is None:
        raise HTTPException(status_code=400, detail=f"Unknown branch name: {payload.branch_name}")

    client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
    try:
        result = await client.create_appointment(
            patient_id=payload.patient_id,
            appointment_type_id=payload.appointment_type_id,
            location_id=location_id,
            starts_at=payload.starts_at,
            note=payload.note,
            provider_id=payload.provider_id,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    finally:
        await client.close()

    appointment = result.get("appointment", {})
    return AppointmentBookingResponse(
        appointment_id=appointment.get("id", 0),
        status=appointment.get("status", "created"),
        starts_at=appointment.get("starts_at", payload.starts_at),
        location_id=appointment.get("location_id", location_id),
        raw_data=result,
    )

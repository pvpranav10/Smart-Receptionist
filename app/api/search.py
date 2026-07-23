from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.clients.cliniko_client import ClinikoClient
from app.config import settings
from app.schemas.search import AppointmentSlot, AvailabilityResponse

router = APIRouter()


@router.get("/availability", response_model=AvailabilityResponse)
async def search_availability(
    branch_name: str | None = Query(None, description="Branch key from BRANCH_LOCATION_MAP"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
) -> AvailabilityResponse:
    location_ids: list[int] | None = None
    if branch_name:
        location_id = settings.branch_location_map.get(branch_name)
        if location_id is None:
            raise HTTPException(status_code=400, detail=f"Unknown branch name: {branch_name}")
        location_ids = [location_id]

    client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
    try:
        result = await client.list_appointments(start_date=start_date, end_date=end_date, location_ids=location_ids)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    finally:
        await client.close()

    appointments = result.get("appointments", [])
    booked_slots: list[AppointmentSlot] = []
    for appointment in appointments:
        booked_slots.append(
            AppointmentSlot(
                appointment_id=appointment.get("id", 0),
                patient_name=" ".join(filter(None, [appointment.get("patient", {}).get("first_name"), appointment.get("patient", {}).get("last_name")])),
                starts_at=appointment.get("starts_at", ""),
                ends_at=appointment.get("ends_at"),
                location_id=appointment.get("location_id", 0),
            )
        )

    return AvailabilityResponse(
        branch_name=branch_name,
        location_id=location_ids[0] if location_ids else None,
        start_date=start_date,
        end_date=end_date,
        booked_slots=booked_slots,
        raw_data=result,
    )

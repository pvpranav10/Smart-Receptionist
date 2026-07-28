from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.clients.cliniko_client import ClinikoClient
from app.config import settings
from app.schemas.search import (
    AppointmentSlot,
    AvailabilityRequest,
    AvailabilityResponse,
    AvailableTimeResponse,
    BusinessesResponse,
    BusinessSummary,
    PractitionersRequest,
    PractitionersResponse,
    PractitionerSummary
)

router = APIRouter()


@router.get("", response_model=BusinessesResponse)
async def list_businesses() -> BusinessesResponse:
    client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
    try:
        result = await client.list_businesses()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    finally:
        await client.close()

    businesses = result.get("businesses", [])
    normalized_businesses = [
        BusinessSummary(
            id=str(item.get("id")) if item.get("id") is not None else None,
            business_name=item.get("business_name"),
            city=item.get("city"),
            appointment_type_ids=[str(appointment_type_id) for appointment_type_id in item.get("appointment_type_ids", [])],
        )
        for item in businesses
        if isinstance(item, dict)
    ]

    return BusinessesResponse(
        businesses=normalized_businesses,
        raw_data=result,
    )


@router.post("/practitioners", response_model=PractitionersResponse)
async def list_practitioners_for_businesses(request:PractitionersRequest) -> PractitionersResponse:
    client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
    try:
        result = await client.list_practitioners_for_businesses(request.business_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    finally:
        await client.close()

    practitioners = result.get("practitioners", [])
    normalized_practitioners = [
        PractitionerSummary(
            id=str(item.get("id")) if item.get("id") is not None else None,
            active=item.get("active"),
            display_name=item.get("display_name"),
            first_name=item.get("first_name"),
            last_name=item.get("last_name"),
            label=item.get("label"),
            title=item.get("title"),
            show_in_online_bookings=item.get("show_in_online_bookings"),
        )
        for item in practitioners
        if isinstance(item, dict)
    ]

    return PractitionersResponse(
        business_id=request.business_id,
        practitioners=normalized_practitioners,
        raw_data=result,
    )


@router.post(
    "/practitioners/available-times",
    response_model=AvailableTimeResponse,
)
async def get_available_times(
   avaliabilities_request: AvailabilityRequest
) -> AvailableTimeResponse:
    client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
    try:
        result = await client.get_available_times(
            business_id=avaliabilities_request.business_id,
            practitioner_id=avaliabilities_request.practitioner_id,
            appointment_type_id="1999469371147169774",#hardcoded for now
            from_date=avaliabilities_request.from_date,
            to_date=avaliabilities_request.to_date,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    finally:
        await client.close()

    available_times = result.get("available_times")
    return AvailableTimeResponse(
        available_times=available_times,
    )


# @router.get("/availability", response_model=AvailabilityResponse)
# async def search_availability(
#     branch_name: str | None = Query(None, description="Branch key from BRANCH_LOCATION_MAP"),
#     start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
#     end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
# ) -> AvailabilityResponse:
#     location_ids: list[int] | None = None
#     if branch_name:
#         location_id = settings.branch_location_map.get(branch_name)
#         if location_id is None:
#             raise HTTPException(status_code=400, detail=f"Unknown branch name: {branch_name}")
#         location_ids = [location_id]

#     client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
#     try:
#         result = await client.list_appointments(start_date=start_date, end_date=end_date, location_ids=location_ids)
#     except httpx.HTTPStatusError as exc:
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     finally:
#         await client.close()

#     appointments = result.get("appointments", [])
#     booked_slots: list[AppointmentSlot] = []
#     for appointment in appointments:
#         booked_slots.append(
#             AppointmentSlot(
#                 appointment_id=appointment.get("id", 0),
#                 patient_name=" ".join(filter(None, [appointment.get("patient", {}).get("first_name"), appointment.get("patient", {}).get("last_name")])),
#                 starts_at=appointment.get("starts_at", ""),
#                 ends_at=appointment.get("ends_at"),
#                 location_id=appointment.get("location_id", 0),
#             )
#         )

#     return AvailabilityResponse(
#         branch_name=branch_name,
#         location_id=location_ids[0] if location_ids else None,
#         start_date=start_date,
#         end_date=end_date,
#         booked_slots=booked_slots,
#         raw_data=result,
#     )

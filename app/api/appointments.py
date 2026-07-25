from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException

from app.clients.cliniko_client import ClinikoClient
from app.config import settings
from app.schemas.appointments import AppointmentBookingRequest, AppointmentBookingResponse, AppointmentCancelRequest, AppointmentUpdateRequest

router = APIRouter()


@router.get("/{appointment_id}", response_model=AppointmentBookingResponse)
async def get_individual_appointment(appointment_id: int) -> AppointmentBookingResponse:
    client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
    try:
        result = await client.get_individual_appointment(appointment_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Appointment not found")
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    finally:
        await client.close()

    appointment = result.get("appointment", result)
    return AppointmentBookingResponse(
        created_at=appointment.get("created_at"),
        deleted_at=appointment.get("deleted_at"),
        did_not_arrive=appointment.get("did_not_arrive"),
        ends_at=appointment.get("ends_at"),
        id=str(appointment.get("id", appointment_id)) if appointment.get("id") is not None else None,
        patient_arrived=appointment.get("patient_arrived"),
        patient_name=appointment.get("patient_name"),
        repeat_rule=appointment.get("repeat_rule", {}),
        repeats=appointment.get("repeats"),
        sms_reminder_sent=appointment.get("sms_reminder_sent"),
        starts_at=appointment.get("starts_at"),
        raw_data=result,
    )

@router.post("", response_model=AppointmentBookingResponse)
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
            ends_at=payload.ends_at,
            patient_case_id=payload.patient_case_id,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    finally:
        await client.close()

    appointment = result.get("appointment", result)
    return AppointmentBookingResponse(
        created_at=appointment.get("created_at"),
        deleted_at=appointment.get("deleted_at"),
        did_not_arrive=appointment.get("did_not_arrive"),
        ends_at=appointment.get("ends_at"),
        id=str(appointment.get("id", 0)) if appointment.get("id") is not None else None,
        patient_arrived=appointment.get("patient_arrived"),
        patient_name=appointment.get("patient_name"),
        repeat_rule=appointment.get("repeat_rule", {}),
        repeats=appointment.get("repeats"),
        sms_reminder_sent=appointment.get("sms_reminder_sent"),
        starts_at=appointment.get("starts_at", payload.starts_at),
        raw_data=result,
    )
# @router.post("", response_model=AppointmentBookingResponse)
# async def update_individual_appointment(appointment_id: int, payload: AppointmentUpdateRequest) -> AppointmentBookingResponse:
#     client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
#     try:
#         result = await client.update_individual_appointment(appointment_id, payload.model_dump(exclude_none=True))
#     except httpx.HTTPStatusError as exc:
#         if exc.response.status_code == 404:
#             raise HTTPException(status_code=404, detail="Appointment not found")
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     finally:
#         await client.close()

#     appointment = result.get("appointment", result)
#     return AppointmentBookingResponse(
#         created_at=appointment.get("created_at"),
#         deleted_at=appointment.get("deleted_at"),
#         did_not_arrive=appointment.get("did_not_arrive"),
#         ends_at=appointment.get("ends_at"),
#         id=str(appointment.get("id", appointment_id)) if appointment.get("id") is not None else None,
#         patient_arrived=appointment.get("patient_arrived"),
#         patient_name=appointment.get("patient_name"),
#         repeat_rule=appointment.get("repeat_rule", {}),
#         repeats=appointment.get("repeats"),
#         sms_reminder_sent=appointment.get("sms_reminder_sent"),
#         starts_at=appointment.get("starts_at"),
#         raw_data=result,
#     )


# @router.patch("/{appointment_id}/cancel", response_model=AppointmentBookingResponse)
# async def cancel_individual_appointment(appointment_id: int, payload: AppointmentCancelRequest) -> AppointmentBookingResponse:
#     client = ClinikoClient(settings.cliniko_api_key, settings.cliniko_base_url)
#     try:
#         result = await client.cancel_individual_appointment(appointment_id, payload.model_dump(exclude_none=True))
#     except httpx.HTTPStatusError as exc:
#         if exc.response.status_code == 404:
#             raise HTTPException(status_code=404, detail="Appointment not found")
#         raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
#     finally:
#         await client.close()

#     appointment = result.get("appointment", result)
#     return AppointmentBookingResponse(
#         created_at=appointment.get("created_at"),
#         deleted_at=appointment.get("deleted_at"),
#         did_not_arrive=appointment.get("did_not_arrive"),
#         ends_at=appointment.get("ends_at"),
#         id=str(appointment.get("id", appointment_id)) if appointment.get("id") is not None else None,
#         patient_arrived=appointment.get("patient_arrived"),
#         patient_name=appointment.get("patient_name"),
#         repeat_rule=appointment.get("repeat_rule", {}),
#         repeats=appointment.get("repeats"),
#         sms_reminder_sent=appointment.get("sms_reminder_sent"),
#         starts_at=appointment.get("starts_at"),
#         raw_data=result,
#     )




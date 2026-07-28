from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AppointmentBookingRequest(BaseModel):
    patient_case_id: str
    appointment_type_id: str
    business_id: str
    starts_at: str
    ends_at: str | None = None
    note: str | None = None
    practitioner_id: str | None = None
    patient_id: str | None = None

    class Config:
        extra = "allow"


class AppointmentUpdateRequest(BaseModel):
    appointment_type_id: str | None = "1999469371147169774"
    business_id: str | None = None
    ends_at: str | None = None
    patient_id: str | None = None
    patient_case_id: str | None = None
    practitioner_id: str | None = None
    starts_at: str | None = None
    appointement_id :str

    class Config:
        extra = "allow"


class AppointmentCancelRequest(AppointmentUpdateRequest):

    class Config:
        extra = "allow"


class AppointmentBookingResponse(BaseModel):
    created_at: str | None = None
    deleted_at: str | None = None
    did_not_arrive: bool | None = None
    ends_at: str | None = None
    id: str | None = None
    patient_arrived: bool | None = None
    patient_name: str | None = None
    repeat_rule: dict[str, Any] = Field(default_factory=dict)
    repeats: Any = None
    sms_reminder_sent: bool | None = None
    starts_at: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    detail: str

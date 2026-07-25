from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AppointmentBookingRequest(BaseModel):
    patient_id: int
    appointment_type_id: int
    branch_name: str
    starts_at: str
    ends_at: str | None = None
    note: str | None = None
    provider_id: int | None = None
    patient_case_id: int | None = None

    class Config:
        extra = "allow"


class AppointmentUpdateRequest(BaseModel):
    appointment_type_id: int | None = None
    business_id: int | None = None
    ends_at: str | None = None
    notes: str | None = None
    patient_id: int | None = None
    patient_case_id: int | None = None
    practitioner_id: int | None = None
    starts_at: str | None = None
    repeat_rule: dict[str, Any] | None = None

    class Config:
        extra = "allow"


class AppointmentCancelRequest(BaseModel):
    cancellation_note: str | None = None
    cancellation_reason: int | None = None
    apply_to_repeats: bool | None = None

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

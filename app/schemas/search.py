from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AppointmentSlot(BaseModel):
    appointment_id: int
    patient_name: str | None = None
    starts_at: str
    ends_at: str | None = None
    location_id: int


class BusinessSummary(BaseModel):
    id: str | None = None
    business_name: str | None = None
    city: str | None = None
    appointment_type_ids: list[str] = Field(default_factory=list)


class BusinessesResponse(BaseModel):
    businesses: list[BusinessSummary] = Field(default_factory=list)
    raw_data: dict[str, Any] = Field(default_factory=dict)


class PractitionerSummary(BaseModel):
    id: str | None = None
    active: bool | None = None
    display_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    label: str | None = None
    title: str | None = None
    show_in_online_bookings: bool | None = None


class PractitionersResponse(BaseModel):
    business_id: int
    practitioners: list[PractitionerSummary] = Field(default_factory=list)
    raw_data: dict[str, Any] = Field(default_factory=dict)


class AvailabilityResponse(BaseModel):
    branch_name: str | None = None
    location_id: int | None = None
    start_date: str
    end_date: str
    booked_slots: list[AppointmentSlot]
    raw_data: dict[str, Any] = Field(default_factory=dict)


class AvailableTimeResponse(BaseModel):
    business_id: int
    practitioner_id: int
    appointment_type_id: int
    from_date: str
    to_date: str
    available_times: list[dict[str, Any]] = Field(default_factory=list)
    raw_data: dict[str, Any] = Field(default_factory=dict)

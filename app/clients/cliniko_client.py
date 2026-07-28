from __future__ import annotations

import base64
from typing import Any

import httpx


class ClinikoClient:
    def __init__(self, api_key: str, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        credentials = f"{api_key}:"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("ascii")
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "test",
            "username": api_key,
            "password": "",
        }
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=30.0)

    async def create_appointment(
        self,
        patient_id: int,
        appointment_type_id: int,
        business_id: int,
        starts_at: str,
        practitioner_id: int | None = None,
        ends_at: str | None = None,
        patient_case_id: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "appointment_type_id": str(appointment_type_id),
            "business_id": str(business_id),
            "patient_id": str(patient_id),
            "practitioner_id": str(practitioner_id) if practitioner_id is not None else None,
            "starts_at": starts_at,
            "repeat_rule": {},
        }
        if ends_at is not None:
            payload["ends_at"] = ends_at
        if note is not None:
            payload["notes"] = note
        if patient_case_id is not None:
            payload["patient_case_id"] = str(patient_case_id)

        response = await self.client.post("/individual_appointments", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_individual_appointment(self, appointment_id: int) -> dict[str, Any]:
        response = await self.client.get(f"/individual_appointments/{appointment_id}")
        response.raise_for_status()
        return response.json()

    async def update_individual_appointment(self, appointment_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self.client.patch(f"/individual_appointments/{appointment_id}", json=payload)
        response.raise_for_status()
        return response.json()

    async def cancel_individual_appointment(self, appointment_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self.client.patch(f"/individual_appointments/{appointment_id}/cancel", json=payload)
        response.raise_for_status()
        return response.json()

    async def create_patient(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self.client.post("/patients", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_patient(self, patient_id: int) -> dict[str, Any]:
        response = await self.client.get(f"/patients/{patient_id}")
        response.raise_for_status()
        return response.json()

    async def list_patients(self) -> dict[str, Any]:
        response = await self.client.get("/patients")
        response.raise_for_status()
        return response.json()

    async def list_businesses(self) -> dict[str, Any]:
        response = await self.client.get("/businesses")
        response.raise_for_status()
        return response.json()

    async def list_practitioners_for_businesses(self, business_id: int) -> dict[str, Any]:
        response = await self.client.get(f"/businesses/{business_id}/practitioners")
        response.raise_for_status()
        return response.json()

    async def get_available_times(
        self,
        business_id: int,
        practitioner_id: int,
        appointment_type_id: int,
        from_date: str,
        to_date: str,
    ) -> dict[str, Any]:
        params = {"from": from_date, "to": to_date}
        response = await self.client.get(
            f"/businesses/{business_id}/practitioners/{practitioner_id}/appointment_types/{appointment_type_id}/available_times",
            params=params,
        )
        response.raise_for_status()
        return response.json()

    async def list_appointments(
        self,
        start_date: str,
        end_date: str,
        business_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "since": start_date,
            "until": end_date,
        }
        if location_ids:
            params["location_id[]"] = [str(location_id) for location_id in location_ids]

        response = await self.client.get("/appointments", params=params)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self.client.aclose()

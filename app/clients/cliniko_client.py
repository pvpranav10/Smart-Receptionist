from __future__ import annotations

from typing import Any

import httpx


class ClinikoClient:
    def __init__(self, api_key: str, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=30.0)

    async def create_appointment(
        self,
        patient_id: int,
        appointment_type_id: int,
        location_id: int,
        starts_at: str,
        note: str | None = None,
        provider_id: int | None = None,
    ) -> dict[str, Any]:
        payload = {
            "appointment": {
                "patient_id": patient_id,
                "appointment_type_id": appointment_type_id,
                "location_id": location_id,
                "starts_at": starts_at,
            }
        }
        if note is not None:
            payload["appointment"]["note"] = note
        if provider_id is not None:
            payload["appointment"]["provider_id"] = provider_id

        response = await self.client.post("/appointments", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_patient(self, patient_id: int) -> dict[str, Any]:
        response = await self.client.get(f"/patients/{patient_id}")
        response.raise_for_status()
        return response.json()

    async def list_appointments(
        self,
        start_date: str,
        end_date: str,
        location_ids: list[int] | None = None,
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

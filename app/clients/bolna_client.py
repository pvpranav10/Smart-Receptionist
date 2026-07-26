from __future__ import annotations

from typing import Any

import httpx


class BolnaClient:
    def __init__(self, api_key: str, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=30.0)

    async def initiate_user_variables_bolna(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self.client.post("/call", json=payload)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self.client.aclose()
